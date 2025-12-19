/**
 * Application configuration
 */

// API base URL - change for production deployment
export const API_BASE_URL =
  typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? 'https://your-backend.example.com' // Replace with your production backend URL
    : 'http://localhost:8000';
