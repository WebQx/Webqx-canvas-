import * as SecureStore from 'expo-secure-store';
import axios from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

class AuthService {
  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/auth`,
      timeout: 10000,
    });
  }

  async login(email, password) {
    try {
      const response = await this.client.post('/login', {
        email,
        password,
      });

      const { token, refreshToken, user } = response.data;

      // Store tokens securely
      await SecureStore.setItemAsync('auth_token', token);
      await SecureStore.setItemAsync('refresh_token', refreshToken);
      await SecureStore.setItemAsync('user_data', JSON.stringify(user));

      return { success: true, user };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        message: error.response?.data?.message || 'Login failed',
      };
    }
  }

  async biometricLogin() {
    try {
      // Check if user has biometric auth enabled
      const biometricToken = await SecureStore.getItemAsync('biometric_token');
      if (!biometricToken) {
        throw new Error('Biometric authentication not set up');
      }

      const response = await this.client.post('/biometric-login', {
        biometricToken,
      });

      const { token, refreshToken, user } = response.data;

      // Store new tokens
      await SecureStore.setItemAsync('auth_token', token);
      await SecureStore.setItemAsync('refresh_token', refreshToken);
      await SecureStore.setItemAsync('user_data', JSON.stringify(user));

      return { success: true, user };
    } catch (error) {
      console.error('Biometric login error:', error);
      return {
        success: false,
        message: 'Biometric authentication failed',
      };
    }
  }

  async logout() {
    try {
      // Notify server of logout
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        await this.client.post('/logout', {}, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear stored data
      await SecureStore.deleteItemAsync('auth_token');
      await SecureStore.deleteItemAsync('refresh_token');
      await SecureStore.deleteItemAsync('user_data');
      await SecureStore.deleteItemAsync('biometric_token');
    }
  }

  async refreshToken() {
    try {
      const refreshToken = await SecureStore.getItemAsync('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await this.client.post('/refresh', {
        refreshToken,
      });

      const { token, refreshToken: newRefreshToken } = response.data;

      // Store new tokens
      await SecureStore.setItemAsync('auth_token', token);
      await SecureStore.setItemAsync('refresh_token', newRefreshToken);

      return { success: true };
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  }

  async checkAuthStatus() {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (!token) {
        return false;
      }

      // Verify token with server
      const response = await this.client.get('/verify', {
        headers: { Authorization: `Bearer ${token}` },
      });

      return response.status === 200;
    } catch (error) {
      console.error('Auth check error:', error);
      return false;
    }
  }

  async resetPassword(email) {
    try {
      await this.client.post('/reset-password', { email });
      return { success: true };
    } catch (error) {
      console.error('Password reset error:', error);
      throw error;
    }
  }

  async getCurrentUser() {
    try {
      const userData = await SecureStore.getItemAsync('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Get user error:', error);
      return null;
    }
  }

  async setupBiometricAuth() {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const response = await this.client.post('/setup-biometric', {}, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const { biometricToken } = response.data;
      await SecureStore.setItemAsync('biometric_token', biometricToken);

      return { success: true };
    } catch (error) {
      console.error('Biometric setup error:', error);
      throw error;
    }
  }
}

export default new AuthService();