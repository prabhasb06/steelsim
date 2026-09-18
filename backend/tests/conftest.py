"""Never let test collection write into the operator's history database."""
import os
import tempfile

_history_directory = tempfile.TemporaryDirectory(prefix='steelsim-test-history-')
os.environ['STEELSIM_HISTORY_DB'] = os.path.join(_history_directory.name, 'history.sqlite3')
