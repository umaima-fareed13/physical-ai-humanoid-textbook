/**
 * Main Chatbot component
 *
 * Provides a floating chat widget that can be used on any page
 * to ask questions about the Physical AI Textbook content.
 */

import React, { useState } from 'react';
import { ChatToggle } from './ChatToggle';
import { ChatWindow } from './ChatWindow';
import { useChat } from './hooks/useChat';
import { useSelection } from './hooks/useSelection';
import { useSession } from './hooks/useSession';
import styles from './styles.module.css';

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const { sessionId, isLoading: sessionLoading } = useSession();
  const { messages, isLoading, sendMessage, clearMessages } = useChat(sessionId);
  const { selectedText, clearSelection } = useSelection();

  // Don't render until session is ready
  if (sessionLoading) {
    return null;
  }

  const handleSend = (message: string, selected?: string) => {
    sendMessage(message, selected);
  };

  const handleClear = () => {
    clearMessages();
    clearSelection();
  };

  return (
    <div className={styles.chatbotContainer}>
      {isOpen && (
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSend={handleSend}
          onClose={() => setIsOpen(false)}
          onClear={handleClear}
          selectedText={selectedText}
          onClearSelection={clearSelection}
        />
      )}

      <ChatToggle
        isOpen={isOpen}
        onClick={() => setIsOpen(!isOpen)}
      />
    </div>
  );
}
