import React, { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Info } from 'lucide-react';

type NotificationType = 'success' | 'error' | 'info' | 'warning';

interface NotificationProps {
  type: NotificationType;
  message: string;
  onClose: () => void;
  duration?: number;
}

const getIcon = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return <CheckCircle size={20} />;
    case 'error':
      return <XCircle size={20} />;
    case 'warning':
      return <AlertCircle size={20} />;
    case 'info':
      return <Info size={20} />;
  }
};

const getStyles = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return 'bg-green-50 text-green-800 border-green-200';
    case 'error':
      return 'bg-red-50 text-red-800 border-red-200';
    case 'warning':
      return 'bg-amber-50 text-amber-800 border-amber-200';
    case 'info':
      return 'bg-blue-50 text-blue-800 border-blue-200';
  }
};

const Notification: React.FC<NotificationProps> = ({ 
  type, 
  message, 
  onClose, 
  duration = 5000 
}) => {
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    // Entrance animation delay
    const showTimer = setTimeout(() => {
      setIsVisible(true);
    }, 10);
    
    // Auto close timer
    const closeTimer = setTimeout(() => {
      setIsVisible(false);
      
      // Wait for exit animation to complete before removing
      setTimeout(onClose, 300);
    }, duration);
    
    return () => {
      clearTimeout(showTimer);
      clearTimeout(closeTimer);
    };
  }, [duration, onClose]);
  
  const iconElement = getIcon(type);
  const styleClasses = getStyles(type);
  
  return (
    <div 
      className={`fixed top-4 right-4 max-w-sm p-4 rounded-lg shadow-md border ${styleClasses} flex items-start space-x-3 transform transition-all duration-300 ${
        isVisible ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
      }`}
    >
      <div className="flex-shrink-0">
        {iconElement}
      </div>
      <div className="flex-1 pt-0.5">
        <p className="text-sm font-medium">{message}</p>
      </div>
      <button 
        onClick={() => setIsVisible(false)} 
        className="flex-shrink-0 text-gray-400 hover:text-gray-600 focus:outline-none" 
        aria-label="Close notification"
      >
        <XCircle size={18} />
      </button>
    </div>
  );
};

export default Notification;