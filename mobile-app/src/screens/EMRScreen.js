import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import ApiService from '../services/ApiService';

const EMRScreen = () => {
  const [emrData, setEmrData] = useState({
    labs: [],
    medications: [],
    appointments: [],
    carePlans: [],
  });
  const [activeTab, setActiveTab] = useState('labs');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadEMRData();
  }, []);

  const loadEMRData = async () => {
    try {
      setRefreshing(true);
      const data = await ApiService.getEMRData();
      setEmrData(data);
    } catch (error) {
      console.error('Failed to load EMR data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    loadEMRData();
  };

  const renderLabResult = (lab) => (
    <View key={lab.id} style={styles.card}>
      <View style={styles.cardHeader}>
        <Icon name="biotech" size={24} color="#2563EB" />
        <Text style={styles.cardTitle}>{lab.name}</Text>
      </View>
      <View style={styles.labResult}>
        <Text style={styles.labValue}>{lab.value} {lab.unit}</Text>
        <Text style={[
          styles.labStatus,
          lab.status === 'normal' ? styles.normalStatus : styles.abnormalStatus
        ]}>
          {lab.status}
        </Text>
      </View>
      <Text style={styles.cardDate}>Date: {lab.date}</Text>
      <Text style={styles.cardSubtext}>Reference: {lab.reference}</Text>
    </View>
  );

  const renderMedication = (medication) => (
    <View key={medication.id} style={styles.card}>
      <View style={styles.cardHeader}>
        <Icon name="medication" size={24} color="#10B981" />
        <Text style={styles.cardTitle}>{medication.name}</Text>
      </View>
      <Text style={styles.medicationDosage}>{medication.dosage}</Text>
      <Text style={styles.cardSubtext}>
        Frequency: {medication.frequency}
      </Text>
      <Text style={styles.cardSubtext}>
        Prescribed by: {medication.prescriber}
      </Text>
      <Text style={styles.cardDate}>Started: {medication.startDate}</Text>
    </View>
  );

  const renderAppointment = (appointment) => (
    <View key={appointment.id} style={styles.card}>
      <View style={styles.cardHeader}>
        <Icon name="event" size={24} color="#8B5CF6" />
        <Text style={styles.cardTitle}>{appointment.type}</Text>
      </View>
      <Text style={styles.appointmentProvider}>
        With: {appointment.provider}
      </Text>
      <Text style={styles.cardDate}>
        {appointment.date} at {appointment.time}
      </Text>
      <Text style={styles.cardSubtext}>
        Location: {appointment.location}
      </Text>
      {appointment.notes && (
        <Text style={styles.appointmentNotes}>
          Notes: {appointment.notes}
        </Text>
      )}
    </View>
  );

  const renderCarePlan = (plan) => (
    <View key={plan.id} style={styles.card}>
      <View style={styles.cardHeader}>
        <Icon name="assignment" size={24} color="#F59E0B" />
        <Text style={styles.cardTitle}>{plan.title}</Text>
      </View>
      <Text style={styles.carePlanDescription}>{plan.description}</Text>
      <Text style={styles.cardSubtext}>
        Created by: {plan.createdBy}
      </Text>
      <Text style={styles.cardDate}>Date: {plan.date}</Text>
      
      {plan.goals && plan.goals.length > 0 && (
        <View style={styles.goalsContainer}>
          <Text style={styles.goalsTitle}>Goals:</Text>
          {plan.goals.map((goal, index) => (
            <View key={index} style={styles.goalItem}>
              <Icon 
                name={goal.completed ? 'check-circle' : 'radio-button-unchecked'} 
                size={16} 
                color={goal.completed ? '#10B981' : '#6B7280'} 
              />
              <Text style={[
                styles.goalText,
                goal.completed && styles.completedGoal
              ]}>
                {goal.text}
              </Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'labs':
        return emrData.labs.map(renderLabResult);
      case 'medications':
        return emrData.medications.map(renderMedication);
      case 'appointments':
        return emrData.appointments.map(renderAppointment);
      case 'carePlans':
        return emrData.carePlans.map(renderCarePlan);
      default:
        return null;
    }
  };

  const tabs = [
    { key: 'labs', title: 'Lab Results', icon: 'biotech' },
    { key: 'medications', title: 'Medications', icon: 'medication' },
    { key: 'appointments', title: 'Appointments', icon: 'event' },
    { key: 'carePlans', title: 'Care Plans', icon: 'assignment' },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.tabContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {tabs.map((tab) => (
            <TouchableOpacity
              key={tab.key}
              style={[
                styles.tab,
                activeTab === tab.key && styles.activeTab,
              ]}
              onPress={() => setActiveTab(tab.key)}
            >
              <Icon 
                name={tab.icon} 
                size={20} 
                color={activeTab === tab.key ? '#FFFFFF' : '#6B7280'} 
              />
              <Text style={[
                styles.tabText,
                activeTab === tab.key && styles.activeTabText,
              ]}>
                {tab.title}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {renderTabContent()}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  tabContainer: {
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    paddingVertical: 12,
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginHorizontal: 4,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
  },
  activeTab: {
    backgroundColor: '#2563EB',
  },
  tabText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 6,
  },
  activeTabText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
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
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginLeft: 8,
  },
  cardDate: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8,
  },
  cardSubtext: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  labResult: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  labValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  labStatus: {
    fontSize: 14,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  normalStatus: {
    backgroundColor: '#D1FAE5',
    color: '#065F46',
  },
  abnormalStatus: {
    backgroundColor: '#FEE2E2',
    color: '#991B1B',
  },
  medicationDosage: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  appointmentProvider: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 8,
  },
  appointmentNotes: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8,
    fontStyle: 'italic',
  },
  carePlanDescription: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 8,
    lineHeight: 20,
  },
  goalsContainer: {
    marginTop: 12,
  },
  goalsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  goalItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  goalText: {
    fontSize: 14,
    color: '#374151',
    marginLeft: 8,
    flex: 1,
  },
  completedGoal: {
    textDecorationLine: 'line-through',
    color: '#6B7280',
  },
});

export default EMRScreen;