import React, { useEffect, useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import axios from 'axios';
import { Link } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

interface Task {
  id: number;
  title: string;
  description: string;
  type: string;
  reward_tokens: number;
  required_game_type: string | null;
  required_count: number;
}

const TasksPage: React.FC = () => {
  const { t } = useTranslation();
  const { profile, addTokens } = useAppContext();
  
  const [tasks, setTasks] = useState<Task[]>([]);
  const [completedTasks, setCompletedTasks] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  useEffect(() => {
    // Fetch tasks when component mounts
    fetchTasks();
  }, []);
  
  const fetchTasks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const token = localStorage.getItem('token');
      if (!token) {
        setError(t('common.notAuthenticated'));
        setIsLoading(false);
        return;
      }
      
      const response = await axios.get(`${API_BASE_URL}/tasks`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setTasks(response.data.tasks);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setError(t('common.errorFetchingData'));
      setIsLoading(false);
    }
  };
  
  const completeTask = async (taskId: number) => {
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.post(
        `${API_BASE_URL}/tasks/${taskId}/complete`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Add task to completed list
      setCompletedTasks([...completedTasks, taskId]);
      
      // Update tokens
      addTokens(response.data.tokens_awarded);
      
      // Show success message
      setSuccessMessage(t('tasks.completedSuccessfully', {
        tokens: response.data.tokens_awarded
      }));
      
      // Hide message after 3 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
      
      // Refresh tasks
      fetchTasks();
    } catch (error) {
      console.error('Error completing task:', error);
      
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
  
  const getTaskTypeLabel = (type: string) => {
    switch (type) {
      case 'daily':
        return t('tasks.types.daily');
      case 'weekly':
        return t('tasks.types.weekly');
      case 'achievement':
        return t('tasks.types.achievement');
      case 'special':
        return t('tasks.types.special');
      default:
        return type;
    }
  };
  
  const getGameTypeLabel = (type: string | null) => {
    if (!type) return null;
    
    switch (type) {
      case 'flip_coin':
        return t('games.flipCoin.title');
      case 'magic_ball':
        return t('games.magicBall.title');
      case 'tarot_card':
        return t('games.tarotCard.title');
      default:
        return type;
    }
  };
  
  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          {t('pages.tasks.title')}
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
      
      {isLoading ? (
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <p className="text-gray-600 mb-4">{t('tasks.noTasksAvailable')}</p>
          <Link to="/games" className="text-blue-500 font-medium">
            {t('tasks.goToGames')}
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map(task => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-md p-4"
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium">{task.title}</h3>
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                  {getTaskTypeLabel(task.type)}
                </span>
              </div>
              
              <p className="text-gray-600 text-sm mb-3">{task.description}</p>
              
              {task.required_game_type && (
                <div className="text-sm text-gray-500 mb-3">
                  {t('tasks.requiredGame')}: {getGameTypeLabel(task.required_game_type)} ({task.required_count}x)
                </div>
              )}
              
              <div className="flex items-center justify-between mt-2">
                <span className="text-sm font-bold text-green-600">+{task.reward_tokens} FLIP</span>
                <motion.button
                  whileTap={{ scale: 0.95 }}
                  className={`px-3 py-1 rounded-full text-sm ${
                    completedTasks.includes(task.id)
                      ? 'bg-gray-300 text-gray-500'
                      : 'bg-green-500 text-white'
                  }`}
                  onClick={() => completeTask(task.id)}
                  disabled={completedTasks.includes(task.id)}
                >
                  {completedTasks.includes(task.id)
                    ? t('tasks.completed')
                    : t('tasks.complete')}
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TasksPage;
