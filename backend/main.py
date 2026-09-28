"""
backend/main.py
FastAPI application for ResumeLens AI.
Provides REST API endpoints for resume analysis, bullet point improvement, and health checks.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from analyzer import analyze_resume, improve_bullet, _get_model_name
from pdf_reader import extract_text_from_pdf, truncate_resume_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("resumelens.api")

app = FastAPI(
    title="ResumeLens AI API",
    description="Backend API for AI-powered resume analysis against job descriptions using Groq.",
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = "ok"
    model: str


class ImproveBulletRequest(BaseModel):
    bullet: str = Field(..., min_length=3, description="The original resume bullet point to improve.")
    context: Optional[str] = Field(None, description="Optional role, project, or technology context.")


class ImproveBulletResponse(BaseModel):
    improved_bullet: str
    original_bullet: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify backend status and active Groq model."""
    return HealthResponse(status="ok", model=_get_model_name())


@app.post("/api/analyze-resume")
async def analyze_resume_endpoint(
    resume: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    job_description: str = Form(...),
):
    """
    Upload a resume PDF and job description to receive structured AI match analysis.
    """
    # Accept either form field name 'resume' or 'file' for flexibility
    uploaded_file = resume or file

    if uploaded_file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A resume PDF file is required. Please upload a file."
        )

    # Validate file format
    filename = uploaded_file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only text-based PDF files are supported."
        )

    # Validate job description
    cleaned_jd = job_description.strip()
    if not cleaned_jd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description cannot be empty. Please paste the job description."
        )

    # Read uploaded file content
    try:
        file_bytes = await uploaded_file.read()
    except Exception as exc:
        logger.error("Failed to read uploaded file: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {exc}"
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF file is empty (0 bytes)."
        )

    # Max upload limit: 10 MB
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is too large. Maximum supported size is 10 MB."
        )

    # Extract text from PDF
    try:
        raw_resume_text = extract_text_from_pdf(file_bytes)
        truncated_resume_text = truncate_resume_text(raw_resume_text)
    except ValueError as exc:
        # Scanned PDF or no extractable text
        logger.warning("Unextractable PDF uploaded (%s): %s", filename, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        )
    except RuntimeError as exc:
        logger.error("PDF parsing failure (%s): %s", filename, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    # Run Groq AI analysis
    try:
        analysis_result = analyze_resume(truncated_resume_text, cleaned_jd)
        return analysis_result
    except EnvironmentError as exc:
        logger.critical("API configuration missing: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: Groq API key is not configured on the backend."
        )
    except RuntimeError as exc:
        err_msg = str(exc)
        logger.error("Analysis RuntimeError: %s", err_msg)
        if "429" in err_msg or "quota" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=err_msg
            )
        if "unavailable" in err_msg.lower() or "503" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )
    except ValueError as exc:
        logger.error("JSON parsing error from AI: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI response parsing failed: {exc}"
        )
    except Exception as exc:
        logger.exception("Unexpected error during resume analysis: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during resume analysis. Please try again."
        )


@app.post("/api/improve-bullet", response_model=ImproveBulletResponse)
async def improve_bullet_endpoint(payload: ImproveBulletRequest):
    """
    Submit a resume bullet point (with optional context) and receive an AI-enhanced version.
    """
    raw_bullet = payload.bullet.strip()
    if not raw_bullet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bullet text cannot be empty."
        )

    # Append optional context if provided
    bullet_to_improve = raw_bullet
    if payload.context and payload.context.strip():
        bullet_to_improve = f"{raw_bullet}\n(Context: {payload.context.strip()})"

    try:
        improved = improve_bullet(bullet_to_improve)
        return ImproveBulletResponse(
            improved_bullet=improved,
            original_bullet=raw_bullet
        )
    except EnvironmentError as exc:
        logger.critical("API configuration missing: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: Groq API key is not configured on the backend."
        )
    except RuntimeError as exc:
        err_msg = str(exc)
        logger.error("Improve bullet RuntimeError: %s", err_msg)
        if "429" in err_msg or "quota" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=err_msg
            )
        if "unavailable" in err_msg.lower() or "503" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )
    except ValueError as exc:
        logger.error("AI response value error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc)
        )
    except Exception as exc:
        logger.exception("Unexpected error in improve_bullet: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while improving the bullet point."
        )
