"""
analyzer.py
Handles all communication with the Groq API and parses the structured response.
This module has no frontend or Streamlit dependency — it is pure Python.
"""

import json
import logging
import os
import re
import time
from typing import Optional

from dotenv import load_dotenv
from groq import (
    Groq,
    APIStatusError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    InternalServerError,
    APIConnectionError,
    APITimeoutError,
    BadRequestError,
)

from prompts import RESUME_ANALYSIS_PROMPT, BULLET_IMPROVEMENT_PROMPT

logger = logging.getLogger(__name__)

# Load .env so GROQ_API_KEY is available when running locally.
load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# The model is read from .env so it can be changed without touching source code.
# Override by setting GROQ_MODEL=<model-name> in your .env file.
# Default is 'openai/gpt-oss-120b', verified active on the Groq Developer tier
# with 131k context and native JSON object support.
_DEFAULT_MODEL = "openai/gpt-oss-120b"

# Increasing backoff delays (in seconds) between retry attempts for transient errors.
_RETRY_DELAYS: tuple[float, ...] = (2.0, 5.0, 10.0)


def _get_model_name() -> str:
    """Return the configured Groq model name (env override or default)."""
    return os.getenv("GROQ_MODEL", _DEFAULT_MODEL).strip()


# Required keys that must be present in a valid analysis response.
REQUIRED_ANALYSIS_KEYS = {
    "match_percentage",
    "matching_skills",
    "missing_skills",
    "strengths",
    "improvements",
    "relevant_experience",
    "suggested_keywords",
    "interview_topics",
    "summary",
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_client() -> Groq:
    """
    Create and return a configured Groq API client.

    Raises:
        EnvironmentError: If GROQ_API_KEY is not set.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Create a .env file with GROQ_API_KEY=your_key_here and restart the app."
        )
    return Groq(api_key=api_key)


def _sanitize_error_message(msg: str) -> str:
    """Remove any API keys, tokens, or authorization headers from an error message."""
    sanitized = msg

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key in sanitized:
        sanitized = sanitized.replace(groq_key, "[REDACTED]")

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key in sanitized:
        sanitized = sanitized.replace(gemini_key, "[REDACTED]")

    # Redact typical Groq API key pattern (gsk_...)
    sanitized = re.sub(r"gsk_[a-zA-Z0-9_-]{15,}", "[REDACTED]", sanitized)
    # Redact Authorization header values if present
    sanitized = re.sub(r"Bearer\s+[a-zA-Z0-9_\-\.]{15,}", "Bearer [REDACTED]", sanitized, flags=re.IGNORECASE)

    return sanitized


def _raise_api_error(exc: Exception, model: str) -> None:
    """
    Convert a raw Groq API exception into a clear, sanitized RuntimeError.

    Surfaces clean, user-facing messages for 401 (auth), 404 (model not found),
    429 (rate limit / quota), and 503 (temporary unavailability) without revealing
    the API key, secrets, or raw traceback.

    Raises:
        RuntimeError: Always.
    """
    raw_msg = str(getattr(exc, "message", None) or exc)
    sanitized_msg = _sanitize_error_message(raw_msg)
    status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)

    # 401 Authentication / Invalid key
    if (
        isinstance(exc, AuthenticationError)
        or status_code == 401
        or "401" in sanitized_msg
        or "unauthenticated" in sanitized_msg.lower()
        or "invalid api key" in sanitized_msg.lower()
        or "invalid_api_key" in sanitized_msg.lower()
    ):
        raise RuntimeError(
            f"Invalid Groq API key (HTTP 401). Please verify GROQ_API_KEY in your .env file."
        ) from exc

    # 429 Rate limit or Quota exhaustion
    if (
        isinstance(exc, RateLimitError)
        or status_code == 429
        or "429" in sanitized_msg
        or "rate_limit" in sanitized_msg.lower()
        or "rate limit" in sanitized_msg.lower()
        or "quota" in sanitized_msg.lower()
        or "resource_exhausted" in sanitized_msg.lower()
    ):
        raise RuntimeError(
            f"Groq API rate limit or request quota exceeded for model '{model}' (HTTP 429). "
            f"Please wait a moment for the limit to reset, or override the model by setting "
            f"GROQ_MODEL=<model-name> in your .env file."
        ) from exc

    # 404 Model Not Found
    if (
        isinstance(exc, NotFoundError)
        or status_code == 404
        or "404" in sanitized_msg
        or "not_found" in sanitized_msg.lower()
        or "not found" in sanitized_msg.lower()
    ):
        raise RuntimeError(
            f"Model '{model}' was not found or is no longer available on Groq (HTTP 404). "
            f"Set GROQ_MODEL=<valid-model-name> in your .env file. "
            f"API detail: {sanitized_msg}"
        ) from exc

    # 503 / 500 / Service Unavailable / Capacity spike
    if (
        isinstance(exc, InternalServerError)
        or status_code in (500, 502, 503, 504)
        or "503" in sanitized_msg
        or "unavailable" in sanitized_msg.lower()
        or "service unavailable" in sanitized_msg.lower()
    ):
        raise RuntimeError(
            f"The Groq API is temporarily unavailable (model: '{model}'). "
            f"This is usually a short-lived capacity spike. Please try again in a moment."
        ) from exc

    # Network / Connection / Timeout errors
    if isinstance(exc, (APIConnectionError, APITimeoutError)) or "connection" in sanitized_msg.lower() or "timeout" in sanitized_msg.lower():
        raise RuntimeError(
            f"Failed to connect to Groq API (model: '{model}'). Please check your network connection and try again."
        ) from exc

    raise RuntimeError(f"Groq API request failed (model: '{model}'): {sanitized_msg}") from exc


def _is_transient_error(exc: Exception) -> bool:
    """
    Determine whether an exception represents a transient API error (e.g. HTTP 503 / capacity).

    Permanent or quota errors (such as 429 rate limit, 404 model not found, 401 auth,
    invalid API key, 400 bad request) return False and must NOT be retried.
    """
    if isinstance(exc, (AuthenticationError, NotFoundError, BadRequestError, RateLimitError)):
        return False

    status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status_code in (400, 401, 403, 404, 422, 429):
        return False

    msg = str(getattr(exc, "message", None) or exc).lower()

    # Rate limits and quota exhaustion must fail immediately without repeated retries
    if (
        "429" in msg
        or "rate_limit" in msg
        or "rate limit" in msg
        or "quota" in msg
        or "resource_exhausted" in msg
    ):
        return False

    # Permanent authentication or model not found indicators
    permanent_indicators = (
        "404", "not_found", "not found",
        "401", "403", "unauthenticated", "permission_denied",
        "invalid_api_key", "invalid api key", "bad request",
    )
    if any(indicator in msg for indicator in permanent_indicators):
        return False

    # Transient error types
    if isinstance(exc, (APIConnectionError, APITimeoutError, InternalServerError)):
        return True

    if (
        "503" in msg
        or "unavailable" in msg
        or "overloaded" in msg
        or "capacity" in msg
        or "timeout" in msg
        or "connection error" in msg
    ):
        return True

    return False


def _call_with_retry(
    client: Groq,
    model: str,
    prompt: str,
    response_format: Optional[dict] = None,
    delays: tuple[float, ...] = _RETRY_DELAYS,
) -> str:
    """
    Call client.chat.completions.create with automatic bounded retry for transient errors.

    Retries up to len(delays) times (default: 3 retries with ~2s, ~5s, ~10s delays)
    for temporary API availability or connection failures. Permanent errors (401, 404, 429)
    fail immediately without retry.

    Args:
        client: The configured Groq API client.
        model:  Groq model name.
        prompt: Formatted prompt text.
        response_format: Optional format dict (e.g. {"type": "json_object"}).
        delays: Sequence of wait times in seconds between attempts.

    Returns:
        The completion text string from response.choices[0].message.content.

    Raises:
        RuntimeError: If all retries fail or a permanent error occurs.
    """
    last_exc = None
    max_attempts = len(delays) + 1

    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    if response_format is not None:
        kwargs["response_format"] = response_format

    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            content = choice.message.content or ""
            return content
        except Exception as exc:
            last_exc = exc
            status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            raw_err = str(getattr(exc, "message", None) or exc)
            err_msg = _sanitize_error_message(raw_err)

            if not _is_transient_error(exc):
                # Permanent error — fail immediately without retrying
                logger.error(
                    "Permanent API error for model '%s' (status: %s): %s",
                    model, status_code, err_msg,
                )
                _raise_api_error(exc, model)

            # Transient error: wait with increasing delay before next attempt
            if attempt < len(delays):
                delay = delays[attempt]
                logger.warning(
                    "Temporary Groq API capacity error (status: %s) for model '%s'. "
                    "Attempt %d of %d failed: %s. Retrying in %.1fs...",
                    status_code, model, attempt + 1, max_attempts, err_msg, delay,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "Groq API retries exhausted (%d attempts) for model '%s' "
                    "due to temporary capacity constraints (status: %s): %s",
                    max_attempts, model, status_code, err_msg,
                )

    # All retries exhausted — raise clean user-facing error
    _raise_api_error(last_exc, model)


def _parse_analysis_response(raw_text: str) -> dict:
    """
    Parse and validate the JSON response from Groq for resume analysis.

    Args:
        raw_text: The raw string returned by the Groq API.

    Returns:
        A validated dictionary matching the expected analysis schema.

    Raises:
        ValueError: If the response is not valid JSON or is missing required keys.
    """
    # Strip markdown code fences if the model added them despite instructions.
    # Handles: ```json, ``` json, or plain ```.
    text = raw_text.strip()
    fence_match = re.match(r"^```[a-zA-Z]*\s*\n([\s\S]*?)\n?```\s*$", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: extract substring between first { and last }
        brace_match = re.search(r"(\{[\s\S]*\})", text)
        if brace_match:
            try:
                data = json.loads(brace_match.group(1))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"The AI returned a response that could not be parsed as JSON. Details: {exc}"
                ) from exc
        else:
            raise ValueError(
                "The AI returned a response that could not be parsed as JSON."
            )

    if not isinstance(data, dict):
        raise ValueError("The AI returned a non-dictionary JSON response.")

    missing_keys = REQUIRED_ANALYSIS_KEYS - data.keys()
    if missing_keys:
        raise ValueError(
            f"The AI response is missing required fields: {', '.join(sorted(missing_keys))}"
        )

    # Coerce match_percentage to int in case the model returns a float or string.
    try:
        data["match_percentage"] = int(data["match_percentage"])
    except (TypeError, ValueError):
        data["match_percentage"] = 0

    # Clamp to [0, 100].
    data["match_percentage"] = max(0, min(100, data["match_percentage"]))

    return data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Send the resume and job description to Groq and return the structured analysis.

    Args:
        resume_text:     Extracted text from the candidate's resume PDF.
        job_description: The job description pasted by the user.

    Returns:
        A dictionary with keys matching REQUIRED_ANALYSIS_KEYS.

    Raises:
        EnvironmentError: If the API key is missing.
        ValueError:       If the AI response cannot be parsed or validated.
        RuntimeError:     If the API request itself fails.
    """
    client = _get_client()
    prompt = RESUME_ANALYSIS_PROMPT.format(
        resume_text=resume_text,
        job_description=job_description,
    )

    model = _get_model_name()
    raw_text = _call_with_retry(
        client=client,
        model=model,
        prompt=prompt,
        response_format={"type": "json_object"},
    )

    if not raw_text or not raw_text.strip():
        raise ValueError("The AI returned an empty response. Please try again.")

    return _parse_analysis_response(raw_text)


def improve_bullet(bullet: str) -> str:
    """
    Send a single resume bullet to Groq and return the improved version.

    Args:
        bullet: The original resume bullet text provided by the user.

    Returns:
        The improved bullet as a plain string.

    Raises:
        EnvironmentError: If the API key is missing.
        RuntimeError:     If the API request fails.
        ValueError:       If the AI returns an empty response.
    """
    client = _get_client()
    prompt = BULLET_IMPROVEMENT_PROMPT.format(bullet=bullet)

    model = _get_model_name()
    raw_text = _call_with_retry(
        client=client,
        model=model,
        prompt=prompt,
        response_format=None,
    )

    improved = (raw_text or "").strip()
    if not improved:
        raise ValueError("The AI returned an empty response. Please try again.")

    return improved
