import React from 'react';
import { ClipboardList } from 'lucide-react';

interface HeaderProps {
  isLoggedIn: boolean;
}

const Header: React.FC<HeaderProps> = ({ isLoggedIn }) => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-6 px-4 shadow-md">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <ClipboardList size={32} className="text-white" />
          <h1 className="text-2xl font-bold">GenTask</h1>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center ${
            isLoggedIn ? 'bg-green-500' : 'bg-gray-500'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              isLoggedIn ? 'bg-green-100 animate-pulse' : 'bg-gray-300'
            } mr-2`}></span>
            {isLoggedIn ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;