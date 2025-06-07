import React from 'react';

interface DinpTask {
  date: string;
  name: string;
  description: string;
  course: string;
}

interface Props {
  dinpTasks: DinpTask[] | undefined;
  isLoading: boolean;
  isLoggedIn: boolean;
}

const DinpTaskList: React.FC<Props> = ({ dinpTasks, isLoading, isLoggedIn }) => {
  if (!isLoggedIn) return null;
  if (!Array.isArray(dinpTasks)) return null; // 🛠️ sigurnosna provjera

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">DINP zadaci</h3>

      {isLoading ? (
        <p className="text-gray-500">Učitavanje zadataka...</p>
      ) : dinpTasks.length === 0 ? (
        <p className="text-gray-500">Nema pronađenih DINP zadataka.</p>
      ) : (
        <ul className="space-y-4">
          {dinpTasks.map((task, index) => (
            <li key={index} className="border p-4 rounded-md bg-gray-50">
              <p className="text-sm text-gray-500 mb-1">{task.date} — {task.course}</p>
              <h4 className="font-medium text-gray-800">{task.name}</h4>
              <p className="text-gray-700 text-sm mt-1">{task.description}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DinpTaskList;
