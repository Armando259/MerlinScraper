import { useState, useCallback } from 'react';
import { Task } from '../types';
import { generateTasks as generateTasksApi, fetchTasks } from '../services/api';

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const generateTasks = useCallback(async (limit: number) => {
    try {
      setIsGenerating(true);
      setError(null);
      
      await generateTasksApi(limit);
      
      setIsFetching(true);
      const response = await fetchTasks();
      
      if (response.tasks) {
        setTasks(response.tasks);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during task generation');
    } finally {
      setIsGenerating(false);
      setIsFetching(false);
    }
  }, []);
  
  return {
    tasks,
    isGenerating,
    isFetching,
    error,
    generateTasks,
  };
};