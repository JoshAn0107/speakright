import { Link, useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import { LogOut, User, Mic } from 'lucide-react';

function Navbar() {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to={user?.role === 'student' ? '/student' : '/teacher'} className="flex items-center">
              <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <span className="ml-3 text-xl font-bold text-gray-900">
                Pronunciation Portal
              </span>
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <User className="w-5 h-5 text-gray-400 mr-2" />
              <div>
                <div className="text-sm font-medium text-gray-900">{user?.username}</div>
                <div className="text-xs text-gray-500 capitalize">{user?.role}</div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
