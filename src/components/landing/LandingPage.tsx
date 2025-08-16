import React from 'react';

const LandingPage = () => {
  return (
    <div className="landing-page min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Welcome to App Template
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            A modern React + TypeScript + Vite + Supabase starter template
          </p>
        </header>

        <div className="max-w-4xl mx-auto">
          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Features
            </h2>
            <ul className="space-y-3 text-gray-600 dark:text-gray-300">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>React 18 with TypeScript for type-safe development</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Vite for lightning-fast development and builds</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Supabase integration for authentication and database</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Tailwind CSS for rapid UI development</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Consolidated logging system for debugging</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Comprehensive CLAUDE.md documentation</span>
              </li>
            </ul>
          </section>

          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Getting Started
            </h2>
            <div className="space-y-4 text-gray-600 dark:text-gray-300">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  1. Configure Environment
                </h3>
                <p>Create a <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">.env</code> file with your Supabase credentials</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  2. Install Dependencies
                </h3>
                <code className="block bg-gray-100 dark:bg-gray-700 p-3 rounded">
                  npm install
                </code>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  3. Start Development
                </h3>
                <code className="block bg-gray-100 dark:bg-gray-700 p-3 rounded">
                  npm run dev
                </code>
              </div>
            </div>
          </section>
        </div>

        <footer className="text-center mt-16 text-gray-600 dark:text-gray-400">
          <p>
            Built with React + TypeScript + Vite + Supabase
          </p>
          <p className="mt-2">
            <a 
              href="https://github.com/ashachar/app_template" 
              className="text-blue-600 dark:text-blue-400 hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
          </p>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage;