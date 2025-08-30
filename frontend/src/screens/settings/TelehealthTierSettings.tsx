import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';
import {
  Text,
  Card,
  Title,
  Paragraph,
  Switch,
  Button,
  RadioButton,
  Chip,
  IconButton,
  ActivityIndicator,
  Portal,
  Modal,
  List,
  Divider,
} from 'react-native-paper';
import { theme } from '../../utils/theme';
import { useAuth } from '../../hooks/useAuth';
import { telehealthAPI } from '../../services/telehealthAPI';

interface ClinicSettings {
  default_telehealth_tier: 'webrtc' | 'zoom';
  enable_fallback_to_webrtc: boolean;
  enable_patient_choice: boolean;
  enable_bandwidth_detection: boolean;
  minimum_bandwidth_for_zoom: number;
  enable_high_contrast_mode: boolean;
  default_language: string;
  clinic_name: string;
  last_modified_by_name?: string;
  updated_at?: string;
}

interface TierPreview {
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

interface UserPermissions {
  can_view_settings: boolean;
  can_edit_settings: boolean;
  can_view_audit_logs: boolean;
  can_view_analytics: boolean;
  user_type: string;
  user_name: string;
  subscription_tier: string;
  can_use_zoom: boolean;
}

const TelehealthTierSettings: React.FC = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState<ClinicSettings | null>(null);
  const [tierPreviews, setTierPreviews] = useState<{webrtc: TierPreview, zoom: TierPreview} | null>(null);
  const [userPermissions, setUserPermissions] = useState<UserPermissions | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [previewModalVisible, setPreviewModalVisible] = useState(false);
  const [selectedPreviewTier, setSelectedPreviewTier] = useState<'webrtc' | 'zoom'>('webrtc');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load settings, tier previews, and user permissions in parallel
      const [settingsResponse, previewResponse, permissionsResponse] = await Promise.all([
        telehealthAPI.getClinicSettings(),
        telehealthAPI.getTierPreview(),
        telehealthAPI.getUserPermissions(),
      ]);

