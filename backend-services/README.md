# Backend Services

This directory contains the backend services for the WebQx Healthcare Platform.

## Services Overview

### 1. OpenEMR Integration (`openemr-integration/`)
- **Purpose**: FHIR/REST API integration with OpenEMR
- **Technology**: Python FastAPI + FHIR Client
- **Features**:
  - Patient record synchronization
  - Appointment management
  - Clinical notes access
  - Lab results integration
  - Medication reconciliation

### 2. Journaling Database (`journaling-db/`)
- **Purpose**: Store and analyze patient journal entries
- **Technology**: PostgreSQL + NLP Processing
- **Features**:
  - Text and audio journal storage
  - NLP tagging and sentiment analysis
  - Symptom tracking and trends
  - Export functionality
  - Search and filtering

### 3. Telehealth Service (`telehealth/`)
- **Purpose**: Video consultation infrastructure
- **Technology**: WebRTC + Zoom SDK
- **Features**:
  - WebRTC signaling server for free tier
  - Zoom SDK integration for premium tier
  - Call recording and transcription
  - Appointment scheduling
  - Session analytics

### 4. Notification Service (`notifications/`)
- **Purpose**: Multi-channel notification delivery
- **Technology**: Firebase + Twilio + Email
- **Features**:
  - Push notifications (Firebase)
  - SMS notifications (Twilio)
  - Email notifications
  - Notification preferences
  - Delivery tracking

### 5. Analytics Engine (`analytics/`)
- **Purpose**: Health data analytics and insights
- **Technology**: Python + Pandas + Scikit-learn
- **Features**:
  - App usage analytics
  - User engagement metrics
  - Symptom trend analysis
  - Health insights generation
  - Reporting dashboard

## Architecture

```
Mobile App (React Native)
          ↓
API Gateway (Django REST)
          ↓
┌─────────────────────────────────────────┐
│              Backend Services           │
├─────────────┬─────────────┬─────────────┤
│  OpenEMR    │ Journaling  │ Telehealth  │
│ Integration │     DB      │   Service   │
├─────────────┼─────────────┼─────────────┤
│Notification │ Analytics   │             │
│   Service   │   Engine    │             │
└─────────────┴─────────────┴─────────────┘
```

## Database Schema

### Core Tables
- `users` - User accounts and profiles
- `journal_entries` - Patient journal data
- `appointments` - Scheduled appointments
- `notifications` - Notification queue
- `analytics_events` - Usage tracking
- `sync_queue` - Offline synchronization

### Integration Tables
- `emr_patients` - OpenEMR patient mapping
- `fhir_resources` - FHIR resource cache
- `telehealth_sessions` - Video call records
- `nlp_analysis` - Journal text analysis results

## Security & Compliance

- **HIPAA Compliance**: All services implement HIPAA safeguards
- **Data Encryption**: Encryption at rest and in transit
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete audit trail
- **Data Backup**: Automated backups and disaster recovery

## Deployment

Each service can be deployed independently using Docker containers:

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Scale specific services
docker-compose up -d --scale analytics=3
```

## API Documentation

- OpenEMR Integration: `http://localhost:8001/docs`
- Journaling DB: `http://localhost:8002/docs`
- Telehealth: `http://localhost:8003/docs`
- Notifications: `http://localhost:8004/docs`
- Analytics: `http://localhost:8005/docs`