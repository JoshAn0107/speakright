import api from './api';

const authService = {
  async register(username, email, password, role) {
    const response = await api.post('/api/auth/register', {
      username,
      email,
      password,
      role,
    });

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data;
  },

  async login(email, password) {
    const response = await api.post('/api/auth/login', {
      email,
      password,
    });

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  getToken() {
    return localStorage.getItem('token');
  }
};

export default authService;
