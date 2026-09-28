import React, { useEffect, useState } from 'react';
import Navbar from './components/Navbar';
import AboutModal from './components/AboutModal';
import AnalyzerPage from './pages/AnalyzerPage';
import BulletImproverPage from './pages/BulletImproverPage';
import { checkHealth } from './services/api';
import './styles/index.css';
import './styles/App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('analyzer');
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const [modelName, setModelName] = useState('');

  useEffect(() => {
    // Check backend health and fetch configured model on mount
    checkHealth()
      .then((data) => {
        if (data?.model) {
          setModelName(data.model);
        }
      })
      .catch(() => {
        // Backend might still be starting
      });
  }, []);

  const handleTabChange = (tab) => {
    if (tab === 'about') {
      setIsAboutOpen(true);
    } else {
      setActiveTab(tab);
    }
  };

  return (
    <>
      <Navbar
        activeTab={activeTab}
        setActiveTab={handleTabChange}
        modelName={modelName}
      />

      <main className="main-content">
        {activeTab === 'analyzer' && <AnalyzerPage />}
        {activeTab === 'bullet' && <BulletImproverPage />}
      </main>

      <footer className="footer-container">
        <div className="footer-inner">
          <span className="footer-brand">ResumeLens AI</span>
          <span className="footer-meta">
            FastAPI &bull; React &bull; Groq Cloud LLM &bull; pypdf
          </span>
          <span className="footer-sub">AI-Powered Career Intelligence</span>
        </div>
      </footer>

      <AboutModal
        isOpen={isAboutOpen}
        onClose={() => setIsAboutOpen(false)}
      />
    </>
  );
}
