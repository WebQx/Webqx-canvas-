import * as SecureStore from 'expo-secure-store';
import axios from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

class TierService {
  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/tiers`,
      timeout: 10000,
    });
  }

  async getUserTier() {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (!token) {
        return 'standard'; // Default tier for unauthenticated users
      }

      const response = await this.client.get('/current', {
        headers: { Authorization: `Bearer ${token}` },
      });

      return response.data.tier || 'standard';
    } catch (error) {
      console.error('Get user tier error:', error);
      return 'standard'; // Fallback to standard tier
    }
  }

  async getTierFeatures(tier = null) {
    try {
      const userTier = tier || await this.getUserTier();
      
      const features = {
        standard: {
          videoCall: 'webrtc',
          maxVideoQuality: '720p',
          recordingDuration: 30, // minutes
          storageLimit: 1, // GB
          analyticsLevel: 'basic',
          supportLevel: 'community',
          features: [
            'WebRTC video calls',
            'Basic health tracking',
            'Journal with text entries',
            'Basic EMR access',
            'Community support',
          ],
        },
        premium: {
          videoCall: 'zoom',
          maxVideoQuality: '1080p',
          recordingDuration: 120, // minutes
          storageLimit: 10, // GB
          analyticsLevel: 'advanced',
          supportLevel: 'priority',
          features: [
            'Zoom HD video calls',
            'Advanced health analytics',
            'Audio + text journal entries',
            'Full EMR integration',
            'Priority support',
            'AI health insights',
            'Extended storage',
          ],
        },
      };

      return features[userTier] || features.standard;
    } catch (error) {
      console.error('Get tier features error:', error);
      return this.getTierFeatures('standard');
    }
  }

  async getUpgradeInfo() {
    try {
      const response = await this.client.get('/upgrade-info');
      return response.data;
    } catch (error) {
      console.error('Get upgrade info error:', error);
      // Return mock data for demo
      return {
        price: '$9.99',
        currency: 'USD',
        billingPeriod: 'month',
        features: [
          'Zoom HD video calls',
          'Advanced health analytics',
          'Priority support',
          'AI health insights',
          '10GB storage',
        ],
        trialPeriod: 7, // days
      };
    }
  }

  async checkFeatureAccess(feature) {
    try {
      const tierFeatures = await this.getTierFeatures();
      
      const featureAccessMap = {
        'zoom_video': tierFeatures.videoCall === 'zoom',
        'hd_video': tierFeatures.maxVideoQuality === '1080p',
        'audio_journal': tierFeatures.features.includes('Audio + text journal entries'),
        'advanced_analytics': tierFeatures.analyticsLevel === 'advanced',
        'priority_support': tierFeatures.supportLevel === 'priority',
        'ai_insights': tierFeatures.features.includes('AI health insights'),
        'extended_storage': tierFeatures.storageLimit > 1,
      };

      return featureAccessMap[feature] || false;
    } catch (error) {
      console.error('Check feature access error:', error);
      return false;
    }
  }

  async getStorageUsage() {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const response = await this.client.get('/storage', {
        headers: { Authorization: `Bearer ${token}` },
      });

      return response.data;
    } catch (error) {
      console.error('Get storage usage error:', error);
      // Return mock data for demo
      return {
        used: 0.5, // GB
        total: 1, // GB
        usage: 0.5, // percentage
      };
    }
  }

  async upgradeTier(newTier, paymentInfo) {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const response = await this.client.post('/upgrade', {
        tier: newTier,
        payment: paymentInfo,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });

      return response.data;
    } catch (error) {
      console.error('Upgrade tier error:', error);
      throw error;
    }
  }

  async downgradeTier(reason = null) {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const response = await this.client.post('/downgrade', {
        reason,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });

      return response.data;
    } catch (error) {
      console.error('Downgrade tier error:', error);
      throw error;
    }
  }

  async getTierUsageStats() {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const response = await this.client.get('/usage-stats', {
        headers: { Authorization: `Bearer ${token}` },
      });

      return response.data;
    } catch (error) {
      console.error('Get tier usage stats error:', error);
      // Return mock data for demo
      return {
        videoCalls: {
          used: 15,
          limit: 100,
          period: 'monthly',
        },
        storage: {
          used: 0.5,
          limit: 1,
          unit: 'GB',
        },
        journalEntries: {
          used: 25,
          limit: null, // unlimited
        },
        apiCalls: {
          used: 450,
          limit: 1000,
          period: 'monthly',
        },
      };
    }
  }

  getTierDisplayName(tier) {
    const displayNames = {
      standard: 'Standard (Free)',
      premium: 'Premium',
      enterprise: 'Enterprise',
    };

    return displayNames[tier] || 'Unknown';
  }

  getTierColor(tier) {
    const colors = {
      standard: '#6B7280',
      premium: '#2563EB',
      enterprise: '#7C3AED',
    };

    return colors[tier] || '#6B7280';
  }
}

export default new TierService();