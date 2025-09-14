/**
 * AWS Cognito authentication service
 */

import { Amplify } from "aws-amplify";
import {
  signUp,
  signIn,
  signOut,
  getCurrentUser,
  confirmSignUp,
  resendSignUpCode,
  fetchAuthSession,
} from "aws-amplify/auth";
import { AMPLIFY_CONFIG } from "../config/cognito";
import type {
  SignUpRequest,
  SignInRequest,
  SignUpResponse,
  SignInResponse,
  CognitoUser,
} from "../types/auth";

// Initialize Amplify once at module level
let amplifyInitialized = false;
let amplifyInitPromise: Promise<void> | null = null;

async function initializeAmplify(): Promise<void> {
  if (amplifyInitialized) {
    return;
  }

  if (amplifyInitPromise) {
    return amplifyInitPromise;
  }

  amplifyInitPromise = AMPLIFY_CONFIG.then((config) => {
    Amplify.configure(config);
    amplifyInitialized = true;
  }).catch((error) => {
    console.error("Failed to initialize Amplify:", error);
    amplifyInitialized = false;
    amplifyInitPromise = null;
    throw error;
  });

  return amplifyInitPromise;
}

export class CognitoService {
  /**
   * Sign up a new user
   */
  async signUp(request: SignUpRequest): Promise<SignUpResponse> {
    try {
      await initializeAmplify();

      const { isSignUpComplete, nextStep } = await signUp({
        username: request.username,
        password: request.password,
        options: {
          userAttributes: {
            email: request.email,
          },
        },
      });

      return {
        isSignUpComplete,
        nextStep,
      };
    } catch (error) {
      console.error("Sign up error:", error);
      throw error;
    }
  }

  /**
   * Confirm user sign up with verification code
   */
  async confirmSignUp(
    username: string,
    confirmationCode: string
  ): Promise<void> {
    try {
      await initializeAmplify();

      await confirmSignUp({
        username,
        confirmationCode,
      });
    } catch (error) {
      console.error("Confirm sign up error:", error);
      throw error;
    }
  }

  /**
   * Resend sign up confirmation code
   */
  async resendSignUpCode(username: string): Promise<void> {
    try {
      await initializeAmplify();

      await resendSignUpCode({ username });
    } catch (error) {
      console.error("Resend sign up code error:", error);
      throw error;
    }
  }

  /**
   * Sign in user
   */
  async signIn(request: SignInRequest): Promise<SignInResponse> {
    try {
      await initializeAmplify();

      const { isSignedIn, nextStep } = await signIn({
        username: request.username,
        password: request.password,
      });

      return {
        isSignedIn,
        nextStep,
      };
    } catch (error) {
      console.error("Sign in error:", error);
      throw error;
    }
  }

  /**
   * Sign out current user
   */
  async signOut(): Promise<void> {
    try {
      await initializeAmplify();

      await signOut();
    } catch (error) {
      console.error("Sign out error:", error);
      throw error;
    }
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<CognitoUser | null> {
    try {
      await initializeAmplify();

      const user = await getCurrentUser();

      return {
        username: user.username,
        userId: user.userId,
        email: user.signInDetails?.loginId,
        emailVerified: true, // Cognito users are verified after confirmation
        groups: [], // Groups would need to be fetched separately
      };
    } catch (error) {
      console.error("Get current user error:", error);
      return null;
    }
  }

  /**
   * Get current user's JWT tokens
   */
  async getCurrentUserTokens(): Promise<{
    accessToken: string;
    idToken: string;
  } | null> {
    try {
      await initializeAmplify();

      const session = await fetchAuthSession();

      if (!session.tokens) {
        return null;
      }

      return {
        accessToken: session.tokens.accessToken.toString(),
        idToken: session.tokens.idToken?.toString() || "",
      };
    } catch (error) {
      console.error("Get current user tokens error:", error);
      return null;
    }
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      await initializeAmplify();

      const user = await getCurrentUser();
      return !!user;
    } catch (error) {
      return false;
    }
  }
}

// Export singleton instance
export const cognitoService = new CognitoService();
