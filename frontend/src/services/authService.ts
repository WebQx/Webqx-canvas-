import * as SecureStore from 'expo-secure-store';
import { apiService } from './apiService';
import { User, AuthTokens } from '../types';

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  user_type: string;
  phone_number?: string;
  date_of_birth?: string;
  language_preference?: string;
}

interface AuthResponse {
  user: User;
  tokens: AuthTokens;
  message: string;
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiService.post<AuthResponse>('/auth/login/', credentials);
      
      // Store tokens securely
      await SecureStore.setItemAsync('accessToken', response.tokens.access);
      await SecureStore.setItemAsync('refreshToken', response.tokens.refresh);
      
      return response;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    try {
      const response = await apiService.post<AuthResponse>('/auth/register/', userData);
      
      // Store tokens securely
      await SecureStore.setItemAsync('accessToken', response.tokens.access);
      await SecureStore.setItemAsync('refreshToken', response.tokens.refresh);
      
      return response;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async logout(refreshToken: string): Promise<void> {
    try {
      await apiService.post('/auth/logout/', { refresh: refreshToken });
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      // Always clear stored tokens
      await SecureStore.deleteItemAsync('accessToken');
      await SecureStore.deleteItemAsync('refreshToken');
    }
  }

  async refreshToken(refreshToken: string): Promise<{ tokens: AuthTokens }> {
    try {
      const response = await apiService.post<{ access: string }>('/auth/token/refresh/', {
        refresh: refreshToken,
      });
      
      const tokens = {
        access: response.access,
        refresh: refreshToken, // Keep the same refresh token
      };
      
      // Update stored access token
      await SecureStore.setItemAsync('accessToken', tokens.access);
      
      return { tokens };
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Token refresh failed');
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      return await apiService.get<User>('/auth/user/');
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get user data');
    }
  }

  async updateUser(userData: Partial<User>): Promise<User> {
    try {
      return await apiService.patch<User>('/auth/user/', userData);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to update user');
    }
  }

  async changePassword(data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }): Promise<void> {
    try {
      await apiService.post('/auth/change-password/', data);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to change password');
    }
  }

  async getUserPermissions(): Promise<any> {
    try {
      return await apiService.get('/auth/permissions/');
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get user permissions');
    }
  }

  async getStoredTokens(): Promise<AuthTokens | null> {
    try {
      const accessToken = await SecureStore.getItemAsync('accessToken');
      const refreshToken = await SecureStore.getItemAsync('refreshToken');
      
      if (accessToken && refreshToken) {
        return {
          access: accessToken,
          refresh: refreshToken,
        };
      }
      
      return null;
    } catch (error) {
      console.error('Error getting stored tokens:', error);
      return null;
    }
  }

  async clearStoredTokens(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync('accessToken');
      await SecureStore.deleteItemAsync('refreshToken');
    } catch (error) {
      console.error('Error clearing stored tokens:', error);
    }
  }
}

export const authService = new AuthService();