import React from 'react';
import { LogIn } from 'lucide-react';

interface LoginButtonProps {
  onClick: () => void;
  isLoggingIn: boolean;
  isLoggedIn: boolean;
}

const LoginButton: React.FC<LoginButtonProps> = ({ onClick, isLoggingIn, isLoggedIn }) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoggingIn || isLoggedIn}
      className={`flex items-center justify-center px-4 py-2 rounded-md font-medium transition-all duration-200 ${
        isLoggedIn 
          ? 'bg-green-100 text-green-800 cursor-default'
          : isLoggingIn
            ? 'bg-blue-100 text-blue-800 cursor-wait'
            : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
      }`}
    >
      {isLoggingIn ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-800" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Logging in...
        </>
      ) : isLoggedIn ? (
        <>
          <LogIn size={18} className="mr-2" />
          Logged In
        </>
      ) : (
        <>
          <LogIn size={18} className="mr-2" />
          Login
        </>
      )}
    </button>
  );
};

export default LoginButton;