import React from 'react';
import { ClipboardList } from 'lucide-react';

interface EmptyStateProps {
  isLoggedIn: boolean;
}

const EmptyState: React.FC<EmptyStateProps> = ({ isLoggedIn }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 mt-8 bg-white rounded-lg shadow-sm border border-gray-100">
      <ClipboardList size={64} className="text-gray-300 mb-4" />
      <h2 className="text-xl font-semibold text-gray-700 mb-2">No Tasks Available</h2>
      <p className="text-gray-500 text-center max-w-md mb-4">
        {isLoggedIn 
          ? 'Click the "Generate Tasks" button to create new tasks for your list.'
          : 'Please log in first and then generate tasks to view them here.'}
      </p>
      <div className="flex flex-col items-center text-sm text-gray-400 space-y-1">
        <div className="flex items-center">
          <div className={`w-2 h-2 rounded-full ${isLoggedIn ? 'bg-green-500' : 'bg-gray-300'} mr-2`}></div>
          <span>Step 1: {isLoggedIn ? '✓ Logged In' : 'Log In'}</span>
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 rounded-full bg-gray-300 mr-2"></div>
          <span>Step 2: Generate Tasks</span>
        </div>
      </div>
    </div>
  );
};

export default EmptyState;