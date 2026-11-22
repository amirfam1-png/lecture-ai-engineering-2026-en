"""Lecture 05 homework (Implementation): adjacent-page retrieval. No API key needed."""

import json

import pytest

from app import retrieval, tools
from app.retrieval import add_neighbor_pages, load_pages


def page(doc, n):
    return {"page_id": f"{doc}-p{n:03d}", "document_id": doc, "page": n,
            "title": f"{doc} {n}", "section": "s", "content": f"text {doc} {n}"}


PAGES = [page("lec01-main", n) for n in range(1, 6)] + [page("lec02-main", n) for n in range(1, 6)]


def hit(doc, n, distance=0.1):
    return {**page(doc, n), "distance": distance}


def ids(results):
    return [r["page_id"] for r in results]


def test_window_zero_is_normal_retrieval():
    hits = [hit("lec01-main", 3), hit("lec02-main", 1)]
    results = add_neighbor_pages(hits, 0, PAGES)
    assert results == hits  # unchanged, no extra fields


def test_neighbors_follow_their_hit_in_page_order():
    results = add_neighbor_pages([hit("lec01-main", 3)], 1, PAGES)
    assert ids(results) == ["lec01-main-p003", "lec01-main-p002", "lec01-main-p004"]
    assert [r.get("offset") for r in results] == [None, -1, 1]
    assert results[1]["neighbor_of"] == "lec01-main-p003"


def test_neighbors_never_cross_documents():
    # lec01-main p005 is the last page; lec02-main p001 is the first. Neither should pull in the other.
    results = add_neighbor_pages([hit("lec01-main", 5), hit("lec02-main", 1)], 1, PAGES)
    assert ids(results) == ["lec01-main-p005", "lec01-main-p004", "lec02-main-p001", "lec02-main-p002"]
    for r in results:
        if r["retrieval"] == "neighbor":
            assert r["document_id"] == r["neighbor_of"].rsplit("-p", 1)[0]


def test_no_duplicates_and_hits_keep_their_rank():
    # p002 and p004 are both hits; p003 is a neighbor of both but must appear once.
    hits = [hit("lec01-main", 2, 0.1), hit("lec01-main", 4, 0.2)]
    results = add_neighbor_pages(hits, 1, PAGES)
    assert ids(results) == ["lec01-main-p002", "lec01-main-p001", "lec01-main-p003",
                            "lec01-main-p004", "lec01-main-p005"]
    assert len(set(ids(results))) == len(results)
    assert [r["page_id"] for r in results if r["retrieval"] == "search"] == ids(hits)


def test_adjacent_hit_is_not_relabelled_as_neighbor():
    hits = [hit("lec01-main", 2), hit("lec01-main", 3)]
    results = add_neighbor_pages(hits, 1, PAGES)
    roles = {r["page_id"]: r["retrieval"] for r in results}
    assert roles["lec01-main-p003"] == "search"
    assert "distance" in next(r for r in results if r["page_id"] == "lec01-main-p003")


def test_neighbors_carry_text_and_citation_metadata():
    pages = [dict(p) for p in PAGES]
    pages[1]["citation"] = "Lecture 01 p.2"
    results = add_neighbor_pages([hit("lec01-main", 3)], 1, pages)
    neighbor = results[1]
    assert neighbor["content"] == "text lec01-main 2"
    assert neighbor["citation"] == "Lecture 01 p.2"
    assert "distance" not in neighbor  # neighbors were not ranked by similarity


def test_unknown_hit_is_kept_without_neighbors():
    results = add_neighbor_pages([hit("lec09-main", 1)], 1, PAGES)
    assert ids(results) == ["lec09-main-p001"]


def test_negative_window_is_rejected():
    with pytest.raises(ValueError):
        add_neighbor_pages([], -1, PAGES)


def test_real_materials_page_52_neighbors():
    """Check against the bundled materials: the LoRA page from the exercise question."""
    pages = load_pages()
    target = next(p for p in pages if p["page_id"] == "lec02-main-p052")
    results = add_neighbor_pages([{**target, "distance": 0.0}], 1, pages)
    assert ids(results) == ["lec02-main-p052", "lec02-main-p051", "lec02-main-p053"]


def test_search_materials_tool_returns_neighbors(monkeypatch):
    monkeypatch.setattr(retrieval, "search", lambda query: [hit("lec01-main", 3)])
    monkeypatch.setattr(retrieval, "load_pages", lambda source=None: PAGES)
    monkeypatch.setattr(retrieval, "RAG_NEIGHBOR_PAGES", 1)
    monkeypatch.setattr(retrieval.search_with_neighbors, "__defaults__", (1,))
    data = json.loads(tools.search_materials("anything"))
    assert ids(data["results"]) == ["lec01-main-p003", "lec01-main-p002", "lec01-main-p004"]
