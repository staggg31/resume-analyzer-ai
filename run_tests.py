"""run_tests.py — comprehensive automated test suite for ResumeLens AI (Groq Provider)"""
import ast
import copy
import json
import os
import sys
from unittest.mock import MagicMock, patch

# Set dummy key for test environment so client instantiation tests can succeed when needed
os.environ["GROQ_API_KEY"] = "gsk_test_placeholder_key_abc123456789"

print("=" * 60)
print("RUNNING RESUMELENS AI TEST SUITE (GROQ INTEGRATION)")
print("=" * 60)

# ---------------------------------------------------------------------------
# 1. Syntax Validation
# ---------------------------------------------------------------------------
for fname in ["analyzer.py", "backend/main.py", "pdf_reader.py", "prompts.py"]:
    with open(fname, encoding="utf-8") as f:
        ast.parse(f.read())
    print(f"Syntax OK: {fname}")

from analyzer import (
    _DEFAULT_MODEL,
    _call_with_retry,
    _get_client,
    _get_model_name,
    _is_transient_error,
    _parse_analysis_response,
    _raise_api_error,
    _sanitize_error_message,
    analyze_resume,
    improve_bullet,
)
from groq import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
)

# ---------------------------------------------------------------------------
# 2. Model Configuration & Env Overrides
# ---------------------------------------------------------------------------
default_model = _get_model_name()
assert default_model == "openai/gpt-oss-120b", f"Expected 'openai/gpt-oss-120b', got: {default_model}"
print(f"Default Groq model ({default_model}): OK")

os.environ["GROQ_MODEL"] = "llama-3.3-70b-versatile"
assert _get_model_name() == "llama-3.3-70b-versatile"
del os.environ["GROQ_MODEL"]
assert _get_model_name() == "openai/gpt-oss-120b"
print("Environment model override (GROQ_MODEL): OK")

# ---------------------------------------------------------------------------
# 3. Missing GROQ_API_KEY Handling
# ---------------------------------------------------------------------------
saved_key = os.environ.pop("GROQ_API_KEY", None)
try:
    _get_client()
    print("FAIL: _get_client should raise EnvironmentError when GROQ_API_KEY is missing")
    sys.exit(1)
except EnvironmentError as e:
    assert "GROQ_API_KEY is not set" in str(e)
    print("Missing GROQ_API_KEY handling: OK")
finally:
    if saved_key:
        os.environ["GROQ_API_KEY"] = saved_key

# ---------------------------------------------------------------------------
# 4. JSON Parsing & Safeguards
# ---------------------------------------------------------------------------
SAMPLE = {
    "match_percentage": 82,
    "matching_skills": ["Python", "FastAPI", "REST APIs"],
    "missing_skills": ["Kubernetes", "AWS"],
    "strengths": ["Strong backend experience with Python and API design"],
    "improvements": ["Add cloud deployment projects and containerization"],
    "relevant_experience": ["3 years developing web services in Python"],
    "suggested_keywords": ["Microservices", "Docker", "CI/CD"],
    "interview_topics": ["FastAPI architecture", "Database optimization"],
    "summary": "Strong candidate match for Python backend engineering with solid fundamentals.",
}

# Plain JSON
parsed_plain = _parse_analysis_response(json.dumps(SAMPLE))
assert parsed_plain["match_percentage"] == 82
assert parsed_plain["matching_skills"] == SAMPLE["matching_skills"]
print("Plain JSON parse: OK")

# Fenced ```json ... ```
fenced_json = "```json\n" + json.dumps(SAMPLE) + "\n```"
parsed_fenced = _parse_analysis_response(fenced_json)
assert parsed_fenced["match_percentage"] == 82
print("Fenced ```json ... ``` parse: OK")

# Plain fence ``` ... ```
plain_fence = "```\n" + json.dumps(SAMPLE) + "\n```"
parsed_plain_fence = _parse_analysis_response(plain_fence)
assert parsed_plain_fence["match_percentage"] == 82
print("Plain fence ``` ... ``` parse: OK")

# JSON embedded in conversational text
embedded_json = f"Here is the resume analysis:\n```json\n{json.dumps(SAMPLE)}\n```\nHope this helps!"
parsed_embedded = _parse_analysis_response(embedded_json)
assert parsed_embedded["match_percentage"] == 82
print("Embedded JSON parse: OK")

