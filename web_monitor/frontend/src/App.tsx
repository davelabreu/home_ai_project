import React from 'react';
import NetworkStatusCard from './components/NetworkStatusCard';
import SystemInfoCard from './components/SystemInfoCard';
import './index.css'; // Tailwind CSS directives

function App() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-4">
      <header className="py-6 border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold text-center">Jetson Dashboard</h1>
          <p className="text-center text-gray-600 dark:text-gray-400">Monitor your Jetson and local network.</p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SystemInfoCard />
          <NetworkStatusCard />
        </div>
        {/* Placeholder for future features */}
        <section className="mt-8 p-4 border rounded-lg shadow-sm bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold mb-4">Other Features (Coming Soon!)</h2>
          <p className="text-gray-600 dark:text-gray-400">
            {/* Deployment tools link to /api/deploy in Flask backend */}
            Deployment tools, 
            {/* Qwen chat interface links to scripts/ollama_chat.py */}
            Qwen chat interface...
          </p>
        </section>
      </main>
    </div>
  );
}

export default App;