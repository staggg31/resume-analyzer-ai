import React, { useState } from 'react';
import { Sparkles, Copy, Check, ShieldAlert, ArrowRight, RefreshCw, FileText } from 'lucide-react';
import { improveBullet } from '../services/api';

export default function BulletImproverPage() {
  const [bullet, setBullet] = useState('');
  const [context, setContext] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [improvedResult, setImprovedResult] = useState('');
  const [originalSubmitted, setOriginalSubmitted] = useState('');
  const [error, setError] = useState(null);
  const [isCopied, setIsCopied] = useState(false);

  const handleImprove = async () => {
    if (!bullet.trim()) {
      setError('Please paste a resume bullet point to improve.');
      return;
    }

    setError(null);
    setIsLoading(true);
    setOriginalSubmitted(bullet.trim());

    try {
      const data = await improveBullet(bullet, context);
      setImprovedResult(data.improved_bullet);
    } catch (err) {
      setError(err.message || 'Failed to improve bullet point.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!improvedResult) return;
    try {
      await navigator.clipboard.writeText(improvedResult);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2200);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = improvedResult;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2200);
    }
  };

  const handleLoadSample = () => {
    setBullet('Worked on fixing bugs and adding some new endpoints for the backend service.');
    setContext('Python & FastAPI microservice handling user authentication and payments');
    setError(null);
  };

  return (
    <div className="page-container animate-fade-in">
      {/* Hero Header */}
      <section className="hero-section">
        <div className="hero-pill-badge">
          <Sparkles size={14} className="text-primary" />
          <span>Precision Bullet Optimization</span>
        </div>
        <h1 className="hero-title">
          Bullet Improver
        </h1>
        <p className="hero-subtitle">
          Turn ordinary resume bullets into clearer, stronger achievement statements.
        </p>
      </section>

      <div className="bullet-improver-layout">
        {/* Left Column: Input Panel */}
        <div className="bullet-col input-panel">
          <div className="card-box">
            <div className="card-header">
              <div className="card-icon-badge">
                <span>✏️</span>
              </div>
              <div className="card-header-flex">
                <div>
                  <h2 className="card-title">Original Bullet</h2>
                  <p className="card-subtitle">Paste a resume bullet point you want to rewrite</p>
                </div>
                <button
                  type="button"
                  className="sample-btn"
                  onClick={handleLoadSample}
                  title="Load sample bullet for quick testing"
                >
                  <FileText size={13} />
                  <span>Load Sample</span>
                </button>
              </div>
            </div>

            <div className="form-group">
              <textarea
                className="jd-textarea bullet-input"
                placeholder="e.g., Responsible for optimizing SQL database queries to make dashboard load faster..."
                value={bullet}
                onChange={(e) => setBullet(e.target.value)}
                rows={4}
                id="bullet-text-input"
              />
            </div>

            <div className="form-group context-group">
              <label className="input-label" htmlFor="context-input">
                Optional Context (Role, technology, or impact scope)
              </label>
              <input
                id="context-input"
                type="text"
                className="text-input"
                placeholder="e.g., PostgreSQL, Python backend, e-commerce checkout service"
                value={context}
                onChange={(e) => setContext(e.target.value)}
              />
              <span className="input-hint">
                Helps the AI select the most precise domain vocabulary without guessing.
              </span>
            </div>

            <div className="button-row">
              <button
                type="button"
                className="btn-primary w-full"
                onClick={handleImprove}
                disabled={isLoading || !bullet.trim()}
                id="btn-improve-bullet"
              >
                {isLoading ? (
                  <>
                    <RefreshCw size={17} className="step-spin" />
                    <span>Improving Bullet with AI...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={17} />
                    <span>Improve with AI</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>

            {error && (
              <div className="inline-error-banner animate-fade-in" role="alert">
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* Truthfulness Guarantee Box */}
          <div className="truthfulness-card">
            <div className="truth-header">
              <ShieldAlert size={17} className="text-warning" />
              <h4>Truthfulness &amp; Integrity Guardrail</h4>
            </div>
            <p className="truth-text">
              Keep AI-generated statements truthful to your actual experience. ResumeLens AI never fabricates metrics, tools, achievements, or titles. Always verify final wording before submission.
            </p>
          </div>
        </div>

        {/* Right Column: Output Panel */}
        <div className="bullet-col output-panel">
          <div className="card-box result-panel-card">
            <div className="card-header">
              <div className="card-icon-badge success-badge">
                <span>✨</span>
              </div>
              <div className="card-header-flex">
                <div>
                  <h2 className="card-title">Improved Bullet</h2>
                  <p className="card-subtitle">Recruiter-ready phrasing with active impact</p>
                </div>

                {improvedResult && (
                  <button
                    type="button"
                    className={`copy-btn ${isCopied ? 'copied' : ''}`}
                    onClick={handleCopy}
                    id="btn-copy-bullet"
                  >
                    {isCopied ? (
                      <>
                        <Check size={14} className="text-success" />
                        <span>Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy size={14} />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>

            {improvedResult ? (
              <div className="improved-output-box animate-fade-in">
                <div className="comparison-block">
                  <span className="comparison-tag original-tag">Original:</span>
                  <p className="original-comparison-text">{originalSubmitted}</p>
                </div>

                <div className="comparison-block active-result">
                  <span className="comparison-tag improved-tag">Improved Version:</span>
                  <p className="improved-result-text" id="improved-bullet-result">
                    {improvedResult}
                  </p>
                </div>

                <div className="result-notice">
                  <span>💡 Tip: Paste into your resume experience section under the relevant role.</span>
                </div>
              </div>
            ) : (
              <div className="empty-output-state">
                <div className="empty-icon-circle">
                  <Sparkles size={26} className="text-muted" />
                </div>
                <h3 className="empty-state-title">No Bullet Generated Yet</h3>
                <p className="empty-state-desc">
                  Input your existing bullet point on the left and click <strong>Improve with AI</strong> to generate a tailored, action-oriented version.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
