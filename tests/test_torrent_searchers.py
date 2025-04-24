import pytest
from spotify_syncer.torrent_searchers import create_searcher, PirateBayTorrentSearcher, AbstractTorrentSearcher

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
