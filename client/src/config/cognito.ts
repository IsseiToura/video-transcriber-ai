/**
 * AWS Cognito configuration
 * This file provides Amplify configuration for authentication
 */

import { configService } from "./configService";

// ========================================
// Public Functions
// ========================================

/**
 * Get Amplify configuration
 * Fetches Cognito configuration from server and transforms it to Amplify format
 */
export async function getAmplifyConfig() {
  const cognitoConfig = await configService.getCognitoConfig();

  return {
    Auth: {
      Cognito: {
        userPoolId: cognitoConfig.userPoolId,
        userPoolClientId: cognitoConfig.userPoolWebClientId,
        loginWith: {
          email: true,
          username: true,
        },
        signUpVerificationMethod: "code" as const,
        userAttributes: {
          email: {
            required: true,
          },
          name: {
            required: false,
          },
        },
      },
    },
  };
}

/**
 * AMPLIFY_CONFIG - Promise that resolves to Amplify configuration
 * This can be used for direct initialization
 */
export const AMPLIFY_CONFIG = getAmplifyConfig();
