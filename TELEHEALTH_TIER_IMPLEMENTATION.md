# Telehealth Tier Settings Implementation

This document describes the implementation of the thoughtfully designed toggle UI flow for switching between Free (WebRTC) and Paid (Zoom SDK) telehealth tiers in the WebQx Healthcare platform.

## Features Implemented

### 🎛️ Toggle UI: "Telehealth Tier Settings"

#### Backend Implementation

1. **ClinicSettings Model** (`backend/apps/telehealth/clinic_models.py`)
   - Stores clinic-wide telehealth preferences
   - Default tier selection (WebRTC/Zoom)
   - Fallback and advanced options
   - Accessibility settings (high contrast, language)
   - Audit trail tracking

2. **API Endpoints** (`backend/apps/telehealth/views.py`)
   - `GET /telehealth/clinic-settings/` - Get current settings
   - `PUT /telehealth/clinic-settings/update/` - Update settings (Admin/Coordinator only)
   - `GET /telehealth/tier-preview/` - Get tier comparison information
   - `GET /telehealth/user-permissions/` - Check user permissions

3. **Role-Based Access Control**
   | Role       | Access Level |
   |------------|-------------|
   | Admin      | ✅ Full access (view + edit) |
   | Coordinator| ✅ Full access (view + edit) |
   | Clinician  | 👁️ View only |
   | Patient    | ❌ No access |

#### Frontend Implementation

1. **TelehealthTierSettings Screen** (`frontend/src/screens/settings/TelehealthTierSettings.tsx`)
   - Radio button selection for WebRTC vs Zoom
   - Detailed tier previews with pros/cons
   - Advanced settings toggles
   - Current configuration display
   - Role-based UI restrictions

2. **Settings Navigation** (`frontend/src/screens/settings/SettingsScreen.tsx`)
   - Link to Telehealth Tier Settings
   - User permission-based visibility
   - Organized settings categories

3. **API Service** (`frontend/src/services/telehealthAPI.ts`)
   - RESTful API client for all telehealth operations
   - Type-safe interfaces
   - Error handling

### 🧠 Smart Features

- **Dynamic Preview**: Displays detailed comparison of each tier's interface
- **Fallback Logic**: Option to auto-switch to WebRTC if Zoom SDK fails
- **Patient Choice Toggle**: Allows patients to choose their preferred tier at session start
- **Audit Logging**: Logs every tier switch for compliance purposes

### 🧑‍⚕️ Accessibility & Inclusion

- **🌍 Multilingual Support**: Built-in localization for English, Spanish, Urdu
- **🧏 Screen Reader Support**: VoiceOver/TalkBack compatibility with proper ARIA labels
- **🎨 High-Contrast Mode**: Toggle for better visual accessibility
- **🧠 Contextual Tooltips**: Plain-language explanations for all features

### 🔐 Security & Compliance

- **Audit Logging**: TelehealthTierAuditLog model tracks all changes
- **Role-Based Permissions**: Enforced at both API and UI levels
- **Data Validation**: Server-side validation of all settings
- **HIPAA Compliance**: Secure handling of clinic configuration data

## UI Flow Example

```
Settings → Clinic Preferences → Telehealth Tier
──────────────────────────────
Telehealth Tier Settings
──────────────────────────────
Choose your clinic's default telehealth provider:

🔘 Free Tier (WebRTC)
   - Peer-to-peer video
   - Lightweight, no cost
   - Ideal for low-bandwidth clinics
   [View Details]

🔘 Paid Tier (Zoom SDK)  [Premium]
   - Enterprise-grade video
   - Screen sharing, recording
   - HIPAA-compliant infrastructure
   [View Details]
   ⚠️ Requires subscription upgrade

📦 Current Tier: WebRTC
🛠️ Advanced Settings
   [✓] Allow fallback to WebRTC if Zoom fails
   [✓] Enable patient choice at session start
   [✓] Enable bandwidth detection
   [ ] High contrast mode

──────────────────────────────
[Refresh]     [Save Changes]
```

## Technical Architecture

### Backend Models
- `ClinicSettings`: Main settings storage
- `TelehealthTierAuditLog`: Compliance audit trail
- `TelehealthUsageAnalytics`: Usage patterns for recommendations

### Frontend Components
- `TelehealthTierSettings`: Main settings screen
- `SettingsScreen`: Updated with navigation
- `telehealthAPI`: API service layer
- `useAuth`: Authentication hook
- `accessibility.ts`: Multilingual and accessibility utilities

### Security Features
- Permission checks at multiple levels
- JWT-based authentication
- Audit logging with IP and user agent tracking
- Input validation and sanitization

## Installation & Usage

1. **Backend Setup**: The new models need to be migrated
2. **Frontend Navigation**: Updated to support nested settings screens
3. **Permissions**: Users need appropriate roles to access settings
4. **Testing**: All endpoints include comprehensive error handling

This implementation provides a complete, accessible, and secure telehealth tier management system that prioritizes intentional decision-making and compliance tracking.