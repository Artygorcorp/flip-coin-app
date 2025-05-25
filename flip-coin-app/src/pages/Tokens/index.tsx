import React, { useEffect, useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

interface Package {
  id: string;
  tokens: number;
  price: number;
  currency: string;
  description: {
    en: string;
    ru: string;
  };
}

const TokensPage: React.FC = () => {
  const { t } = useTranslation();
  const { profile, addTokens } = useAppContext();
  
  const [packages, setPackages] = useState<Package[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  useEffect(() => {
    // Fetch token packages when component mounts
    fetchPackages();
  }, []);
  
  const fetchPackages = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const token = localStorage.getItem('token');
      if (!token) {
        setError(t('common.notAuthenticated'));
        setIsLoading(false);
        return;
      }
      
      const response = await axios.get(`${API_BASE_URL}/payments/packages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPackages(response.data.packages);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching packages:', error);
      setError(t('common.errorFetchingData'));
      setIsLoading(false);
    }
  };
  
  const purchaseTokens = async (packageId: string) => {
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.post(
        `${API_BASE_URL}/payments/create`,
        { package_id: packageId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // In a real implementation, redirect to Telegram payment
      // For now, just simulate a successful payment
      simulateSuccessfulPayment(response.data.payment_id, packageId);
      
    } catch (error) {
      console.error('Error creating payment:', error);
      
      // Show specific error if available
      if (axios.isAxiosError(error) && error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError(t('common.errorOccurred'));
      }
      
      // Hide error after 3 seconds
      setTimeout(() => {
        setError(null);
      }, 3000);
    }
  };
  
  // This is just for testing - in production, payment would be handled by Telegram
  const simulateSuccessfulPayment = (paymentId: number, packageId: string) => {
    const selectedPackage = packages.find(p => p.id === packageId);
    
    if (!selectedPackage) return;
    
    // Show loading
    setIsLoading(true);
    
    // Simulate payment processing
    setTimeout(() => {
      // Add tokens
      addTokens(selectedPackage.tokens);
      
      // Show success message
      setSuccessMessage(t('payments.purchaseSuccess', {
        tokens: selectedPackage.tokens
      }));
      
      // Hide message after 3 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
      
      setIsLoading(false);
    }, 2000);
  };
  
  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          {t('pages.tokens.title')}
        </h1>
        <div className="bg-blue-100 px-3 py-1 rounded-full">
          <span className="font-medium">{profile.flipTokens} FLIP</span>
        </div>
      </div>
      
      {successMessage && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="bg-green-100 text-green-800 p-3 rounded-lg mb-4 text-center"
        >
          {successMessage}
        </motion.div>
      )}
      
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="bg-red-100 text-red-800 p-3 rounded-lg mb-4 text-center"
        >
          {error}
        </motion.div>
      )}
      
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <h2 className="font-medium mb-4">{t('payments.buyTokens')}</h2>
        
        {isLoading ? (
          <div className="flex justify-center items-center h-40">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {packages.map(pkg => (
              <motion.div
                key={pkg.id}
                whileHover={{ scale: 1.02 }}
                className="border border-gray-200 rounded-lg p-4 flex flex-col"
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xl font-bold">{pkg.tokens} FLIP</span>
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                    {pkg.price} {pkg.currency}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-4">
                  {profile.language === 'en' ? pkg.description.en : pkg.description.ru}
                </p>
                
                <motion.button
                  whileTap={{ scale: 0.95 }}
                  className="mt-auto bg-green-500 text-white py-2 rounded-lg font-medium"
                  onClick={() => purchaseTokens(pkg.id)}
                >
                  {t('payments.buyNow')}
                </motion.button>
              </motion.div>
            ))}
          </div>
        )}
      </div>
      
      <div className="bg-gray-100 rounded-lg p-4">
        <h2 className="font-medium mb-2">{t('payments.aboutTokens')}</h2>
        <p className="text-gray-600 text-sm">
          {t('payments.tokensDescription')}
        </p>
      </div>
    </div>
  );
};

export default TokensPage;
