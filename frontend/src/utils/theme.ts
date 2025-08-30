import { DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#007AFF',
    accent: '#34C759',
    background: '#FFFFFF',
    surface: '#F8F9FA',
    text: '#1C1C1E',
    disabled: '#8E8E93',
    placeholder: '#C7C7CC',
    backdrop: '#000000',
    error: '#FF3B30',
    warning: '#FF9500',
    success: '#34C759',
    info: '#007AFF',
    
    // Custom healthcare colors
    medical: {
      primary: '#007AFF',
      secondary: '#34C759',
      urgent: '#FF3B30',
      warning: '#FF9500',
      info: '#007AFF',
      neutral: '#8E8E93',
    },
    
    // Mood colors
    mood: {
      veryPoor: '#FF3B30',
      poor: '#FF9500',
      fair: '#FFCC00',
      good: '#34C759',
      veryGood: '#30D158',
    },
    
    // Telehealth colors
    telehealth: {
      connected: '#34C759',
      connecting: '#FF9500',
      disconnected: '#FF3B30',
      waiting: '#007AFF',
    },
  },
  fonts: {
    ...DefaultTheme.fonts,
    regular: {
      fontFamily: 'System',
      fontWeight: '400' as const,
    },
    medium: {
      fontFamily: 'System',
      fontWeight: '500' as const,
    },
    bold: {
      fontFamily: 'System',
      fontWeight: '700' as const,
    },
  },
  roundness: 8,
  animation: {
    scale: 1.0,
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const fontSizes = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  xxl: 24,
  xxxl: 28,
};

export const shadows = {
  small: {
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  medium: {
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  large: {
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.32,
    shadowRadius: 5.46,
    elevation: 9,
  },
};

export const borderRadius = {
  small: 4,
  medium: 8,
  large: 16,
  pill: 50,
};

// Utility functions for consistent styling
export const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'active':
    case 'connected':
    case 'completed':
    case 'confirmed':
      return theme.colors.success;
    case 'pending':
    case 'waiting':
    case 'scheduled':
      return theme.colors.warning;
    case 'failed':
    case 'cancelled':
    case 'disconnected':
    case 'error':
      return theme.colors.error;
    case 'in-progress':
    case 'connecting':
      return theme.colors.info;
    default:
      return theme.colors.disabled;
  }
};

export const getMoodColor = (mood: number): string => {
  switch (mood) {
    case 1:
      return theme.colors.mood.veryPoor;
    case 2:
      return theme.colors.mood.poor;
    case 3:
      return theme.colors.mood.fair;
    case 4:
      return theme.colors.mood.good;
    case 5:
      return theme.colors.mood.veryGood;
    default:
      return theme.colors.disabled;
  }
};

export const getPriorityColor = (priority: string): string => {
  switch (priority.toLowerCase()) {
    case 'urgent':
      return theme.colors.error;
    case 'high':
      return theme.colors.warning;
    case 'normal':
      return theme.colors.info;
    case 'low':
      return theme.colors.disabled;
    default:
      return theme.colors.text;
  }
};