import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

interface GameCardProps {
  title: string;
  description: string;
  icon: string;
  path: string;
}

const GameCard: React.FC<GameCardProps> = ({ title, description, icon, path }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
      className="bg-white rounded-lg shadow-md p-4 mb-4"
    >
      <Link to={path} className="flex items-center">
        <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mr-4">
          <span className="text-2xl">{icon}</span>
        </div>
        <div>
          <h3 className="font-medium text-lg">{title}</h3>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </Link>
    </motion.div>
  );
};

const GamesPage: React.FC = () => {
  const { t } = useTranslation();
  
  const games = [
    {
      id: 'flip-coin',
      title: t('games.flipCoin.title'),
      description: t('games.flipCoin.description'),
      icon: '🪙',
      path: '/home'
    },
    {
      id: 'magic-ball',
      title: t('games.magicBall.title'),
      description: t('games.magicBall.description'),
      icon: '🔮',
      path: '/games/magic-ball'
    },
    {
      id: 'tarot-card',
      title: t('games.tarotCard.title'),
      description: t('games.tarotCard.description'),
      icon: '🃏',
      path: '/games/tarot-card'
    }
  ];
  
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6 text-center">
        {t('pages.games.title')}
      </h1>
      
      <div className="max-w-md mx-auto">
        {games.map(game => (
          <GameCard
            key={game.id}
            title={game.title}
            description={game.description}
            icon={game.icon}
            path={game.path}
          />
        ))}
      </div>
    </div>
  );
};

export default GamesPage;
