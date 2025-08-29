import * as SecureStore from 'expo-secure-store';
import axios from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

class SettingsService {
  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/settings`,
      timeout: 10000,
    });

    // Default settings
    this.defaultSettings = {
      language: 'en',
      notifications: true,
      biometricAuth: false,
      darkMode: false,
      syncEnabled: true,
      userTier: 'standard',
      accessibility: {
        fontSize: 'normal', // small, normal, large, extra-large
        highContrast: false,
        screenReader: false,
        reducedMotion: false,
      },
      privacy: {
        analyticsEnabled: true,
        crashReporting: true,
        personalizedAds: false,
      },
      notifications_detail: {
        appointments: true,
        medications: true,
        lab_results: true,
        messages: true,
        journal_reminders: true,
        system_updates: false,
      },
    };
  }

  async getUserSettings() {
    try {
      // Try to get from server first
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        const response = await this.client.get('/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (response.data) {
          // Merge with defaults to ensure all settings exist
          return { ...this.defaultSettings, ...response.data };
        }
      }
    } catch (error) {
      console.error('Failed to fetch settings from server:', error);
    }

    // Fallback to local storage
    try {
      const localSettings = await SecureStore.getItemAsync('user_settings');
      if (localSettings) {
        const parsed = JSON.parse(localSettings);
        return { ...this.defaultSettings, ...parsed };
      }
    } catch (error) {
      console.error('Failed to load local settings:', error);
    }

    // Return defaults if nothing else works
    return this.defaultSettings;
  }

  async updateSetting(key, value) {
    try {
      // Update locally first
      const currentSettings = await this.getUserSettings();
      const newSettings = { ...currentSettings, [key]: value };
      
      await SecureStore.setItemAsync('user_settings', JSON.stringify(newSettings));

      // Try to sync with server
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        await this.client.put('/', newSettings, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }

      return newSettings;
    } catch (error) {
      console.error('Update setting error:', error);
      throw error;
    }
  }

  async updateMultipleSettings(settings) {
    try {
      const currentSettings = await this.getUserSettings();
      const newSettings = { ...currentSettings, ...settings };
      
      await SecureStore.setItemAsync('user_settings', JSON.stringify(newSettings));

      // Try to sync with server
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        await this.client.put('/', newSettings, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }

      return newSettings;
    } catch (error) {
      console.error('Update multiple settings error:', error);
      throw error;
    }
  }

  async syncUserData() {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (!token) {
        throw new Error('Not authenticated');
      }

      // Upload local settings to server
      const localSettings = await this.getUserSettings();
      await this.client.put('/', localSettings, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Trigger data sync
      await this.client.post('/sync', {}, {
        headers: { Authorization: `Bearer ${token}` },
      });

      return { success: true };
    } catch (error) {
      console.error('Sync user data error:', error);
      throw error;
    }
  }

  async getLanguages() {
    return [
      { code: 'en', name: 'English', nativeName: 'English', rtl: false },
      { code: 'es', name: 'Spanish', nativeName: 'Español', rtl: false },
      { code: 'fr', name: 'French', nativeName: 'Français', rtl: false },
      { code: 'ar', name: 'Arabic', nativeName: 'العربية', rtl: true },
      { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', rtl: false },
      { code: 'sw', name: 'Swahili', nativeName: 'Kiswahili', rtl: false },
      { code: 'pt', name: 'Portuguese', nativeName: 'Português', rtl: false },
      { code: 'zh', name: 'Chinese', nativeName: '中文', rtl: false },
    ];
  }

  async exportSettings() {
    try {
      const settings = await this.getUserSettings();
      const exportData = {
        settings,
        exported_at: new Date().toISOString(),
        version: '1.0',
      };

      return JSON.stringify(exportData, null, 2);
    } catch (error) {
      console.error('Export settings error:', error);
      throw error;
    }
  }

  async importSettings(settingsData) {
    try {
      const parsed = JSON.parse(settingsData);
      
      if (!parsed.settings || !parsed.version) {
        throw new Error('Invalid settings format');
      }

      // Validate settings structure
      const validatedSettings = { ...this.defaultSettings, ...parsed.settings };
      
      await this.updateMultipleSettings(validatedSettings);
      
      return { success: true };
    } catch (error) {
      console.error('Import settings error:', error);
      throw error;
    }
  }

  async resetSettings() {
    try {
      await SecureStore.setItemAsync('user_settings', JSON.stringify(this.defaultSettings));
      
      // Try to reset on server too
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        await this.client.delete('/reset', {
          headers: { Authorization: `Bearer ${token}` },
        });
      }

      return this.defaultSettings;
    } catch (error) {
      console.error('Reset settings error:', error);
      throw error;
    }
  }

  async getNotificationPermissions() {
    try {
      const { Permissions } = require('expo');
      const { status } = await Permissions.getAsync(Permissions.NOTIFICATIONS);
      return status === 'granted';
    } catch (error) {
      console.error('Get notification permissions error:', error);
      return false;
    }
  }

  async requestNotificationPermissions() {
    try {
      const { Permissions } = require('expo');
      const { status } = await Permissions.askAsync(Permissions.NOTIFICATIONS);
      return status === 'granted';
    } catch (error) {
      console.error('Request notification permissions error:', error);
      return false;
    }
  }

  async getAccessibilitySettings() {
    try {
      const settings = await this.getUserSettings();
      return settings.accessibility || this.defaultSettings.accessibility;
    } catch (error) {
      console.error('Get accessibility settings error:', error);
      return this.defaultSettings.accessibility;
    }
  }

  async updateAccessibilitySettings(accessibilitySettings) {
    try {
      const settings = await this.getUserSettings();
      const newSettings = {
        ...settings,
        accessibility: { ...settings.accessibility, ...accessibilitySettings },
      };
      
      await this.updateMultipleSettings(newSettings);
      return newSettings.accessibility;
    } catch (error) {
      console.error('Update accessibility settings error:', error);
      throw error;
    }
  }

  async getPrivacySettings() {
    try {
      const settings = await this.getUserSettings();
      return settings.privacy || this.defaultSettings.privacy;
    } catch (error) {
      console.error('Get privacy settings error:', error);
      return this.defaultSettings.privacy;
    }
  }

  async updatePrivacySettings(privacySettings) {
    try {
      const settings = await this.getUserSettings();
      const newSettings = {
        ...settings,
        privacy: { ...settings.privacy, ...privacySettings },
      };
      
      await this.updateMultipleSettings(newSettings);
      return newSettings.privacy;
    } catch (error) {
      console.error('Update privacy settings error:', error);
      throw error;
    }
  }
}

export default new SettingsService();