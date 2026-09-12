from __future__ import annotations

from api.errors import humanize_exception, humanize_message


def test_daily_usage_limit():
    raw = (
        "Error code: 429 - {'error': {'message': 'Rate limit reached for model "
        "`openai/gpt-oss-20b` on tokens per day (TPD): Limit 200000, Used 198824, "
        "Requested 2739. Please try again in 11m15.216s.'}}"
    )
    err = humanize_message(raw)
    assert err.title == "Daily usage limit reached"
    assert "tokens for today" in err.message or "free-tier" in err.message
    assert "minute" in err.message
    assert "429" not in err.message
    assert "groq" not in err.message.lower()


def test_long_wait_treated_as_daily_limit():
    err = humanize_exception(
        Exception("429 rate limit exceeded. Please try again in 16145.09s")
    )
    assert err.title == "Daily usage limit reached"
    assert "269" in err.message or "minute" in err.message


def test_demo_unavailable_for_missing_key():
    err = humanize_message("GROQ_API_KEY is not set. Add it as a secret on the API host.")
    assert err.title == "This demo isn't available right now"
    assert "api key" not in err.message.lower()


def test_unknown_demo():
    err = humanize_message("Unknown demo: foo")
    assert err.title == "Demo not found"


def test_json_parse_error():
    err = humanize_message("Expecting ',' delimiter: line 1 column 1283 (char 1282)")
    assert err.title == "Couldn't finish the response"
    assert "delimiter" not in err.message
    assert "1283" not in err.message


def test_model_not_found():
    err = humanize_message(
        "The model meta-llama/llama-4-scout-17b-16e-instruct does not exist "
        "or you do not have access to it."
    )
    assert err.title == "Vision model unavailable"
    assert "meta-llama" not in err.message


def test_youtube_bot_check_not_demo_unavailable():
    err = humanize_exception(
        Exception(
            "youtube transcript unavailable; "
            "ytdlp=DownloadError: Sign in to confirm you're not a bot"
        )
    )
    assert err.title == "Couldn't fetch the transcript"
    assert "caption" in err.message.lower() or "blocked" in err.message.lower()


def test_unknown_includes_exception_detail():
    err = humanize_exception(RuntimeError("weird failure xyz"))
    assert err.title == "Something went wrong"
    assert "RuntimeError" in err.message
    assert "weird failure xyz" in err.message
