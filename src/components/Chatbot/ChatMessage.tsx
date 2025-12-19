/**
 * Individual chat message component
 */

import React from 'react';
import { SourceCard } from './SourceCard';
import styles from './styles.module.css';
import type { Message, SourceReference } from './hooks/useChat';

interface ChatMessageProps {
  message: Message;
}

/**
 * Simple markdown-like rendering for assistant messages
 */
function renderContent(content: string): React.ReactNode {
  // Split by code blocks
  const parts = content.split(/(```[\s\S]*?```)/g);

  return parts.map((part, i) => {
    if (part.startsWith('```')) {
      // Code block
      const match = part.match(/```(\w*)\n?([\s\S]*?)```/);
      if (match) {
        const [, lang, code] = match;
        return (
          <pre key={i} className={styles.codeBlock}>
            <code className={lang ? `language-${lang}` : ''}>{code.trim()}</code>
          </pre>
        );
      }
    }

    // Regular text - handle inline formatting
    const lines = part.split('\n');
    return lines.map((line, j) => {
      // Bold
      let formatted: React.ReactNode = line.replace(
        /\*\*(.*?)\*\*/g,
        '<strong>$1</strong>'
      );

      // Inline code
      formatted = String(formatted).replace(
        /`([^`]+)`/g,
        '<code class="' + styles.inlineCode + '">$1</code>'
      );

      return (
        <React.Fragment key={`${i}-${j}`}>
          <span dangerouslySetInnerHTML={{ __html: formatted }} />
          {j < lines.length - 1 && <br />}
        </React.Fragment>
      );
    });
  });
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`${styles.messageContainer} ${isUser ? styles.userMessage : styles.assistantMessage}`}
    >
      <div className={styles.messageAvatar}>
        {isUser ? (
          // User icon
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
        ) : (
          // Bot icon
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2zM7.5 13a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm9 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z" />
          </svg>
        )}
      </div>

      <div className={styles.messageContent}>
        {/* Show selected text context for user messages */}
        {isUser && message.selectedText && (
          <div className={styles.selectedTextContext}>
            <span className={styles.selectedTextLabel}>Selected text:</span>
            <span className={styles.selectedTextPreview}>
              {message.selectedText.length > 100
                ? `${message.selectedText.substring(0, 100)}...`
                : message.selectedText}
            </span>
          </div>
        )}

        <div className={styles.messageText}>
          {isUser ? message.content : renderContent(message.content)}
        </div>

        {/* Show sources for assistant messages */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className={styles.sourcesContainer}>
            <div className={styles.sourcesHeader}>Sources</div>
            {message.sources.map((source, index) => (
              <SourceCard
                key={index}
                file={source.file}
                chunk={source.chunk}
                index={index + 1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
