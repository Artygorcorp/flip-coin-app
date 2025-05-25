import React, { useEffect, useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const CoinFlip: React.FC = () => {
  const { t } = useTranslation();
  const { profile, addTokens } = useAppContext();
  
  const [isFlipping, setIsFlipping] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [tokensEarned, setTokensEarned] = useState(0);
  const [playsToday, setPlaysToday] = useState(0);
  const [maxPlays, setMaxPlays] = useState(50);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Fetch daily limits when component mounts
    const fetchLimits = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;
        
        const response = await axios.get(`${API_BASE_URL}/games/limits`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.data.limits && response.data.limits.flip_coin) {
          setPlaysToday(response.data.limits.flip_coin.current);
          setMaxPlays(response.data.limits.flip_coin.max);
        }
      } catch (error) {
        console.error('Error fetching limits:', error);
      }
    };
    
    fetchLimits();
  }, []);
  
  const flipCoin = async () => {
    if (isFlipping) return;
    
    try {
      setIsFlipping(true);
      setResult(null);
      setError(null);
      
      // Play flip sound if enabled
      if (profile.soundEnabled) {
        const audio = new Audio('/sounds/coin-flip.mp3');
        audio.play();
      }
      
      // Call API to flip coin
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/games/flip-coin`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Wait for animation
      setTimeout(() => {
        setResult(response.data.result);
        setTokensEarned(response.data.tokens_earned);
        setPlaysToday(response.data.plays_today);
        
        // Update tokens in context
        addTokens(response.data.tokens_earned);
        
        // Play result sound if enabled
        if (profile.soundEnabled) {
          const resultAudio = new Audio('/sounds/coin-result.mp3');
          resultAudio.play();
        }
        
        setIsFlipping(false);
      }, 1500);
      
    } catch (error) {
      console.error('Error flipping coin:', error);
      setIsFlipping(false);
      
      // Check if daily limit reached
      if (axios.isAxiosError(error) && error.response?.status === 429) {
        setError(t('games.dailyLimitReached'));
      } else {
        setError(t('common.errorOccurred'));
      }
    }
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <h1 className="text-2xl font-bold mb-6">
        {t('games.flipCoin.title')}
      </h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 w-full max-w-md mb-6">
        <div className="flex justify-between items-center mb-4">
          <span className="text-gray-600">
            {t('games.playsToday')}: {playsToday}/{maxPlays}
          </span>
          <span className="font-medium">{profile.flipTokens} FLIP</span>
        </div>
        
        <div className="flex justify-center mb-8">
          <motion.div
            className="w-32 h-32 rounded-full bg-yellow-400 flex items-center justify-center shadow-lg"
            animate={{
              rotateX: isFlipping ? [0, 720] : 0,
              scale: isFlipping ? [1, 1.2, 1] : 1,
            }}
            transition={{ duration: 1.5 }}
          >
            {!isFlipping && result && (
              <span className="text-4xl">
                {result === 'heads' ? '🦅' : '👑'}
              </span>
            )}
            {!isFlipping && !result && (
              <span className="text-4xl">?</span>
            )}
          </motion.div>
        </div>
        
        {result && !isFlipping && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-6"
          >
            <p className="text-xl font-medium mb-1">
              {result === 'heads' 
                ? t('games.flipCoin.resultHeads') 
                : t('games.flipCoin.resultTails')}
            </p>
            <p className="text-green-600">
              +{tokensEarned} FLIP
            </p>
          </motion.div>
        )}
        
        {error && (
          <div className="bg-red-100 text-red-800 p-3 rounded-lg mb-4 text-center">
            {error}
          </div>
        )}
        
        <motion.button
          whileTap={{ scale: 0.95 }}
          className="w-full bg-blue-500 text-white py-3 rounded-lg font-medium"
          onClick={flipCoin}
          disabled={isFlipping || playsToday >= maxPlays}
        >
          {isFlipping 
            ? t('games.flipCoin.flipping') 
            : t('games.flipCoin.flipButton')}
        </motion.button>
      </div>
      
      <div className="bg-gray-100 rounded-lg p-4 w-full max-w-md">
        <h2 className="font-medium mb-2">{t('games.flipCoin.howToPlay')}</h2>
        <p className="text-gray-600 text-sm">
          {t('games.flipCoin.instructions')}
        </p>
      </div>
    </div>
  );
};

export default CoinFlip;
