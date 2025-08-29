from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'entries', views.JournalEntryViewSet, basename='journalentry')
router.register(r'tags', views.JournalTagViewSet, basename='journaltag')
router.register(r'mood', views.MoodTrackingViewSet, basename='moodtracking')
router.register(r'symptoms', views.SymptomLogViewSet, basename='symptomlog')
router.register(r'prompts', views.JournalPromptViewSet, basename='journalprompt')
router.register(r'prompt-responses', views.JournalPromptResponseViewSet, basename='journalpromptresponse')
router.register(r'exports', views.JournalExportViewSet, basename='journalexport')

urlpatterns = [
    path('', include(router.urls)),
]