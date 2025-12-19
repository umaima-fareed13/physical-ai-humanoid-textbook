/**
 * Chat input component with selected text preview
 */

import React, { useRef, useState, useEffect } from 'react';
import styles from './styles.module.css';

interface ChatInputProps {
  onSend: (message: string, selectedText?: string) => void;
  isLoading: boolean;
  selectedText?: string;
  onClearSelection: () => void;
}

export function ChatInput({
  onSend,
  isLoading,
  selectedText,
  onClearSelection,
}: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();

    if (!input.trim() || isLoading) return;

    onSend(input.trim(), selectedText || undefined);
    setInput('');
    onClearSelection();

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter to send, Shift+Enter for newline
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form className={styles.inputContainer} onSubmit={handleSubmit}>
      {/* Selected text preview */}
      {selectedText && (
        <div className={styles.selectionPreview}>
          <div className={styles.selectionHeader}>
            <span className={styles.selectionIcon}>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M14 17H4v2h10v-2zm6-8H4v2h16V9zM4 15h16v-2H4v2zM4 5v2h16V5H4z" />
              </svg>
            </span>
            <span>Ask about selected text</span>
            <button
              type="button"
              className={styles.clearSelection}
              onClick={onClearSelection}
              aria-label="Clear selection"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <p className={styles.selectionText}>
            {selectedText.length > 150
              ? `"${selectedText.substring(0, 150)}..."`
              : `"${selectedText}"`}
          </p>
        </div>
      )}

      <div className={styles.inputWrapper}>
        <textarea
          ref={textareaRef}
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            selectedText
              ? 'Ask about the selected text...'
              : 'Ask about the textbook...'
          }
          disabled={isLoading}
          rows={1}
        />

        <button
          type="submit"
          className={styles.sendButton}
          disabled={!input.trim() || isLoading}
          aria-label="Send message"
        >
          {isLoading ? (
            <div className={styles.loadingSpinner} />
          ) : (
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>

      <p className={styles.inputHint}>
        Press Enter to send, Shift+Enter for new line
      </p>
    </form>
  );
}
