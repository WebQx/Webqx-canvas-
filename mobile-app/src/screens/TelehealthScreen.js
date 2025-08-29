import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { RTCPeerConnection, RTCView, mediaDevices } from 'react-native-webrtc';
import ApiService from '../services/ApiService';
import TierService from '../services/TierService';

const { width, height } = Dimensions.get('window');

const TelehealthScreen = () => {
  const [isInCall, setIsInCall] = useState(false);
  const [localStream, setLocalStream] = useState(null);
  const [remoteStream, setRemoteStream] = useState(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [userTier, setUserTier] = useState(null);
  const [appointments, setAppointments] = useState([]);
  
  const peerConnection = useRef(null);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);

  useEffect(() => {
    initializeTelehealth();
    loadAppointments();
  }, []);

  const initializeTelehealth = async () => {
    try {
      const tier = await TierService.getUserTier();
      setUserTier(tier);
    } catch (error) {
      console.error('Failed to get user tier:', error);
    }
  };

  const loadAppointments = async () => {
    try {
      const data = await ApiService.getTelehealthAppointments();
      setAppointments(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load appointments');
    }
  };

  const startCall = async (appointmentId) => {
    try {
      if (userTier === 'premium') {
        // Use Zoom SDK for premium users
        await startZoomCall(appointmentId);
      } else {
        // Use WebRTC for free users
        await startWebRTCCall(appointmentId);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to start call');
    }
  };

  const startZoomCall = async (appointmentId) => {
    try {
      const zoomMeeting = await ApiService.createZoomMeeting(appointmentId);
      // In a real implementation, you would integrate with Zoom SDK here
      Alert.alert(
        'Zoom Meeting',
        `Meeting ID: ${zoomMeeting.meetingId}\nPassword: ${zoomMeeting.password}`,
        [
          {
            text: 'Join Meeting',
            onPress: () => {
              // Launch Zoom app or web client
              console.log('Launching Zoom meeting...');
            },
          },
          { text: 'Cancel', style: 'cancel' },
        ]
      );
    } catch (error) {
      throw error;
    }
  };

  const startWebRTCCall = async (appointmentId) => {
    try {
      // Get user media
      const stream = await mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      setLocalStream(stream);

      // Create peer connection
      const configuration = {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          // Add TURN servers for production
        ],
      };
      
      peerConnection.current = new RTCPeerConnection(configuration);

      // Add local stream to peer connection
      stream.getTracks().forEach(track => {
        peerConnection.current.addTrack(track, stream);
      });

      // Handle remote stream
      peerConnection.current.ontrack = (event) => {
        setRemoteStream(event.streams[0]);
      };

      // Handle ICE candidates
      peerConnection.current.onicecandidate = (event) => {
        if (event.candidate) {
          // Send ICE candidate to signaling server
          ApiService.sendIceCandidate(appointmentId, event.candidate);
        }
      };

      // Create offer
      const offer = await peerConnection.current.createOffer();
      await peerConnection.current.setLocalDescription(offer);
      
      // Send offer to signaling server
      await ApiService.sendOffer(appointmentId, offer);
      
      setIsInCall(true);
    } catch (error) {
      throw error;
    }
  };

  const endCall = async () => {
    try {
      if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        setLocalStream(null);
      }
      
      if (peerConnection.current) {
        peerConnection.current.close();
        peerConnection.current = null;
      }
      
      setRemoteStream(null);
      setIsInCall(false);
      setIsMuted(false);
      setIsVideoOff(false);
    } catch (error) {
      console.error('Error ending call:', error);
    }
  };

  const toggleMute = () => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMuted(!audioTrack.enabled);
      }
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoOff(!videoTrack.enabled);
      }
    }
  };

  const renderAppointment = (appointment) => (
    <View key={appointment.id} style={styles.appointmentCard}>
      <View style={styles.appointmentHeader}>
        <Icon name="video-call" size={24} color="#2563EB" />
        <Text style={styles.appointmentTitle}>{appointment.title}</Text>
      </View>
      <Text style={styles.appointmentProvider}>
        With: {appointment.provider}
      </Text>
      <Text style={styles.appointmentDate}>
        {appointment.date} at {appointment.time}
      </Text>
      <Text style={styles.appointmentTier}>
        Type: {userTier === 'premium' ? 'Zoom HD Video' : 'WebRTC Video'}
      </Text>
      
      <TouchableOpacity
        style={styles.joinButton}
        onPress={() => startCall(appointment.id)}
      >
        <Icon name="video-call" size={20} color="#FFFFFF" />
        <Text style={styles.joinButtonText}>Join Call</Text>
      </TouchableOpacity>
    </View>
  );

  if (isInCall) {
    return (
      <View style={styles.callContainer}>
        {remoteStream && (
          <RTCView
            style={styles.remoteVideo}
            streamURL={remoteStream.toURL()}
            objectFit="cover"
          />
        )}
        
        {localStream && !isVideoOff && (
          <RTCView
            style={styles.localVideo}
            streamURL={localStream.toURL()}
            objectFit="cover"
            mirror={true}
          />
        )}

        <View style={styles.callControls}>
          <TouchableOpacity
            style={[styles.controlButton, isMuted && styles.activeControlButton]}
            onPress={toggleMute}
          >
            <Icon 
              name={isMuted ? 'mic-off' : 'mic'} 
              size={24} 
              color={isMuted ? '#FFFFFF' : '#6B7280'} 
            />
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, isVideoOff && styles.activeControlButton]}
            onPress={toggleVideo}
          >
            <Icon 
              name={isVideoOff ? 'videocam-off' : 'videocam'} 
              size={24} 
              color={isVideoOff ? '#FFFFFF' : '#6B7280'} 
            />
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, styles.endCallButton]}
            onPress={endCall}
          >
            <Icon name="call-end" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Video Consultations</Text>
        <View style={styles.tierBadge}>
          <Text style={styles.tierText}>
            {userTier === 'premium' ? 'Premium (Zoom HD)' : 'Standard (WebRTC)'}
          </Text>
        </View>
      </View>

      <View style={styles.content}>
        {appointments.length === 0 ? (
          <View style={styles.emptyState}>
            <Icon name="video-call" size={64} color="#D1D5DB" />
            <Text style={styles.emptyTitle}>No upcoming appointments</Text>
            <Text style={styles.emptySubtitle}>
              Schedule a video consultation with your care team
            </Text>
          </View>
        ) : (
          appointments.map(renderAppointment)
        )}
      </View>
    </View>
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
    marginBottom: 8,
  },
  tierBadge: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignSelf: 'flex-start',
  },
  tierText: {
    fontSize: 12,
    color: '#2563EB',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  appointmentCard: {
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
  appointmentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  appointmentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginLeft: 8,
  },
  appointmentProvider: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 4,
  },
  appointmentDate: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  appointmentTier: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 16,
  },
  joinButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2563EB',
    paddingVertical: 12,
    borderRadius: 8,
  },
  joinButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
  },
  callContainer: {
    flex: 1,
    backgroundColor: '#000000',
  },
  remoteVideo: {
    flex: 1,
    width: width,
    height: height,
  },
  localVideo: {
    position: 'absolute',
    top: 50,
    right: 20,
    width: 120,
    height: 160,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  callControls: {
    position: 'absolute',
    bottom: 50,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  controlButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 8,
  },
  activeControlButton: {
    backgroundColor: '#EF4444',
  },
  endCallButton: {
    backgroundColor: '#EF4444',
  },
});

export default TelehealthScreen;