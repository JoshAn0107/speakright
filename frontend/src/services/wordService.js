import api from './api';

const wordService = {
  async getWord(word) {
    const response = await api.get(`/api/words/${word}`);
    return response.data;
  },

  async getDailyWord() {
    const response = await api.get('/api/words/daily/challenge');
    return response.data;
  },

  async getWordsByTopic(topic) {
    const response = await api.get(`/api/words/topic/${topic}`);
    return response.data;
  },

  async searchWord(query) {
    const response = await api.get(`/api/words/search/${query}`);
    return response.data;
  },

  async getAllWordAssignments() {
    const response = await api.get('/api/words/assignments/all');
    return response.data;
  },

  // Teacher only
  async assignWord(wordText, difficulty, topics) {
    const response = await api.post('/api/words/assign', {
      word_text: wordText,
      difficulty_level: difficulty,
      topic_tags: topics,
    });
    return response.data;
  },
};

export default wordService;
