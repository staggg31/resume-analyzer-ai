import React, { useEffect, useState } from 'react';
import { Sparkles, CheckCircle2, CircleDashed } from 'lucide-react';

const STEPS = [
  'Extracting resume information',
  'Comparing candidate skills & technologies',
  'Evaluating job requirements & alignment',
  'Generating recommendations & match insights',
];

export default function LoadingAnalysis() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 1600);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-card animate-fade-in" id="loading-analysis-container">
      <div className="loading-spinner-wrapper">
        <div className="pulse-ring"></div>
        <div className="loading-center-icon">
          <Sparkles className="sparkle-spin text-primary" size={30} />
        </div>
      </div>

      <div className="loading-header-group">
        <span className="loading-badge">
          <span>✦</span> AI Processing Active
        </span>
        <h3 className="loading-title">Analyzing your resume</h3>
        <p className="loading-subtitle">
          Our AI pipeline is inspecting your credentials against the target role requirements.
        </p>
      </div>

      <div className="loading-steps-list">
        {STEPS.map((step, idx) => {
          const isDone = idx < currentStep;
          const isCurrent = idx === currentStep;
          return (
            <div
              key={idx}
              className={`loading-step-item ${isDone ? 'done' : ''} ${isCurrent ? 'active' : ''}`}
            >
              <div className="step-icon">
                {isDone ? (
                  <CheckCircle2 size={16} className="text-success" />
                ) : isCurrent ? (
                  <CircleDashed size={16} className="step-spin text-primary" />
                ) : (
                  <div className="step-dot" />
                )}
              </div>
              <span className="step-label">{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
