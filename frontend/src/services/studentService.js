import api from './api';

const studentService = {
  async submitRecording(wordText, audioFile) {
    const formData = new FormData();
    formData.append('word_text', wordText);
    formData.append('audio_file', audioFile);

    const response = await api.post('/api/student/recordings/submit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async getMyRecordings(status = null) {
    const params = status ? { status } : {};
    const response = await api.get('/api/student/recordings', { params });
    return response.data;
  },

  async getMyProgress(period = 'week') {
    const response = await api.get('/api/student/progress', {
      params: { period },
    });
    return response.data;
  },
};

export default studentService;
