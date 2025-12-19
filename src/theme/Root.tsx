/**
 * Root theme wrapper for Docusaurus
 *
 * This component wraps the entire application and allows
 * us to add global components like the chatbot.
 *
 * @see https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */

import React from 'react';
import Chatbot from '@site/src/components/Chatbot';

interface RootProps {
  children: React.ReactNode;
}

export default function Root({ children }: RootProps) {
  return (
    <>
      {children}
      <Chatbot />
    </>
  );
}
