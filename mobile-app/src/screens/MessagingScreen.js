import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  Modal,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import ApiService from '../services/ApiService';

const MessagingScreen = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await ApiService.getConversations();
      setConversations(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load conversations');
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      const data = await ApiService.getMessages(conversationId);
      setMessages(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load messages');
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      const messageData = {
        conversationId: selectedConversation.id,
        text: newMessage,
        timestamp: new Date().toISOString(),
      };

      await ApiService.sendMessage(messageData);
      setNewMessage('');
      loadMessages(selectedConversation.id);
    } catch (error) {
      Alert.alert('Error', 'Failed to send message');
    }
  };

  const renderConversation = ({ item }) => (
    <TouchableOpacity
      style={styles.conversationItem}
      onPress={() => {
        setSelectedConversation(item);
        setModalVisible(true);
        loadMessages(item.id);
      }}
    >
      <View style={styles.avatar}>
        <Icon name="person" size={24} color="#6B7280" />
      </View>
      <View style={styles.conversationContent}>
        <Text style={styles.conversationName}>{item.participantName}</Text>
        <Text style={styles.conversationRole}>{item.participantRole}</Text>
        <Text style={styles.lastMessage} numberOfLines={1}>
          {item.lastMessage}
        </Text>
      </View>
      <View style={styles.conversationMeta}>
        <Text style={styles.timestamp}>{item.lastMessageTime}</Text>
        {item.unreadCount > 0 && (
          <View style={styles.unreadBadge}>
            <Text style={styles.unreadCount}>{item.unreadCount}</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );

  const renderMessage = ({ item }) => (
    <View style={[
      styles.messageContainer,
      item.isFromUser ? styles.userMessage : styles.otherMessage,
    ]}>
      <Text style={[
        styles.messageText,
        item.isFromUser ? styles.userMessageText : styles.otherMessageText,
      ]}>
        {item.text}
      </Text>
      <Text style={[
        styles.messageTime,
        item.isFromUser ? styles.userMessageTime : styles.otherMessageTime,
      ]}>
        {new Date(item.timestamp).toLocaleTimeString()}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Messages</Text>
        <TouchableOpacity style={styles.headerButton}>
          <Icon name="add" size={24} color="#2563EB" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={conversations}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderConversation}
        style={styles.conversationsList}
      />

      <Modal
        animationType="slide"
        transparent={false}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.chatContainer}>
          <View style={styles.chatHeader}>
            <TouchableOpacity onPress={() => setModalVisible(false)}>
              <Icon name="arrow-back" size={24} color="#6B7280" />
            </TouchableOpacity>
            <View style={styles.chatHeaderInfo}>
              <Text style={styles.chatHeaderName}>
                {selectedConversation?.participantName}
              </Text>
              <Text style={styles.chatHeaderRole}>
                {selectedConversation?.participantRole}
              </Text>
            </View>
            <TouchableOpacity>
              <Icon name="videocam" size={24} color="#2563EB" />
            </TouchableOpacity>
          </View>

          <FlatList
            data={messages}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderMessage}
            style={styles.messagesList}
            inverted
          />

          <View style={styles.messageInput}>
            <TextInput
              style={styles.textInput}
              placeholder="Type a message..."
              value={newMessage}
              onChangeText={setNewMessage}
              multiline
            />
            <TouchableOpacity onPress={sendMessage} style={styles.sendButton}>
              <Icon name="send" size={24} color="#2563EB" />
            </TouchableOpacity>
          </View>
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
  headerButton: {
    padding: 8,
  },
  conversationsList: {
    flex: 1,
  },
  conversationItem: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  conversationContent: {
    flex: 1,
  },
  conversationName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  conversationRole: {
    fontSize: 12,
    color: '#2563EB',
    marginBottom: 4,
  },
  lastMessage: {
    fontSize: 14,
    color: '#6B7280',
  },
  conversationMeta: {
    alignItems: 'flex-end',
  },
  timestamp: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 4,
  },
  unreadBadge: {
    backgroundColor: '#EF4444',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  unreadCount: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  chatContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  chatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  chatHeaderInfo: {
    flex: 1,
    marginLeft: 16,
  },
  chatHeaderName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  chatHeaderRole: {
    fontSize: 14,
    color: '#2563EB',
  },
  messagesList: {
    flex: 1,
    padding: 16,
  },
  messageContainer: {
    marginBottom: 16,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
  },
  otherMessage: {
    alignSelf: 'flex-start',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 20,
    marginBottom: 4,
  },
  userMessageText: {
    backgroundColor: '#2563EB',
    color: '#FFFFFF',
    padding: 12,
    borderRadius: 18,
    borderBottomRightRadius: 4,
  },
  otherMessageText: {
    backgroundColor: '#F3F4F6',
    color: '#1F2937',
    padding: 12,
    borderRadius: 18,
    borderBottomLeftRadius: 4,
  },
  messageTime: {
    fontSize: 12,
    marginTop: 4,
  },
  userMessageTime: {
    color: '#9CA3AF',
    textAlign: 'right',
  },
  otherMessageTime: {
    color: '#9CA3AF',
    textAlign: 'left',
  },
  messageInput: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 8,
    maxHeight: 100,
  },
  sendButton: {
    padding: 8,
  },
});

export default MessagingScreen;