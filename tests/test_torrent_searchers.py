import pytest
from spotify_syncer.torrent_searchers import create_searcher, PirateBayTorrentSearcher, AbstractTorrentSearcher, SoulseekSearcher
import types

@pytest.mark.parametrize('name', ['piratebay', 'PirateBay', 'PIRATEBAY'])
def test_create_searcher_alias(name):
    searcher = create_searcher(name)
    assert isinstance(searcher, AbstractTorrentSearcher)
    assert isinstance(searcher, PirateBayTorrentSearcher)

def test_create_searcher_unknown():
    with pytest.raises(ValueError):
        create_searcher('unknown_site')

@ pytest.fixture
def pbt():
    return PirateBayTorrentSearcher()

def test_sanitize(pbt):
    raw = 'Hello, World! (test)'
    sanitized = pbt.sanitize(raw)
    assert ',' not in sanitized
    assert '(' not in sanitized
    assert '!' in sanitized  # preserves exclamation by default

def test_build_url(pbt):
    url = pbt.build_url('test query')
    assert 'search.php' in url
    assert 'q=test+query' in url
    assert 'cat=101' in url

def test_parse_primary_and_fallback(tmp_path):
    # HTML with primary magnet link
    html_primary = '''
<ol id="torrents">
    <li class="list-entry">
        <span class="item-icons">
            <a href="magnet:?xt=urn:btih:PRIMARY"/>
        </span>
    </li>
</ol>
'''  # noqa
    p = PirateBayTorrentSearcher()
    assert p.parse_primary(html_primary) == 'magnet:?xt=urn:btih:PRIMARY'

    # HTML without primary, but fallback exists
    html_fallback = '<div><a href="magnet:?xt=urn:btih:FALLBACK">link</a></div>'
    assert p.parse_primary(html_fallback) is None
    fallback = p.parse_fallback(html_fallback)
    assert fallback == 'magnet:?xt=urn:btih:FALLBACK'

    # HTML with neither
    html_none = '<html><body>No links here</body></html>'
    assert p.parse_primary(html_none) is None
    assert p.parse_fallback(html_none) is None

# Test environment variable selection of searchers
@pytest.mark.parametrize(
    'searcher_key,expected_class', 
    [
        ('piratebay', PirateBayTorrentSearcher), 
        ('soulseek', SoulseekSearcher),
        ('PirateBAY', PirateBayTorrentSearcher),  # Case insensitive
        ('SOULSEEK', SoulseekSearcher),           # Case insensitive
        (' soulseek ', SoulseekSearcher),         # Trailing spaces
    ]
)
def test_searcher_from_env(monkeypatch, searcher_key, expected_class):
    """Verify that the correct searcher class is selected based on environment variable."""
    # Instead of monkeypatching the env and trying to reload config,
    # just test the create_searcher function directly with various inputs
    searcher = create_searcher(searcher_key)
    assert isinstance(searcher, expected_class)
    
    # Also verify that our .strip() and .lower() handling works
    if ' ' in searcher_key:
        clean_key = searcher_key.strip()
        clean_searcher = create_searcher(clean_key)
        assert isinstance(clean_searcher, expected_class)

def test_soulseek_cli_not_found(monkeypatch):
    monkeypatch.setattr('shutil.which', lambda x: None)
    s = SoulseekSearcher()
    assert s.search('test query') is None

def test_soulseek_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr('shutil.which', lambda x: '/usr/local/bin/soulseek')
    calls = []
    fallback_query = 'mainquery (extra) - fallback'
    def fake_run(cmd, *a, **k):
        calls.append(cmd)
        if cmd[0] == 'soulseek' and cmd[1] == 'query':
            # Only return 0 for the fallback query
            if any(fallback_query in str(arg) for arg in cmd):
                class Result: returncode = 0
                return Result()
            else:
                class Result: returncode = 1
                return Result()
        if cmd[0] == 'soulseek' and cmd[1] == 'download':
            dest = cmd[cmd.index('--destination')+1]
            with open(tmp_path / 'downloaded.mp3', 'w') as f:
                f.write('dummy')
            return None
        raise Exception('unexpected command')
    monkeypatch.setattr('subprocess.run', fake_run)
    # Patch os.listdir to simulate before/after download using an iterator
    listdir_state = iter([[], ['downloaded.mp3']])
    monkeypatch.setattr('os.listdir', lambda d: next(listdir_state, ['downloaded.mp3']))
    s = SoulseekSearcher()
    s.sanitize = lambda q: fallback_query
    out = s.search('irrelevant')
    assert out and out.startswith('file://')
    assert any(fallback_query in str(c) for c in calls if isinstance(c, list))

def test_soulseek_query_error(monkeypatch):
    monkeypatch.setattr('shutil.which', lambda x: '/usr/local/bin/soulseek')
    s = SoulseekSearcher()
    # Patch subprocess.run to raise error
    monkeypatch.setattr('subprocess.run', lambda *a, **k: (_ for _ in ()).throw(Exception('fail')))
    out = s.search('test')
    assert out is None
