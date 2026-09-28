import React from 'react';
import { Sparkles, FileText, HelpCircle } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, modelName }) {
  return (
    <header className="navbar-container">
      <div className="navbar-inner">
        {/* Brand */}
        <div className="brand" onClick={() => setActiveTab('analyzer')} role="button" tabIndex={0}>
          <div className="brand-logo-icon">
            <span className="logo-emoji">🔍</span>
          </div>
          <div className="brand-text">
            <div className="brand-title-wrap">
              <span className="brand-name">
                ResumeLens <span className="brand-highlight">AI</span>
              </span>
              <span className="brand-subtitle">AI-Powered Resume Intelligence</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="nav-links" aria-label="Main Navigation">
          <button
            type="button"
            className={`nav-btn ${activeTab === 'analyzer' ? 'active' : ''}`}
            onClick={() => setActiveTab('analyzer')}
            id="nav-analyzer-btn"
          >
            <FileText size={16} />
            <span>Analyze Resume</span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'bullet' ? 'active' : ''}`}
            onClick={() => setActiveTab('bullet')}
            id="nav-bullet-btn"
          >
            <Sparkles size={16} />
            <span>Bullet Improver</span>
          </button>

          <button
            type="button"
            className={`nav-btn ${activeTab === 'about' ? 'active' : ''}`}
            onClick={() => setActiveTab('about')}
            id="nav-about-btn"
          >
            <HelpCircle size={16} />
            <span>About</span>
          </button>
        </nav>

        {/* System Indicator */}
        <div
          className="system-pill"
          title={modelName ? `Active Model: ${modelName}` : 'AI Engine Active'}
        >
          <span className="pulse-dot"></span>
          <span className="system-text">AI Engine Active</span>
        </div>
      </div>
    </header>
  );
}
