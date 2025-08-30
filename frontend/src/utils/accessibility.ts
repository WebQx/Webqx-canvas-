import React from 'react';
import { AccessibilityInfo, Platform } from 'react-native';

export interface AccessibilityProps {
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: string;
  accessible?: boolean;
  testID?: string;
}

export const useAccessibility = () => {
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = React.useState(false);
  const [isHighContrastEnabled, setIsHighContrastEnabled] = React.useState(false);

  React.useEffect(() => {
    const checkScreenReader = async () => {
      try {
        const screenReaderEnabled = await AccessibilityInfo.isScreenReaderEnabled();
        setIsScreenReaderEnabled(screenReaderEnabled);
      } catch (error) {
        console.warn('Failed to check screen reader status:', error);
      }
    };

    checkScreenReader();

    // Listen for changes in screen reader status
    const subscription = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      setIsScreenReaderEnabled
    );

    return () => {
      if (subscription?.remove) {
        subscription.remove();
      }
    };
  }, []);

  const announceForAccessibility = (message: string) => {
    if (Platform.OS === 'ios') {
      AccessibilityInfo.announceForAccessibility(message);
    } else {
      // For Android, we can use the announceForAccessibilityWithOptions
      AccessibilityInfo.announceForAccessibility(message);
    }
  };

  const makeAccessible = (
    label: string,
    hint?: string,
    role?: string
  ): AccessibilityProps => ({
    accessible: true,
    accessibilityLabel: label,
    accessibilityHint: hint,
    accessibilityRole: role as any,
  });

  return {
    isScreenReaderEnabled,
    isHighContrastEnabled,
    setIsHighContrastEnabled,
    announceForAccessibility,
    makeAccessible,
  };
};

export const getAccessibilityProps = (
  label: string,
  hint?: string,
  role?: string
): AccessibilityProps => ({
  accessible: true,
  accessibilityLabel: label,
  accessibilityHint: hint,
  accessibilityRole: role as any,
});

// Multilingual support helper
export const getLocalizedText = (
  key: string,
  language: string = 'en',
  fallback?: string
): string => {
  // Simple multilingual text mapping
  const translations: Record<string, Record<string, string>> = {
    'telehealth.tier.free': {
      en: 'Free Tier (WebRTC)',
      es: 'Nivel Gratuito (WebRTC)',
      ur: 'مفت ٹیئر (WebRTC)',
    },
    'telehealth.tier.paid': {
      en: 'Paid Tier (Zoom SDK)',
      es: 'Nivel Pagado (Zoom SDK)',
      ur: 'پیڈ ٹیئر (Zoom SDK)',
    },
    'telehealth.description.free': {
      en: 'Peer-to-peer video communication',
      es: 'Comunicación de video peer-to-peer',
      ur: 'پیئر ٹو پیئر ویڈیو کمیونیکیشن',
    },
    'telehealth.description.paid': {
      en: 'Enterprise-grade video platform',
      es: 'Plataforma de video de nivel empresarial',
      ur: 'انٹرپرائز گریڈ ویڈیو پلیٹفارم',
    },
    'settings.telehealth': {
      en: 'Telehealth Tier Settings',
      es: 'Configuración de Nivel de Telemedicina',
      ur: 'ٹیلی ہیلتھ ٹیئر سیٹنگز',
    },
    'accessibility.high_contrast': {
      en: 'High contrast mode for better visibility',
      es: 'Modo de alto contraste para mejor visibilidad',
      ur: 'بہتر نظر کے لیے ہائی کنٹراسٹ موڈ',
    },
    'button.save': {
      en: 'Save Changes',
      es: 'Guardar Cambios',
      ur: 'تبدیلیاں محفوظ کریں',
    },
    'button.cancel': {
      en: 'Cancel',
      es: 'Cancelar',
      ur: 'منسوخ کریں',
    },
    'access_denied': {
      en: 'Access Denied',
      es: 'Acceso Denegado',
      ur: 'رسائی مسترد',
    },
    'fallback.enable': {
      en: 'Allow fallback to WebRTC if Zoom fails',
      es: 'Permitir respaldo a WebRTC si Zoom falla',
      ur: 'اگر زوم فیل ہو تو WebRTC کو فال بیک کی اجازت دیں',
    },
    'patient_choice.enable': {
      en: 'Enable patient choice at session start',
      es: 'Habilitar elección del paciente al inicio de la sesión',
      ur: 'سیشن شروع ہونے پر مریض کا انتخاب فعال کریں',
    },
  };

  const text = translations[key]?.[language] || translations[key]?.['en'] || fallback || key;
  return text;
};

export default {
  useAccessibility,
  getAccessibilityProps,
  getLocalizedText,
};