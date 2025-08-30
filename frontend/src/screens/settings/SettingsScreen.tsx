import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { 
  Text, 
  Card, 
  Title, 
  Paragraph, 
  List, 
  Divider,
  Button,
  IconButton 
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { theme } from '../../utils/theme';
import { useAuth } from '../../hooks/useAuth';
import { telehealthAPI } from '../../services/telehealthAPI';

const SettingsScreen: React.FC = () => {
  const navigation = useNavigation();
  const { user } = useAuth();
  const [userPermissions, setUserPermissions] = useState<any>(null);

  useEffect(() => {
    loadUserPermissions();
  }, []);

  const loadUserPermissions = async () => {
    try {
      const response = await telehealthAPI.getUserPermissions();
      setUserPermissions(response.data);
    } catch (error) {
      console.error('Failed to load user permissions:', error);
    }
  };

  const navigateToTelehealthSettings = () => {
    // @ts-ignore - Navigation typing issue
    navigation.navigate('TelehealthTierSettings');
  };

  const canAccessTelehealthSettings = () => {
    return user?.user_type === 'admin' || 
           user?.user_type === 'care_team' || 
           userPermissions?.can_view_settings;
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.headerCard}>
        <Card.Content>
          <Title style={styles.title}>Settings</Title>
          <Paragraph>Customize your WebQx Healthcare experience</Paragraph>
        </Card.Content>
      </Card>

      {/* Clinic Preferences Section */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>🏥 Clinic Preferences</Title>
          
          {canAccessTelehealthSettings() && (
            <List.Item
              title="Telehealth Tier Settings"
              description="Configure WebRTC vs Zoom SDK preferences"
              left={props => <List.Icon {...props} icon="video" />}
              right={props => <List.Icon {...props} icon="chevron-right" />}
              onPress={navigateToTelehealthSettings}
              style={styles.listItem}
            />
          )}
          
          <List.Item
            title="Language Preferences"
            description="Set default language for clinic interface"
            left={props => <List.Icon {...props} icon="translate" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // TODO: Navigate to language settings
              console.log('Navigate to language settings');
            }}
            style={styles.listItem}
          />
          
          <List.Item
            title="Accessibility Options"
            description="Configure accessibility and display options"
            left={props => <List.Icon {...props} icon="human-accessible" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // TODO: Navigate to accessibility settings
              console.log('Navigate to accessibility settings');
            }}
            style={styles.listItem}
          />
        </Card.Content>
      </Card>

      {/* User Preferences Section */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>👤 User Preferences</Title>
          
          <List.Item
            title="Profile Management"
            description="Update your personal information and credentials"
            left={props => <List.Icon {...props} icon="account-edit" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // TODO: Navigate to profile settings
              console.log('Navigate to profile settings');
            }}
            style={styles.listItem}
          />
          
          <List.Item
            title="Notification Settings"
            description="Manage your notification preferences"
            left={props => <List.Icon {...props} icon="bell-outline" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // TODO: Navigate to notification settings
              console.log('Navigate to notification settings');
            }}
            style={styles.listItem}
          />
          
          <List.Item
            title="Privacy Controls"
            description="Manage your privacy and data sharing preferences"
            left={props => <List.Icon {...props} icon="shield-account" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // TODO: Navigate to privacy settings
              console.log('Navigate to privacy settings');
            }}
            style={styles.listItem}
          />
        </Card.Content>
      </Card>

      {/* Subscription and Account Section */}
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>💼 Account & Subscription</Title>
          
          <List.Item
            title="Subscription Management"
            description={`Current tier: ${user?.subscription_tier || 'Free'}`}
            left={props => <List.Icon {...props} icon="credit-card-outline" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // TODO: Navigate to subscription management
              console.log('Navigate to subscription management');
            }}
            style={styles.listItem}
          />
          
          <List.Item
            title="Billing Information"
            description="Manage your billing details and payment methods"
            left={props => <List.Icon {...props} icon="receipt" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // TODO: Navigate to billing settings
              console.log('Navigate to billing settings');
            }}
            style={styles.listItem}
          />
        </Card.Content>
      </Card>

      {/* System Information */}
      <Card style={styles.infoCard}>
        <Card.Content>
          <Title style={styles.infoTitle}>📱 System Information</Title>
          <Text style={styles.infoText}>
            <Text style={styles.infoLabel}>User Type: </Text>
            {user?.user_type || 'Unknown'}
          </Text>
          <Text style={styles.infoText}>
            <Text style={styles.infoLabel}>Subscription: </Text>
            {user?.subscription_tier || 'Free'}
          </Text>
          <Text style={styles.infoText}>
            <Text style={styles.infoLabel}>Zoom Access: </Text>
            {userPermissions?.can_use_zoom ? 'Available' : 'Not Available'}
          </Text>
          <Text style={styles.infoText}>
            <Text style={styles.infoLabel}>App Version: </Text>
            1.0.0
          </Text>
        </Card.Content>
      </Card>

      <View style={styles.bottomPadding} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: 16,
  },
  headerCard: {
    marginBottom: 16,
  },
  title: {
    marginBottom: 8,
    color: theme.colors.primary,
    fontSize: 24,
    fontWeight: 'bold',
  },
  sectionCard: {
    marginBottom: 16,
  },
  sectionTitle: {
    color: theme.colors.primary,
    fontSize: 18,
    marginBottom: 8,
  },
  listItem: {
    marginVertical: 2,
  },
  infoCard: {
    backgroundColor: theme.colors.surface,
    marginBottom: 16,
  },
  infoTitle: {
    color: theme.colors.primary,
    fontSize: 16,
    marginBottom: 12,
  },
  infoText: {
    fontSize: 14,
    marginBottom: 4,
    color: theme.colors.text,
  },
  infoLabel: {
    fontWeight: 'bold',
  },
  bottomPadding: {
    height: 32,
  },
});

export default SettingsScreen;