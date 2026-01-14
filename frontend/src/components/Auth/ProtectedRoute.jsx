import { Navigate } from 'react-router-dom';
import authService from '../../services/authService';

function ProtectedRoute({ children, requiredRole }) {
  const isAuthenticated = authService.isAuthenticated();
  const user = authService.getCurrentUser();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    // Redirect to their appropriate dashboard
    if (user?.role === 'student') {
      return <Navigate to="/student" replace />;
    } else if (user?.role === 'teacher') {
      return <Navigate to="/teacher" replace />;
    }
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
