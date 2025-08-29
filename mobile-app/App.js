import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Screen imports
import HomeScreen from './src/screens/HomeScreen';
import JournalScreen from './src/screens/JournalScreen';
import EMRScreen from './src/screens/EMRScreen';
import TelehealthScreen from './src/screens/TelehealthScreen';
import MessagingScreen from './src/screens/MessagingScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import LoginScreen from './src/screens/auth/LoginScreen';

// Services
import AuthService from './src/services/AuthService';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          switch (route.name) {
            case 'Home':
              iconName = 'home';
              break;
            case 'Journal':
              iconName = 'book';
              break;
            case 'EMR':
              iconName = 'medical-services';
              break;
            case 'Telehealth':
              iconName = 'video-call';
              break;
            case 'Messages':
              iconName = 'message';
              break;
            case 'Settings':
              iconName = 'settings';
              break;
            default:
              iconName = 'circle';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2563EB',
        tabBarInactiveTintColor: 'gray',
        headerStyle: {
          backgroundColor: '#1E40AF',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ title: 'Home' }}
      />
      <Tab.Screen 
        name="Journal" 
        component={JournalScreen} 
        options={{ title: 'Journal' }}
      />
      <Tab.Screen 
        name="EMR" 
        component={EMRScreen} 
        options={{ title: 'Medical Records' }}
      />
      <Tab.Screen 
        name="Telehealth" 
        component={TelehealthScreen} 
        options={{ title: 'Video Calls' }}
      />
      <Tab.Screen 
        name="Messages" 
        component={MessagingScreen} 
        options={{ title: 'Messages' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen} 
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    // Check authentication status on app launch
    AuthService.checkAuthStatus()
      .then(setIsAuthenticated)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return null; // Show loading screen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainTabs} />
        ) : (
          <Stack.Screen name="Login" component={LoginScreen} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}