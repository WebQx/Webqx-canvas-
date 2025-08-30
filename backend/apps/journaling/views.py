from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import transaction

from .models import (
    JournalEntry, JournalTag, JournalEntryTag, JournalPrompt,
    JournalPromptResponse, MoodTracking, SymptomLog, JournalExport
)
from .serializers import (
    JournalEntrySerializer, JournalEntryCreateSerializer, JournalTagSerializer,
    MoodTrackingSerializer, SymptomLogSerializer, JournalPromptSerializer,
    JournalPromptResponseSerializer, JournalExportSerializer,
    JournalInsightsSerializer, JournalStatsSerializer
)
from .nlp_service import JournalNLPService
from .tasks import process_journal_entry_nlp, generate_journal_export


class JournalEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for journal entries"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = JournalEntry.objects.filter(user=user)
        
        # Filter by entry type
        entry_type = self.request.query_params.get('entry_type')
        if entry_type:
            queryset = queryset.filter(entry_type=entry_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Filter by tags
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(journalentrytag__tag__name__in=tags).distinct()
        
        # Search in content
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JournalEntryCreateSerializer
        return JournalEntrySerializer
    
    def perform_create(self, serializer):
        """Create journal entry and trigger NLP analysis"""
        entry = serializer.save()
        
        # Process NLP analysis asynchronously
        process_journal_entry_nlp.delay(entry.id)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Manually trigger NLP analysis for an entry"""
        entry = self.get_object()
        
        nlp_service = JournalNLPService()
        analysis = nlp_service.analyze_entry(entry)
        
        # Update entry with analysis results
        entry.sentiment_score = analysis['sentiment_score']
        entry.sentiment_label = analysis['sentiment_label']
        entry.keywords = analysis['keywords']
        entry.entities = analysis['entities']
        entry.topics = analysis['topics']
        entry.urgency_score = analysis['urgency_score']
        entry.clinical_flags = analysis['clinical_flags']
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def insights(self, request):
        """Get insights from user's journal entries"""
        entries = self.get_queryset()
        
        nlp_service = JournalNLPService()
        insights = nlp_service.generate_insights(entries)
        
        # Add additional insights
        insights.update(self._calculate_additional_insights(entries))
        
        serializer = JournalInsightsSerializer(insights)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive journal statistics"""
        user = request.user
        entries = self.get_queryset()
        
        stats = self._calculate_journal_stats(user, entries)
        serializer = JournalStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent journal entries"""
        recent_entries = self.get_queryset()[:10]
        serializer = self.get_serializer(recent_entries, many=True)
        return Response(serializer.data)
    
    def _calculate_additional_insights(self, entries):
        """Calculate additional insights beyond basic NLP"""
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        insights = {
            'entries_this_week': entries.filter(created_at__gte=week_ago).count(),
            'entries_this_month': entries.filter(created_at__gte=month_ago).count(),
            'longest_streak': self._calculate_longest_streak(entries),
            'current_streak': self._calculate_current_streak(entries)
        }
        
        return insights
    
    def _calculate_longest_streak(self, entries):
        """Calculate longest consecutive days of journaling"""
        if not entries:
            return 0
        
        dates = entries.values_list('created_at__date', flat=True).distinct().order_by('-created_at__date')
        
        longest_streak = 0
        current_streak = 1
        
        for i in range(1, len(dates)):
            if (dates[i-1] - dates[i]).days == 1:
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1
        
        return max(longest_streak, current_streak)
    
    def _calculate_current_streak(self, entries):
        """Calculate current consecutive days of journaling"""
        if not entries:
            return 0
        
        today = timezone.now().date()
        dates = entries.values_list('created_at__date', flat=True).distinct().order_by('-created_at__date')
        
        if not dates or dates[0] != today:
            # Check if there's an entry yesterday
            yesterday = today - timedelta(days=1)
            if dates and dates[0] == yesterday:
                dates = list(dates)
                dates.insert(0, today)
            else:
                return 0
        
        streak = 1
        for i in range(1, len(dates)):
            if (dates[i-1] - dates[i]).days == 1:
                streak += 1
            else:
                break
        
        return streak
    
    def _calculate_journal_stats(self, user, entries):
        """Calculate comprehensive journal statistics"""
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Basic stats
        total_entries = entries.count()
        total_words = sum(entry.word_count for entry in entries)
        avg_words = total_words / total_entries if total_entries > 0 else 0
        
        # Time-based stats
        entries_today = entries.filter(created_at__date=today).count()
        entries_this_week = entries.filter(created_at__gte=week_ago).count()
        entries_this_month = entries.filter(created_at__gte=month_ago).count()
        
        # Content analysis
        tag_counts = JournalEntryTag.objects.filter(
            entry__user=user
        ).values('tag__name').annotate(count=Count('tag')).order_by('-count')[:5]
        
        most_used_tags = [{'name': item['tag__name'], 'count': item['count']} for item in tag_counts]
        
        # Keywords from recent entries
        recent_entries = entries[:50]
        all_keywords = []
        for entry in recent_entries:
            if entry.keywords:
                all_keywords.extend(entry.keywords)
        
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        common_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Sentiment distribution
        sentiment_counts = entries.exclude(sentiment_label='').values('sentiment_label').annotate(
            count=Count('sentiment_label')
        )
        sentiment_distribution = {item['sentiment_label']: item['count'] for item in sentiment_counts}
        
        # Health tracking
        mood_entries = MoodTracking.objects.filter(user=user).count()
        symptom_entries = SymptomLog.objects.filter(user=user).count()
        clinical_flags = entries.exclude(clinical_flags=[]).count()
        
        return {
            'total_entries': total_entries,
            'total_words': total_words,
            'avg_words_per_entry': round(avg_words, 1),
            'entries_today': entries_today,
            'entries_this_week': entries_this_week,
            'entries_this_month': entries_this_month,
            'current_streak': self._calculate_current_streak(entries),
            'longest_streak': self._calculate_longest_streak(entries),
            'most_used_tags': most_used_tags,
            'common_keywords': common_keywords,
            'sentiment_distribution': sentiment_distribution,
            'mood_entries': mood_entries,
            'symptom_entries': symptom_entries,
            'clinical_flags': clinical_flags
        }


class JournalTagViewSet(viewsets.ModelViewSet):
    """ViewSet for journal tags"""
    
    serializer_class = JournalTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return JournalTag.objects.filter(
            Q(is_system_tag=True) | Q(created_by=user)
        ).order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MoodTrackingViewSet(viewsets.ModelViewSet):
    """ViewSet for mood tracking"""
    
    serializer_class = MoodTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MoodTracking.objects.filter(user=self.request.user).order_by('-recorded_at')
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get mood trends over time"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        mood_data = self.get_queryset().filter(
            recorded_at__gte=start_date
        ).values(
            'recorded_at__date'
        ).annotate(
            avg_mood=Avg('overall_mood'),
            avg_energy=Avg('energy_level'),
            avg_anxiety=Avg('anxiety_level'),
            avg_sleep=Avg('sleep_quality'),
            count=Count('id')
        ).order_by('recorded_at__date')
        
        return Response(list(mood_data))
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's mood entry if exists"""
        today = timezone.now().date()
        try:
            mood = self.get_queryset().filter(recorded_at__date=today).first()
            if mood:
                serializer = self.get_serializer(mood)
                return Response(serializer.data)
            else:
                return Response({'detail': 'No mood entry for today'}, status=status.HTTP_404_NOT_FOUND)
        except MoodTracking.DoesNotExist:
            return Response({'detail': 'No mood entry for today'}, status=status.HTTP_404_NOT_FOUND)


