/**
 * Hook for managing chat state and API communication
 */

import { useCallback, useEffect, useState } from 'react';
import { API_BASE_URL } from '@site/src/config';

export interface SourceReference {
  file: string;
  chunk: string;
  score?: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceReference[];
  selectedText?: string;
  createdAt?: string;
}

interface ChatResponse {
  response: string;
  sources: SourceReference[];
  session_id: string;
}

interface HistoryResponse {
  session_id: string;
  messages: Array<{
    id: number;
    role: string;
    content: string;
    selected_text?: string;
    sources?: SourceReference[];
    created_at?: string;
  }>;
}

/**
 * Hook to manage chat messages and API communication
 */
export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load conversation history from the server
   */
  const loadHistory = useCallback(async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/chat/history/${sessionId}?limit=50`
      );

      if (response.ok) {
        const data: HistoryResponse = await response.json();
        setMessages(
          data.messages.map((msg) => ({
            id: String(msg.id),
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            sources: msg.sources,
            selectedText: msg.selected_text,
            createdAt: msg.created_at,
          }))
        );
      }
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  }, [sessionId]);

  // Load history when session ID changes
  useEffect(() => {
    if (sessionId) {
      loadHistory();
    }
  }, [sessionId, loadHistory]);

  /**
   * Send a message to the chatbot
   */
  const sendMessage = useCallback(
    async (content: string, selectedText?: string) => {
      if (!sessionId || !content.trim()) return;

      setIsLoading(true);
      setError(null);

      // Add user message optimistically
      const userMessageId = `user-${Date.now()}`;
      const userMessage: Message = {
        id: userMessageId,
        role: 'user',
        content: content.trim(),
        selectedText,
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: content.trim(),
            session_id: sessionId,
            selected_text: selectedText || null,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to send message');
        }

        const data: ChatResponse = await response.json();

        // Add assistant response
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: data.response,
          sources: data.sources,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);

        // Add error message as assistant response
        setMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            role: 'assistant',
            content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(async () => {
    if (!sessionId) return;

    try {
      await fetch(`${API_BASE_URL}/chat/history/${sessionId}`, {
        method: 'DELETE',
      });
      setMessages([]);
    } catch (err) {
      console.error('Failed to clear history:', err);
    }
  }, [sessionId]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    loadHistory,
  };
}
