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

  createWordDatabase: async (name, description = null) => {
    const response = await api.post('/api/assignments/databases', { name, description });
    return response.data;
  },

  addWordsToDatabase: async (databaseId, words) => {
    // words: array of { word_text, definition?, example_sentence?, difficulty_level? }
    const response = await api.post(`/api/assignments/databases/${databaseId}/words`, { words });
    return response.data;
  },

  deleteDatabaseWord: async (databaseId, wordId) => {
    const response = await api.delete(`/api/assignments/databases/${databaseId}/words/${wordId}`);
    return response.data;
  },

  exportDatabaseExcel: async (databaseId, databaseName) => {
    const response = await api.get(`/api/assignments/databases/${databaseId}/export`, {
      responseType: 'blob',
    });
    const url = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${databaseName}.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  },

  deleteWordDatabase: async (databaseId) => {
    const response = await api.delete(`/api/assignments/databases/${databaseId}`);
    return response.data;
  },

  getTrashedDatabases: async () => {
    const response = await api.get('/api/assignments/databases/trash');
    return response.data;
  },

  restoreDatabase: async (databaseId) => {
    const response = await api.post(`/api/assignments/databases/${databaseId}/restore`);
    return response.data;
  },

  purgeDatabase: async (databaseId) => {
    const response = await api.delete(`/api/assignments/databases/${databaseId}/purge`);
    return response.data;
  },

  emptyTrash: async () => {
    const response = await api.delete('/api/assignments/databases/trash');
    return response.data;
  },

  uploadWordlistFile: async (file, targetName = null, note = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (targetName) formData.append('target_name', targetName);
    if (note) formData.append('note', note);
    const response = await api.post('/api/assignments/wordlist-uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getWordlistUploads: async () => {
    const response = await api.get('/api/assignments/wordlist-uploads');
    return response.data;
  },

  deleteWordlistUpload: async (uploadId) => {
    const response = await api.delete(`/api/assignments/wordlist-uploads/${uploadId}`);
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
