import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { useAppContext } from '../../context/AppContext';

const RewardsPage: React.FC = () => {
  const { t } = useTranslation();
  const { profile, addTokens } = useAppContext();
  
  const [redeemMessage, setRedeemMessage] = React.useState<string | null>(null);
  
  const rewards = [
    {
      id: 1,
      name: {
        ru: 'Стикерпак "Монетки"',
        en: 'Coin Sticker Pack'
      },
      description: {
        ru: 'Набор из 10 стикеров с монетками для Telegram',
        en: '10 coin-themed stickers for Telegram'
      },
      cost: 50,
      image: '🎭'
    },
    {
      id: 2,
      name: {
        ru: 'VIP статус',
        en: 'VIP Status'
      },
      description: {
        ru: 'Особый статус в приложении и доступ к эксклюзивным играм',
        en: 'Special status in the app and access to exclusive games'
      },
      cost: 100,
      image: '👑'
    },
    {
      id: 3,
      name: {
        ru: 'Кастомная тема',
        en: 'Custom Theme'
      },
      description: {
        ru: 'Уникальная тема оформления для приложения',
        en: 'Unique theme for the application'
      },
      cost: 75,
      image: '🎨'
    },
    {
      id: 4,
      name: {
        ru: 'Премиум аватар',
        en: 'Premium Avatar'
      },
      description: {
        ru: 'Эксклюзивный аватар для вашего профиля',
        en: 'Exclusive avatar for your profile'
      },
      cost: 60,
      image: '🧩'
    }
  ];
  
  const handleRedeem = (_id: number, cost: number) => {
    if (profile.flipTokens >= cost) {
      addTokens(-cost);
      setRedeemMessage(t('rewards.redeemSuccess'));
      
      setTimeout(() => {
        setRedeemMessage(null);
      }, 3000);
    }
  };
  
  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          {t('pages.rewards.title')}
        </h1>
        <div className="bg-blue-100 px-3 py-1 rounded-full">
          <span className="font-medium">{profile.flipTokens} FLIP</span>
        </div>
      </div>
      
      {redeemMessage && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="bg-green-100 text-green-800 p-3 rounded-lg mb-4 text-center"
        >
          {redeemMessage}
        </motion.div>
      )}
      
      <div className="max-w-md mx-auto">
        {rewards.map(reward => (
          <div
            key={reward.id}
            className="bg-white rounded-lg shadow-md p-4 mb-4 flex items-center"
          >
            <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center mr-4">
              <span className="text-2xl">{reward.image}</span>
            </div>
            <div className="flex-1">
              <h3 className="font-medium">{reward.name[profile.language]}</h3>
              <p className="text-sm text-gray-600">{reward.description[profile.language]}</p>
              <div className="flex items-center justify-between mt-2">
                <span className="text-sm font-bold">{reward.cost} FLIP</span>
                <motion.button
                  whileTap={{ scale: 0.95 }}
                  className={`px-3 py-1 rounded-full text-sm ${
                    profile.flipTokens < reward.cost 
                      ? 'bg-gray-300 text-gray-500' 
                      : 'bg-green-500 text-white'
                  }`}
                  onClick={() => handleRedeem(reward.id, reward.cost)}
                  disabled={profile.flipTokens < reward.cost}
                >
                  {t('common.redeem', 'Redeem')}
                </motion.button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RewardsPage;
