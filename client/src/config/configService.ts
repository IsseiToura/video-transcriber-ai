/**
 * Configuration service for fetching app configuration from server
 */

import type { AppConfig, CognitoConfig, ApiConfig } from "../types/config";
import { ApiEndpoints } from "./api";

class ConfigService {
  private config: AppConfig | null = null;
  private configPromise: Promise<AppConfig> | null = null;

  /**
   * Get application configuration from server
   */
  async getConfig(): Promise<AppConfig> {
    if (this.config) {
      return this.config;
    }

    if (this.configPromise) {
      return this.configPromise;
    }

    this.configPromise = this.fetchConfig();
    this.config = await this.configPromise;
    return this.config;
  }

  /**
   * Fetch configuration from server API
   */
  private async fetchConfig(): Promise<AppConfig> {
    const response = await ApiEndpoints.getConfig();

    if (!response.ok) {
      throw new Error(
        `Failed to fetch config: ${response.status} ${response.statusText}`
      );
    }

    const config = await response.json();
    return config;
  }

  /**
   * Get Cognito configuration
   */
  async getCognitoConfig(): Promise<CognitoConfig> {
    const config = await this.getConfig();
    return config.cognito;
  }

  /**
   * Get API configuration
   */
  async getApiConfig(): Promise<ApiConfig> {
    const config = await this.getConfig();
    return config.api;
  }

  /**
   * Clear cached configuration (useful for testing or config updates)
   */
  clearCache(): void {
    this.config = null;
    this.configPromise = null;
  }
}

// Export singleton instance
export const configService = new ConfigService();
