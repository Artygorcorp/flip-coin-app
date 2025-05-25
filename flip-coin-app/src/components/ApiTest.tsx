import React, { useEffect, useState } from 'react';
import api from '../config/api';

const ApiTest: React.FC = () => {
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await api.get('/');
        setStatus(JSON.stringify(response.data, null, 2));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
    };

    checkApi();
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h2>API Connection Test</h2>
      {status && (
        <div style={{ backgroundColor: '#e8f5e9', padding: '15px', borderRadius: '5px' }}>
          <pre>{status}</pre>
        </div>
      )}
      {error && (
        <div style={{ backgroundColor: '#ffebee', padding: '15px', borderRadius: '5px' }}>
          <pre>{error}</pre>
        </div>
      )}
    </div>
  );
};

export default ApiTest;
