// Application Constants
export const APP_CONFIG = {
  NAME: "Video Transcriber AI",
  VERSION: "0.1.0",
};

// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL,
  ENDPOINTS: {
    AUTH: {
      LOGIN: "/auth/login",
      REGISTER: "/auth/register",
      VERIFY: "/auth/verify",
    },
    VIDEOS: {
      UPLOAD: "/videos/",
      LIST: "/videos/",
      DETAIL: (id: string) => `/videos/${id}`,
      PROCESS: (id: string) => `/videos/${id}/process`,
      TRANSCRIPT: (id: string) => `/videos/${id}/transcript`,
      SUMMARY: (id: string) => `/videos/${id}/summary`,
      CHAT: (id: string) => `/videos/${id}/chat`,
    },
  },
};

// API utility functions
export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;

  const defaultOptions: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  return fetch(url, defaultOptions);
};

export const apiRequestWithAuth = async (
  endpoint: string,
  token: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    Authorization: `Bearer ${token}`,
  };

  // Only set Content-Type for non-FormData requests
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (options.headers) {
    Object.assign(headers, options.headers);
  }

  const defaultOptions: RequestInit = {
    ...options,
    headers,
  };

  return fetch(url, defaultOptions);
};
