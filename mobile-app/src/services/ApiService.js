import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
    });

    // Add auth token to requests
    this.client.interceptors.request.use(async (config) => {
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          try {
            await AuthService.refreshToken();
            // Retry the original request
            return this.client.request(error.config);
          } catch (refreshError) {
            // Refresh failed, redirect to login
            await AuthService.logout();
            throw refreshError;
          }
        }
        throw error;
      }
    );
  }

  // Dashboard API
  async getDashboardData() {
    try {
      const response = await this.client.get('/dashboard');
      return response.data;
    } catch (error) {
      console.error('API Error - getDashboardData:', error);
      // Return mock data for demo
      return {
        dailyCheckIns: [
          {
            id: 1,
            title: 'Morning Wellness Check',
            dueTime: '9:00 AM',
          },
        ],
        reminders: [
          {
            id: 1,
            message: 'Take your morning medication',
            time: '8:00 AM',
          },
        ],
        careTeamUpdates: [
          {
            id: 1,
            message: 'Your lab results are ready for review',
            from: 'Dr. Smith',
            timestamp: '2 hours ago',
          },
        ],
        upcomingAppointments: [
          {
            id: 1,
            title: 'Follow-up Consultation',
            provider: 'Dr. Smith',
            dateTime: 'Tomorrow at 2:00 PM',
          },
        ],
      };
    }
  }

  async completeCheckIn(checkInId) {
    const response = await this.client.post(`/checkins/${checkInId}/complete`);
    return response.data;
  }

  // Journal API
  async getJournalEntries() {
    try {
      const response = await this.client.get('/journal/entries');
      return response.data;
    } catch (error) {
      // Return mock data for demo
      return [
        {
          id: 1,
          text: 'Feeling much better today. The new medication seems to be working well.',
          timestamp: new Date().toISOString(),
          tags: ['positive', 'medication', 'improvement'],
        },
        {
          id: 2,
          text: 'Had some side effects yesterday but they seem to be subsiding.',
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          tags: ['side effects', 'medication'],
          audio: '/path/to/audio.mp3',
        },
      ];
    }
  }

  async saveJournalEntry(entryData) {
    const response = await this.client.post('/journal/entries', entryData);
    return response.data;
  }

  async exportJournalEntries() {
    const response = await this.client.get('/journal/export');
    return response.data;
  }

  // EMR API
  async getEMRData() {
    try {
      const response = await this.client.get('/emr/data');
      return response.data;
    } catch (error) {
      // Return mock data for demo
      return {
        labs: [
          {
            id: 1,
            name: 'Blood Glucose',
            value: '95',
            unit: 'mg/dL',
            status: 'normal',
            date: '2024-01-15',
            reference: '70-100 mg/dL',
          },
          {
            id: 2,
            name: 'Blood Pressure',
            value: '120/80',
            unit: 'mmHg',
            status: 'normal',
            date: '2024-01-15',
            reference: '<140/90 mmHg',
          },
        ],
        medications: [
          {
            id: 1,
            name: 'Metformin',
            dosage: '500mg',
            frequency: 'Twice daily',
            prescriber: 'Dr. Smith',
            startDate: '2024-01-01',
          },
        ],
        appointments: [
          {
            id: 1,
            type: 'Follow-up',
            provider: 'Dr. Smith',
            date: '2024-01-20',
            time: '2:00 PM',
            location: 'Main Clinic',
            notes: 'Review recent lab results',
          },
        ],
        carePlans: [
          {
            id: 1,
            title: 'Diabetes Management Plan',
            description: 'Comprehensive plan for managing Type 2 diabetes',
            createdBy: 'Dr. Smith',
            date: '2024-01-01',
            goals: [
              { text: 'Maintain HbA1c below 7%', completed: false },
              { text: 'Exercise 30 minutes daily', completed: true },
              { text: 'Monitor blood glucose twice daily', completed: true },
            ],
          },
        ],
      };
    }
  }

  // Telehealth API
  async getTelehealthAppointments() {
    try {
      const response = await this.client.get('/telehealth/appointments');
      return response.data;
    } catch (error) {
      // Return mock data for demo
      return [
        {
          id: 1,
          title: 'Routine Check-up',
          provider: 'Dr. Smith',
          date: 'Today',
          time: '3:00 PM',
        },
      ];
    }
  }

  async createZoomMeeting(appointmentId) {
    const response = await this.client.post(`/telehealth/zoom/${appointmentId}`);
    return response.data;
  }

  async sendOffer(appointmentId, offer) {
    const response = await this.client.post(`/telehealth/webrtc/${appointmentId}/offer`, { offer });
    return response.data;
  }

  async sendIceCandidate(appointmentId, candidate) {
    const response = await this.client.post(`/telehealth/webrtc/${appointmentId}/ice`, { candidate });
    return response.data;
  }

  // Messaging API
  async getConversations() {
    try {
      const response = await this.client.get('/messaging/conversations');
      return response.data;
    } catch (error) {
      // Return mock data for demo
      return [
        {
          id: 1,
          participantName: 'Dr. Smith',
          participantRole: 'Primary Care Physician',
          lastMessage: 'Your lab results look good. Let\'s schedule a follow-up.',
          lastMessageTime: '10:30 AM',
          unreadCount: 2,
        },
        {
          id: 2,
          participantName: 'Nurse Johnson',
          participantRole: 'Care Coordinator',
          lastMessage: 'Don\'t forget your appointment tomorrow.',
          lastMessageTime: 'Yesterday',
          unreadCount: 0,
        },
      ];
    }
  }

  async getMessages(conversationId) {
    try {
      const response = await this.client.get(`/messaging/conversations/${conversationId}/messages`);
      return response.data;
    } catch (error) {
      // Return mock data for demo
      return [
        {
          id: 1,
          text: 'Hello, how are you feeling today?',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          isFromUser: false,
        },
        {
          id: 2,
          text: 'Much better, thank you! The new medication is working well.',
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          isFromUser: true,
        },
        {
          id: 3,
          text: 'That\'s great to hear! Your lab results look good too.',
          timestamp: new Date(Date.now() - 900000).toISOString(),
          isFromUser: false,
        },
      ];
    }
  }

  async sendMessage(messageData) {
    const response = await this.client.post('/messaging/send', messageData);
    return response.data;
  }
}

export default new ApiService();