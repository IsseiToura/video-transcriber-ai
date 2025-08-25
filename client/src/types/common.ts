// Common types used across the application
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Error handling types
export interface ApiError {
  detail: string;
  status_code: number;
  headers?: Record<string, string>;
}

// File upload types
export interface FileUploadOptions {
  maxSize?: number;
  allowedTypes?: string[];
  multiple?: boolean;
}

// Chat conversation types
export interface Conversation {
  id: string;
  videoId: string;
  question: string;
  answer: string;
  timestamp: Date;
}
