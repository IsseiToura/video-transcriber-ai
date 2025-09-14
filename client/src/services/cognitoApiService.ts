/**
 * API service for Cognito-authenticated requests
 */

import { API_ENDPOINTS, apiRequest } from "../config/api";
import { cognitoService } from "./cognitoService";
import type { UserInfo, TokenValidationResponse } from "../types/auth";

export class CognitoApiService {
  /**
   * Get current user information from the API
   */
  async getCurrentUserInfo(): Promise<UserInfo> {
    const tokens = await cognitoService.getCurrentUserTokens();
    if (!tokens) {
      throw new Error("User not authenticated");
    }

    const response = await apiRequest(API_ENDPOINTS.AUTH.ME, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${tokens.accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to get user info");
    }

    return response.json();
  }

  /**
   * Validate JWT token with the API
   */
  async validateToken(): Promise<TokenValidationResponse> {
    const tokens = await cognitoService.getCurrentUserTokens();
    if (!tokens) {
      return { valid: false, user_info: undefined };
    }

    const response = await apiRequest(API_ENDPOINTS.AUTH.VALIDATE_TOKEN, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${tokens.accessToken}`,
      },
    });

    if (!response.ok) {
      return { valid: false, user_info: undefined };
    }

    return response.json();
  }

  /**
   * Make authenticated API request
   */
  async authenticatedRequest(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const tokens = await cognitoService.getCurrentUserTokens();
    if (!tokens) {
      throw new Error("User not authenticated");
    }

    const headers: Record<string, string> = {
      Authorization: `Bearer ${tokens.accessToken}`,
      ...(options.headers as Record<string, string>),
    };

    // Only set Content-Type for non-FormData requests
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    return apiRequest(endpoint, {
      ...options,
      headers,
    });
  }

  /**
   * Check if user is authenticated and token is valid
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      const isCognitoAuthenticated = await cognitoService.isAuthenticated();
      if (!isCognitoAuthenticated) {
        return false;
      }

      const validation = await this.validateToken();
      return validation.valid;
    } catch (error) {
      console.error("Authentication check error:", error);
      return false;
    }
  }
}

// Export singleton instance
export const cognitoApiService = new CognitoApiService();
