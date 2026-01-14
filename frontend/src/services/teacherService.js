import api from './api';

const teacherService = {
  async getSubmissions(statusFilter = null, classId = null) {
    const params = {};
    if (statusFilter) params.status_filter = statusFilter;
    if (classId) params.class_id = classId;

    const response = await api.get('/api/teacher/submissions', { params });
    return response.data;
  },

  async submitFeedback(recordingId, feedbackText, grade, flagForPractice = false) {
    const response = await api.post('/api/teacher/feedback', {
      recording_id: recordingId,
      feedback_text: feedbackText,
      grade,
      flag_for_practice: flagForPractice,
    });
    return response.data;
  },

  async getStudents(classId = null) {
    const params = classId ? { class_id: classId } : {};
    const response = await api.get('/api/teacher/students', { params });
    return response.data;
  },

  async getAnalytics(classId = null) {
    const params = classId ? { class_id: classId } : {};
    const response = await api.get('/api/teacher/analytics', { params });
    return response.data;
  },

  async createClass(className, description = null) {
    const response = await api.post('/api/teacher/classes', null, {
      params: {
        class_name: className,
        description,
      },
    });
    return response.data;
  },

  async getMyClasses() {
    const response = await api.get('/api/teacher/classes');
    return response.data;
  },
};

export default teacherService;
