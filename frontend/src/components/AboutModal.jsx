import React from 'react';
import { X, ShieldCheck, Cpu, Code2, Sparkles, CheckCircle2, Zap } from 'lucide-react';

export default function AboutModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div
      className="modal-backdrop animate-fade-in"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="about-modal-title"
    >
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="brand-logo-icon">
            <span>🔍</span>
          </div>
          <div className="modal-title-group">
            <h2 className="modal-title" id="about-modal-title">About ResumeLens AI</h2>
            <p className="modal-subtitle">AI-powered resume intelligence for students and early-career professionals.</p>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close dialog"
          >
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <p className="about-p">
            <strong>ResumeLens AI</strong> empowers job seekers with objective, recruiter-grade analysis
            of their resumes compared directly against target job descriptions — highlighting verified strengths,
            concrete skill gaps, and ATS-optimized recommendations.
          </p>

          <h3 className="section-label">Built With</h3>
          <div className="tech-stack-grid">
            <div className="tech-item">
              <Code2 size={20} className="text-primary" />
              <div>
                <strong>React 18 &amp; Vite</strong>
                <span>Clean, responsive, modern SaaS interface built with zero-dependency CSS.</span>
              </div>
            </div>

            <div className="tech-item">
              <Cpu size={20} className="text-info" />
              <div>
                <strong>FastAPI &amp; Python 3.12</strong>
                <span>High-performance asynchronous backend with strict Pydantic validation.</span>
              </div>
            </div>

            <div className="tech-item">
              <Zap size={20} className="text-warning" />
              <div>
                <strong>Groq Cloud LLM</strong>
                <span>Ultra-fast inference engine powering deep skill extraction and structured JSON.</span>
              </div>
            </div>

            <div className="tech-item">
              <ShieldCheck size={20} className="text-success" />
              <div>
                <strong>pypdf &amp; Guardrails</strong>
                <span>In-memory extraction with strict truthfulness constraints — no hallucinated metrics.</span>
              </div>
            </div>
          </div>

          <h3 className="section-label">Core Features</h3>
          <div className="features-grid">
            <div className="feature-pill">
              <CheckCircle2 size={15} className="text-success" />
              <span>Resume Analysis</span>
            </div>
            <div className="feature-pill">
              <CheckCircle2 size={15} className="text-success" />
              <span>Job Matching</span>
            </div>
            <div className="feature-pill">
              <CheckCircle2 size={15} className="text-success" />
              <span>Skill Gap Detection</span>
            </div>
            <div className="feature-pill">
              <CheckCircle2 size={15} className="text-success" />
              <span>Bullet Improvement</span>
            </div>
            <div className="feature-pill">
              <CheckCircle2 size={15} className="text-success" />
              <span>Interview Preparation</span>
            </div>
          </div>

          <h3 className="section-label">Privacy &amp; Reliability</h3>
          <ul className="about-checks">
            <li>
              <CheckCircle2 size={16} className="text-success" />
              <span>API credentials remain strictly isolated on the backend; never exposed to the client.</span>
            </li>
            <li>
              <CheckCircle2 size={16} className="text-success" />
              <span>Resumes are parsed securely in-memory and analyzed ephemerally — never stored or logged.</span>
            </li>
            <li>
              <CheckCircle2 size={16} className="text-success" />
              <span>Bounded exponential backoff and rate-limit handling protect against service spikes.</span>
            </li>
          </ul>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-primary" onClick={onClose}>
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
