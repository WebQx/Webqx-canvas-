import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Title, Paragraph } from 'react-native-paper';
import { theme } from '../../utils/theme';

const SettingsScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Settings</Title>
          <Paragraph>Customize your WebQx experience</Paragraph>
          <Text style={styles.message}>Settings features will be implemented here including:</Text>
          <Text style={styles.feature}>• Profile management</Text>
          <Text style={styles.feature}>• Language preferences</Text>
          <Text style={styles.feature}>• Accessibility options</Text>
          <Text style={styles.feature}>• Notification settings</Text>
          <Text style={styles.feature}>• Privacy controls</Text>
          <Text style={styles.feature}>• Subscription management</Text>
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

export default SettingsScreen;