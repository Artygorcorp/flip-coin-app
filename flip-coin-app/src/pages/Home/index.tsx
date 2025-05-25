import React from 'react';
import CoinFlip from '../../components/games/CoinFlip';

const HomePage: React.FC = () => {
  return (
    <div className="p-4">
      <CoinFlip />
    </div>
  );
};

export default HomePage;
