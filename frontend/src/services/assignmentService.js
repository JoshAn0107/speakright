import api from './api';

const assignmentService = {
  // Word Databases
  getWordDatabases: async () => {
    const response = await api.get('/api/assignments/databases');
    return response.data;
  },

  getDatabaseWords: async (databaseId) => {
    const response = await api.get(`/api/assignments/databases/${databaseId}/words`);
    return response.data;
  },

  // Teacher - Assignment Management
  createAssignment: async (assignmentData) => {
    const response = await api.post('/api/assignments/teacher/assignments', assignmentData);
    return response.data;
  },

  getTeacherAssignments: async () => {
    const response = await api.get('/api/assignments/teacher/assignments');
    return response.data;
  },

  getTeacherAssignment: async (assignmentId) => {
    const response = await api.get(`/api/assignments/teacher/assignments/${assignmentId}`);
    return response.data;
  },

  updateAssignment: async (assignmentId, updateData) => {
    const response = await api.put(`/api/assignments/teacher/assignments/${assignmentId}`, updateData);
    return response.data;
  },

  deleteAssignment: async (assignmentId) => {
    const response = await api.delete(`/api/assignments/teacher/assignments/${assignmentId}`);
    return response.data;
  },

  getAssignmentProgress: async (assignmentId) => {
    const response = await api.get(`/api/assignments/teacher/assignments/${assignmentId}/progress`);
    return response.data;
  },

  getStudentProgressForTeacher: async (assignmentId, studentId) => {
    const response = await api.get(`/api/assignments/teacher/assignments/${assignmentId}/students/${studentId}/progress`);
    return response.data;
  },

  // Student - Assignment Access
  getStudentAssignments: async () => {
    const response = await api.get('/api/assignments/student/assignments');
    return response.data;
  },

  getStudentAssignment: async (assignmentId) => {
    const response = await api.get(`/api/assignments/student/assignments/${assignmentId}`);
    return response.data;
  },

  submitAssignmentWord: async (assignmentId, wordText, recordingId) => {
    const response = await api.post(`/api/assignments/student/assignments/${assignmentId}/submit`, null, {
      params: {
        word_text: wordText,
        recording_id: recordingId
      }
    });
    return response.data;
  },

  getStudentAssignmentProgress: async (assignmentId) => {
    const response = await api.get(`/api/assignments/student/assignments/${assignmentId}/progress`);
    return response.data;
  },
};

export default assignmentService;
