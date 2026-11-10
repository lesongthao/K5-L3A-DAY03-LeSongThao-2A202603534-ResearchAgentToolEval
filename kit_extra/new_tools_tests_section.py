

# =====================================================================
# 2. Team-added tools (wikipedia, hackernews, github_repos, hf_models) — >= 3 tests per tool
# =====================================================================

wikipedia = TOOL_FUNCTIONS["wikipedia"]
hackernews = TOOL_FUNCTIONS["hackernews"]
github_repos = TOOL_FUNCTIONS["github_repos"]
hf_models = TOOL_FUNCTIONS["hf_models"]


# ---------------- wikipedia ----------------

def test_wikipedia_search_maps_pages_and_enriches_top_summary(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "pages": [
            {"key": "Andrej_Karpathy", "title": "Andrej Karpathy",
             "excerpt": "<span class=\"searchmatch\">Andrej</span> Karpathy is", "description": "AI researcher"},
            {"key": "Karpathy", "title": "Karpathy", "excerpt": "surname", "description": ""},
        ],
        "extract": "Andrej Karpathy is a Slovak-Canadian computer scientist.",
    }))
    result = wikipedia(query="Andrej Karpathy", lang="en", limit=2)

    assert calls[0]["url"] == "https://en.wikipedia.org/w/rest.php/v1/search/page"
    assert calls[0]["params"] == {"q": "Andrej Karpathy", "limit": 2}
    assert "User-Agent" in calls[0]["headers"]
    assert calls[1]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/Andrej_Karpathy"
    assert [item["url"] for item in result["items"]] == [
        "https://en.wikipedia.org/wiki/Andrej_Karpathy", "https://en.wikipedia.org/wiki/Karpathy"]
    assert result["items"][0]["summary"].startswith("Andrej Karpathy is a Slovak")
    assert "<span" not in result["items"][1]["summary"]


def test_wikipedia_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse({"pages": []}))
    empty = wikipedia(query="   ")
    assert empty["error"] == "ValueError"
    assert calls == []  # empty query never hits the network

    result = wikipedia(query="Transformer", lang="Vietnamese!!", limit="999")
    assert calls[0]["url"].startswith("https://en.wikipedia.org/")  # invalid lang -> en
    assert calls[0]["params"]["limit"] == 10  # string + out of range -> clamped
    assert result["items"] == []


def test_wikipedia_vi_lang_uses_vi_domain(fake_http) -> None:
    calls = fake_http(FakeResponse({"pages": [{"key": "Học_máy", "title": "Học máy"}]}))
    result = wikipedia(query="Học máy", lang="VI")

    assert calls[0]["url"] == "https://vi.wikipedia.org/w/rest.php/v1/search/page"
    assert result["items"][0]["source"] == "vi.wikipedia.org"


def test_wikipedia_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))
    result = wikipedia(query="Yann LeCun")
    assert result == {"tool": "wiki_search", "error": "HTTPError", "message": "HTTP 503"}


# ---------------- hackernews ----------------

def test_hackernews_top_week_builds_request_and_maps_hits(fake_http, monkeypatch) -> None:
    monkeypatch.setattr("tools.hackernews.tool.time.time", lambda: 1_000_000)
    calls = fake_http(FakeResponse({"hits": [
        {"objectID": "42", "title": "Rust 2.0", "url": "https://blog.rust-lang.org/x", "points": 300,
         "num_comments": 120, "author": "steve", "created_at": "2026-11-01T00:00:00Z"},
        {"objectID": "43", "title": "Ask HN: Rust?", "url": None, "points": 10, "num_comments": 5},
        {"title": "no id"},
    ]}))
    result = hackernews(query="Rust", sort="top", timeframe="week", limit=5)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"] == {"query": "Rust", "tags": "story", "hitsPerPage": 5,
                                  "numericFilters": "created_at_i>395200"}
    assert len(result["items"]) == 2
    first, ask = result["items"]
    assert first["source"] == "blog.rust-lang.org"
    assert first["discussion_url"] == "https://news.ycombinator.com/item?id=42"
    assert first["metrics"] == {"points": 300, "comments": 120}
    assert ask["url"] == "https://news.ycombinator.com/item?id=43"  # Ask HN has no external url


