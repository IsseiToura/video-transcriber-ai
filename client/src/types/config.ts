/**
 * Configuration types for the application
 */

export interface CognitoConfig {
  region: string;
  userPoolId: string;
  userPoolWebClientId: string;
  authenticationFlowType: "USER_SRP_AUTH";
  oauth: {
    domain: string;
    scope: string[];
    redirectSignIn: string;
    redirectSignOut: string;
    responseType: "code";
  };
}

export interface ApiConfig {
  baseUrl: string;
  allowedOrigins: string[];
}

export interface AppConfig {
  cognito: CognitoConfig;
  api: ApiConfig;
}
