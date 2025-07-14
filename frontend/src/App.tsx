"use client"

import type React from "react"
import { useState, useEffect } from "react"


const BASE_URL = import.meta.env.VITE_BACKEND_URL

const App: React.FC = () => {
  const [prompt, setPrompt] = useState<string>("")
  const [improvedPrompt, setImprovedPrompt] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)

  useEffect(() => {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    if (prefersDark) {
      document.documentElement.classList.add("dark")
    }
  }, [])

  const handleImprovePrompt = async () => {
    if (!prompt.trim()) return

    setIsLoading(true)
    console.log(BASE_URL)

    try {
      const response = await fetch(`${BASE_URL}/improve-prompt`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt,
        max_iterations: 3,
        min_consecutive_improvements: 1
        })
      });

      const data = await response.json();
      const jobId = data.job_id;

      const pollJob = async() => {
        const resultResponse = await fetch(`${BASE_URL}/job/${jobId}`);
        const result = await resultResponse.json();

        if (result.status === "completed" && result.final_prompt){
          setImprovedPrompt(result.final_prompt)
          setIsLoading(false)
        } else if (result.status === "failed"){
          setImprovedPrompt("Error: " + result.error)
          setIsLoading(false)
        } else{
          setTimeout(pollJob, 1000)
        }
      }

      pollJob()
    } 
    catch (error){
        console.error("error: ", error)
    }
  }
    
  return (
  <div className="flex flex-col min-h-screen w-full bg-white dark:bg-black text-gray-900 dark:text-white">
    {/* Header */}
    <header className="border-b border-gray-200 dark:border-gray-800">
      <div className="w-full px-6 lg:px-12">
        <div className="flex justify-between items-center h-16">
          <h1 className="text-2xl font-bold text-black dark:text-white">PromptX</h1>
        </div>
      </div>
    </header>

    {/* Main */}
    <main className="flex-grow w-full px-6 lg:px-12 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 text-black dark:text-white">
            AI-Powered Prompt Optimization
          </h1>
          <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-400 mb-12">
            Refine your prompts, maximize performance
          </p>
        </div>

        {/* Content Section */}
        <div className="w-full space-y-8">
          {/* Input Form */}
          <div className="w-full bg-gray-50 dark:bg-gray-900 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-800">
            <div className="space-y-6">
              <div>
                <label htmlFor="prompt" className="block text-sm font-medium mb-2">
                  Enter your prompt
                </label>
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Type your prompt here..."
                  className="w-full h-40 px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-black focus:ring-2 focus:ring-gray-500 dark:focus:ring-gray-400 focus:border-transparent resize-none transition-colors duration-200"
                />
              </div>

              <div className="flex justify-center">
                <button
                  onClick={handleImprovePrompt}
                  disabled={!prompt.trim() || isLoading}
                  className="px-12 py-4 bg-black dark:bg-white hover:bg-gray-800 dark:hover:bg-gray-200 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white dark:text-black font-semibold rounded-lg transition-all duration-200 disabled:cursor-not-allowed flex items-center justify-center"
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
          </div>

          {/* Results Section */}
          {(improvedPrompt || isLoading) && (
            <div className="w-full bg-gray-50 dark:bg-gray-900 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-800">
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
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Optimized Prompt:</h3>
                    <div className="bg-white dark:bg-black p-6 rounded-lg border border-gray-200 dark:border-gray-800">
                      <p className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 leading-relaxed">
                        {improvedPrompt}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
