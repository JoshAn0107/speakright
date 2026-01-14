import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import StudentDashboard from './components/Student/StudentDashboard';
import TeacherDashboard from './components/Teacher/TeacherDashboard';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import authService from './services/authService';

function App() {
  const isAuthenticated = authService.isAuthenticated();
  const user = authService.getCurrentUser();

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to={user?.role === 'student' ? '/student' : '/teacher'} replace /> : <Login />}
        />
        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to={user?.role === 'student' ? '/student' : '/teacher'} replace /> : <Register />}
        />

        {/* Protected Student Routes */}
        <Route
          path="/student"
          element={
            <ProtectedRoute requiredRole="student">
              <StudentDashboard />
            </ProtectedRoute>
          }
        />

        {/* Protected Teacher Routes */}
        <Route
          path="/teacher"
          element={
            <ProtectedRoute requiredRole="teacher">
              <TeacherDashboard />
            </ProtectedRoute>
          }
        />

        {/* Default Route */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to={user?.role === 'student' ? '/student' : '/teacher'} replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
