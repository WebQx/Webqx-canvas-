from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.TelehealthSessionViewSet, basename='telehealthsession')
router.register(r'device-tests', views.TelehealthDeviceTestViewSet, basename='telehealthdevicetest')
router.register(r'signaling', views.WebRTCSignalingViewSet, basename='webrtcsignaling')
router.register(r'recordings', views.TelehealthRecordingViewSet, basename='telehealthrecording')
router.register(r'waiting-rooms', views.TelehealthWaitingRoomViewSet, basename='telehealthwaitingroom')

urlpatterns = [
    path('', include(router.urls)),
    
    # Clinic Settings endpoints
    path('clinic-settings/', views.get_clinic_settings, name='get_clinic_settings'),
    path('clinic-settings/update/', views.update_clinic_settings, name='update_clinic_settings'),
    path('tier-preview/', views.get_telehealth_tier_preview, name='tier_preview'),
    path('user-permissions/', views.check_user_permissions, name='user_permissions'),
]