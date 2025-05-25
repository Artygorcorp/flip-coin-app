import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// English translations
const enTranslations = {
  common: {
    save: 'Save',
    edit: 'Edit',
    copy: 'Copy',
    copied: 'Copied!',
    loading: 'Loading...',
  },
  pages: {
    home: {
      title: 'Heads or Tails',
    },
    games: {
      title: 'Games',
    },
    tasks: {
      title: 'Tasks',
      comingSoon: 'Coming Soon',
      description: 'This section is under development. Check back later for exciting tasks and challenges!',
    },
    rewards: {
      title: 'Rewards',
    },
    profile: {
      title: 'Profile',
    },
  },
  game: {
    flipCoin: {
      title: 'Heads or Tails',
      description: 'Flip a coin and test your luck!',
      flip: 'Flip Coin',
      flipping: 'Flipping...',
      tokens: 'Your tokens',
    },
    magicBall: {
      title: 'Magic 8 Ball',
      description: 'Ask a question and shake the ball for an answer',
      questionPlaceholder: 'Type your question here...',
      shake: 'Shake Ball',
      shaking: 'Shaking...',
    },
    tarotCard: {
      title: 'Tarot Card',
      description: 'Draw a card to reveal your fortune',
      draw: 'Draw Card',
      drawing: 'Drawing...',
      cardBack: 'TAROT',
      cardImage: 'Card Image',
    },
  },
  games: {
    flipCoin: {
      title: 'Heads or Tails',
      description: 'Flip a coin and test your luck',
    },
    magicBall: {
      title: 'Magic 8 Ball',
      description: 'Get answers to your questions',
    },
    tarotCard: {
      title: 'Tarot Card',
      description: 'Reveal your fortune with a card',
    },
  },
  profile: {
    nickname: 'Nickname',
    enterNickname: 'Enter your nickname',
    balance: 'Token Balance',
    inviteFriend: 'Invite a Friend',
    language: 'Language',
    sound: 'Sound',
  },
  rewards: {
    redeemSuccess: 'Successfully redeemed reward!',
  },
  navigation: {
    home: 'Home',
    games: 'Games',
    tasks: 'Tasks',
    rewards: 'Rewards',
    profile: 'Profile',
  },
};

// Russian translations
const ruTranslations = {
  common: {
    save: 'Сохранить',
    edit: 'Изменить',
    copy: 'Копировать',
    copied: 'Скопировано!',
    loading: 'Загрузка...',
  },
  pages: {
    home: {
      title: 'Орел или Решка',
    },
    games: {
      title: 'Игры',
    },
    tasks: {
      title: 'Задания',
      comingSoon: 'Скоро',
      description: 'Этот раздел находится в разработке. Загляните позже для интересных заданий и испытаний!',
    },
    rewards: {
      title: 'Награды',
    },
    profile: {
      title: 'Профиль',
    },
  },
  game: {
    flipCoin: {
      title: 'Орел или Решка',
      description: 'Подбросьте монету и испытайте удачу!',
      flip: 'Подбросить',
      flipping: 'Подбрасываем...',
      tokens: 'Ваши токены',
    },
    magicBall: {
      title: 'Шар Предсказаний',
      description: 'Задайте вопрос и встряхните шар для ответа',
      questionPlaceholder: 'Введите ваш вопрос здесь...',
      shake: 'Встряхнуть',
      shaking: 'Встряхиваем...',
    },
    tarotCard: {
      title: 'Карта Таро',
      description: 'Вытяните карту, чтобы узнать свою судьбу',
      draw: 'Вытянуть Карту',
      drawing: 'Тянем карту...',
      cardBack: 'ТАРО',
      cardImage: 'Изображение карты',
    },
  },
  games: {
    flipCoin: {
      title: 'Орел или Решка',
      description: 'Подбросьте монету и испытайте удачу',
    },
    magicBall: {
      title: 'Шар Предсказаний',
      description: 'Получите ответы на ваши вопросы',
    },
    tarotCard: {
      title: 'Карта Таро',
      description: 'Узнайте свою судьбу с помощью карты',
    },
  },
  profile: {
    nickname: 'Никнейм',
    enterNickname: 'Введите ваш никнейм',
    balance: 'Баланс токенов',
    inviteFriend: 'Пригласить друга',
    language: 'Язык',
    sound: 'Звук',
  },
  rewards: {
    redeemSuccess: 'Награда успешно получена!',
  },
  navigation: {
    home: 'Главная',
    games: 'Игры',
    tasks: 'Задания',
    rewards: 'Награды',
    profile: 'Профиль',
  },
};

// Initialize i18next
i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      ru: { translation: ruTranslations },
    },
    lng: 'en', // Default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already escapes values
    },
  });

export default i18n;
