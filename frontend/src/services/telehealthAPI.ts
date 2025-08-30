import { apiService } from './apiService';

export interface ClinicSettings {
  id?: number;
  clinic_name: string;
  default_telehealth_tier: 'webrtc' | 'zoom';
  enable_fallback_to_webrtc: boolean;
  enable_patient_choice: boolean;
  enable_bandwidth_detection: boolean;
  minimum_bandwidth_for_zoom: number;
  enable_high_contrast_mode: boolean;
  default_language: string;
  created_at?: string;
  updated_at?: string;
  last_modified_by?: number;
  last_modified_by_name?: string;
}

export interface TierPreview {
  tier: string;
  title: string;
  description: string;
  features: string[];
  pros: string[];
  cons: string[];
  ideal_for: string[];
  bandwidth_requirement: string;
  cost: string;
}

export interface UserPermissions {
  can_view_settings: boolean;
  can_edit_settings: boolean;
  can_view_audit_logs: boolean;
  can_view_analytics: boolean;
  user_type: string;
  user_name: string;
  subscription_tier: string;
  can_use_zoom: boolean;
}

export interface AuditLog {
  id: number;
  change_type: string;
  change_type_display: string;
  user_name: string;
  timestamp: string;
  old_value: Record<string, any>;
  new_value: Record<string, any>;
  reason: string;
  ip_address?: string;
}

export interface UsageAnalytics {
  date: string;
  webrtc_sessions_count: number;
  zoom_sessions_count: number;
  webrtc_total_duration_minutes: number;
  zoom_total_duration_minutes: number;
  webrtc_average_quality_score: number;
  zoom_average_quality_score: number;
  webrtc_connection_failures: number;
  zoom_connection_failures: number;
  webrtc_satisfaction_score: number;
  zoom_satisfaction_score: number;
  total_sessions: number;
  webrtc_usage_percentage: number;
  zoom_usage_percentage: number;
  tier_recommendation: {
    recommended_tier: string;
    reason: string;
    confidence: number;
  };
}

export const telehealthAPI = {
  /**
   * Get current clinic telehealth settings
   */
  async getClinicSettings() {
    return apiService.get<ClinicSettings>('/telehealth/clinic-settings/');
  },

  /**
   * Update clinic telehealth settings
   */
  async updateClinicSettings(settings: Partial<ClinicSettings>) {
    return apiService.put<ClinicSettings>('/telehealth/clinic-settings/update/', settings);
  },

  /**
   * Get tier preview information for both WebRTC and Zoom
   */
  async getTierPreview() {
    return apiService.get<{ webrtc: TierPreview; zoom: TierPreview }>('/telehealth/tier-preview/');
  },

  /**
   * Check current user's permissions for telehealth settings
   */
  async getUserPermissions() {
    return apiService.get<UserPermissions>('/telehealth/user-permissions/');
  },

  /**
   * Get telehealth tier change audit logs (Admin/Coordinator only)
   */
  async getAuditLogs(days: number = 30) {
    return apiService.get<{ audit_logs: AuditLog[]; total_count: number }>(`/telehealth/audit-logs/?days=${days}`);
  },

  /**
   * Get usage analytics for recommendations (Admin/Coordinator only)
   */
  async getUsageAnalytics(days: number = 30) {
    return apiService.get<{
      analytics: UsageAnalytics[];
      overall_recommendation: {
        recommended_tier: string;
        reason: string;
        confidence: number;
      };
      period_days: number;
    }>(`/telehealth/usage-analytics/?days=${days}`);
  },

  /**
   * Test bandwidth for tier recommendation
   */
  async testBandwidth() {
    // This would typically integrate with a bandwidth testing service
    // For now, return a mock response
    return new Promise<{ upload_mbps: number; download_mbps: number; recommended_tier: string }>((resolve) => {
      setTimeout(() => {
        // Simulate bandwidth test
        const upload_mbps = Math.random() * 10 + 0.5; // 0.5-10.5 Mbps
        const download_mbps = Math.random() * 20 + 1; // 1-21 Mbps
        const recommended_tier = (upload_mbps > 1.5 && download_mbps > 2) ? 'zoom' : 'webrtc';
        
        resolve({
          upload_mbps: Math.round(upload_mbps * 100) / 100,
          download_mbps: Math.round(download_mbps * 100) / 100,
          recommended_tier
        });
      }, 2000); // Simulate 2 second test
    });
  },

  /**
   * Get telehealth session history for analytics
   */
  async getSessionHistory(days: number = 30) {
    return apiService.get(`/telehealth/sessions/?days=${days}`);
  },

  /**
   * Create a new telehealth session with the specified tier
   */
  async createSession(sessionData: {
    patient_id: number;
    provider_id: number;
    scheduled_start: string;
    scheduled_end: string;
    platform?: 'webrtc' | 'zoom';
    notes?: string;
  }) {
    return apiService.post('/telehealth/sessions/', sessionData);
  },

  /**
   * Get join information for a telehealth session
   */
  async getSessionJoinInfo(sessionId: string) {
    return apiService.get(`/telehealth/sessions/${sessionId}/join-info/`);
  },

  /**
   * Leave a telehealth session
   */
  async leaveSession(sessionId: string) {
    return apiService.post(`/telehealth/sessions/${sessionId}/leave/`);
  },

  /**
   * Test device compatibility for telehealth
   */
  async testDevice(testType: 'microphone' | 'camera' | 'speaker' | 'network' | 'bandwidth') {
    return apiService.post('/telehealth/device-tests/', {
      test_type: testType
    });
  },

  /**
   * Get device test results
   */
  async getDeviceTestResults() {
    return apiService.get('/telehealth/device-tests/');
  }
};

export default telehealthAPI;