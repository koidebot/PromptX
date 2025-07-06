"use client"

import type React from "react"
import { useState, useEffect } from "react"

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState<boolean>(false)
  const [prompt, setPrompt] = useState<string>("")
  const [improvedPrompt, setImprovedPrompt] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)

  // Initialize dark mode from localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme")
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches

    if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
      setDarkMode(true)
      document.documentElement.classList.add("dark")
    }
  }, [])

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode
    setDarkMode(newDarkMode)

    if (newDarkMode) {
      document.documentElement.classList.add("dark")
      localStorage.setItem("theme", "dark")
    } else {
      document.documentElement.classList.remove("dark")
      localStorage.setItem("theme", "light")
    }
  }

  const handleImprovePrompt = async () => {
    if (!prompt.trim()) return

    setIsLoading(true)

    // TODO: Implement API call to backend service
    // try {
    //   const response = await fetch('/api/improve-prompt', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ prompt })
    //   });
    //   const data = await response.json();
    //   setImprovedPrompt(data.improvedPrompt);
    // } catch (error) {
    //   console.error('Error improving prompt:', error);
    // }

    // Mock response for demonstration
    setTimeout(() => {
      setImprovedPrompt(
        `Enhanced version of: "${prompt}"\n\nThis improved prompt incorporates better structure, clearer instructions, and optimized phrasing to achieve higher performance across key evaluation criteria.`,
      )
      setIsLoading(false)
    }, 2000)
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? "dark" : ""}`}>
      <div className="min-h-screen bg-white dark:bg-black text-gray-900 dark:text-white">
        {/* Header */}
        <header className="border-b border-gray-200 dark:border-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-black dark:text-white">PromptX</h1>
              </div>

              {/* Dark Mode Toggle */}
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-900 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors duration-200"
                aria-label="Toggle dark mode"
              >
                {darkMode ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="text-black dark:text-white">AI-Powered Prompt Optimization</span>
            </h1>
            <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-400 mb-12">
              Refine your prompts, maximize performance
            </p>
          </div>

          {/* Input Form */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-8 mb-8 shadow-lg border border-gray-200 dark:border-gray-800">
            <div className="space-y-6">
              {/* Prompt Input */}
              <div>
                <label htmlFor="prompt" className="block text-sm font-medium mb-2">
                  Enter your prompt
                </label>
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Type your prompt here..."
                  className="w-full h-32 px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-black focus:ring-2 focus:ring-gray-500 dark:focus:ring-gray-400 focus:border-transparent resize-none transition-colors duration-200"
                />
              </div>

              {/* Improve Button */}
              <button
                onClick={handleImprovePrompt}
                disabled={!prompt.trim() || isLoading}
                className="w-full bg-black dark:bg-white hover:bg-gray-800 dark:hover:bg-gray-200 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white dark:text-black font-semibold py-4 px-6 rounded-lg transition-all duration-200 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isLoading ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Improving...
                  </>
                ) : (
                  "Improve Prompt"
                )}
              </button>
            </div>
          </div>

          {/* Results Section */}
          {(improvedPrompt || isLoading) && (
            <div className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-800">
              <h2 className="text-2xl font-bold mb-6">Improved Prompt</h2>

              {isLoading ? (
                <div className="space-y-4">
                  <div className="animate-pulse">
                    <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
                    <div className="h-32 bg-gray-300 dark:bg-gray-700 rounded mb-4"></div>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Improved Prompt */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Optimized Prompt:</h3>
                    <div className="bg-white dark:bg-black p-4 rounded-lg border border-gray-200 dark:border-gray-800">
                      <p className="whitespace-pre-wrap text-gray-800 dark:text-gray-200">{improvedPrompt}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
