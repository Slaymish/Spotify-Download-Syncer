import pytest
from spotify_syncer.qb_client import QbClient

class DummyClient:
    def __init__(self, **kwargs):
        self.login_called = False
        self.added = None
    def auth_log_in(self):
        self.login_called = True
    def torrents_add(self, urls, save_path):
        self.added = (urls, save_path)

@pytest.fixture(autouse=True)
def patch_qb(monkeypatch):
    dummy = DummyClient()
    # Patch the qbittorrentapi.Client used in QbClient
    import spotify_syncer.qb_client as qb_client_module
    monkeypatch.setattr(qb_client_module.qbittorrentapi, 'Client', lambda **kwargs: dummy)
    return dummy


def test_init_auth(patch_qb):
    client = QbClient()
    assert patch_qb.login_called is True


def test_add_torrent(patch_qb):
    client = QbClient()
    client.add_torrent('magnetURI', '/tmp')
    assert patch_qb.added == ('magnetURI', '/tmp')