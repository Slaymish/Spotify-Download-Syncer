import os
import subprocess
import shutil
import pytest

from spotify_syncer.torrent_searchers import SoulseekSearcher


@pytest.fixture(autouse=True)
def ensure_download_dir(tmp_path, monkeypatch):
    monkeypatch.setenv('DOWNLOAD_DIR', str(tmp_path))
    yield


def test_soulseek_cli_not_found(monkeypatch):
    monkeypatch.setattr(shutil, 'which', lambda x: None)
    searcher = SoulseekSearcher()
    result = searcher.search('test query')
    assert result is None


def test_soulseek_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(shutil, 'which', lambda x: '/usr/local/bin/soulseek')
    calls = []
    fallback_query = 'mainquery (extra) - fallback'

    def fake_run(cmd, *args, **kwargs):
        calls.append(cmd)
        if cmd[0] == 'soulseek' and cmd[1] == 'query':
            rc = 0 if any(fallback_query in str(arg) for arg in cmd) else 1
            class Result:
                returncode = rc
            return Result()
        if cmd[0] == 'soulseek' and cmd[1] == 'download':
            dest = cmd[cmd.index('--destination') + 1]
            filepath = os.path.join(dest, 'downloaded.mp3')
            open(filepath, 'w').close()
            return None
        raise RuntimeError('unexpected command')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    state = iter([[], ['downloaded.mp3']])
    monkeypatch.setattr(os, 'listdir', lambda d: next(state, ['downloaded.mp3']))

    searcher = SoulseekSearcher()
    searcher.sanitize = lambda q: fallback_query
    url = searcher.search('irrelevant')
    assert url and url.startswith('file://')
    assert any(fallback_query in str(c) for c in calls if isinstance(c, list))


def test_soulseek_query_error(monkeypatch):
    monkeypatch.setattr(shutil, 'which', lambda x: '/usr/local/bin/soulseek')
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: (_ for _ in ()).throw(Exception('fail')))
    searcher = SoulseekSearcher()
    assert searcher.search('test') is None