import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Title, Paragraph } from 'react-native-paper';
import { theme } from '../../utils/theme';

const TelehealthScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Telehealth</Title>
          <Paragraph>Connect with your healthcare providers remotely</Paragraph>
          <Text style={styles.message}>Telehealth features will be implemented here including:</Text>
          <Text style={styles.feature}>• Video consultations</Text>
          <Text style={styles.feature}>• WebRTC for free users</Text>
          <Text style={styles.feature}>• Zoom SDK for premium users</Text>
          <Text style={styles.feature}>• Device testing</Text>
          <Text style={styles.feature}>• Session recordings</Text>
          <Text style={styles.feature}>• Waiting rooms</Text>
        </Card.Content>
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: theme.colors.surface,
  },
  card: {
    padding: 16,
  },
  title: {
    marginBottom: 8,
    color: theme.colors.primary,
  },
  message: {
    marginTop: 16,
    marginBottom: 8,
    color: theme.colors.text,
  },
  feature: {
    marginLeft: 8,
    marginBottom: 4,
    color: theme.colors.text,
  },
});

export default TelehealthScreen;