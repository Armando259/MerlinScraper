
import { useEffect, useState } from 'react';

export function useDinpTasks(isLoggedIn: boolean) {
  const [dinpTasks, setDinpTasks] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchDinpTasks = async () => {
    if (!isLoggedIn) return;
    setLoading(true);
    try {
      const response = await fetch('http://localhost:3000/dinp_tasks', {
        credentials: 'include',
      });
      const data = await response.json();
      setDinpTasks(data.tasks || []);
    } catch (error) {
      console.error('Greška prilikom dohvaćanja DINP zadataka:', error);
    } finally {
      setLoading(false);
    }
  };

useEffect(() => {
    fetchDinpTasks();
  }, [isLoggedIn]);

  return { dinpTasks, loading, refetch: fetchDinpTasks };
}
