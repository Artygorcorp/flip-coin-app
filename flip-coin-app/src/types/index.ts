export type Language = 'ru' | 'en';

export interface UserProfile {
  nickname: string;
  flipTokens: number;
  language: Language;
  soundEnabled: boolean;
}

export type CoinSide = 'heads' | 'tails';

export interface GameResult {
  result: CoinSide;
  timestamp: number;
}

export interface TarotCard {
  id: number;
  name: {
    ru: string;
    en: string;
  };
  meaning: {
    ru: string;
    en: string;
  };
  image: string;
}

export interface Prediction {
  id: number;
  text: {
    ru: string;
    en: string;
  };
}

export interface Reward {
  id: number;
  name: {
    ru: string;
    en: string;
  };
  description: {
    ru: string;
    en: string;
  };
  cost: number;
  image: string;
}
