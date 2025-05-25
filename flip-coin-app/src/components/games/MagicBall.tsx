import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Prediction } from '../../types';
import { useAppContext } from '../../context/AppContext';

const predictions: Prediction[] = [
  {
    id: 1,
    text: {
      ru: 'Определенно да',
      en: 'Definitely yes'
    }
  },
  {
    id: 2,
    text: {
      ru: 'Весьма вероятно',
      en: 'Very likely'
    }
  },
  {
    id: 3,
    text: {
      ru: 'Возможно',
      en: 'Perhaps'
    }
  },
  {
    id: 4,
    text: {
      ru: 'Спросите позже',
      en: 'Ask again later'
    }
  },
  {
    id: 5,
    text: {
      ru: 'Не могу предсказать сейчас',
      en: 'Cannot predict now'
    }
  },
  {
    id: 6,
    text: {
      ru: 'Не рассчитывайте на это',
      en: 'Don\'t count on it'
    }
  },
  {
    id: 7,
    text: {
      ru: 'Мои источники говорят нет',
      en: 'My sources say no'
    }
  },
  {
    id: 8,
    text: {
      ru: 'Определенно нет',
      en: 'Definitely no'
    }
  }
];

const MagicBall: React.FC = () => {
  const { t } = useTranslation();
  const { profile, addTokens } = useAppContext();
  
  const [isShaking, setIsShaking] = React.useState(false);
  const [prediction, setPrediction] = React.useState<Prediction | null>(null);
  const [question, setQuestion] = React.useState('');
  
  // Sound effect references
  const shakeSoundRef = React.useRef<HTMLAudioElement | null>(null);
  const resultSoundRef = React.useRef<HTMLAudioElement | null>(null);
  
  React.useEffect(() => {
    // Initialize sound effects
    shakeSoundRef.current = new Audio('/src/assets/sounds/shake.mp3');
    resultSoundRef.current = new Audio('/src/assets/sounds/result.mp3');
  }, []);
  
  const playSound = (sound: HTMLAudioElement | null) => {
    if (sound && profile.soundEnabled) {
      sound.currentTime = 0;
      sound.play().catch(e => console.error("Error playing sound:", e));
    }
  };
  
  const shakeBall = () => {
    if (isShaking || !question.trim()) return;
    
    setIsShaking(true);
    playSound(shakeSoundRef.current);
    setPrediction(null);
    
    setTimeout(() => {
      const randomPrediction = predictions[Math.floor(Math.random() * predictions.length)];
      setPrediction(randomPrediction);
      setIsShaking(false);
      playSound(resultSoundRef.current);
      
      // Add tokens for playing
      addTokens(1);
    }, 2000);
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold mb-2">
          {t('game.magicBall.title')}
        </h1>
        <p className="text-sm text-gray-600">
          {t('game.magicBall.description')}
        </p>
      </div>
      
      <div className="w-full max-w-md mb-6">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={t('game.magicBall.questionPlaceholder')}
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isShaking}
        />
      </div>
      
      <div className="relative w-48 h-48 mb-8">
        <motion.div
          className="w-full h-full rounded-full bg-black flex items-center justify-center shadow-lg"
          animate={{
            rotate: isShaking ? [0, -10, 10, -10, 10, 0] : 0,
            scale: isShaking ? [1, 1.05, 0.95, 1.05, 0.95, 1] : 1
          }}
          transition={{
            duration: isShaking ? 1 : 0.5,
            repeat: isShaking ? 1 : 0,
            ease: "easeInOut"
          }}
        >
          <motion.div
            className="w-24 h-24 rounded-full bg-blue-500 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ 
              opacity: prediction ? 1 : 0,
              scale: prediction ? [0.5, 1.1, 1] : 0.5
            }}
            transition={{ duration: 0.5 }}
          >
            {prediction && (
              <p className="text-white text-center text-sm px-2">
                {prediction.text[profile.language]}
              </p>
            )}
          </motion.div>
        </motion.div>
      </div>
      
      <motion.button
        className="px-6 py-3 bg-blue-500 text-white rounded-full font-medium shadow-lg"
        whileTap={{ scale: 0.95 }}
        whileHover={{ scale: 1.05 }}
        disabled={isShaking || !question.trim()}
        onClick={shakeBall}
      >
        {isShaking ? t('game.magicBall.shaking') : t('game.magicBall.shake')}
      </motion.button>
    </div>
  );
};

export default MagicBall;
