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

  async updateClass(classId, className = null, description = null) {
    const params = {};
    if (className !== null) params.class_name = className;
    if (description !== null) params.description = description;
    const response = await api.put(`/api/teacher/classes/${classId}`, null, { params });
    return response.data;
  },

  async deleteClass(classId) {
    const response = await api.delete(`/api/teacher/classes/${classId}`);
    return response.data;
  },

  async removeStudentFromClass(classId, studentId) {
    const response = await api.delete(`/api/teacher/classes/${classId}/students/${studentId}`);
    return response.data;
  },

  async createSuggestion(content) {
    const response = await api.post('/api/teacher/suggestions', null, {
      params: { content },
    });
    return response.data;
  },

  async getMySuggestions() {
    const response = await api.get('/api/teacher/suggestions');
    return response.data;
  },
};

export default teacherService;
