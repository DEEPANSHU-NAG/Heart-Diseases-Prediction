import React from 'react'
import { useState } from 'react';
import AuthPage from './components/AuthPage';
import Dashboard from './components/Dashboard';
const App = () => {
  const [user, setUser] = useState(null);

  return (
    <>
      {user ? (
        <Dashboard user={user} onLogout={() => setUser(null)} />
      ) : (
        <AuthPage onLogin={(username) => setUser(username)} />
      )}
    </>
  );
};

export default App;