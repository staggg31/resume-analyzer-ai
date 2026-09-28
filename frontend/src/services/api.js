/**
 * services/api.js
 * API client layer communicating with FastAPI backend.
 * All GenAI calls are processed securely server-side by the backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * Helper to handle HTTP errors cleanly and return user-friendly messages.
 */
async function handleResponse(response) {
  if (response.ok) {
    return response.json();
  }

  let errorDetail = 'An unexpected server error occurred.';
  try {
    const errorData = await response.json();
    if (errorData?.detail) {
      errorDetail = errorData.detail;
    }
  } catch {
    errorDetail = `Server error (${response.status}: ${response.statusText})`;
  }

  // Map HTTP status codes to friendly user explanations
  if (response.status === 429) {
    throw new Error(
      errorDetail ||
      'AI analysis is temporarily unavailable because the daily request quota or rate limit has been reached. Please try again later.'
    );
  }

  if (response.status === 503) {
    throw new Error(
      errorDetail ||
      'The AI service is currently experiencing high demand. Please try again in a few moments.'
    );
  }

  if (response.status === 400 || response.status === 422) {
    throw new Error(errorDetail || 'Invalid input. Please verify your PDF and job description.');
  }

  throw new Error(errorDetail);
}

/**
 * Verify backend health and model configuration.
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
    });
    return await handleResponse(response);
  } catch (err) {
    throw new Error(err.message || 'Cannot connect to backend server. Make sure FastAPI is running.');
  }
}

/**
 * Upload resume PDF and job description for full AI analysis.
 * @param {File} resumeFile 
 * @param {string} jobDescription 
 */
export async function analyzeResume(resumeFile, jobDescription) {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('job_description', jobDescription.trim());

  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze-resume`, {
      method: 'POST',
      body: formData,
    });
    return await handleResponse(response);
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Could not connect to ResumeLens API backend. Please ensure the backend is running at http://localhost:8000.');
    }
    throw err;
  }
}

/**
 * Submit resume bullet point for AI enhancement.
 * @param {string} bullet 
 * @param {string} [context] 
 */
export async function improveBullet(bullet, context = '') {
  try {
    const response = await fetch(`${API_BASE_URL}/api/improve-bullet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        bullet: bullet.trim(),
        context: context.trim() || null,
      }),
    });
    return await handleResponse(response);
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Could not connect to ResumeLens API backend. Please ensure the backend is running at http://localhost:8000.');
    }
    throw err;
  }
}
