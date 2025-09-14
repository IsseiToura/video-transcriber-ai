// Authentication related types for Cognito integration
export interface SignUpRequest {
  username: string;
  email: string;
  password: string;
}

export interface SignInRequest {
  username: string;
  password: string;
}

export interface SignUpResponse {
  isSignUpComplete: boolean;
  nextStep: {
    signUpStep: string;
    codeDeliveryDetails?: {
      destination?: string;
      deliveryMedium?: string;
    };
  };
}

export interface SignInResponse {
  isSignedIn: boolean;
  nextStep: {
    signInStep: string;
    additionalInfo?: any;
  };
}

export interface CognitoUser {
  username: string;
  userId: string;
  email?: string;
  emailVerified?: boolean;
  groups?: string[];
}
export interface User {
  id: string;
  username: string;
  email?: string;
  emailVerified?: boolean;
  access_token: string;
  groups?: string[];
}

// API response types
export interface UserInfo {
  username?: string;
  email?: string;
  email_verified: boolean;
  cognito_groups: string[];
}

export interface TokenValidationResponse {
  valid: boolean;
  user_info?: UserInfo;
}
