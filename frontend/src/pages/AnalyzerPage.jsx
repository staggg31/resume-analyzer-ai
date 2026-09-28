import React, { useState } from 'react';
import { Sparkles, AlertCircle, RefreshCw, ArrowRight, CheckCircle2 } from 'lucide-react';
import ResumeUploader from '../components/ResumeUploader';
import JobDescriptionInput from '../components/JobDescriptionInput';
import LoadingAnalysis from '../components/LoadingAnalysis';
import ResultsDashboard from '../components/ResultsDashboard';
import { analyzeResume } from '../services/api';

export default function AnalyzerPage() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [fileError, setFileError] = useState(null);

  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [apiError, setApiError] = useState(null);

  const isStep1Done = file !== null;
  const isStep2Done = jobDescription.trim().length > 0;
  const isReadyToAnalyze = isStep1Done && isStep2Done && !isLoading;

  const handleAnalyze = async () => {
    if (!file) {
      setFileError('Please select a resume PDF file.');
      return;
    }
    if (!jobDescription.trim()) {
      setApiError('Please enter a target job description.');
      return;
    }

    setApiError(null);
    setFileError(null);
    setIsLoading(true);

    try {
      const data = await analyzeResume(file, jobDescription);
      setAnalysisResult(data);
    } catch (err) {
      setApiError(err.message || 'An error occurred while analyzing the resume.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setApiError(null);
    setFile(null);
    setJobDescription('');
  };

  return (
    <div className="page-container">
      {/* If results exist, show Dashboard */}
      {analysisResult ? (
        <ResultsDashboard data={analysisResult} onReset={handleReset} />
      ) : isLoading ? (
        <LoadingAnalysis />
      ) : (
        <div className="analyzer-flow animate-fade-in">
          {/* Main Hero Header */}
          <section className="hero-section">
            <div className="hero-pill-badge">
              <Sparkles size={14} className="text-primary" />
              <span>AI-Powered Career Intelligence</span>
            </div>
            <h1 className="hero-title">
              Turn your resume into your <span className="hero-gradient-text">next opportunity.</span>
            </h1>
            <p className="hero-subtitle">
              Analyze your resume against any job description and discover exactly where you match,
              where you're missing skills, and what to improve.
            </p>

            {/* Section 6: Three-Step Workflow Indicator */}
            <div className="workflow-steps" aria-label="Analysis Workflow Steps">
              <div className={`step-item ${isStep1Done ? 'completed' : 'active'}`}>
                <span className="step-badge">
                  {isStep1Done ? <CheckCircle2 size={14} /> : '01'}
                </span>
                <span className="step-text">Upload Resume</span>
              </div>

              <div className="step-divider" aria-hidden="true">→</div>

              <div
                className={`step-item ${
                  isStep2Done ? 'completed' : isStep1Done ? 'active' : 'pending'
                }`}
              >
                <span className="step-badge">
                  {isStep2Done ? <CheckCircle2 size={14} /> : '02'}
                </span>
                <span className="step-text">Add Job Description</span>
              </div>

              <div className="step-divider" aria-hidden="true">→</div>

              <div className={`step-item ${isReadyToAnalyze ? 'active' : 'pending'}`}>
                <span className="step-badge">03</span>
                <span className="step-text">Analyze Match</span>
              </div>
            </div>
          </section>

          {/* Workspace Two-Column Grid */}
          <div className="workspace-grid">
            <div className="workspace-col">
              <ResumeUploader
                file={file}
                setFile={setFile}
                error={fileError}
                setError={setFileError}
              />
            </div>

            <div className="workspace-col">
              <JobDescriptionInput
                jobDescription={jobDescription}
                setJobDescription={setJobDescription}
              />
            </div>
          </div>

          {/* Error Banner */}
          {apiError && (
            <div className="api-error-card animate-fade-in" role="alert" id="analysis-error-banner">
              <div className="error-icon-box">
                <AlertCircle size={20} className="text-danger" />
              </div>
              <div className="error-text-content">
                <h3 className="error-title">Analysis Unavailable</h3>
                <p className="error-msg">{apiError}</p>
              </div>
              <button
                type="button"
                className="btn-secondary error-retry-btn"
                onClick={handleAnalyze}
                disabled={!isReadyToAnalyze}
              >
                <RefreshCw size={14} />
                <span>Try Again</span>
              </button>
            </div>
          )}

          {/* Action Bar */}
          <div className="action-bar-container">
            <button
              type="button"
              className="btn-primary analyze-cta-btn"
              onClick={handleAnalyze}
              disabled={!isReadyToAnalyze}
              id="btn-analyze-resume"
            >
              <Sparkles size={18} />
              <span>Analyze Resume</span>
              <ArrowRight size={18} className="cta-arrow" />
            </button>

            {!file && !jobDescription.trim() && (
              <p className="cta-hint">Upload a PDF resume and paste a job description to activate analysis</p>
            )}
            {file && !jobDescription.trim() && (
              <p className="cta-hint">Now paste the target job description to proceed</p>
            )}
            {!file && jobDescription.trim() && (
              <p className="cta-hint">Upload your resume PDF to proceed</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
