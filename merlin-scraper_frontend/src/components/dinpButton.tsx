import React, { useState } from 'react';

interface DinpButtonProps {
  isLoggedIn: boolean;
  setNotification: (notif: {
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
  }) => void;
  onCompleted?: () => void; // ← Callback koji se poziva nakon uspješnog fetcha
}

const DinpButton: React.FC<DinpButtonProps> = ({
  isLoggedIn,
  setNotification,
  onCompleted
}) => {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleDinpProcess = async () => {
    setIsProcessing(true);

    try {
      const response = await fetch('http://localhost:3000/process_dinp', {
        method: 'GET',
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Greška prilikom pokretanja DINP obrade.');
      }

      setNotification({
        type: 'success',
        message: data.message || 'DINP obrada završena!',
      });

      // ✅ Pozovi callback za dohvat novih zadataka
      if (onCompleted) {
        onCompleted();
      }

    } catch (error: any) {
      setNotification({
        type: 'error',
        message: error.message || 'Greška prilikom pokretanja DINP obrade.',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <button
      onClick={handleDinpProcess}
      disabled={!isLoggedIn || isProcessing}
      className={`px-4 py-2 text-sm rounded-md font-medium border 
        ${isLoggedIn ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-gray-300 text-gray-600 cursor-not-allowed'}
        transition duration-200`}
    >
      {isProcessing ? 'Obrađujem DINP...' : 'Obradi DINP'}
    </button>
  );
};

export default DinpButton;
