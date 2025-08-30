import spacy
import json
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class JournalNLPService:
    """NLP service for analyzing journal entries"""
    
    def __init__(self):
        try:
            # Load spaCy model for NER and advanced NLP
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy English model not found. NLP features will be limited.")
            self.nlp = None
        
        # Clinical keywords for flagging
        self.clinical_keywords = {
            'mental_health': [
                'depression', 'anxiety', 'panic', 'suicide', 'self-harm',
                'hopeless', 'worthless', 'overwhelming', 'can\'t cope'
            ],
            'pain': [
                'severe pain', 'unbearable', 'excruciating', 'constant pain',
                'sharp pain', 'burning pain', 'chronic pain'
            ],
            'emergency': [
                'emergency', 'urgent', 'can\'t breathe', 'chest pain',
                'heart attack', 'stroke', 'bleeding', 'unconscious'
            ],
            'substance': [
                'alcohol', 'drugs', 'overdose', 'addiction', 'withdrawal',
                'relapse', 'drinking', 'high', 'intoxicated'
            ]
        }
    
    def analyze_entry(self, journal_entry):
        """Comprehensive analysis of a journal entry"""
        results = {
            'sentiment_score': None,
            'sentiment_label': 'neutral',
            'keywords': [],
            'entities': [],
            'topics': [],
            'urgency_score': 0.0,
            'clinical_flags': []
        }
        
        if not journal_entry.content:
            return results
        
        text = journal_entry.content.lower()
        
        # Sentiment Analysis
        sentiment = self._analyze_sentiment(text)
        results['sentiment_score'] = sentiment['score']
        results['sentiment_label'] = sentiment['label']
        
        # Keyword Extraction
        results['keywords'] = self._extract_keywords(text)
        
        # Named Entity Recognition
        if self.nlp:
            results['entities'] = self._extract_entities(journal_entry.content)
        
        # Topic Classification
        results['topics'] = self._classify_topics(text)
        
        # Clinical Flag Detection
        clinical_analysis = self._analyze_clinical_content(text, journal_entry)
        results['clinical_flags'] = clinical_analysis['flags']
        results['urgency_score'] = clinical_analysis['urgency_score']
        
        return results
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'score': polarity,
                'label': label
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {'score': 0.0, 'label': 'neutral'}
    
    def _extract_keywords(self, text):
        """Extract important keywords using TF-IDF"""
        try:
            # Simple keyword extraction
            words = text.split()
            
            # Filter out common words and short words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                'may', 'might', 'can', 'cant', 'i', 'me', 'my', 'myself', 'we', 'our',
                'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it',
                'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'
            }
            
            keywords = []
            for word in words:
                word = word.strip('.,!?";:()[]{}').lower()
                if len(word) > 3 and word not in stop_words:
                    keywords.append(word)
            
            # Return top keywords by frequency
            word_freq = {}
            for word in keywords:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and return top 10
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:10]]
            
        except Exception as e:
            logger.error(f"Keyword extraction error: {str(e)}")
            return []
    
    def _extract_entities(self, text):
        """Extract named entities using spaCy"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_)
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction error: {str(e)}")
            return []
    
    def _classify_topics(self, text):
        """Classify text into health-related topics"""
        topics = []
        
        topic_keywords = {
            'mental_health': [
                'anxiety', 'depression', 'stress', 'mood', 'emotional',
                'therapy', 'counseling', 'psychiatrist', 'medication'
            ],
            'physical_health': [
                'pain', 'symptoms', 'doctor', 'hospital', 'treatment',
                'medication', 'surgery', 'diagnosis', 'test', 'exam'
            ],
            'lifestyle': [
                'exercise', 'diet', 'sleep', 'nutrition', 'fitness',
                'workout', 'food', 'eating', 'weight', 'activity'
            ],
            'relationships': [
                'family', 'friends', 'partner', 'spouse', 'relationship',
                'social', 'support', 'love', 'conflict', 'communication'
            ],
            'work': [
                'job', 'work', 'career', 'boss', 'colleague', 'office',
                'stress', 'deadline', 'meeting', 'project', 'business'
            ]
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if topic not in topics:
                        topics.append(topic)
                    break
        
        return topics
    
    def _analyze_clinical_content(self, text, journal_entry):
        """Analyze for clinical relevance and urgency"""
        flags = []
        urgency_score = 0.0
        
        # Check for clinical keywords
        for category, keywords in self.clinical_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    flags.append({
                        'category': category,
                        'keyword': keyword,
                        'severity': self._get_keyword_severity(keyword)
                    })
                    urgency_score = max(urgency_score, self._get_keyword_severity(keyword))
        
        # Check mood and pain ratings
        if hasattr(journal_entry, 'mood_rating') and journal_entry.mood_rating:
            if journal_entry.mood_rating <= 2:
                flags.append({
                    'category': 'mood',
                    'keyword': 'low_mood_rating',
                    'severity': 0.6
                })
                urgency_score = max(urgency_score, 0.6)
        
        if hasattr(journal_entry, 'pain_level') and journal_entry.pain_level:
            if journal_entry.pain_level >= 8:
                flags.append({
                    'category': 'pain',
                    'keyword': 'high_pain_level',
                    'severity': 0.8
                })
                urgency_score = max(urgency_score, 0.8)
        
        # Check sentiment for extreme negativity
        if journal_entry.sentiment_score and journal_entry.sentiment_score < -0.7:
            flags.append({
                'category': 'sentiment',
                'keyword': 'extreme_negative_sentiment',
                'severity': 0.5
            })
            urgency_score = max(urgency_score, 0.5)
        
        return {
            'flags': flags,
            'urgency_score': min(urgency_score, 1.0)  # Cap at 1.0
        }
    
    def _get_keyword_severity(self, keyword):
        """Get severity score for clinical keywords"""
        high_severity = [
            'suicide', 'self-harm', 'emergency', 'can\'t breathe',
            'chest pain', 'heart attack', 'stroke', 'overdose'
        ]
        
        medium_severity = [
            'severe pain', 'unbearable', 'depression', 'panic',
            'hopeless', 'overwhelming'
        ]
        
        if keyword in high_severity:
            return 0.9
        elif keyword in medium_severity:
            return 0.7
        else:
            return 0.4
    
    def generate_insights(self, user_entries):
        """Generate insights from multiple journal entries"""
        if not user_entries:
            return {}
        
        insights = {
            'total_entries': len(user_entries),
            'avg_sentiment': 0.0,
            'mood_trend': [],
            'common_topics': [],
            'word_count_trend': [],
            'clinical_concerns': 0
        }
        
        sentiments = []
        topics = []
        clinical_count = 0
        
        for entry in user_entries:
            if entry.sentiment_score is not None:
                sentiments.append(entry.sentiment_score)
            
            if entry.topics:
                topics.extend(entry.topics)
            
            if entry.has_clinical_concerns:
                clinical_count += 1
        
        # Calculate averages
        if sentiments:
            insights['avg_sentiment'] = sum(sentiments) / len(sentiments)
        
        # Most common topics
        if topics:
            topic_counts = {}
            for topic in topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            insights['common_topics'] = [topic for topic, count in sorted_topics[:5]]
        
        insights['clinical_concerns'] = clinical_count
        
        return insights