import React, { useState } from 'react';
import {
  CheckCircle,
  XCircle,
  TrendingUp,
  AlertOctagon,
  Tag,
  HelpCircle,
  Briefcase,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  Award,
  AlertTriangle,
  Layers,
} from 'lucide-react';
import ScoreVisualizer from './ScoreVisualizer';

export default function ResultsDashboard({ data, onReset }) {
  const [isExpOpen, setIsExpOpen] = useState(true);

  if (!data) return null;

  const {
    match_percentage = 0,
    matching_skills = [],
    missing_skills = [],
    strengths = [],
    improvements = [],
    relevant_experience = [],
    suggested_keywords = [],
    interview_topics = [],
    summary = '',
  } = data;

  return (
    <div className="results-container animate-fade-in" id="resume-analysis-results">
      {/* Top Header & Reset Action */}
      <div className="results-header-bar">
        <div>
          <div className="results-context-line">
            <span>Resume Analyzer</span>
            <span className="context-separator">/</span>
            <span>Target Role Alignment</span>
          </div>
          <h1 className="results-title">Resume Match Analysis</h1>
          <p className="results-desc">
            AI-powered comparison between your resume and the selected role.
          </p>
        </div>
        <button
          type="button"
          className="btn-secondary reset-btn"
          onClick={onReset}
          id="btn-analyze-another"
        >
          <RotateCcw size={15} />
          <span>Analyze Another</span>
        </button>
      </div>

      {/* Main Score Hero Card */}
      <ScoreVisualizer score={match_percentage} />

      {/* Section 12: Key Insights Summary (Compact Metric Cards) */}
      <div className="insights-summary-grid">
        <div className="insight-card insight-matching">
          <div className="insight-icon-wrap">
            <CheckCircle size={18} />
          </div>
          <div className="insight-content">
            <span className="insight-number">{matching_skills.length}</span>
            <span className="insight-label">Matching Skills</span>
          </div>
        </div>

        <div className="insight-card insight-gaps">
          <div className="insight-icon-wrap">
            <AlertTriangle size={18} />
          </div>
          <div className="insight-content">
            <span className="insight-number">{missing_skills.length}</span>
            <span className="insight-label">Skill Gaps</span>
          </div>
        </div>

        <div className="insight-card insight-strengths">
          <div className="insight-icon-wrap">
            <Award size={18} />
          </div>
          <div className="insight-content">
            <span className="insight-number">{strengths.length}</span>
            <span className="insight-label">Strengths Identified</span>
          </div>
        </div>

        <div className="insight-card insight-keywords">
          <div className="insight-icon-wrap">
            <Layers size={18} />
          </div>
          <div className="insight-content">
            <span className="insight-number">{suggested_keywords.length}</span>
            <span className="insight-label">ATS Keywords</span>
          </div>
        </div>
      </div>

      {/* Executive Summary Card */}
      {summary && (
        <div className="summary-card">
          <div className="summary-header">
            <div className="summary-icon-badge">
              <Sparkles size={16} className="text-primary" />
            </div>
            <h2 className="summary-title">Executive Evaluation</h2>
          </div>
          <p className="summary-body">{summary}</p>
        </div>
      )}

      {/* Skills Grid: Matching vs Missing */}
      <div className="two-col-grid">
        {/* Matching Skills */}
        <div className="card-box skill-card-matching">
          <div className="card-header-simple">
            <div className="header-icon-box success-icon-box">
              <CheckCircle size={16} className="text-success" />
            </div>
            <h2 className="card-header-title">
              Matching Skills <span className="count-pill success">{matching_skills.length}</span>
            </h2>
          </div>
          <p className="section-desc">Identified in both your resume and the target job description.</p>
          <div className="tags-flex">
            {matching_skills.length > 0 ? (
              matching_skills.map((skill, idx) => (
                <span key={idx} className="skill-pill pill-match">
                  <span className="pill-symbol">✓</span>
                  <span>{skill}</span>
                </span>
              ))
            ) : (
              <span className="empty-text">No direct matching skills detected.</span>
            )}
          </div>
        </div>

        {/* Missing Skills */}
        <div className="card-box skill-card-missing">
          <div className="card-header-simple">
            <div className="header-icon-box danger-icon-box">
              <XCircle size={16} className="text-danger" />
            </div>
            <h2 className="card-header-title">
              Missing / Gap Skills <span className="count-pill danger">{missing_skills.length}</span>
            </h2>
          </div>
          <p className="section-desc">Required by the job description but not explicitly found in your resume.</p>
          <div className="tags-flex">
            {missing_skills.length > 0 ? (
              missing_skills.map((skill, idx) => (
                <span key={idx} className="skill-pill pill-miss">
                  <span className="pill-symbol">!</span>
                  <span>{skill}</span>
                </span>
              ))
            ) : (
              <span className="empty-text">No critical skill gaps identified! Great alignment.</span>
            )}
          </div>
        </div>
      </div>

      {/* Strengths & Improvements Grid */}
      <div className="two-col-grid">
        {/* Strengths */}
        <div className="card-box detail-card">
          <div className="card-header-simple">
            <div className="header-icon-box success-icon-box">
              <TrendingUp size={16} className="text-success" />
            </div>
            <h2 className="card-header-title">Key Strengths</h2>
          </div>
          <ul className="styled-bullet-list">
            {strengths.map((item, idx) => (
              <li key={idx} className="strength-item">
                <span className="bullet-marker success">&bull;</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Improvements */}
        <div className="card-box detail-card">
          <div className="card-header-simple">
            <div className="header-icon-box warning-icon-box">
              <AlertOctagon size={16} className="text-warning" />
            </div>
            <h2 className="card-header-title">Actionable Improvements</h2>
          </div>
          <ul className="styled-bullet-list">
            {improvements.map((item, idx) => (
              <li key={idx} className="improvement-item">
                <span className="bullet-marker warning">&bull;</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Relevant Experience (Collapsible) */}
      {relevant_experience.length > 0 && (
        <div className="card-box collapsible-card">
          <button
            type="button"
            className="collapsible-header"
            onClick={() => setIsExpOpen(!isExpOpen)}
            aria-expanded={isExpOpen}
          >
            <div className="header-left">
              <div className="header-icon-box primary-icon-box">
                <Briefcase size={16} className="text-primary" />
              </div>
              <h2 className="card-header-title">
                Relevant Experience Alignment <span className="count-pill">{relevant_experience.length}</span>
              </h2>
            </div>
            {isExpOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>

          {isExpOpen && (
            <div className="collapsible-body animate-fade-in">
              <ul className="styled-bullet-list">
                {relevant_experience.map((item, idx) => (
                  <li key={idx} className="experience-item">
                    <span className="bullet-marker info">&bull;</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Keywords & Interview Topics */}
      <div className="two-col-grid">
        {/* Suggested Keywords */}
        <div className="card-box tag-section-card">
          <div className="card-header-simple">
            <div className="header-icon-box info-icon-box">
              <Tag size={16} className="text-info" />
            </div>
            <h2 className="card-header-title">Suggested Keywords for ATS</h2>
          </div>
          <p className="section-desc">Integrate these relevant industry terms to improve ATS visibility.</p>
          <div className="tags-flex">
            {suggested_keywords.map((kw, idx) => (
              <span key={idx} className="keyword-pill">
                #{kw}
              </span>
            ))}
          </div>
        </div>

        {/* Interview Preparation Topics */}
        <div className="card-box tag-section-card">
          <div className="card-header-simple">
            <div className="header-icon-box primary-icon-box">
              <HelpCircle size={16} className="text-primary" />
            </div>
            <h2 className="card-header-title">Targeted Interview Topics</h2>
          </div>
          <p className="section-desc">Key technical and behavioral domains recruiters will likely explore.</p>
          <div className="interview-topics-list">
            {interview_topics.map((topic, idx) => (
              <div key={idx} className="interview-topic-item">
                <span className="topic-index">{idx + 1}</span>
                <span className="topic-text">{topic}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Section 17: AI Trust & Transparency Banner */}
      <div className="ai-trust-banner">
        <ShieldCheck size={16} className="text-muted" />
        <span>
          AI-generated insights are recommendations. Verify resume claims and job requirements before applying.
        </span>
      </div>
    </div>
  );
}
