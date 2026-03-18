from app.rag.generator import _expand_adjacent_article_ids


def test_expand_adjacent_article_ids_numeric():
    base = {"41", "79"}
    expanded = _expand_adjacent_article_ids(base, window=2)
    # should include 39-43 for 41 and 77-81 for 79
    assert "39" in expanded and "43" in expanded
    assert "77" in expanded and "81" in expanded
    # original ids must be preserved
    assert "41" in expanded and "79" in expanded


def test_expand_adjacent_article_ids_ignores_non_numeric():
    base = {"IV", "10"}
    expanded = _expand_adjacent_article_ids(base, window=1)
    # 'IV' is non-numeric token; only '10' should expand to 9 and 11
    assert "9" in expanded and "11" in expanded
    assert "IV" in expanded
