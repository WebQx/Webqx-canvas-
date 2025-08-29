import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Title } from 'react-native-paper';
import { theme } from '../../utils/theme';

const RegisterScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Create Account</Title>
          <Text style={styles.subtitle}>Join WebQx Healthcare Platform</Text>
          <Text style={styles.message}>Registration functionality will be implemented here</Text>
        </Card.Content>
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
    backgroundColor: theme.colors.background,
  },
  card: {
    padding: 16,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    color: theme.colors.primary,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 16,
    color: theme.colors.text,
  },
  message: {
    textAlign: 'center',
    color: theme.colors.disabled,
  },
});

export default RegisterScreen;