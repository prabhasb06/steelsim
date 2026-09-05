from fastapi.testclient import TestClient
from app.api.routes import manager
from app.acamis import detector, service
from main import app


def test_demo_endpoint_changes_telemetry_without_creating_incident():
    with TestClient(app) as client:
        plant = client.get('/api/plant/template/tmt').json()
        sim_id = client.post('/api/simulations', json={'plant': plant}).json()['id']
        try:
            base = f'/api/simulations/{sim_id}'
            assert client.post(base + '/acamis/monitoring/demo').status_code == 409
            client.post(base + '/command', json={'command': 'start'})
            response = client.post(base + '/acamis/monitoring/demo')
            assert response.status_code == 200
            assert response.json()['incident'] is None
            assert response.json()['automatic_monitoring']['demo_active']
            assert client.post(base + '/acamis/monitoring/demo').status_code == 409
            assert client.post(base + '/acamis/scenarios/' + detector.INCIDENT).status_code == 409
            cleared = client.post(base + '/acamis/scenarios/reset').json()
            assert not cleared['automatic_monitoring']['demo_active']
            assert cleared['automatic_monitoring']['state'] == 'Normal'
        finally:
            client.delete(base)
