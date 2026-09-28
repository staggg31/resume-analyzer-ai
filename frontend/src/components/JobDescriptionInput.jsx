import React from 'react';
import { FileCode, AlertTriangle, Briefcase } from 'lucide-react';

export default function JobDescriptionInput({ jobDescription, setJobDescription }) {
  const charCount = jobDescription.length;

  const handleSampleLoad = () => {
    const sample = `Senior Full-Stack Python & React Engineer
Requirements:
- 3+ years experience with Python, FastAPI, and modern web application development.
- Strong proficiency with React, JavaScript/TypeScript, and modern responsive CSS interfaces.
- Hands-on experience integrating Generative AI / LLM APIs (Groq, OpenAI, Anthropic).
- Solid knowledge of relational databases (PostgreSQL/MySQL), Docker, and Git workflows.
- Experience with PDF text processing, prompt engineering, and structured JSON output.
- Excellent communication and ability to explain architectural decisions clearly.`;
    setJobDescription(sample);
  };

  return (
    <div className="card-box jd-card">
      <div className="card-header">
        <div className="card-icon-badge">
          <Briefcase size={18} className="text-primary" />
        </div>
        <div className="card-header-flex">
          <div>
            <h2 className="card-title">Job Description</h2>
            <p className="card-subtitle">Paste the role you're targeting.</p>
          </div>
          <button
            type="button"
            className="sample-btn"
            onClick={handleSampleLoad}
            title="Load sample job description for quick testing"
          >
            <FileCode size={13} />
            <span>Load Sample</span>
          </button>
        </div>
      </div>

      <div className="textarea-container">
        <textarea
          className="jd-textarea"
          placeholder="Paste the target job description here... (e.g. required qualifications, core technologies, responsibilities, and experience)"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows={9}
          id="job-description-textarea"
        />

        <div className="textarea-footer">
          <div className="char-badge">
            <span className="char-number">{charCount.toLocaleString()}</span>
            <span className="char-label">characters</span>
          </div>

          {charCount > 8000 && (
            <div className="char-warning">
              <AlertTriangle size={14} />
              <span>Lengthy description &bull; consider trimming</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
