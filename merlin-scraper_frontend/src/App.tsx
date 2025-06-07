import React, { useState } from 'react';
import Header from './components/Header';
import LoginButton from './components/LoginButton';
import GenerateButton from './components/GenerateButton';
import DinpButton from './components/dinpButton';
import TaskList from './components/TaskList';
import DinpTaskList from './components/DinpTaskList';
import DownloadCalendarButton from './components/DownloadCalendarButton';
import Notification from './components/Notification';
import { useAuth } from './hooks/useAuth';
import { useTasks } from './hooks/useTasks';
import VectorSearch from './components/VectorSearch';


type NotificationData = {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
} | null;

function App() {
  const { isLoggedIn, isLoggingIn, error: loginError, login } = useAuth();
  const { 
    tasks, 
    isGenerating, 
    isFetching, 
    error: tasksError, 
    generateTasks 
  } = useTasks();

  const [notification, setNotification] = useState<NotificationData>(null);
  const [dinpTasks, setDinpTasks] = useState([]);
  const [isFetchingDinp, setIsFetchingDinp] = useState(false);

  const handleLogin = async () => {
    try {
      const success = await login();
      if (success) {
        setNotification({
          type: 'success',
          message: 'Uspješna prijava!'
        });
      }
    } catch {
      setNotification({
        type: 'error',
        message: loginError || 'Greška prilikom prijave. Pokušaj ponovno.'
      });
    }
  };

  const handleGenerateTasks = async (limit: number) => {
    try {
      await generateTasks(limit);
      setNotification({
        type: 'success',
        message: `Uspješno generirano ${tasks.length} zadataka!`
      });
    } catch {
      setNotification({
        type: 'error',
        message: tasksError || 'Greška prilikom generiranja zadataka.'
      });
    }
  };

  const clearNotification = () => setNotification(null);

  const fetchDinpTasks = async () => {
    setIsFetchingDinp(true);
    try {
      const res = await fetch('http://localhost:3000/dinp_tasks', {
        credentials: 'include'
      });
      const data = await res.json();
      setDinpTasks(data.tasks || []); // ✅ uzimamo samo listu iz objekta
    } catch {
      setNotification({
        type: 'error',
        message: 'Greška prilikom dohvaćanja DINP zadataka.'
      });
    } finally {
      setIsFetchingDinp(false);
    }
  };


  return (
    <div className="min-h-screen bg-gray-50">
      <Header isLoggedIn={isLoggedIn} />
      <main className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 sm:space-x-4">
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-800 mb-1">
                Generator taskova MERLIN
              </h2>
              <p className="text-gray-500 text-sm">
                Generiraj zadatke iz Merlina koristeći obavijesti i DINP dokumente
              </p>
            </div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
              <LoginButton 
                onClick={handleLogin}
                isLoggingIn={isLoggingIn}
                isLoggedIn={isLoggedIn}
              />
              <GenerateButton 
                onGenerate={handleGenerateTasks}
                isGenerating={isGenerating || isFetching}
                disabled={!isLoggedIn}
              />
              <DinpButton 
                isLoggedIn={isLoggedIn}
                setNotification={setNotification}
                onCompleted={fetchDinpTasks}
              />
              <DownloadCalendarButton isLoggedIn={isLoggedIn} />
             

            </div>
          </div>
        </div>
        <VectorSearch />
        <TaskList 
          tasks={tasks}
          isLoading={isGenerating || isFetching}
          isLoggedIn={isLoggedIn}
        />

        <div className="mt-8">
          <DinpTaskList 
            dinpTasks={dinpTasks}
            isLoading={isFetchingDinp}
            isLoggedIn={isLoggedIn}
          />
          
        </div>
      </main>

      {notification && (
        <Notification
          type={notification.type}
          message={notification.message}
          onClose={clearNotification}
        />
      )}
    </div>
  );
}

export default App;