# Clamping match_percentage
high_sample = copy.deepcopy(SAMPLE)
high_sample["match_percentage"] = 140
assert _parse_analysis_response(json.dumps(high_sample))["match_percentage"] == 100

low_sample = copy.deepcopy(SAMPLE)
low_sample["match_percentage"] = -25
assert _parse_analysis_response(json.dumps(low_sample))["match_percentage"] == 0

str_score_sample = copy.deepcopy(SAMPLE)
str_score_sample["match_percentage"] = "78"
assert _parse_analysis_response(json.dumps(str_score_sample))["match_percentage"] == 78
print("Match percentage clamping and coercion: OK")

# Missing required key
missing_key_sample = copy.deepcopy(SAMPLE)
del missing_key_sample["summary"]
try:
    _parse_analysis_response(json.dumps(missing_key_sample))
    print("FAIL: should raise ValueError for missing required key")
    sys.exit(1)
except ValueError as e:
    assert "summary" in str(e)
    print("Missing schema key detection: OK")

# Malformed JSON
try:
    _parse_analysis_response("This is completely invalid non-JSON output.")
    print("FAIL: should raise ValueError for malformed JSON")
    sys.exit(1)
except ValueError as e:
    assert "could not be parsed as JSON" in str(e)
    print("Malformed JSON error handling: OK")

# ---------------------------------------------------------------------------
# 5. Error Sanitization & Categorization
# ---------------------------------------------------------------------------
# Secret key sanitization
test_secret = "gsk_live_supersecrettoken9876543210"
os.environ["GROQ_API_KEY"] = test_secret
sanitized = _sanitize_error_message(f"Error communicating with Groq: Key {test_secret} rejected.")
assert test_secret not in sanitized
assert "[REDACTED]" in sanitized
print("Secret key redaction: OK")

# 401 Authentication error
try:
    _raise_api_error(Exception("401 Unauthorized invalid_api_key"), "openai/gpt-oss-120b")
except RuntimeError as e:
    msg = str(e)
    assert "invalid groq api key" in msg.lower(), msg
    assert "401" in msg
    assert test_secret not in msg
    print("401 Authentication error handling: OK")

# 404 Model not found
try:
    _raise_api_error(Exception("404 model not found"), "old-retired-model")
except RuntimeError as e:
    msg = str(e)
    assert "not found" in msg.lower(), msg
    assert "old-retired-model" in msg
    assert "404" in msg
    print("404 Model not found error handling: OK")

# 429 Rate limit / Quota exceeded
try:
    _raise_api_error(Exception("429 rate_limit_exceeded quota reached"), "openai/gpt-oss-120b")
except RuntimeError as e:
    msg = str(e)
    assert "rate limit" in msg.lower() or "quota" in msg.lower(), msg
    assert "429" in msg
    assert "openai/gpt-oss-120b" in msg
    print("429 Rate limit / Quota error handling: OK")

# 503 Temporary capacity / service unavailable
try:
    _raise_api_error(Exception("503 Service Unavailable"), "openai/gpt-oss-120b")
except RuntimeError as e:
    msg = str(e)
    assert "temporarily unavailable" in msg.lower(), msg
    assert "openai/gpt-oss-120b" in msg
    print("503 Temporary unavailability handling: OK")

# Connection error
try:
    _raise_api_error(Exception("Connection error: connection refused"), "openai/gpt-oss-120b")
except RuntimeError as e:
    msg = str(e)
    assert "failed to connect" in msg.lower(), msg
    print("Connection error handling: OK")

# ---------------------------------------------------------------------------
# 6. Transient Error Classification
# ---------------------------------------------------------------------------
assert _is_transient_error(Exception("503 Service Unavailable")) is True
assert _is_transient_error(Exception("Temporary capacity issue: overloaded")) is True
assert _is_transient_error(Exception("401 Unauthorized invalid api key")) is False
assert _is_transient_error(Exception("404 Not Found")) is False
assert _is_transient_error(Exception("400 Bad Request")) is False
assert _is_transient_error(Exception("429 Rate limit exceeded")) is False
print("Transient error classification: OK")

