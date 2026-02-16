import sys
from pathlib import Path
import pytest
import socket

# ----------------------------------------
# Make src importable
# ----------------------------------------
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ----------------------------------------
# Disable real network calls during tests
# ----------------------------------------
@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def guard(*args, **kwargs):
        raise RuntimeError("Network calls are disabled during tests.")
    monkeypatch.setattr(socket, "socket", guard)
