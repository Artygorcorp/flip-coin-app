import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import type { TarotCard as TarotCardType } from '../../types';
import { useAppContext } from '../../context/AppContext';

const tarotCards: TarotCardType[] = [
  {
    id: 1,
    name: {
      ru: 'Шут',
      en: 'The Fool'
    },
    meaning: {
      ru: 'Новые начинания, спонтанность, свобода, риск, потенциал',
      en: 'New beginnings, spontaneity, freedom, risk, potential'
    },
    image: '/src/assets/images/fool.png'
  },
  {
    id: 2,
    name: {
      ru: 'Маг',
      en: 'The Magician'
    },
    meaning: {
      ru: 'Проявление, сила воли, мастерство, вдохновение',
      en: 'Manifestation, willpower, skill, inspiration'
    },
    image: '/src/assets/images/magician.png'
  },
  {
    id: 3,
    name: {
      ru: 'Верховная Жрица',
      en: 'The High Priestess'
    },
    meaning: {
      ru: 'Интуиция, подсознание, божественное женское начало',
      en: 'Intuition, unconscious, divine feminine'
    },
    image: '/src/assets/images/priestess.png'
  },
  {
    id: 4,
    name: {
      ru: 'Императрица',
      en: 'The Empress'
    },
    meaning: {
      ru: 'Плодородие, женственность, красота, природа, изобилие',
      en: 'Fertility, femininity, beauty, nature, abundance'
    },
    image: '/src/assets/images/empress.png'
  },
  {
    id: 5,
    name: {
      ru: 'Император',
      en: 'The Emperor'
    },
    meaning: {
      ru: 'Авторитет, структура, контроль, отцовская фигура',
      en: 'Authority, structure, control, fatherhood'
    },
    image: '/src/assets/images/emperor.png'
  },
  {
    id: 6,
    name: {
      ru: 'Иерофант',
      en: 'The Hierophant'
    },
    meaning: {
      ru: 'Духовная мудрость, религиозные убеждения, традиции',
      en: 'Spiritual wisdom, religious beliefs, tradition'
    },
    image: '/src/assets/images/hierophant.png'
  },
  {
    id: 7,
    name: {
      ru: 'Влюбленные',
      en: 'The Lovers'
    },
    meaning: {
      ru: 'Любовь, гармония, отношения, выбор, выравнивание ценностей',
      en: 'Love, harmony, relationships, choices, alignment of values'
    },
    image: '/src/assets/images/lovers.png'
  },
  {
    id: 8,
    name: {
      ru: 'Колесница',
      en: 'The Chariot'
    },
    meaning: {
      ru: 'Контроль, сила воли, победа, напор, решительность',
      en: 'Control, willpower, victory, assertion, determination'
    },
    image: '/src/assets/images/chariot.png'
  }
];

const TarotCard: React.FC = () => {
  const { t } = useTranslation();
  const { profile, addTokens } = useAppContext();
  
  const [isFlipping, setIsFlipping] = React.useState(false);
  const [selectedCard, setSelectedCard] = React.useState<TarotCardType | null>(null);
  
  // Sound effect references
  const cardSoundRef = React.useRef<HTMLAudioElement | null>(null);
  const resultSoundRef = React.useRef<HTMLAudioElement | null>(null);
  
  React.useEffect(() => {
    // Initialize sound effects
    cardSoundRef.current = new Audio('/src/assets/sounds/card.mp3');
    resultSoundRef.current = new Audio('/src/assets/sounds/result.mp3');
  }, []);
  
  const playSound = (sound: HTMLAudioElement | null) => {
    if (sound && profile.soundEnabled) {
      sound.currentTime = 0;
      sound.play().catch(e => console.error("Error playing sound:", e));
    }
  };
  
  const drawCard = () => {
    if (isFlipping) return;
    
    setIsFlipping(true);
    playSound(cardSoundRef.current);
    setSelectedCard(null);
    
    setTimeout(() => {
      const randomCard = tarotCards[Math.floor(Math.random() * tarotCards.length)];
      setSelectedCard(randomCard);
      setIsFlipping(false);
      playSound(resultSoundRef.current);
      
      // Add tokens for playing
      addTokens(1);
    }, 1500);
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold mb-2">
          {t('game.tarotCard.title')}
        </h1>
        <p className="text-sm text-gray-600">
          {t('game.tarotCard.description')}
        </p>
      </div>
      
      <div className="relative w-64 h-96 mb-8">
        <motion.div
          className="absolute w-full h-full rounded-lg bg-gradient-to-b from-purple-600 to-indigo-900 flex items-center justify-center"
          animate={{
            rotateY: isFlipping ? 180 : 0,
            scale: isFlipping ? [1, 1.05, 1] : 1,
          }}
          transition={{
            duration: isFlipping ? 1 : 0.5,
            ease: "easeInOut"
          }}
        >
          {selectedCard ? (
            <div className="w-full h-full p-4 flex flex-col items-center justify-between">
              <h3 className="text-xl font-bold text-white">
                {selectedCard.name[profile.language]}
              </h3>
              
              <div className="w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center">
                <span className="text-gray-500">[{t('game.tarotCard.cardImage')}]</span>
              </div>
              
              <p className="text-sm text-white text-center">
                {selectedCard.meaning[profile.language]}
              </p>
            </div>
          ) : (
            <div className="w-full h-full bg-indigo-800 rounded-lg flex items-center justify-center">
              <div className="w-3/4 h-3/4 border-2 border-white rounded-lg flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {t('game.tarotCard.cardBack')}
                </span>
              </div>
            </div>
          )}
        </motion.div>
      </div>
      
      <motion.button
        className="px-6 py-3 bg-purple-600 text-white rounded-full font-medium shadow-lg"
        whileTap={{ scale: 0.95 }}
        whileHover={{ scale: 1.05 }}
        disabled={isFlipping}
        onClick={drawCard}
      >
        {isFlipping ? t('game.tarotCard.drawing') : t('game.tarotCard.draw')}
      </motion.button>
    </div>
  );
};

export default TarotCard;
