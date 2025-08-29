// API Configuration
export const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api' 
  : 'https://api.webqx.healthcare/api';

// App Configuration
export const APP_NAME = 'WebQx Healthcare';
export const APP_VERSION = '1.0.0';

// Feature Flags
export const FEATURES = {
  BIOMETRIC_AUTH: true,
  OFFLINE_MODE: true,
  VOICE_NOTES: true,
  VIDEO_CALLS: true,
  PUSH_NOTIFICATIONS: true,
};

// Subscription Tiers
export const SUBSCRIPTION_TIERS = {
  FREE: 'free',
  BASIC: 'basic',
  PREMIUM: 'premium',
  ENTERPRISE: 'enterprise',
} as const;

// User Types
export const USER_TYPES = {
  PATIENT: 'patient',
  PROVIDER: 'provider',
  ADMIN: 'admin',
  CARE_TEAM: 'care_team',
} as const;

// Message Types
export const MESSAGE_TYPES = {
  GENERAL: 'general',
  APPOINTMENT: 'appointment',
  PRESCRIPTION: 'prescription',
  LAB_RESULT: 'lab_result',
  URGENT: 'urgent',
  SYSTEM: 'system',
} as const;

// Priority Levels
export const PRIORITY_LEVELS = {
  LOW: 'low',
  NORMAL: 'normal',
  HIGH: 'high',
  URGENT: 'urgent',
} as const;

// Telehealth Platforms
export const TELEHEALTH_PLATFORMS = {
  WEBRTC: 'webrtc',
  ZOOM: 'zoom',
  JITSI: 'jitsi',
} as const;

// Journal Entry Types
export const JOURNAL_ENTRY_TYPES = {
  TEXT: 'text',
  AUDIO: 'audio',
  VOICE_NOTE: 'voice_note',
  MOOD: 'mood',
  SYMPTOM: 'symptom',
} as const;

// Mood Rating Scale
export const MOOD_SCALE = {
  VERY_POOR: 1,
  POOR: 2,
  FAIR: 3,
  GOOD: 4,
  VERY_GOOD: 5,
} as const;

// Pain Level Scale (0-10)
export const PAIN_SCALE = {
  NO_PAIN: 0,
  MILD: 1,
  MODERATE: 5,
  SEVERE: 7,
  WORST: 10,
} as const;

// Notification Types
export const NOTIFICATION_TYPES = {
  APPOINTMENT_REMINDER: 'appointment_reminder',
  TELEHEALTH_REMINDER: 'telehealth_reminder',
  TELEHEALTH_INVITATION: 'telehealth_invitation',
  MESSAGE_RECEIVED: 'message_received',
  LAB_RESULT: 'lab_result',
  PRESCRIPTION_READY: 'prescription_ready',
  SYSTEM_UPDATE: 'system_update',
} as const;

// Common Regex Patterns
export const REGEX_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^\+?[\d\s\-\(\)]+$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
  USERNAME: /^[a-zA-Z0-9_]{3,20}$/,
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  OFFLINE_ERROR: 'You are offline. Some features may not be available.',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Welcome back!',
  REGISTER_SUCCESS: 'Account created successfully!',
  LOGOUT_SUCCESS: 'You have been logged out.',
  PROFILE_UPDATED: 'Profile updated successfully.',
  PASSWORD_CHANGED: 'Password changed successfully.',
  MESSAGE_SENT: 'Message sent successfully.',
  APPOINTMENT_SCHEDULED: 'Appointment scheduled successfully.',
} as const;

// Storage Keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'accessToken',
  REFRESH_TOKEN: 'refreshToken',
  USER_PREFERENCES: 'userPreferences',
  OFFLINE_DATA: 'offlineData',
  BIOMETRIC_ENABLED: 'biometricEnabled',
} as const;

// Image Picker Options
export const IMAGE_PICKER_OPTIONS = {
  mediaTypes: 'Images' as const,
  allowsEditing: true,
  aspect: [4, 3] as [number, number],
  quality: 0.8,
};

// Audio Recording Options
export const AUDIO_RECORDING_OPTIONS = {
  android: {
    extension: '.m4a',
    outputFormat: 'mpeg_4' as const,
    audioEncoder: 'aac' as const,
    sampleRate: 44100,
    numberOfChannels: 2,
    bitRate: 128000,
  },
  ios: {
    extension: '.m4a',
    outputFormat: 'mpeg_4' as const,
    audioQuality: 'high' as const,
    sampleRate: 44100,
    numberOfChannels: 2,
    bitRate: 128000,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
};

// Pagination Defaults
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;