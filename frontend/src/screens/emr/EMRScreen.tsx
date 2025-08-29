import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Title, Paragraph } from 'react-native-paper';
import { theme } from '../../utils/theme';

const EMRScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Electronic Medical Records</Title>
          <Paragraph>Access your complete medical history</Paragraph>
          <Text style={styles.message}>EMR features will be implemented here including:</Text>
          <Text style={styles.feature}>• Patient records</Text>
          <Text style={styles.feature}>• Lab results</Text>
          <Text style={styles.feature}>• Medications</Text>
          <Text style={styles.feature}>• Appointment history</Text>
          <Text style={styles.feature}>• OpenEMR integration</Text>
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

export default EMRScreen;