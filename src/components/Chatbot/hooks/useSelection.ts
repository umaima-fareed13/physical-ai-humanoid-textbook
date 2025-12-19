/**
 * Hook for detecting user text selection on the page
 */

import { useCallback, useEffect, useState } from 'react';

/**
 * Hook to detect and capture text selected by the user
 * - Listens for mouseup/touchend events
 * - Filters to only content areas (not UI elements)
 * - Returns selected text and clear function
 */
export function useSelection() {
  const [selectedText, setSelectedText] = useState<string>('');

  const handleSelection = useCallback(() => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) {
      return;
    }

    const text = selection.toString().trim();

    // Ignore very short or very long selections
    if (text.length < 10 || text.length > 2000) {
      return;
    }

    // Check if selection is within content areas (docs, articles)
    const anchorNode = selection.anchorNode;
    if (!anchorNode) {
      return;
    }

    // Find parent element
    const parentElement =
      anchorNode.nodeType === Node.ELEMENT_NODE
        ? (anchorNode as Element)
        : anchorNode.parentElement;

    if (!parentElement) {
      return;
    }

    // Check if selection is in valid content areas
    const validSelectors = [
      'article',
      '.markdown',
      '.theme-doc-markdown',
      '[class*="docMainContainer"]',
      '[class*="docItemContainer"]',
      'main',
    ];

    const isInContentArea = validSelectors.some((selector) =>
      parentElement.closest(selector)
    );

    // Exclude UI elements
    const excludeSelectors = [
      'nav',
      'footer',
      'header',
      '.navbar',
      '[class*="chatbot"]',
      '[class*="Chatbot"]',
      'button',
      'input',
      'textarea',
    ];

    const isInExcludedArea = excludeSelectors.some((selector) =>
      parentElement.closest(selector)
    );

    if (isInContentArea && !isInExcludedArea) {
      setSelectedText(text);
    }
  }, []);

  useEffect(() => {
    // Listen for selection changes
    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('touchend', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('touchend', handleSelection);
    };
  }, [handleSelection]);

  const clearSelection = useCallback(() => {
    setSelectedText('');
    // Also clear browser selection
    window.getSelection()?.removeAllRanges();
  }, []);

  return {
    selectedText,
    clearSelection,
    hasSelection: selectedText.length > 0,
  };
}
