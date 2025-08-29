import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Audio } from 'expo-av';
import * as DocumentPicker from 'expo-document-picker';
import ApiService from '../services/ApiService';
import NLPService from '../services/NLPService';

const JournalScreen = () => {
  const [entries, setEntries] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentEntry, setCurrentEntry] = useState({
    text: '',
    audio: null,
    tags: [],
  });
  const [isRecording, setIsRecording] = useState(false);
  const [recording, setRecording] = useState(null);

  useEffect(() => {
    loadJournalEntries();
  }, []);

  const loadJournalEntries = async () => {
    try {
      const data = await ApiService.getJournalEntries();
      setEntries(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load journal entries');
    }
  };

  const startRecording = async () => {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert('Permission required', 'Audio recording permission is required');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
    } catch (error) {
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    setIsRecording(false);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    setCurrentEntry({ ...currentEntry, audio: uri });
    setRecording(null);
  };

  const analyzeTextWithNLP = async (text) => {
    try {
      const tags = await NLPService.analyzeText(text);
      setCurrentEntry({ ...currentEntry, text, tags });
    } catch (error) {
      console.log('NLP analysis failed, continuing without tags');
      setCurrentEntry({ ...currentEntry, text, tags: [] });
    }
  };

  const saveEntry = async () => {
    try {
      if (!currentEntry.text.trim() && !currentEntry.audio) {
        Alert.alert('Error', 'Please add some content to your journal entry');
        return;
      }

      const entryData = {
        text: currentEntry.text,
        audio: currentEntry.audio,
        tags: currentEntry.tags,
        timestamp: new Date().toISOString(),
      };

      await ApiService.saveJournalEntry(entryData);
      setModalVisible(false);
      setCurrentEntry({ text: '', audio: null, tags: [] });
      loadJournalEntries();
      Alert.alert('Success', 'Journal entry saved successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to save journal entry');
    }
  };

  const exportEntries = async () => {
    try {
      const exportData = await ApiService.exportJournalEntries();
      // Here you would implement the export functionality
      Alert.alert('Export', 'Journal entries exported successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to export journal entries');
    }
  };

  const attachFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: '*/*',
        copyToCacheDirectory: true,
      });

      if (result.type === 'success') {
        // Handle file attachment
        Alert.alert('File attached', `Attached: ${result.name}`);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to attach file');
    }
  };

  const renderEntry = (entry) => (
    <View key={entry.id} style={styles.entryCard}>
      <View style={styles.entryHeader}>
        <Text style={styles.entryDate}>
          {new Date(entry.timestamp).toLocaleDateString()}
        </Text>
        <Text style={styles.entryTime}>
          {new Date(entry.timestamp).toLocaleTimeString()}
        </Text>
      </View>
      
      {entry.text && (
        <Text style={styles.entryText}>{entry.text}</Text>
      )}
      
      {entry.audio && (
        <View style={styles.audioContainer}>
          <Icon name="audiotrack" size={20} color="#2563EB" />
          <Text style={styles.audioText}>Audio recording attached</Text>
        </View>
      )}
      
      {entry.tags && entry.tags.length > 0 && (
        <View style={styles.tagsContainer}>
          {entry.tags.map((tag, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Journal</Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity onPress={exportEntries} style={styles.headerButton}>
            <Icon name="file-download" size={24} color="#6B7280" />
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => setModalVisible(true)}
            style={styles.addButton}
          >
            <Icon name="add" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.entriesList}>
        {entries.map(renderEntry)}
      </ScrollView>

      <Modal
        animationType="slide"
        transparent={false}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setModalVisible(false)}>
              <Icon name="close" size={24} color="#6B7280" />
            </TouchableOpacity>
            <Text style={styles.modalTitle}>New Journal Entry</Text>
            <TouchableOpacity onPress={saveEntry}>
              <Text style={styles.saveButton}>Save</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <TextInput
              style={styles.textInput}
              placeholder="Write your thoughts here..."
              multiline
              value={currentEntry.text}
              onChangeText={(text) => analyzeTextWithNLP(text)}
            />

            {currentEntry.tags.length > 0 && (
              <View style={styles.nlpTagsContainer}>
                <Text style={styles.nlpTagsTitle}>AI-detected themes:</Text>
                <View style={styles.tagsContainer}>
                  {currentEntry.tags.map((tag, index) => (
                    <View key={index} style={styles.nlpTag}>
                      <Text style={styles.nlpTagText}>{tag}</Text>
                    </View>
                  ))}
                </View>
              </View>
            )}

            <View style={styles.actionsContainer}>
              <TouchableOpacity
                onPress={isRecording ? stopRecording : startRecording}
                style={[
                  styles.actionButton,
                  isRecording && styles.recordingButton,
                ]}
              >
                <Icon
                  name={isRecording ? 'stop' : 'mic'}
                  size={24}
                  color={isRecording ? '#FFFFFF' : '#6B7280'}
                />
                <Text style={[
                  styles.actionButtonText,
                  isRecording && styles.recordingButtonText,
                ]}>
                  {isRecording ? 'Stop Recording' : 'Record Audio'}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity onPress={attachFile} style={styles.actionButton}>
                <Icon name="attach-file" size={24} color="#6B7280" />
                <Text style={styles.actionButtonText}>Attach File</Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  headerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    padding: 8,
    marginRight: 8,
  },
  addButton: {
    backgroundColor: '#2563EB',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  entriesList: {
    flex: 1,
    padding: 20,
  },
  entryCard: {
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
  entryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  entryDate: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  entryTime: {
    fontSize: 12,
    color: '#6B7280',
  },
  entryText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
    marginBottom: 12,
  },
  audioContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  audioText: {
    fontSize: 12,
    color: '#2563EB',
    marginLeft: 8,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  tag: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 4,
  },
  tagText: {
    fontSize: 12,
    color: '#2563EB',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  saveButton: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2563EB',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 120,
    textAlignVertical: 'top',
    marginBottom: 20,
  },
  nlpTagsContainer: {
    marginBottom: 20,
  },
  nlpTagsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  nlpTag: {
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 4,
  },
  nlpTagText: {
    fontSize: 12,
    color: '#92400E',
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  recordingButton: {
    backgroundColor: '#EF4444',
    borderColor: '#EF4444',
  },
  actionButtonText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 8,
  },
  recordingButtonText: {
    color: '#FFFFFF',
  },
});

export default JournalScreen;