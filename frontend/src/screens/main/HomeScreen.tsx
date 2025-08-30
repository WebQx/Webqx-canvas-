import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Title, Paragraph, Button } from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../utils/theme';

const HomeScreen: React.FC = () => {
  const quickActions = [
    { title: 'New Journal Entry', icon: 'journal', color: theme.colors.primary },
    { title: 'Schedule Appointment', icon: 'calendar', color: theme.colors.accent },
    { title: 'Start Video Call', icon: 'videocam', color: theme.colors.medical.urgent },
    { title: 'View Lab Results', icon: 'flask', color: theme.colors.medical.info },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.title}>Welcome to WebQx</Title>
        <Paragraph style={styles.subtitle}>Your healthcare dashboard</Paragraph>
      </View>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Quick Actions</Title>
          <View style={styles.actionsGrid}>
            {quickActions.map((action, index) => (
              <Button
                key={index}
                mode="outlined"
                style={[styles.actionButton, { borderColor: action.color }]}
                labelStyle={{ color: action.color }}
                icon={({ size }) => (
                  <Ionicons 
                    name={action.icon as any} 
                    size={size} 
                    color={action.color} 
                  />
                )}
              >
                {action.title}
              </Button>
            ))}
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Recent Activity</Title>
          <Paragraph>Your recent healthcare activities will appear here</Paragraph>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Upcoming Appointments</Title>
          <Paragraph>Your scheduled appointments will be displayed here</Paragraph>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.surface,
  },
  header: {
    padding: 20,
    backgroundColor: theme.colors.primary,
  },
  title: {
    color: 'white',
    fontSize: 24,
  },
  subtitle: {
    color: 'white',
    opacity: 0.8,
  },
  card: {
    margin: 16,
  },
  actionsGrid: {
    marginTop: 16,
  },
  actionButton: {
    marginBottom: 12,
  },
});

export default HomeScreen;