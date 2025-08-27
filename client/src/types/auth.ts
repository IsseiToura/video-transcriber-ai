// Authentication related types based on server schemas
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  username: string;
  user_id: string;
}

export interface User {
  id: string;
  username: string;
  access_token: string;
}
