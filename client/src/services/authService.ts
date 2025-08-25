import { API_CONFIG, apiRequest } from "../config/api";
import type { LoginRequest, LoginResponse } from "../types";

export class AuthService {
  /**
   * User login
   */
  async login(loginRequest: LoginRequest): Promise<LoginResponse> {
    const response = await apiRequest(API_CONFIG.ENDPOINTS.AUTH.LOGIN, {
      method: "POST",
      body: JSON.stringify({
        username: loginRequest.username,
        password: loginRequest.password,
      }),
    });

    if (!response.ok) {
      throw new Error("Authentication failed");
    }

    return response.json();
  }
}
