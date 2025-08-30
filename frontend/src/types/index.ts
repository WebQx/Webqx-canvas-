export interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  fullName: string;
  userType: 'patient' | 'provider' | 'admin' | 'care_team';
  subscriptionTier: 'free' | 'basic' | 'premium' | 'enterprise';
  phoneNumber?: string;
  dateOfBirth?: string;
  languagePreference: string;
  timezone: string;
  biometricEnabled: boolean;
  twoFactorEnabled: boolean;
  isVerified: boolean;
  canUseZoom: boolean;
  dateJoined: string;
  lastLogin?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

export interface JournalEntry {
  id: number;
  title: string;
  content: string;
  entryType: 'text' | 'audio' | 'voice_note' | 'mood' | 'symptom';
  audioFile?: string;
  transcription?: string;
  moodRating?: number;
  painLevel?: number;
  isPrivate: boolean;
  sharedWithProvider: boolean;
  sentimentScore?: number;
  sentimentLabel?: string;
  keywords: string[];
  entities: any[];
  topics: string[];
  urgencyScore?: number;
  clinicalFlags: any[];
  wordCount: number;
  hasClinicalConcerns: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Patient {
  id: number;
  user?: number;
  openemrPatientId: string;
  medicalRecordNumber: string;
  firstName: string;
  lastName: string;
  fullName: string;
  dateOfBirth: string;
  gender: 'male' | 'female' | 'other' | 'unknown';
  phone: string;
  email: string;
  address: {
    line1: string;
    line2?: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  bloodType?: string;
  allergies?: string;
  medications?: string;
  emergencyContact: {
    name: string;
    phone: string;
  };
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  lastSync?: string;
}

export interface Appointment {
  id: number;
  patient: number;
  patientName: string;
  provider: number;
  providerName: string;
  appointmentType: 'routine' | 'follow-up' | 'urgent' | 'telehealth' | 'consultation';
  status: 'scheduled' | 'confirmed' | 'arrived' | 'in-progress' | 'completed' | 'cancelled' | 'no-show';
  startTime: string;
  endTime: string;
  durationMinutes: number;
  chiefComplaint?: string;
  notes?: string;
  isTelehealth: boolean;
  meetingUrl?: string;
  meetingId?: string;
  canJoinTelehealth: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface TelehealthSession {
  id: number;
  sessionId: string;
  roomName: string;
  patient: number;
  provider: number;
  platform: 'webrtc' | 'zoom' | 'jitsi';
  status: 'scheduled' | 'waiting' | 'active' | 'ended' | 'cancelled' | 'failed';
  scheduledStart: string;
  scheduledEnd: string;
  actualStart?: string;
  actualEnd?: string;
  zoomMeetingId?: string;
  zoomJoinUrl?: string;
  jitsiRoomUrl?: string;
  webrtcRoomConfig?: any;
  notes?: string;
  recordingEnabled: boolean;
  recordingUrl?: string;
  connectionQuality?: string;
  technicalIssues?: string;
  canJoin: boolean;
  isActive: boolean;
  durationMinutes?: number;
  createdAt: string;
  updatedAt: string;
}

export interface MoodEntry {
  id: number;
  user: number;
  overallMood: number;
  energyLevel: number;
  anxietyLevel: number;
  sleepQuality?: number;
  activities: string[];
  triggers: string[];
  location?: string;
  weather?: string;
  notes?: string;
  journalEntry?: number;
  recordedAt: string;
}

export interface SymptomLog {
  id: number;
  user: number;
  symptomName: string;
  severity: number;
  severityDisplay: string;
  durationHours?: number;
  triggers: string[];
  reliefMethods: string[];
  medicationsTaken: string[];
  description?: string;
  journalEntry?: number;
  recordedAt: string;
}

export interface Medication {
  id: number;
  patient: number;
  patientName: string;
  name: string;
  dosage: string;
  frequency: string;
  route?: string;
  prescriber?: number;
  prescriberName?: string;
  startDate: string;
  endDate?: string;
  isActive: boolean;
  isExpired: boolean;
  instructions?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface LabResult {
  id: number;
  patient: number;
  patientName: string;
  encounter?: number;
  testName: string;
  testCode?: string;
  category?: string;
  resultValue: string;
  unit?: string;
  referenceRange?: string;
  status: string;
  interpretation?: 'H' | 'L' | 'N' | 'A' | 'C';
  isAbnormal: boolean;
  collectedDatetime: string;
  resultedDatetime: string;
  orderingProvider?: number;
  providerName?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Message {
  id: number;
  sender: number;
  senderName: string;
  recipient: number;
  recipientName: string;
  subject: string;
  content: string;
  messageType: 'general' | 'appointment' | 'prescription' | 'lab_result' | 'urgent';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  isRead: boolean;
  parentMessage?: number;
  attachments: string[];
  sentAt: string;
  readAt?: string;
}

export interface Notification {
  id: number;
  user: number;
  title: string;
  message: string;
  notificationType: string;
  isRead: boolean;
  data?: any;
  createdAt: string;
  expiresAt?: string;
}