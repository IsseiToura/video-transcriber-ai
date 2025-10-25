import { configService } from "../services/configService";

// Application Constants
export const APP_CONFIG = {
  NAME: "Video Transcriber AI",
  VERSION: "0.1.0",
};

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    ME: "/auth/me",
    VALIDATE_TOKEN: "/auth/validate-token",
  },
  VIDEOS: {
    PRESIGNED: "/videos/presigned-url",
    METADATA: "/videos/metadata",
    LIST: "/videos/",
    DETAIL: (id: string) => `/videos/${id}`,
    TRANSCRIPT: (id: string) => `/videos/${id}/transcript`,
    SUMMARY: (id: string) => `/videos/${id}/summary`,
    CHAT: (id: string) => `/videos/${id}/chat`,
  },
  CONFIG: {
    CONFIG: "/config/config",
  },
};

// Get API base URL from environment variables (for initial config fetch)
function getInitialApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL;
  if (!baseUrl) {
    throw new Error("VITE_API_BASE_URL environment variable is not set");
  }
  return baseUrl;
}

// Get API base URL from server configuration (after config is loaded)
async function getApiBaseUrl(): Promise<string> {
  const config = await configService.getApiConfig();
  return config.baseUrl;
}

// Initial API request function (uses environment variable)
const initialApiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const baseUrl = getInitialApiBaseUrl();
  const url = `${baseUrl}${endpoint}`;

  const defaultOptions: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  return fetch(url, defaultOptions);
};

// API Endpoint Functions
export const ApiEndpoints = {
  async getConfig(): Promise<Response> {
    return initialApiRequest(API_ENDPOINTS.CONFIG.CONFIG, {
      method: "GET",
    });
  },
};

// API utility functions
export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const baseUrl = await getApiBaseUrl();
  const url = `${baseUrl}${endpoint}`;

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
  const baseUrl = await getApiBaseUrl();
  const url = `${baseUrl}${endpoint}`;

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
