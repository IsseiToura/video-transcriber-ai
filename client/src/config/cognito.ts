/**
 * AWS Cognito configuration
 */

import { configService } from "../services/configService";
import type { CognitoConfig } from "../types/config";

/**
 * Get Cognito configuration from server
 */
export async function getCognitoConfig(): Promise<CognitoConfig> {
  return await configService.getCognitoConfig();
}

/**
 * Get Amplify configuration
 */
export async function getAmplifyConfig() {
  const cognitoConfig = await getCognitoConfig();

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
