"""Market Intel: feed parsing (RSS + Atom) and deterministic relevance routing."""
import market_intel as mi

RSS = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Feed</title>
<item><title>Startup raises seed round</title>
<link>https://example.com/a</link>
<description>A hiring startup about verification.</description>
<pubDate>Wed, 01 Jan 2026 00:00:00 GMT</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>AtomFeed</title>
<entry><title>Recruiter tools update</title>
<link href="https://example.com/b"/>
<summary>News about recruiter and campus hiring.</summary>
<updated>2026-01-02T00:00:00Z</updated></entry>
</feed>"""


def test_parse_rss():
    items = mi._parse_feed(RSS, "Feed")
    assert len(items) == 1
    assert items[0]["title"] == "Startup raises seed round"
    assert items[0]["link"] == "https://example.com/a"


def test_parse_atom_link_href():
    items = mi._parse_feed(ATOM, "AtomFeed")
    assert items[0]["link"] == "https://example.com/b"
    assert "recruiter" in items[0]["summary"].lower()


def test_parse_garbage_is_safe():
    assert mi._parse_feed(b"not xml at all", "x") == []


def test_relevance_scoring_and_routing():
    kws = ["verification", "hiring", "recruiter"]
    assert mi._score_relevance("a verification and hiring story", kws) == ["hiring", "verification"]
    assert mi._route(2) == "flag-for-review"
    assert mi._route(1) == "log"
    assert mi._route(0) == "ignore"
