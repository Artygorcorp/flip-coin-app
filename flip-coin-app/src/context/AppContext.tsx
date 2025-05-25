import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Language } from '../types';

// Define types for user profile
export interface UserProfile {
  id: number;
  telegramId: string;
  nickname: string;
  flipTokens: number;
  language: Language;
  soundEnabled: boolean;
  role: string;
}

// Define types for game results
export interface GameResult {
  result: string;
  tokensEarned: number;
}

// Define context interface
interface AppContextType {
  profile: UserProfile;
  isAuthenticated: boolean;
  updateProfile: (userData: Partial<UserProfile>) => void;
  setLanguage: (lang: Language) => void;
  setSoundEnabled: (enabled: boolean) => void;
  addTokens: (amount: number) => void;
  login: (token: string, userData: UserProfile) => void;
  logout: () => void;
}

// Create default context values
const defaultProfile: UserProfile = {
  id: 0,
  telegramId: '',
  nickname: 'Guest',
  flipTokens: 0,
  language: 'en',
  soundEnabled: true,
  role: 'user'
};

// Create context
const AppContext = createContext<AppContextType>({
  profile: defaultProfile,
  isAuthenticated: false,
  updateProfile: () => {},
  setLanguage: () => {},
  setSoundEnabled: () => {},
  addTokens: () => {},
  login: () => {},
  logout: () => {}
});

// Create provider component
export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [profile, setProfile] = useState<UserProfile>(() => {
    // Try to load profile from localStorage
    const savedProfile = localStorage.getItem('userProfile');
    if (savedProfile) {
      try {
        return JSON.parse(savedProfile);
      } catch (e) {
        return defaultProfile;
      }
    }
    return defaultProfile;
  });
  
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return !!localStorage.getItem('token');
  });

  // Update profile
  const updateProfile = (userData: Partial<UserProfile>) => {
    setProfile(prev => {
      const updated = { ...prev, ...userData };
      localStorage.setItem('userProfile', JSON.stringify(updated));
      return updated;
    });
  };

  // Set language
  const setLanguage = (lang: Language) => {
    updateProfile({ language: lang });
  };

  // Set sound enabled
  const setSoundEnabled = (enabled: boolean) => {
    updateProfile({ soundEnabled: enabled });
  };

  // Add tokens
  const addTokens = (amount: number) => {
    updateProfile({ flipTokens: profile.flipTokens + amount });
  };

  // Login
  const login = (token: string, userData: UserProfile) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
    updateProfile(userData);
  };

  // Logout
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userProfile');
    setIsAuthenticated(false);
    setProfile(defaultProfile);
  };

  return (
    <AppContext.Provider
      value={{
        profile,
        isAuthenticated,
        updateProfile,
        setLanguage,
        setSoundEnabled,
        addTokens,
        login,
        logout
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

// Create hook for using context
export const useAppContext = () => useContext(AppContext);
