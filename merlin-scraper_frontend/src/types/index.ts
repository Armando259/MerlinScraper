export interface Task {
  _id: string;
  task_name: string;
  task_description: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  message?: string;
  tasks?: T[];
  count?: number;
}