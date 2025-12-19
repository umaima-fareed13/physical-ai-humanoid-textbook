/**
 * Hook for managing anonymous chat sessions
 */

import { useEffect, useState } from 'react';

const SESSION_KEY = 'physical-ai-chatbot-session';

/**
 * Generate a UUID v4
 */
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Hook to manage session ID for anonymous chat
 * - Generates UUID on first visit
 * - Persists in localStorage
 * - Returns consistent session ID across page loads
 */
export function useSession() {
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    let id = localStorage.getItem(SESSION_KEY);

    if (!id) {
      // Generate new session ID
      id = generateUUID();
      localStorage.setItem(SESSION_KEY, id);
    }

    setSessionId(id);
    setIsLoading(false);
  }, []);

  /**
   * Clear session and start fresh
   */
  const clearSession = () => {
    const newId = generateUUID();
    localStorage.setItem(SESSION_KEY, newId);
    setSessionId(newId);
  };

  return {
    sessionId,
    isLoading,
    clearSession,
  };
}
