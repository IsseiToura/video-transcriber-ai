import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import { cognitoService } from "../services";
import type { User } from "../types/auth";

type AuthView = "signin" | "signup" | "email-confirmation";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  authView: AuthView;
  pendingUsername: string;
  pendingEmail: string;
  checkAuth: () => Promise<void>;
  logout: () => Promise<void>;
  setAuthView: (view: AuthView) => void;
  handleSignUpSuccess: (username: string, email: string) => void;
  handleEmailConfirmationSuccess: () => Promise<void>;
  handleSwitchToSignIn: () => void;
  handleSwitchToSignUp: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authView, setAuthView] = useState<AuthView>("signin");
  const [pendingUsername, setPendingUsername] = useState<string>("");
  const [pendingEmail, setPendingEmail] = useState<string>("");

  const checkAuth = async () => {
    setIsLoading(true);
    try {
      const isAuth = await cognitoService.isAuthenticatedWithValidation();
      if (isAuth) {
        const cognitoUser = await cognitoService.getCurrentUser();
        const tokens = await cognitoService.getCurrentUserTokens();

        if (cognitoUser && tokens) {
          const user: User = {
            id: cognitoUser.userId,
            username: cognitoUser.username,
            email: cognitoUser.email,
            emailVerified: cognitoUser.emailVerified,
            access_token: tokens.accessToken,
            groups: cognitoUser.groups,
          };
          setUser(user);
        }
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error("Auth check error:", error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await cognitoService.signOut();
      setUser(null);
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Auth flow handlers
  const handleSignUpSuccess = (username: string, email: string) => {
    setPendingUsername(username);
    setPendingEmail(email);
    setAuthView("email-confirmation");
  };

  const handleEmailConfirmationSuccess = async () => {
    await checkAuth();
  };

  const handleSwitchToSignIn = () => {
    setAuthView("signin");
  };

  const handleSwitchToSignUp = () => {
    setAuthView("signup");
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    authView,
    pendingUsername,
    pendingEmail,
    checkAuth,
    logout,
    setAuthView,
    handleSignUpSuccess,
    handleEmailConfirmationSuccess,
    handleSwitchToSignIn,
    handleSwitchToSignUp,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
