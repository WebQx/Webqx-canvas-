import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import ApiService from '../services/ApiService';

const HomeScreen = () => {
  const [dashboardData, setDashboardData] = useState({
    dailyCheckIns: [],
    reminders: [],
    careTeamUpdates: [],
    upcomingAppointments: [],
  });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setRefreshing(true);
      const data = await ApiService.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    loadDashboardData();
  };

  const handleCheckInComplete = async (checkInId) => {
    try {
      await ApiService.completeCheckIn(checkInId);
      loadDashboardData(); // Refresh data
      Alert.alert('Success', 'Check-in completed successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to complete check-in');
    }
  };

  const renderCheckInCard = (checkIn) => (
    <TouchableOpacity
      key={checkIn.id}
      style={styles.card}
      onPress={() => handleCheckInComplete(checkIn.id)}
    >
      <View style={styles.cardHeader}>
        <Icon name="assignment" size={24} color="#2563EB" />
        <Text style={styles.cardTitle}>Daily Check-in</Text>
      </View>
      <Text style={styles.cardContent}>{checkIn.title}</Text>
      <Text style={styles.cardTime}>Due: {checkIn.dueTime}</Text>
    </TouchableOpacity>
  );

  const renderReminderCard = (reminder) => (
    <TouchableOpacity key={reminder.id} style={styles.card}>
      <View style={styles.cardHeader}>
        <Icon name="notifications" size={24} color="#F59E0B" />
        <Text style={styles.cardTitle}>Reminder</Text>
      </View>
      <Text style={styles.cardContent}>{reminder.message}</Text>
      <Text style={styles.cardTime}>{reminder.time}</Text>
    </TouchableOpacity>
  );

  const renderUpdateCard = (update) => (
    <TouchableOpacity key={update.id} style={styles.card}>
      <View style={styles.cardHeader}>
        <Icon name="people" size={24} color="#10B981" />
        <Text style={styles.cardTitle}>Care Team Update</Text>
      </View>
      <Text style={styles.cardContent}>{update.message}</Text>
      <Text style={styles.cardSubtext}>From: {update.from}</Text>
      <Text style={styles.cardTime}>{update.timestamp}</Text>
    </TouchableOpacity>
  );

  const renderAppointmentCard = (appointment) => (
    <TouchableOpacity key={appointment.id} style={styles.card}>
      <View style={styles.cardHeader}>
        <Icon name="event" size={24} color="#8B5CF6" />
        <Text style={styles.cardTitle}>Upcoming Appointment</Text>
      </View>
      <Text style={styles.cardContent}>{appointment.title}</Text>
      <Text style={styles.cardSubtext}>
        With: {appointment.provider}
      </Text>
      <Text style={styles.cardTime}>{appointment.dateTime}</Text>
    </TouchableOpacity>
  );

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Good Morning!</Text>
        <Text style={styles.headerSubtitle}>Here's your health overview</Text>
      </View>

      {dashboardData.dailyCheckIns.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Daily Check-ins</Text>
          {dashboardData.dailyCheckIns.map(renderCheckInCard)}
        </View>
      )}

      {dashboardData.reminders.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Reminders</Text>
          {dashboardData.reminders.map(renderReminderCard)}
        </View>
      )}

      {dashboardData.upcomingAppointments.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Upcoming Appointments</Text>
          {dashboardData.upcomingAppointments.map(renderAppointmentCard)}
        </View>
      )}

      {dashboardData.careTeamUpdates.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Care Team Updates</Text>
          {dashboardData.careTeamUpdates.map(renderUpdateCard)}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#6B7280',
  },
  section: {
    marginTop: 20,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginLeft: 8,
  },
  cardContent: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 4,
  },
  cardSubtext: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  cardTime: {
    fontSize: 12,
    color: '#9CA3AF',
  },
});

export default HomeScreen;