# ---------------------------------------------------------------------------
# 7. Bounded Retry Behavior
# ---------------------------------------------------------------------------
# Permanent error (401 / 404 / 429): Must fail immediately without retry (1 attempt)
mock_client_perm = MagicMock()
mock_client_perm.chat.completions.create.side_effect = Exception("401 Unauthorized invalid_api_key")
try:
    _call_with_retry(mock_client_perm, "openai/gpt-oss-120b", "test prompt", delays=(0.001, 0.001, 0.001))
    print("FAIL: permanent error should raise RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    assert "invalid groq api key" in str(e).lower()
    assert mock_client_perm.chat.completions.create.call_count == 1
    print("Retry: permanent error rejected immediately (1 attempt, no retries): OK")

# 429 Quota: Must fail immediately without retry (1 attempt)
mock_client_quota = MagicMock()
mock_client_quota.chat.completions.create.side_effect = Exception("429 Rate limit exceeded")
try:
    _call_with_retry(mock_client_quota, "openai/gpt-oss-120b", "test prompt", delays=(0.001, 0.001, 0.001))
    print("FAIL: 429 quota error should raise RuntimeError")
    sys.exit(1)
except RuntimeError as e:
    assert "rate limit" in str(e).lower()
    assert mock_client_quota.chat.completions.create.call_count == 1
    print("Retry: 429 rate limit rejected immediately (1 attempt, no retries): OK")

# Transient error: Recovers on retry attempt 2
mock_client_trans = MagicMock()
mock_success_choice = MagicMock()
mock_success_choice.message.content = json.dumps(SAMPLE)
mock_success_resp = MagicMock()
mock_success_resp.choices = [mock_success_choice]
mock_client_trans.chat.completions.create.side_effect = [
    Exception("503 Service Unavailable"),
    mock_success_resp,
]
res = _call_with_retry(mock_client_trans, "openai/gpt-oss-120b", "test prompt", delays=(0.001, 0.001, 0.001))
assert json.loads(res)["match_percentage"] == 82
assert mock_client_trans.chat.completions.create.call_count == 2
print("Retry: transient 503 recovered on retry 2: OK")

# Transient error: Exhausts all 3 retries with expected delays
mock_client_fail = MagicMock()
mock_client_fail.chat.completions.create.side_effect = Exception("503 Capacity spike")
recorded_sleeps = []
with patch("time.sleep", side_effect=lambda s: recorded_sleeps.append(s)):
    try:
        _call_with_retry(mock_client_fail, "openai/gpt-oss-120b", "test prompt")
        print("FAIL: should raise RuntimeError after exhausting retries")
        sys.exit(1)
    except RuntimeError as e:
        assert "temporarily unavailable" in str(e).lower()
        # 1 initial + 3 retries = 4 total attempts
        assert mock_client_fail.chat.completions.create.call_count == 4
        assert recorded_sleeps == [2.0, 5.0, 10.0]
        print("Retry: transient 503 exhausts 3 retries with [2s, 5s, 10s] delays: OK")

# ---------------------------------------------------------------------------
# 8. Mocked Public Functions (analyze_resume & improve_bullet)
# ---------------------------------------------------------------------------
with patch("analyzer._get_client") as mock_get_client:
    mock_sdk_client = MagicMock()
    mock_get_client.return_value = mock_sdk_client

    # analyze_resume
    choice_analysis = MagicMock()
    choice_analysis.message.content = json.dumps(SAMPLE)
    resp_analysis = MagicMock()
    resp_analysis.choices = [choice_analysis]
    mock_sdk_client.chat.completions.create.return_value = resp_analysis

    res_analysis = analyze_resume("Python candidate resume", "Python developer job description")
    assert res_analysis["match_percentage"] == 82
    assert "Python" in res_analysis["matching_skills"]
    # Verify response_format was passed as json_object
    call_kwargs = mock_sdk_client.chat.completions.create.call_args[1]
    assert call_kwargs["response_format"] == {"type": "json_object"}
    assert call_kwargs["model"] == "openai/gpt-oss-120b"
    print("Mocked analyze_resume with Groq JSON response format: OK")

    # improve_bullet
    choice_bullet = MagicMock()
    choice_bullet.message.content = "Spearheaded high-performance API design using FastAPI and Python."
    resp_bullet = MagicMock()
    resp_bullet.choices = [choice_bullet]
    mock_sdk_client.chat.completions.create.return_value = resp_bullet

    improved = improve_bullet("Created some python endpoints")
    assert improved == "Spearheaded high-performance API design using FastAPI and Python."
    print("Mocked improve_bullet with Groq: OK")

# ---------------------------------------------------------------------------
# 9. PDF Reader Validation
# ---------------------------------------------------------------------------
from pdf_reader import extract_text_from_pdf, truncate_resume_text

try:
    extract_text_from_pdf(b"not a valid pdf")
    print("FAIL: should raise RuntimeError for bad PDF bytes")
    sys.exit(1)
except RuntimeError:
    print("Bad PDF handling: OK")

assert "[Resume truncated" in truncate_resume_text("Z" * 20000, max_chars=100)
assert truncate_resume_text("Short text", max_chars=100) == "Short text"
print("PDF text truncation: OK")

# ---------------------------------------------------------------------------
# 10. FastAPI Endpoints & Contracts
# ---------------------------------------------------------------------------
from fastapi.testclient import TestClient
from backend.main import app as fastapi_app

test_client = TestClient(fastapi_app)

# GET /api/health
health_res = test_client.get("/api/health")
assert health_res.status_code == 200
assert health_res.json()["status"] == "ok"
assert health_res.json()["model"] == "openai/gpt-oss-120b"
print("FastAPI: GET /api/health returns active Groq model: OK")

# POST /api/analyze-resume validation
missing_file_res = test_client.post("/api/analyze-resume", data={"job_description": "Python Developer"})
assert missing_file_res.status_code == 400
assert "PDF file is required" in missing_file_res.json()["detail"]

txt_file_res = test_client.post(
    "/api/analyze-resume",
    files={"resume": ("sample.txt", b"plain text", "text/plain")},
    data={"job_description": "Valid JD"}
)
assert txt_file_res.status_code == 400
assert "Only text-based PDF files are supported" in txt_file_res.json()["detail"]

empty_jd_res = test_client.post(
    "/api/analyze-resume",
    files={"resume": ("sample.pdf", b"%PDF-1.4 dummy", "application/pdf")},
    data={"job_description": "   "}
)
assert empty_jd_res.status_code == 400
assert "Job description cannot be empty" in empty_jd_res.json()["detail"]
print("FastAPI: POST /api/analyze-resume input validation: OK")

# POST /api/improve-bullet validation and mock execution
empty_bullet_res = test_client.post("/api/improve-bullet", json={"bullet": "  "})
assert empty_bullet_res.status_code in (400, 422)

with patch("backend.main.improve_bullet", return_value="Engineered low-latency microservices with Python and FastAPI"):
    bullet_res = test_client.post(
        "/api/improve-bullet",
        json={"bullet": "Worked on backend APIs", "context": "Python backend"}
    )
    assert bullet_res.status_code == 200
    assert bullet_res.json()["improved_bullet"] == "Engineered low-latency microservices with Python and FastAPI"
    assert bullet_res.json()["original_bullet"] == "Worked on backend APIs"
print("FastAPI: POST /api/improve-bullet mock execution: OK")

# POST /api/analyze-resume mock execution
with patch("backend.main.extract_text_from_pdf", return_value="Candidate resume text with Python"):
    with patch("backend.main.analyze_resume", return_value=SAMPLE):
        mock_analysis_res = test_client.post(
            "/api/analyze-resume",
            files={"resume": ("resume.pdf", b"%PDF-1.4 dummy", "application/pdf")},
            data={"job_description": "Python Backend Engineer"}
        )
        assert mock_analysis_res.status_code == 200
        data = mock_analysis_res.json()
        assert data["match_percentage"] == 82
        assert "Python" in data["matching_skills"]
        assert "Kubernetes" in data["missing_skills"]
        assert data["summary"] == SAMPLE["summary"]
print("FastAPI: POST /api/analyze-resume mock execution: OK")

print()
print("=" * 60)
print("ALL TESTS PASSED (100% Mocked - 0 Live Groq API calls).")
print("=" * 60)