def test_hackernews_latest_uses_search_by_date_and_no_time_filter(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    hackernews(query="Claude", sort="latest")

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert "numericFilters" not in calls[0]["params"]


def test_hackernews_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    assert hackernews(query="")["error"] == "ValueError"
    assert calls == []

    result = hackernews(query="AI", sort="Most popular", timeframe="forever", limit="0")
    assert calls[0]["url"].endswith("/search")  # unknown sort -> top
    assert "numericFilters" not in calls[0]["params"]  # unknown timeframe -> all
    assert calls[0]["params"]["hitsPerPage"] == 1  # "0" -> clamped to 1
    assert (result["sort"], result["timeframe"]) == ("top", "all")


def test_hackernews_network_error_returns_error_dict(fake_http) -> None:
    import requests

    fake_http(requests.Timeout("timed out"))
    result = hackernews(query="AI")
    assert result["error"] == "Timeout"


# ---------------- github_repos ----------------

def test_github_repos_builds_qualifiers_and_maps_items(fake_http, monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    calls = fake_http(FakeResponse({"total_count": 1, "items": [
        {"full_name": "qdrant/qdrant", "html_url": "https://github.com/qdrant/qdrant", "description": "Vector DB",
         "language": "Rust", "stargazers_count": 25000, "forks_count": 1500, "pushed_at": "2026-11-09T00:00:00Z"},
        {"html_url": "https://github.com/broken"},
    ]}))
    result = github_repos(query="vector database", language="Rust", sort="stars", limit=5)

    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {"q": "vector database language:Rust", "per_page": 5, "sort": "stars", "order": "desc"}
    assert "Authorization" not in calls[0]["headers"]
    assert result["items"] == [{
        "title": "qdrant/qdrant", "url": "https://github.com/qdrant/qdrant", "source": "github.com",
        "summary": "Vector DB", "language": "Rust", "date": "2026-11-09T00:00:00Z",
        "metrics": {"stars": 25000, "forks": 1500},
    }]


def test_github_repos_token_is_sent_but_never_returned(fake_http, monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_SECRET")
    calls = fake_http(FakeResponse({"items": []}))
    result = github_repos(query="agent", created_within="month", sort="best_match")

    assert calls[0]["headers"]["Authorization"] == "Bearer ghp_SECRET"
    assert "created:>" in calls[0]["params"]["q"]
    assert "sort" not in calls[0]["params"]  # best_match = GitHub default ordering
    assert "ghp_SECRET" not in str(result)


def test_github_repos_bad_input_from_model(fake_http, monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    calls = fake_http(FakeResponse({"items": []}))
    assert github_repos(query=" ")["error"] == "ValueError"
    assert calls == []

    github_repos(query="llm", language="C++ \" OR evil:", sort="popularity", created_within="decade", limit=-4)
    params = calls[0]["params"]
    assert params["q"] == 'llm language:"C++  OR evil"'  # quotes/colons stripped from the qualifier
    assert params["sort"] == "stars"  # out-of-enum -> default
    assert params["per_page"] == 1


def test_github_repos_rate_limit_returns_error_dict(fake_http, monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    fake_http(FakeResponse(status_code=403))
    assert github_repos(query="agent")["error"] == "HTTPError"


# ---------------- hf_models ----------------

def test_hf_models_task_and_sort_mapping(fake_http) -> None:
    calls = fake_http(FakeResponse([
        {"id": "black-forest-labs/FLUX.1-dev", "pipeline_tag": "text-to-image", "downloads": 9, "likes": 3},
        {"downloads": 1},
    ]))
    result = hf_models(task="Text to Image", sort="trending", limit=3)

    assert calls[0]["url"] == "https://huggingface.co/api/models"
    assert calls[0]["params"] == {"sort": "trendingScore", "direction": -1, "limit": 3, "pipeline_tag": "text-to-image"}
    assert len(result["items"]) == 1
    assert result["items"][0]["url"] == "https://huggingface.co/black-forest-labs/FLUX.1-dev"
    assert result["items"][0]["metrics"] == {"downloads": 9, "likes": 3}


def test_hf_models_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse({"error": "not a list"}))
    assert hf_models(query="", task="")["error"] == "ValueError"
    assert calls == []

    result = hf_models(query="whisper", sort="most downloaded", limit="50")
    assert calls[0]["params"]["sort"] == "downloads"
    assert calls[0]["params"]["limit"] == 20
    assert calls[0]["params"]["search"] == "whisper"
    assert result["items"] == []  # non-list payload handled, no crash


def test_hf_models_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=500))
    assert hf_models(query="llama")["error"] == "HTTPError"
