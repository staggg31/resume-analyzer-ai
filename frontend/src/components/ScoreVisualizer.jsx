import React, { useEffect, useState } from 'react';

export default function ScoreVisualizer({ score = 0 }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    // Smooth counter animation
    const duration = 1000;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const ease = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Math.round(ease * score));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [score]);

  // SVG ring parameters
  const size = 160;
  const strokeWidth = 11;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;

  let tierClass = 'score-high';
  let tierLabel = 'Strong Alignment';
  let tierDesc = 'Strong candidate alignment with major role requirements.';

  if (score < 40) {
    tierClass = 'score-low';
    tierLabel = 'Needs Tailoring';
    tierDesc = 'Significant gaps identified. Further keyword and experience tailoring recommended.';
  } else if (score < 60) {
    tierClass = 'score-mid';
    tierLabel = 'Moderate Match';
    tierDesc = 'Core background exists, but notable requirements are absent.';
  } else if (score < 80) {
    tierClass = 'score-good';
    tierLabel = 'Good Match';
    tierDesc = 'Solid foundation with key qualifications present; minor skill gaps identified.';
  }

  return (
    <div className={`score-card-hero ${tierClass}`} id="score-visualizer">
      <div className="score-ring-wrapper">
        <svg width={size} height={size} className="score-svg" viewBox={`0 0 ${size} ${size}`}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            className="score-track"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            className="score-fill"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>

        <div className="score-center-content">
          <span className="score-number">
            {animatedScore}<span className="score-percent">%</span>
          </span>
          <span className="score-subtext">MATCH</span>
        </div>
      </div>

      <div className="score-details">
        <div className="score-badge-pill">{tierLabel}</div>
        <h3 className="score-heading">AI-Estimated Match</h3>
        <p className="score-summary-text">{tierDesc}</p>
      </div>
    </div>
  );
}
