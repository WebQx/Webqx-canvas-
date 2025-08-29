import axios from 'axios';

const NLP_API_URL = process.env.EXPO_PUBLIC_NLP_URL || 'http://localhost:8000/api/nlp';

class NLPService {
  constructor() {
    this.client = axios.create({
      baseURL: NLP_API_URL,
      timeout: 15000,
    });
  }

  async analyzeText(text) {
    try {
      if (!text || text.trim().length < 10) {
        return [];
      }

      const response = await this.client.post('/analyze', {
        text: text.trim(),
        analysis_types: ['sentiment', 'entities', 'themes', 'symptoms'],
      });

      const { tags, sentiment, entities, themes } = response.data;

      // Combine different analysis results into tags
      const allTags = [];

      // Add sentiment tags
      if (sentiment && sentiment.label) {
        allTags.push(sentiment.label.toLowerCase());
      }

      // Add entity tags (medical terms, medications, etc.)
      if (entities && entities.length > 0) {
        entities.forEach(entity => {
          if (entity.type === 'MEDICATION' || entity.type === 'SYMPTOM' || entity.type === 'CONDITION') {
            allTags.push(entity.text.toLowerCase());
          }
        });
      }

      // Add theme tags
      if (themes && themes.length > 0) {
        allTags.push(...themes.map(theme => theme.toLowerCase()));
      }

      // Add custom tags if available
      if (tags && tags.length > 0) {
        allTags.push(...tags);
      }

      // Remove duplicates and return
      return [...new Set(allTags)];

    } catch (error) {
      console.error('NLP analysis error:', error);
      
      // Fallback: Simple keyword-based tagging
      return this.fallbackAnalysis(text);
    }
  }

  fallbackAnalysis(text) {
    const keywords = {
      symptoms: ['pain', 'ache', 'hurt', 'fever', 'nausea', 'dizzy', 'tired', 'fatigue', 'headache', 'cough'],
      emotions: ['happy', 'sad', 'anxious', 'worried', 'stressed', 'calm', 'excited', 'depressed', 'angry'],
      medications: ['medication', 'medicine', 'pill', 'tablet', 'dose', 'prescription', 'drug'],
      activities: ['exercise', 'walk', 'run', 'sleep', 'eat', 'work', 'rest'],
      improvements: ['better', 'good', 'great', 'improved', 'healing', 'recovery'],
      concerns: ['worse', 'bad', 'terrible', 'concerning', 'worry', 'problem'],
    };

    const tags = [];
    const lowerText = text.toLowerCase();

    // Check for keyword matches
    Object.entries(keywords).forEach(([category, words]) => {
      const matches = words.filter(word => lowerText.includes(word));
      if (matches.length > 0) {
        tags.push(category);
        // Add specific matches for symptoms and medications
        if (category === 'symptoms' || category === 'medications') {
          tags.push(...matches);
        }
      }
    });

    return [...new Set(tags)];
  }

  async analyzeSymptoms(text) {
    try {
      const response = await this.client.post('/symptoms', {
        text: text.trim(),
      });

      return response.data.symptoms || [];
    } catch (error) {
      console.error('Symptom analysis error:', error);
      return [];
    }
  }

  async analyzeMedications(text) {
    try {
      const response = await this.client.post('/medications', {
        text: text.trim(),
      });

      return response.data.medications || [];
    } catch (error) {
      console.error('Medication analysis error:', error);
      return [];
    }
  }

  async getSentiment(text) {
    try {
      const response = await this.client.post('/sentiment', {
        text: text.trim(),
      });

      return response.data.sentiment || { label: 'neutral', score: 0 };
    } catch (error) {
      console.error('Sentiment analysis error:', error);
      return { label: 'neutral', score: 0 };
    }
  }

  async generateSummary(entries) {
    try {
      const response = await this.client.post('/summarize', {
        entries: entries.map(entry => ({
          text: entry.text,
          timestamp: entry.timestamp,
          tags: entry.tags,
        })),
      });

      return response.data.summary || 'No summary available';
    } catch (error) {
      console.error('Summary generation error:', error);
      return 'Summary generation failed';
    }
  }

  async getInsights(entries) {
    try {
      const response = await this.client.post('/insights', {
        entries: entries.map(entry => ({
          text: entry.text,
          timestamp: entry.timestamp,
          tags: entry.tags,
        })),
      });

      return response.data.insights || [];
    } catch (error) {
      console.error('Insights generation error:', error);
      return [];
    }
  }
}

export default new NLPService();