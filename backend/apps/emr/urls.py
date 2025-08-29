from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet, basename='patient')
router.register(r'encounters', views.EncounterViewSet, basename='encounter')
router.register(r'medications', views.MedicationViewSet, basename='medication')
router.register(r'lab-results', views.LabResultViewSet, basename='labresult')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]