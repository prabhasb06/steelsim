import asyncio
import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from types import SimpleNamespace

import pytest

from app.acamis import model_gateway as gateway
from app.api.acamis import _model_context
from test_rolling_detector import plant_engine


def test_connect_requires_generation_and_preserves_existing_connection_on_failure(monkeypatch):
    previous = {'connected': True, 'model': 'working'}
    sim = SimpleNamespace(acamis_model_config=previous)
    calls = []
    def request(url, **kw):
        calls.append(kw['method'])
        raise ValueError('MODEL RATE LIMIT REACHED')
    monkeypatch.setattr(gateway, '_request_json', request)
    with pytest.raises(ValueError, match='RATE LIMIT'):
        asyncio.run(gateway.connect(sim, 'OPENAI_COMPATIBLE', 'test', 'test-key', 'https://provider.example/v1'))
    assert calls == ['POST']
    assert sim.acamis_model_config is previous


def test_catalog_pagination_and_generation_verification(monkeypatch):
    sim = SimpleNamespace(acamis_model_config=None)
    calls = []
    def request(url, **kw):
        calls.append(url)
        if kw.get('method') == 'POST':
            return {'candidates': [{'content': {'parts': [{'text': 'Verified'}]}}]}
        if 'pageToken=second' in url:
            return {'models': [{'name': 'models/gemini-test-flash', 'supportedGenerationMethods': ['generateContent']}]}
        return {'models': [{'name': 'models/gemini-image', 'supportedGenerationMethods': ['generateContent']}], 'nextPageToken': 'second'}
    monkeypatch.setattr(gateway, '_request_json', request)
    result = asyncio.run(gateway.connect(sim, 'GEMINI', 'auto', 'test-key', None))
    assert result['connected']
    assert result['model'] == 'gemini-test-flash'
    assert len(calls) == 3
    assert calls[-1].endswith('gemini-test-flash:generateContent')
    assert 'test-key' not in json.dumps(result)


def test_review_failure_updates_connection_status(monkeypatch):
    sim = SimpleNamespace(acamis_model_config={'provider': 'OPENAI_COMPATIBLE', 'model': 'test', 'api_key': 'fake', 'base_url': 'https://provider.example', 'connected': True})
    monkeypatch.setattr(gateway, '_request_json', lambda *a, **k: {'choices': [{'message': {'content': None}}]})
    with pytest.raises(ValueError, match='empty text'):
        asyncio.run(gateway.ask(sim, 'Review', {}))
    assert not gateway.public_status(sim)['connected']


def test_context_contains_telemetry_not_gateway_or_previous_replies():
    sim = plant_engine()
    context = _model_context(sim)
    assert context['snapshot']['node_telemetry']
    assert 'model_gateway' not in context
    assert 'model_advisory' not in context
    assert 'audit' not in context


@pytest.mark.parametrize('url', ['http://localhost.attacker.example/v1', 'https://user:secret@example.com/v1', 'https://example.com/v1?key=secret'])
def test_invalid_base_urls_are_rejected(url):
    with pytest.raises(ValueError):
        asyncio.run(gateway.connect(SimpleNamespace(), 'OPENAI_COMPATIBLE', 'test', 'fake', url))


def test_actual_http_transport_uses_key_and_operational_context(monkeypatch):
    requests = []
    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            requests.append((self.path, self.headers.get('Authorization'), payload))
            body = json.dumps({'choices': [{'message': {'content': 'Review received'}}]}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)

    monkeypatch.setenv('STEELSIM_ALLOW_LOCAL_MODEL_ENDPOINTS', '1')
    server = ThreadingHTTPServer(('127.0.0.1', 0), Provider)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        sim = SimpleNamespace(acamis_model_config=None)
        asyncio.run(gateway.connect(sim, 'OPENAI_COMPATIBLE', 'test', 'fake-local-key', f'http://127.0.0.1:{server.server_port}/v1'))
        result = asyncio.run(gateway.ask(sim, 'Assess the plant', {'snapshot': {'tick': 42}}))
        assert result['reply'] == 'Review received'
        assert len(requests) == 2
        assert all(r[0] == '/v1/chat/completions' and r[1] == 'Bearer fake-local-key' for r in requests)
        assert '42' in requests[-1][2]['messages'][1]['content']
        assert 'fake-local-key' not in json.dumps(requests[-1][2])
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize('url', [
    'https://127.0.0.1/v1/chat/completions',
    'https://169.254.169.254/latest/meta-data',
    'http://localhost/v1/chat/completions',
])
def test_model_transport_rejects_internal_addresses_by_default(monkeypatch, url):
    monkeypatch.delenv('STEELSIM_ALLOW_LOCAL_MODEL_ENDPOINTS', raising=False)
    with pytest.raises(ValueError, match='private or local|developer opt-in'):
        gateway._request_json(url, api_key='fake', provider='OPENAI_COMPATIBLE', method='POST')


def test_model_transport_rejects_private_dns_alias(monkeypatch):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *args, **kwargs: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('10.0.0.8', 443)),
    ])
    with pytest.raises(ValueError, match='private or local'):
        gateway._request_json('https://model.example/v1', api_key='fake', provider='OPENAI_COMPATIBLE')


def test_model_transport_does_not_follow_redirects_or_read_oversized_replies(monkeypatch):
    monkeypatch.setenv('STEELSIM_ALLOW_LOCAL_MODEL_ENDPOINTS', '1')
    requests = []

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            requests.append(self.path)
            if self.path == '/redirect':
                self.send_response(302)
                self.send_header('Location', '/secret')
                self.end_headers()
            elif self.path == '/large':
                data = b'{' + b' ' * (gateway.MAX_MODEL_RESPONSE_BYTES + 1) + b'}'
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(200)
                self.end_headers()

    server = ThreadingHTTPServer(('127.0.0.1', 0), Provider)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f'http://127.0.0.1:{server.server_port}'
        with pytest.raises(ValueError, match='redirects are not allowed'):
            gateway._request_json(f'{base}/redirect', api_key='fake', provider='OPENAI_COMPATIBLE')
        assert requests == ['/redirect']
        with pytest.raises(ValueError, match='oversized response'):
            gateway._request_json(f'{base}/large', api_key='fake', provider='OPENAI_COMPATIBLE')
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_operator_message_size_is_bounded(monkeypatch):
    sim = SimpleNamespace(acamis_model_config={
        'provider': 'OPENAI_COMPATIBLE', 'model': 'test', 'api_key': 'fake',
        'base_url': 'https://provider.example', 'connected': True,
    })
    monkeypatch.setattr(gateway, '_request_json', lambda *a, **k: pytest.fail('network request was made'))
    with pytest.raises(ValueError, match='too long'):
        asyncio.run(gateway.ask(sim, 'x' * (gateway.MAX_OPERATOR_MESSAGE_LENGTH + 1), {}))
    assert sim.acamis_model_config['connected']
