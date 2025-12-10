import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { CareerCounsellor } from './pages/CareerCounsellor';
import { TextSummarizer } from './pages/TextSummarizer';
import { StockPredictor } from './pages/StockPredictor';
import { ResumeOptimizer } from './pages/ResumeOptimizer';
import { AppRoute } from './types';

const App: React.FC = () => {
  const [currentRoute, setCurrentRoute] = useState<AppRoute>(AppRoute.DASHBOARD);

  const renderContent = () => {
    switch (currentRoute) {
      case AppRoute.DASHBOARD:
        return <Dashboard />;
      case AppRoute.CAREER_COUNSELLOR:
        return <CareerCounsellor />;
      case AppRoute.TEXT_SUMMARIZER:
        return <TextSummarizer />;
      case AppRoute.STOCK_PREDICTOR:
        return <StockPredictor />;
      case AppRoute.RESUME_OPTIMIZER:
        return <ResumeOptimizer />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout currentRoute={currentRoute} onNavigate={setCurrentRoute}>
      {renderContent()}
    </Layout>
  );
};

export default App;