import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import { AuthService } from "../services";
import type { LoginRequest, User } from "../types";

interface AuthContextType {
  user: User | null;
  login: (loginRequest: LoginRequest) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
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

  useEffect(() => {
    // Check if user is logged in on app start
    const savedUser = localStorage.getItem("user");
    const savedToken = localStorage.getItem("access_token");

    if (savedUser && savedToken) {
      try {
        const userData = JSON.parse(savedUser);
        const user: User = {
          ...userData,
          access_token: savedToken,
        };
        setUser(user);
      } catch (error) {
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (loginRequest: LoginRequest): Promise<boolean> => {
    setIsLoading(true);

    try {
      // Use AuthService for authentication
      const authService = new AuthService();
      const authData = await authService.login(loginRequest);

      const user: User = {
        id: authData.user_id,
        username: authData.username,
        access_token: authData.access_token,
      };

      setUser(user);
      localStorage.setItem(
        "user",
        JSON.stringify({ id: user.id, username: user.username })
      );
      localStorage.setItem("access_token", user.access_token);
      return true;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
  };

  const value = {
    user,
    login,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
