/**
 * Source reference card for displaying RAG sources
 */

import React, { useState } from 'react';
import styles from './styles.module.css';

interface SourceCardProps {
  file: string;
  chunk: string;
  index: number;
}

export function SourceCard({ file, chunk, index }: SourceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Convert filename to display name
  const displayName = file
    .replace('.md', '')
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());

  // Get doc URL
  const docUrl = `/docs/${file.replace('.md', '')}`;

  return (
    <div className={styles.sourceCard}>
      <button
        className={styles.sourceHeader}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <span className={styles.sourceIndex}>{index}</span>
        <span className={styles.sourceTitle}>{displayName}</span>
        <svg
          className={`${styles.sourceChevron} ${isExpanded ? styles.expanded : ''}`}
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {isExpanded && (
        <div className={styles.sourceContent}>
          <p className={styles.sourceChunk}>{chunk}</p>
          <a
            href={docUrl}
            className={styles.sourceLink}
            target="_blank"
            rel="noopener noreferrer"
          >
            View in textbook
          </a>
        </div>
      )}
    </div>
  );
}
