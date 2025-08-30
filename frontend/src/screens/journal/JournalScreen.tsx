import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Title, Paragraph } from 'react-native-paper';
import { theme } from '../../utils/theme';

const JournalScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Health Journal</Title>
          <Paragraph>Track your daily health, mood, and symptoms</Paragraph>
          <Text style={styles.message}>Journal features will be implemented here including:</Text>
          <Text style={styles.feature}>• Text and voice entries</Text>
          <Text style={styles.feature}>• Mood tracking</Text>
          <Text style={styles.feature}>• Symptom logging</Text>
          <Text style={styles.feature}>• NLP analysis</Text>
          <Text style={styles.feature}>• Export functionality</Text>
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

export default JournalScreen;