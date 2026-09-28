"""
prompts.py
Contains all prompt templates sent to the LLM API.
Keeping prompts here makes them easy to review, adjust, and version-control
independently of the business logic in analyzer.py.
"""

# ---------------------------------------------------------------------------
# Resume analysis prompt
# ---------------------------------------------------------------------------

RESUME_ANALYSIS_PROMPT = """
You are an expert technical recruiter and resume coach.

Analyze the candidate's resume against the provided job description.
Base your analysis ONLY on information that is explicitly present in the resume.

IMPORTANT RULES:
- Do not invent skills, experience, or metrics that are not in the resume.
- Clearly distinguish between what is explicitly stated and what can be inferred.
- Be constructive, specific, and honest.

Return your analysis as a single, valid JSON object with EXACTLY this structure
(no markdown fences, no extra keys, no trailing commas):

{{
    "match_percentage": <integer 0-100>,
    "matching_skills": [<list of skill strings found in both resume and JD>],
    "missing_skills": [<list of skills the JD requires that are absent from the resume>],
    "strengths": [<list of resume strengths relevant to this role>],
    "improvements": [<list of specific, actionable improvement suggestions>],
    "relevant_experience": [<list of experience items from the resume that are relevant to the JD>],
    "suggested_keywords": [<list of keywords from the JD that should appear in the resume>],
    "interview_topics": [<list of likely interview topics based on the JD>],
    "summary": "<one concise paragraph summarising the overall alignment and top recommendation>"
}}

---
RESUME:
{resume_text}

---
JOB DESCRIPTION:
{job_description}
"""

# ---------------------------------------------------------------------------
# Resume bullet improvement prompt
# ---------------------------------------------------------------------------

BULLET_IMPROVEMENT_PROMPT = """
You are a professional resume writer.

Improve the following resume bullet point so that it:
- Uses strong action verbs and professional resume language.
- Is concise (ideally one sentence, two at most).
- Preserves the original meaning exactly — do NOT invent metrics, tools,
  or experience that are not already implied by the original bullet.
- Does NOT exaggerate or make unsupported claims.

Return ONLY the improved bullet text — no explanation, no quotation marks,
no preamble.

ORIGINAL BULLET:
{bullet}
"""
