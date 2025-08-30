import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useSelector } from 'react-redux';

// Screens (placeholder imports)
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
import HomeScreen from '../screens/main/HomeScreen';
import JournalScreen from '../screens/journal/JournalScreen';
import EMRScreen from '../screens/emr/EMRScreen';
import TelehealthScreen from '../screens/telehealth/TelehealthScreen';
import MessagingScreen from '../screens/messaging/MessagingScreen';
import SettingsScreen from '../screens/settings/SettingsScreen';

// Types
import { RootState } from '../store/store';
import { theme } from '../utils/theme';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Register" component={RegisterScreen} />
  </Stack.Navigator>
);

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        let iconName: keyof typeof Ionicons.glyphMap;

        switch (route.name) {
          case 'Home':
            iconName = focused ? 'home' : 'home-outline';
            break;
          case 'Journal':
            iconName = focused ? 'journal' : 'journal-outline';
            break;
          case 'EMR':
            iconName = focused ? 'medical' : 'medical-outline';
            break;
          case 'Telehealth':
            iconName = focused ? 'videocam' : 'videocam-outline';
            break;
          case 'Messages':
            iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
            break;
          case 'Settings':
            iconName = focused ? 'settings' : 'settings-outline';
            break;
          default:
            iconName = 'help-outline';
        }

        return <Ionicons name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: theme.colors.primary,
      tabBarInactiveTintColor: theme.colors.disabled,
      headerShown: false,
    })}
  >
    <Tab.Screen name="Home" component={HomeScreen} />
    <Tab.Screen name="Journal" component={JournalScreen} />
    <Tab.Screen name="EMR" component={EMRScreen} />
    <Tab.Screen name="Telehealth" component={TelehealthScreen} />
    <Tab.Screen name="Messages" component={MessagingScreen} />
    <Tab.Screen name="Settings" component={SettingsScreen} />
  </Tab.Navigator>
);

const RootNavigator = () => {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  return isAuthenticated ? <MainTabs /> : <AuthStack />;
};

export default RootNavigator;