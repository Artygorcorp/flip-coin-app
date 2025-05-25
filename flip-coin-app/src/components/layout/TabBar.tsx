import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';

interface TabBarProps {
  className?: string;
}

const TabBar: React.FC<TabBarProps> = ({ className = '' }) => {
  const { t } = useTranslation();
  const location = useLocation();
  
  const tabs = [
    {
      id: 'home',
      label: t('navigation.home'),
      icon: '🪙',
      path: '/'
    },
    {
      id: 'games',
      label: t('navigation.games'),
      icon: '🎮',
      path: '/games'
    },
    {
      id: 'tasks',
      label: t('navigation.tasks'),
      icon: '✅',
      path: '/tasks'
    },
    {
      id: 'rewards',
      label: t('navigation.rewards'),
      icon: '🎁',
      path: '/rewards'
    },
    {
      id: 'profile',
      label: t('navigation.profile'),
      icon: '👤',
      path: '/profile'
    }
  ];
  
  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };
  
  return (
    <div className={`fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 ${className}`}>
      <div className="flex justify-around items-center h-16">
        {tabs.map(tab => (
          <Link
            key={tab.id}
            to={tab.path}
            className={`flex flex-col items-center justify-center w-full h-full ${
              isActive(tab.path) ? 'text-blue-500' : 'text-gray-500'
            }`}
          >
            <div className="text-xl mb-1">{tab.icon}</div>
            <motion.span
              animate={{ scale: isActive(tab.path) ? 1.05 : 1 }}
              className="text-xs font-medium"
            >
              {tab.label}
            </motion.span>
            {isActive(tab.path) && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 w-1/5 h-0.5 bg-blue-500"
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              />
            )}
          </Link>
        ))}
      </div>
    </div>
  );
};

export default TabBar;
