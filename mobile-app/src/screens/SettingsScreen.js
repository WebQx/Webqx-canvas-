import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  Alert,
  Modal,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Picker } from '@react-native-picker/picker';
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';
import SettingsService from '../services/SettingsService';
import TierService from '../services/TierService';

const SettingsScreen = () => {
  const [settings, setSettings] = useState({
    language: 'en',
    notifications: true,
    biometricAuth: false,
    darkMode: false,
    syncEnabled: true,
    userTier: 'standard',
  });
  const [languageModalVisible, setLanguageModalVisible] = useState(false);
  const [tierModalVisible, setTierModalVisible] = useState(false);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Español' },
    { code: 'fr', name: 'Français' },
    { code: 'ar', name: 'العربية' },
    { code: 'hi', name: 'हिन्दी' },
    { code: 'sw', name: 'Kiswahili' },
  ];

  const tiers = [
    { 
      code: 'standard', 
      name: 'Standard (Free)', 
      description: 'WebRTC video calls, basic features' 
    },
    { 
      code: 'premium', 
      name: 'Premium', 
      description: 'Zoom HD video, advanced analytics, priority support' 
    },
  ];

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const userSettings = await SettingsService.getUserSettings();
      setSettings(userSettings);
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const updateSetting = async (key, value) => {
    try {
      const newSettings = { ...settings, [key]: value };
      setSettings(newSettings);
      await SettingsService.updateSetting(key, value);
    } catch (error) {
      Alert.alert('Error', 'Failed to update setting');
    }
  };

  const toggleBiometricAuth = async () => {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      if (!hasHardware) {
        Alert.alert('Not Supported', 'Biometric authentication is not supported on this device');
        return;
      }

      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      if (!isEnrolled) {
        Alert.alert('Setup Required', 'Please set up biometric authentication in your device settings first');
        return;
      }

      if (!settings.biometricAuth) {
        const result = await LocalAuthentication.authenticateAsync({
          promptMessage: 'Enable biometric authentication',
          fallbackLabel: 'Use Passcode',
        });

        if (result.success) {
          updateSetting('biometricAuth', true);
        }
      } else {
        updateSetting('biometricAuth', false);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to toggle biometric authentication');
    }
  };

  const syncData = async () => {
    try {
      Alert.alert(
        'Sync Data',
        'This will sync your data across all devices. Continue?',
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Sync',
            onPress: async () => {
              await SettingsService.syncUserData();
              Alert.alert('Success', 'Data synced successfully');
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to sync data');
    }
  };

  const upgradeTier = async () => {
    try {
      const upgradeInfo = await TierService.getUpgradeInfo();
      Alert.alert(
        'Upgrade to Premium',
        `Premium features include:\n• Zoom HD video calls\n• Advanced health analytics\n• Priority support\n\nPrice: ${upgradeInfo.price}/month`,
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Upgrade',
            onPress: async () => {
              // In a real app, this would redirect to payment flow
              Alert.alert('Upgrade', 'Redirecting to payment...');
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to load upgrade information');
    }
  };

  const renderSettingItem = (title, subtitle, rightComponent) => (
    <View style={styles.settingItem}>
      <View style={styles.settingContent}>
        <Text style={styles.settingTitle}>{title}</Text>
        {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
      </View>
      {rightComponent}
    </View>
  );

  const renderLanguageModal = () => (
    <Modal
      animationType="slide"
      transparent={true}
      visible={languageModalVisible}
      onRequestClose={() => setLanguageModalVisible(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Select Language</Text>
            <TouchableOpacity onPress={() => setLanguageModalVisible(false)}>
              <Icon name="close" size={24} color="#6B7280" />
            </TouchableOpacity>
          </View>
          
          {languages.map((lang) => (
            <TouchableOpacity
              key={lang.code}
              style={[
                styles.languageOption,
                settings.language === lang.code && styles.selectedLanguage,
              ]}
              onPress={() => {
                updateSetting('language', lang.code);
                setLanguageModalVisible(false);
              }}
            >
              <Text style={[
                styles.languageText,
                settings.language === lang.code && styles.selectedLanguageText,
              ]}>
                {lang.name}
              </Text>
              {settings.language === lang.code && (
                <Icon name="check" size={20} color="#2563EB" />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </Modal>
  );

  const renderTierModal = () => (
    <Modal
      animationType="slide"
      transparent={true}
      visible={tierModalVisible}
      onRequestClose={() => setTierModalVisible(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Subscription Tier</Text>
            <TouchableOpacity onPress={() => setTierModalVisible(false)}>
              <Icon name="close" size={24} color="#6B7280" />
            </TouchableOpacity>
          </View>
          
          {tiers.map((tier) => (
            <TouchableOpacity
              key={tier.code}
              style={[
                styles.tierOption,
                settings.userTier === tier.code && styles.selectedTier,
              ]}
              onPress={() => {
                if (tier.code === 'premium' && settings.userTier !== 'premium') {
                  setTierModalVisible(false);
                  upgradeTier();
                } else {
                  setTierModalVisible(false);
                }
              }}
            >
              <View style={styles.tierContent}>
                <Text style={[
                  styles.tierTitle,
                  settings.userTier === tier.code && styles.selectedTierText,
                ]}>
                  {tier.name}
                </Text>
                <Text style={styles.tierDescription}>{tier.description}</Text>
              </View>
              {settings.userTier === tier.code && (
                <Icon name="check" size={20} color="#2563EB" />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </Modal>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences</Text>
        
        {renderSettingItem(
          'Language',
          languages.find(l => l.code === settings.language)?.name,
          <TouchableOpacity onPress={() => setLanguageModalVisible(true)}>
            <Icon name="chevron-right" size={24} color="#9CA3AF" />
          </TouchableOpacity>
        )}

        {renderSettingItem(
          'Notifications',
          'Receive push notifications',
          <Switch
            value={settings.notifications}
            onValueChange={(value) => updateSetting('notifications', value)}
            trackColor={{ false: '#D1D5DB', true: '#93C5FD' }}
            thumbColor={settings.notifications ? '#2563EB' : '#6B7280'}
          />
        )}

        {renderSettingItem(
          'Dark Mode',
          'Use dark theme',
          <Switch
            value={settings.darkMode}
            onValueChange={(value) => updateSetting('darkMode', value)}
            trackColor={{ false: '#D1D5DB', true: '#93C5FD' }}
            thumbColor={settings.darkMode ? '#2563EB' : '#6B7280'}
          />
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Security</Text>
        
        {renderSettingItem(
          'Biometric Authentication',
          'Use fingerprint or face ID',
          <Switch
            value={settings.biometricAuth}
            onValueChange={toggleBiometricAuth}
            trackColor={{ false: '#D1D5DB', true: '#93C5FD' }}
            thumbColor={settings.biometricAuth ? '#2563EB' : '#6B7280'}
          />
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data & Sync</Text>
        
        {renderSettingItem(
          'Device Sync',
          'Sync data across devices',
          <Switch
            value={settings.syncEnabled}
            onValueChange={(value) => updateSetting('syncEnabled', value)}
            trackColor={{ false: '#D1D5DB', true: '#93C5FD' }}
            thumbColor={settings.syncEnabled ? '#2563EB' : '#6B7280'}
          />
        )}

        <TouchableOpacity onPress={syncData} style={styles.actionButton}>
          <Icon name="sync" size={24} color="#2563EB" />
          <Text style={styles.actionButtonText}>Sync Now</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Subscription</Text>
        
        {renderSettingItem(
          'Current Plan',
          tiers.find(t => t.code === settings.userTier)?.name,
          <TouchableOpacity onPress={() => setTierModalVisible(true)}>
            <Icon name="chevron-right" size={24} color="#9CA3AF" />
          </TouchableOpacity>
        )}

        {settings.userTier === 'standard' && (
          <TouchableOpacity onPress={upgradeTier} style={styles.upgradeButton}>
            <Icon name="star" size={24} color="#FFFFFF" />
            <Text style={styles.upgradeButtonText}>Upgrade to Premium</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Accessibility</Text>
        
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="accessibility" size={24} color="#2563EB" />
          <Text style={styles.actionButtonText}>Accessibility Settings</Text>
        </TouchableOpacity>
      </View>

      {renderLanguageModal()}
      {renderTierModal()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  section: {
    backgroundColor: '#FFFFFF',
    marginBottom: 12,
    paddingVertical: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F9FAFB',
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    color: '#1F2937',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 14,
    color: '#6B7280',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F9FAFB',
  },
  actionButtonText: {
    fontSize: 16,
    color: '#2563EB',
    marginLeft: 12,
  },
  upgradeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2563EB',
    marginHorizontal: 20,
    marginVertical: 12,
    paddingVertical: 12,
    borderRadius: 8,
  },
  upgradeButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginLeft: 8,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    margin: 20,
    minWidth: 300,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  languageOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F9FAFB',
  },
  selectedLanguage: {
    backgroundColor: '#EFF6FF',
  },
  languageText: {
    fontSize: 16,
    color: '#1F2937',
  },
  selectedLanguageText: {
    color: '#2563EB',
    fontWeight: '600',
  },
  tierOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F9FAFB',
  },
  selectedTier: {
    backgroundColor: '#EFF6FF',
  },
  tierContent: {
    flex: 1,
  },
  tierTitle: {
    fontSize: 16,
    color: '#1F2937',
    marginBottom: 4,
  },
  selectedTierText: {
    color: '#2563EB',
    fontWeight: '600',
  },
  tierDescription: {
    fontSize: 14,
    color: '#6B7280',
  },
});

export default SettingsScreen;