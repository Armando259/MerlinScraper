import React from 'react';
import { Task } from '../types';
import TaskItem from './TaskItem';
import EmptyState from './EmptyState';

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  isLoggedIn: boolean;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, isLoading, isLoggedIn }) => {
  if (isLoading) {
    return (
      <div className="mt-8 grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 animate-pulse">
            <div className="flex justify-between items-start mb-3">
              <div className="h-5 bg-gray-200 rounded w-3/4"></div>
              <div className="h-5 bg-gray-200 rounded-full w-16"></div>
            </div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="mt-3 h-3 bg-gray-200 rounded w-1/4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return <EmptyState isLoggedIn={isLoggedIn} />;
  }

  return (
    <div className="mt-8 grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 animate-fadeIn">
      {tasks.map((task, index) => (
        <TaskItem key={task._id || index} task={task} />
      ))}
    </div>
  );
};

export default TaskList;
