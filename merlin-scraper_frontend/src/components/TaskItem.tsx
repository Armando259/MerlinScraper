import React from 'react';
import { Task } from '../types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface TaskItemProps {
  task: Task;
}

const getDifficultyColor = (difficulty: string) => {
  switch (difficulty.toLowerCase()) {
    case 'easy':
      return 'bg-green-100 text-green-800';
    case 'medium':
      return 'bg-amber-100 text-amber-800';
    case 'hard':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const TaskItem: React.FC<TaskItemProps> = ({ task }) => {
  const difficultyClass = getDifficultyColor(task.difficulty);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 transition-all duration-200 hover:shadow-md">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-medium text-gray-900 mb-1">{task.task_name}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${difficultyClass}`}>
          {task.difficulty}
        </span>
      </div>

      <div className="prose prose-sm text-gray-600">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {task.task_description}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default TaskItem;