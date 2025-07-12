import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ApiService } from '../services/api';

interface UserInfo {
  username: string;
  role: string;
}

interface AuthContextType {
  user: UserInfo | null;
  token: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user_info');

    if (storedToken && storedUser) {
      try {
        const userInfo = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(userInfo);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing stored user info:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
      }
    }
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await ApiService.login({ username, password });
      
      if (response.success && response.token && response.user_info) {
        // update localStorage
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('user_info', JSON.stringify(response.user_info));
        
        // then update state
        setToken(response.token);
        setUser(response.user_info);
        setIsAuthenticated(true);
        
        console.log('Login successful:', response.user_info.username);
        return true;
      } else {
        console.error('Login failed:', response.message);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    // first clear localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    
    // then update state
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    
    // call logout API
    ApiService.logout().catch(console.error);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 