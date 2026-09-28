"""
pdf_reader.py
Handles PDF text extraction from an uploaded file object.
"""

import io
from pypdf import PdfReader


# Maximum number of characters accepted from a resume to avoid oversized prompts.
MAX_RESUME_CHARS = 15_000


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all readable text from a PDF given its raw bytes.

    Args:
        file_bytes: The raw bytes of the uploaded PDF file.

    Returns:
        A single string containing all extracted text, with pages
        separated by newlines.

    Raises:
        ValueError: If the PDF contains no extractable text (e.g., scanned image).
        RuntimeError: If the PDF cannot be parsed at all.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise RuntimeError(f"Could not parse the PDF file: {exc}") from exc

    pages_text: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages_text.append(page_text)

    full_text = "\n".join(pages_text).strip()

    if not full_text:
        raise ValueError(
            "No text could be extracted from this PDF. "
            "It may be a scanned image or a protected file. "
            "Please use a text-based PDF."
        )

    return full_text


def truncate_resume_text(text: str, max_chars: int = MAX_RESUME_CHARS) -> str:
    """
    Truncate resume text to a safe maximum length for the AI prompt.

    Args:
        text:      The full extracted resume text.
        max_chars: Maximum number of characters to keep.

    Returns:
        The (possibly truncated) resume text.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Resume truncated to fit analysis limit.]"
