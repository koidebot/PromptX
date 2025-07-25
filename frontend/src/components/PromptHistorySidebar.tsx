import React from 'react';

interface User {
  id: string;
  email: string;
  total_prompts: number;
  total_jobs: number;
  created_at: string;
}

interface PromptHistoryItem {
  id: string;
  initial_prompt: string;
  final_prompt: string;
  optimization_score: number;
  created_at: string;
}

interface PromptHistorySidebarProps {
  promptHistory: PromptHistoryItem[];
  onLoadHistoryItem: (item: PromptHistoryItem) => void;
  user: User | null;
  onLogout: () => void;
}

const PromptHistorySidebar: React.FC<PromptHistorySidebarProps> = ({
  promptHistory,
  onLoadHistoryItem,
  user,
  onLogout
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="w-80 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col">
      {/* User Info */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-black dark:bg-white rounded-full flex items-center justify-center">
            <span className="text-white dark:text-black font-semibold">
              {user?.email.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-white">
              {user?.email}
            </p>
          </div>
        </div>
      </div>

      {/* History Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Prompt History
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {promptHistory.length} saved prompts
        </p>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto">
        {promptHistory.length === 0 ? (
          <div className="p-6 text-center">
            <div className="text-gray-400 dark:text-gray-600 mb-2">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No prompts yet. Start by optimizing your first prompt!
            </p>
          </div>
        ) : (
          <div className="space-y-2 p-4">
            {promptHistory.map((item) => (
              <div
                key={item.id}
                onClick={() => onLoadHistoryItem(item)}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition-colors duration-200"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {truncateText(item.initial_prompt, 50)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {formatDate(item.created_at)}
                    </p>
                  </div>
                  <div className="ml-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                      {item.optimization_score}%
                    </span>
                  </div>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  <p className="line-clamp-2">
                    {truncateText(item.final_prompt, 80)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-800">
        <button
          onClick={onLogout}
          className="w-full px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Sign out</span>
        </button>
      </div>
    </div>
  );
};

export default PromptHistorySidebar;