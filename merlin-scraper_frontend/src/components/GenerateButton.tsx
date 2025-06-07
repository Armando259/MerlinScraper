import React, { useState } from 'react';
import { RefreshCw } from 'lucide-react';

interface GenerateButtonProps {
  onGenerate: (limit: number) => void;
  isGenerating: boolean;
  disabled: boolean;
}

const GenerateButton: React.FC<GenerateButtonProps> = ({ onGenerate, isGenerating, disabled }) => {
  const [limit, setLimit] = useState<number>(10);
  
  const handleLimitChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (!isNaN(value) && value > 0) {
      setLimit(value);
    }
  };
  
  const handleGenerate = () => {
    onGenerate(limit);
  };
  
  return (
    <div className="flex items-center space-x-2">
      <input
        type="number"
        value={limit}
        onChange={handleLimitChange}
        disabled={disabled || isGenerating}
        min="1"
        className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
      />
      <button
        onClick={handleGenerate}
        disabled={disabled || isGenerating}
        className={`flex items-center justify-center px-4 py-2 rounded-md font-medium transition-all duration-200 ${
          disabled 
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : isGenerating
              ? 'bg-purple-100 text-purple-800 cursor-wait'
              : 'bg-purple-600 text-white hover:bg-purple-700 active:bg-purple-800'
        }`}
      >
        {isGenerating ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-purple-800" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating...
          </>
        ) : (
          <>
            <RefreshCw size={18} className="mr-2" />
            Generate Tasks
          </>
        )}
      </button>
    </div>
  );
};

export default GenerateButton;