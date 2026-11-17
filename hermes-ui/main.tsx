import React from 'react';
import ReactDOM from 'react-dom/client';
import { MultiplayerDashboard } from './MultiplayerDashboard';
import { MotionProvider } from './MotionProvider';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <MotionProvider>
      <MultiplayerDashboard />
    </MotionProvider>
  </React.StrictMode>
);
