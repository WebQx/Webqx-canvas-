import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Title, Paragraph } from 'react-native-paper';
import { theme } from '../../utils/theme';

const MessagingScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Secure Messaging</Title>
          <Paragraph>Communicate securely with your care team</Paragraph>
          <Text style={styles.message}>Messaging features will be implemented here including:</Text>
          <Text style={styles.feature}>• Secure messaging</Text>
          <Text style={styles.feature}>• File attachments</Text>
          <Text style={styles.feature}>• Message templates</Text>
          <Text style={styles.feature}>• Priority levels</Text>
          <Text style={styles.feature}>• Notification settings</Text>
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

export default MessagingScreen;