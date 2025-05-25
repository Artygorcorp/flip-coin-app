import React, { useEffect, useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const ProfilePage: React.FC = () => {
  const { t } = useTranslation();
  const { profile, updateProfile, setLanguage, setSoundEnabled } = useAppContext();
  const [nickname, setNickname] = useState(profile.nickname);
  const [referralCode, setReferralCode] = useState('');
  const [referralMessage, setReferralMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Fetch user profile from API
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await axios.get(`${API_BASE_URL}/auth/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data.user) {
          updateProfile(response.data.user);
          setNickname(response.data.user.nickname);
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
      }
    };

    fetchProfile();
  }, [updateProfile]);

  const handleSaveProfile = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await axios.patch(
        `${API_BASE_URL}/auth/profile`,
        { nickname },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.user) {
        updateProfile(response.data.user);
      }
    } catch (error) {
      console.error('Error updating profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLanguageChange = async (lang: 'ru' | 'en') => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await axios.patch(
        `${API_BASE_URL}/auth/profile`,
        { language: lang },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.user) {
        updateProfile(response.data.user);
        setLanguage(lang);
      }
    } catch (error) {
      console.error('Error updating language:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSoundToggle = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await axios.patch(
        `${API_BASE_URL}/auth/profile`,
        { sound_enabled: !profile.soundEnabled },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.user) {
        updateProfile(response.data.user);
        setSoundEnabled(!profile.soundEnabled);
      }
    } catch (error) {
      console.error('Error updating sound settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReferralSubmit = async () => {
    if (!referralCode.trim()) return;
    
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await axios.post(
        `${API_BASE_URL}/auth/referral`,
        { referral_code: referralCode },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setReferralMessage(t('profile.referralSuccess', 'Referral code applied successfully!'));
      updateProfile({
        ...profile,
        flipTokens: response.data.current_balance
      });
      
      setTimeout(() => {
        setReferralMessage(null);
      }, 3000);
      
      setReferralCode('');
    } catch (error) {
      console.error('Error applying referral code:', error);
      setReferralMessage(t('profile.referralError', 'Invalid referral code'));
      
      setTimeout(() => {
        setReferralMessage(null);
      }, 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const copyReferralLink = () => {
    const referralLink = `https://t.me/your_bot?start=ref_${profile.telegramId}`;
    navigator.clipboard.writeText(referralLink);
    setReferralMessage(t('profile.linkCopied', 'Referral link copied to clipboard!'));
    
    setTimeout(() => {
      setReferralMessage(null);
    }, 3000);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6">{t('pages.profile.title')}</h1>
      
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium">{t('profile.accountInfo')}</h2>
          <div className="bg-blue-100 px-3 py-1 rounded-full">
            <span className="font-medium">{profile.flipTokens} FLIP</span>
          </div>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('profile.nickname')}
          </label>
          <div className="flex">
            <input
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2"
              placeholder={t('profile.enterNickname')}
            />
            <button
              onClick={handleSaveProfile}
              disabled={isLoading}
              className="bg-blue-500 text-white px-4 py-2 rounded-r-lg"
            >
              {t('common.save')}
            </button>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <h2 className="text-lg font-medium mb-4">{t('profile.settings')}</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('profile.language')}
          </label>
          <div className="flex space-x-2">
            <button
              onClick={() => handleLanguageChange('ru')}
              className={`px-4 py-2 rounded-lg ${
                profile.language === 'ru'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              RU
            </button>
            <button
              onClick={() => handleLanguageChange('en')}
              className={`px-4 py-2 rounded-lg ${
                profile.language === 'en'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              EN
            </button>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-700">
            {t('profile.sound')}
          </label>
          <div
            onClick={handleSoundToggle}
            className={`w-12 h-6 flex items-center rounded-full p-1 cursor-pointer ${
              profile.soundEnabled ? 'bg-green-500' : 'bg-gray-300'
            }`}
          >
            <div
              className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
                profile.soundEnabled ? 'translate-x-6' : ''
              }`}
            />
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-4">
        <h2 className="text-lg font-medium mb-4">{t('profile.referral')}</h2>
        
        {referralMessage && (
          <div className="bg-blue-100 text-blue-800 p-3 rounded-lg mb-4 text-center">
            {referralMessage}
          </div>
        )}
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('profile.inviteFriend')}
          </label>
          <button
            onClick={copyReferralLink}
            className="w-full bg-green-500 text-white px-4 py-2 rounded-lg"
          >
            {t('profile.copyReferralLink')}
          </button>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('profile.enterReferralCode')}
          </label>
          <div className="flex">
            <input
              type="text"
              value={referralCode}
              onChange={(e) => setReferralCode(e.target.value)}
              className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2"
              placeholder={t('profile.referralCodePlaceholder')}
            />
            <button
              onClick={handleReferralSubmit}
              disabled={isLoading || !referralCode.trim()}
              className="bg-blue-500 text-white px-4 py-2 rounded-r-lg"
            >
              {t('common.apply')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