class SymptomLogViewSet(viewsets.ModelViewSet):
    """ViewSet for symptom logging"""
    
    serializer_class = SymptomLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SymptomLog.objects.filter(user=self.request.user).order_by('-recorded_at')
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get symptom trends over time"""
        days = int(request.query_params.get('days', 30))
        symptom = request.query_params.get('symptom')
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(recorded_at__gte=start_date)
        
        if symptom:
            queryset = queryset.filter(symptom_name__icontains=symptom)
        
        trend_data = queryset.values(
            'recorded_at__date', 'symptom_name'
        ).annotate(
            avg_severity=Avg('severity'),
            frequency=Count('id'),
            avg_duration=Avg('duration_hours')
        ).order_by('recorded_at__date', 'symptom_name')
        
        return Response(list(trend_data))
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get symptom summary"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        symptoms = self.get_queryset().filter(
            recorded_at__gte=start_date
        ).values('symptom_name').annotate(
            frequency=Count('id'),
            avg_severity=Avg('severity'),
            max_severity=models.Max('severity'),
            avg_duration=Avg('duration_hours')
        ).order_by('-frequency')
        
        return Response(list(symptoms))


class JournalPromptViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for journal prompts (read-only)"""
    
    serializer_class = JournalPromptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return JournalPrompt.objects.filter(
            is_active=True,
            target_user_types__contains=[user.user_type]
        ).order_by('?')  # Random order
    
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Get daily prompts for user"""
        prompts = self.get_queryset().filter(prompt_type='daily')[:3]
        serializer = self.get_serializer(prompts, many=True)
        return Response(serializer.data)


class JournalPromptResponseViewSet(viewsets.ModelViewSet):
    """ViewSet for journal prompt responses"""
    
    serializer_class = JournalPromptResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JournalPromptResponse.objects.filter(user=self.request.user).order_by('-completed_at')


class JournalExportViewSet(viewsets.ModelViewSet):
    """ViewSet for journal exports"""
    
    serializer_class = JournalExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JournalExport.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create export and trigger generation"""
        export = serializer.save()
        
        # Generate export asynchronously
        generate_journal_export.delay(export.id)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download export file"""
        export = self.get_object()
        
        if not export.is_complete:
            return Response(
                {'error': 'Export is not ready yet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return download URL or file
        return Response({
            'download_url': f'/api/journal/exports/{export.id}/file/',
            'file_size': export.file_size_bytes,
            'expires_at': export.expires_at
        })