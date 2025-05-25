import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';

// Layout
import TabBar from './components/layout/TabBar';

// Pages
import HomePage from './pages/Home';
import GamesPage from './pages/Games';
import TasksPage from './pages/Tasks';
import RewardsPage from './pages/Rewards';
import ProfilePage from './pages/Profile';

// Game Components
import MagicBall from './components/games/MagicBall';
import TarotCard from './components/games/TarotCard';

// Telegram WebApp integration
const initTelegramWebApp = () => {
  // Check if Telegram WebApp is available
  if (window.Telegram && window.Telegram.WebApp) {
    const tg = window.Telegram.WebApp;
    
    // Initialize Telegram WebApp
    tg.expand();
    tg.ready();
    
    // Set theme based on Telegram theme
    document.documentElement.classList.add(tg.colorScheme);
  }
};

const App: React.FC = () => {
  React.useEffect(() => {
    initTelegramWebApp();
  }, []);
  
  return (
    <I18nextProvider i18n={i18n}>
      <AppProvider>
        <Router>
          <div className="app-container pb-16 min-h-screen bg-gray-50">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/games" element={<GamesPage />} />
              <Route path="/games/magic-ball" element={<MagicBall />} />
              <Route path="/games/tarot-card" element={<TarotCard />} />
              <Route path="/tasks" element={<TasksPage />} />
              <Route path="/rewards" element={<RewardsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <TabBar />
          </div>
        </Router>
      </AppProvider>
    </I18nextProvider>
  );
};

export default App;