      setSettings(settingsResponse.data);
      setTierPreviews(previewResponse.data);
      setUserPermissions(permissionsResponse.data);
    } catch (error) {
      console.error('Failed to load telehealth settings:', error);
      Alert.alert('Error', 'Failed to load settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    if (!settings || !userPermissions?.can_edit_settings) {
      Alert.alert('Access Denied', 'You do not have permission to modify clinic settings.');
      return;
    }

    try {
      setSaving(true);
      
      // Validate settings before saving
      if (settings.default_telehealth_tier === 'zoom' && !userPermissions.can_use_zoom) {
        Alert.alert(
          'Subscription Required',
          'Your current subscription does not include Zoom integration. Please upgrade to use the Paid Tier.'
        );
        return;
      }

      const response = await telehealthAPI.updateClinicSettings(settings);
      setSettings(response.data);
      
      Alert.alert('Success', 'Telehealth tier settings have been updated successfully.');
    } catch (error: any) {
      console.error('Failed to update settings:', error);
      const errorMessage = error.response?.data?.error || 'Failed to update settings. Please try again.';
      Alert.alert('Error', errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleTierChange = (tier: 'webrtc' | 'zoom') => {
    if (!settings) return;
    
    if (tier === 'zoom' && !userPermissions?.can_use_zoom) {
      Alert.alert(
        'Subscription Required',
        'Zoom integration requires a Premium or Enterprise subscription. Would you like to learn more about upgrading?',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Learn More', onPress: () => {
            // TODO: Navigate to subscription upgrade page
            console.log('Navigate to subscription upgrade');
          }}
        ]
      );
      return;
    }

    setSettings({
      ...settings,
      default_telehealth_tier: tier
    });
  };

  const renderTierSelection = () => {
    if (!settings || !tierPreviews) return null;

    return (
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Choose Your Default Telehealth Tier</Title>
          <Paragraph style={styles.sectionDescription}>
            Select the default platform for new telehealth sessions in your clinic.
          </Paragraph>

          {/* WebRTC Option */}
          <View style={styles.tierOption}>
            <RadioButton.Android
              value="webrtc"
              status={settings.default_telehealth_tier === 'webrtc' ? 'checked' : 'unchecked'}
              onPress={() => handleTierChange('webrtc')}
              color={theme.colors.primary}
              disabled={!userPermissions?.can_edit_settings}
            />
            <View style={styles.tierInfo}>
              <View style={styles.tierHeader}>
                <Text style={styles.tierTitle}>🔘 Free Tier (WebRTC)</Text>
                <Chip
                  mode="outlined"
                  style={styles.costChip}
                  textStyle={styles.costChipText}
                >
                  Free
                </Chip>
              </View>
              <Text style={styles.tierDescription}>
                • Peer-to-peer video{'\n'}
                • Lightweight, no cost{'\n'}
                • Ideal for low-bandwidth clinics
              </Text>
              <Button
                mode="text"
                onPress={() => {
                  setSelectedPreviewTier('webrtc');
                  setPreviewModalVisible(true);
                }}
                style={styles.previewButton}
              >
                View Details
              </Button>
            </View>
          </View>

          {/* Zoom Option */}
          <View style={styles.tierOption}>
            <RadioButton.Android
              value="zoom"
              status={settings.default_telehealth_tier === 'zoom' ? 'checked' : 'unchecked'}
              onPress={() => handleTierChange('zoom')}
              color={theme.colors.primary}
              disabled={!userPermissions?.can_edit_settings || !userPermissions?.can_use_zoom}
            />
            <View style={styles.tierInfo}>
              <View style={styles.tierHeader}>
                <Text style={styles.tierTitle}>🔘 Paid Tier (Zoom SDK)</Text>
                <Chip
                  mode="outlined"
                  style={[styles.costChip, { backgroundColor: theme.colors.accent }]}
                  textStyle={[styles.costChipText, { color: 'white' }]}
                >
                  Premium
                </Chip>
              </View>
              <Text style={styles.tierDescription}>
                • Enterprise-grade video{'\n'}
                • Screen sharing, recording{'\n'}
                • HIPAA-compliant infrastructure
              </Text>
              <Button
                mode="text"
                onPress={() => {
                  setSelectedPreviewTier('zoom');
                  setPreviewModalVisible(true);
                }}
                style={styles.previewButton}
              >
                View Details
              </Button>
              {!userPermissions?.can_use_zoom && (
                <Text style={styles.upgradeNote}>
                  ⚠️ Requires subscription upgrade
                </Text>
              )}
            </View>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderAdvancedSettings = () => {
    if (!settings) return null;

    return (
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>🛠️ Advanced Settings</Title>
          
          <List.Item
            title="Allow fallback to WebRTC if Zoom fails"
            description="Automatically switch to WebRTC if Zoom connection fails"
            left={() => <List.Icon icon="backup-restore" />}
            right={() => (
              <Switch
                value={settings.enable_fallback_to_webrtc}
                onValueChange={(value) => setSettings({...settings, enable_fallback_to_webrtc: value})}
                disabled={!userPermissions?.can_edit_settings}
              />
            )}
          />
          
          <List.Item
            title="Enable patient choice at session start"
            description="Allow patients to choose their preferred platform"
            left={() => <List.Icon icon="account-check" />}
            right={() => (
              <Switch
                value={settings.enable_patient_choice}
                onValueChange={(value) => setSettings({...settings, enable_patient_choice: value})}
                disabled={!userPermissions?.can_edit_settings}
              />
            )}
          />
          
          <List.Item
            title="Enable bandwidth detection"
            description="Automatically detect connection quality and suggest optimal tier"
            left={() => <List.Icon icon="speedometer" />}
            right={() => (
              <Switch
                value={settings.enable_bandwidth_detection}
                onValueChange={(value) => setSettings({...settings, enable_bandwidth_detection: value})}
                disabled={!userPermissions?.can_edit_settings}
              />
            )}
          />
          
          <List.Item
            title="High contrast mode"
            description="Enable high contrast interface for better accessibility"
            left={() => <List.Icon icon="contrast-box" />}
            right={() => (
              <Switch
                value={settings.enable_high_contrast_mode}
                onValueChange={(value) => setSettings({...settings, enable_high_contrast_mode: value})}
                disabled={!userPermissions?.can_edit_settings}
              />
            )}
          />
        </Card.Content>
      </Card>
    );
  };

  const renderCurrentStatus = () => {
    if (!settings) return null;

    const currentTierPreview = tierPreviews?.[settings.default_telehealth_tier];
    
    return (
      <Card style={styles.statusCard}>
        <Card.Content>
          <Title style={styles.statusTitle}>📦 Current Configuration</Title>
          <Text style={styles.statusText}>
            <Text style={styles.statusLabel}>Tier: </Text>
            {currentTierPreview?.title || settings.default_telehealth_tier.toUpperCase()}
          </Text>
          <Text style={styles.statusText}>
            <Text style={styles.statusLabel}>Fallback: </Text>
            {settings.enable_fallback_to_webrtc ? 'Enabled' : 'Disabled'}
          </Text>
          <Text style={styles.statusText}>
            <Text style={styles.statusLabel}>Patient Choice: </Text>
            {settings.enable_patient_choice ? 'Enabled' : 'Disabled'}
          </Text>
          {settings.last_modified_by_name && (
            <Text style={styles.lastModified}>
              Last modified by {settings.last_modified_by_name}
            </Text>
          )}
        </Card.Content>
      </Card>
    );
  };

  const renderTierPreviewModal = () => {
    const preview = tierPreviews?.[selectedPreviewTier];
    if (!preview) return null;

    return (
      <Portal>
        <Modal
          visible={previewModalVisible}
          onDismiss={() => setPreviewModalVisible(false)}
          contentContainerStyle={styles.modalContainer}
        >
          <ScrollView style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Title style={styles.modalTitle}>{preview.title}</Title>
              <IconButton
                icon="close"
                onPress={() => setPreviewModalVisible(false)}
              />
            </View>
            
            <Paragraph style={styles.modalDescription}>
              {preview.description}
            </Paragraph>
            
            <Text style={styles.modalSectionTitle}>✨ Features</Text>
            {preview.features.map((feature, index) => (
              <Text key={index} style={styles.modalListItem}>• {feature}</Text>
            ))}
            
            <Text style={styles.modalSectionTitle}>👍 Advantages</Text>
            {preview.pros.map((pro, index) => (
              <Text key={index} style={styles.modalListItem}>• {pro}</Text>
            ))}
            
            <Text style={styles.modalSectionTitle}>⚠️ Considerations</Text>
            {preview.cons.map((con, index) => (
              <Text key={index} style={styles.modalListItem}>• {con}</Text>
            ))}
            
            <Text style={styles.modalSectionTitle}>🎯 Ideal For</Text>
            {preview.ideal_for.map((use, index) => (
              <Text key={index} style={styles.modalListItem}>• {use}</Text>
            ))}
            
            <Divider style={styles.modalDivider} />
            
            <View style={styles.modalSpecs}>
              <Text style={styles.modalSpecItem}>
                <Text style={styles.modalSpecLabel}>Bandwidth: </Text>
                {preview.bandwidth_requirement}
              </Text>
              <Text style={styles.modalSpecItem}>
                <Text style={styles.modalSpecLabel}>Cost: </Text>
                {preview.cost}
              </Text>
            </View>
            
            <Button
              mode="contained"
              onPress={() => setPreviewModalVisible(false)}
              style={styles.modalCloseButton}
            >
              Close
            </Button>
          </ScrollView>
        </Modal>
      </Portal>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Loading telehealth settings...</Text>
      </View>
    );
  }

  if (!userPermissions?.can_view_settings) {
    return (
      <View style={styles.container}>
        <Card style={styles.errorCard}>
          <Card.Content>
            <Title style={styles.errorTitle}>Access Denied</Title>
            <Paragraph>
              You do not have permission to view telehealth tier settings. 
              Contact your administrator for access.
            </Paragraph>
          </Card.Content>
        </Card>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.headerCard}>
        <Card.Content>
          <Title style={styles.title}>Telehealth Tier Settings</Title>
          <Paragraph style={styles.subtitle}>
            Configure your clinic's default telehealth platform and preferences
          </Paragraph>
        </Card.Content>
      </Card>

      {renderCurrentStatus()}
      {renderTierSelection()}
      {renderAdvancedSettings()}

      {userPermissions?.can_edit_settings && (
        <View style={styles.actionButtons}>
          <Button
            mode="outlined"
            onPress={loadData}
            style={styles.actionButton}
            disabled={loading || saving}
          >
            Refresh
          </Button>
          <Button
            mode="contained"
            onPress={handleSaveSettings}
            style={styles.actionButton}
            loading={saving}
            disabled={loading || saving}
          >
            Save Changes
          </Button>
        </View>
      )}

      {renderTierPreviewModal()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingText: {
    marginTop: 16,
    color: theme.colors.text,
    fontSize: 16,
  },
  headerCard: {
    marginBottom: 16,
  },
  title: {
    color: theme.colors.primary,
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitle: {
    color: theme.colors.text,
    fontSize: 16,
    marginTop: 4,
  },
  sectionCard: {
    marginBottom: 16,
  },
  sectionTitle: {
    color: theme.colors.primary,
    fontSize: 18,
    marginBottom: 8,
  },
  sectionDescription: {
    color: theme.colors.text,
    marginBottom: 16,
  },
  tierOption: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
    paddingVertical: 8,
  },
  tierInfo: {
    flex: 1,
    marginLeft: 8,
  },
  tierHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  tierTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    flex: 1,
  },
  costChip: {
    marginLeft: 8,
  },
  costChipText: {
    fontSize: 12,
  },
  tierDescription: {
    color: theme.colors.text,
    fontSize: 14,
    marginBottom: 8,
    lineHeight: 20,
  },
  previewButton: {
    alignSelf: 'flex-start',
  },
  upgradeNote: {
    fontSize: 12,
    color: theme.colors.accent,
    fontStyle: 'italic',
    marginTop: 4,
  },
  statusCard: {
    marginBottom: 16,
    backgroundColor: theme.colors.surface,
  },
  statusTitle: {
    color: theme.colors.primary,
    fontSize: 18,
    marginBottom: 12,
  },
  statusText: {
    fontSize: 14,
    marginBottom: 4,
    color: theme.colors.text,
  },
  statusLabel: {
    fontWeight: 'bold',
  },
  lastModified: {
    fontSize: 12,
    color: theme.colors.placeholder,
    marginTop: 8,
    fontStyle: 'italic',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
    marginBottom: 32,
  },
  actionButton: {
    flex: 1,
    marginHorizontal: 8,
  },
  errorCard: {
    margin: 16,
  },
  errorTitle: {
    color: theme.colors.error,
  },
  modalContainer: {
    margin: 20,
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    maxHeight: '80%',
  },
  modalContent: {
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    color: theme.colors.primary,
    fontSize: 20,
    flex: 1,
  },
  modalDescription: {
    fontSize: 16,
    marginBottom: 20,
    color: theme.colors.text,
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 16,
    marginBottom: 8,
    color: theme.colors.primary,
  },
  modalListItem: {
    fontSize: 14,
    marginBottom: 4,
    marginLeft: 8,
    color: theme.colors.text,
  },
  modalDivider: {
    marginVertical: 16,
  },
  modalSpecs: {
    marginBottom: 20,
  },
  modalSpecItem: {
    fontSize: 14,
    marginBottom: 4,
    color: theme.colors.text,
  },
  modalSpecLabel: {
    fontWeight: 'bold',
  },
  modalCloseButton: {
    marginTop: 8,
  },
});

export default TelehealthTierSettings;