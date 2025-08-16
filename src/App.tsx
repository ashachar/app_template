import React from 'react';
import { AuthContext } from './contexts/AuthContext';
import LandingPage from './components/landing/LandingPage';

function App() {
  return (
    <AuthContext.Provider value={{ user: null, signIn: async () => {}, signOut: async () => {}, loading: false }}>
      <div className="app-container">
        <LandingPage />
      </div>
    </AuthContext.Provider>
  );
}

export default App;