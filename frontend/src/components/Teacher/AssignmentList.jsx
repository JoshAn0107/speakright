import { useState, useEffect } from 'react';
import { Plus, Calendar, Users, BookOpen, Trash2, BarChart3, AlertCircle, Home } from 'lucide-react';
import Navbar from '../Common/Navbar';
import CreateAssignment from './CreateAssignment';
import AssignmentProgress from './AssignmentProgress';
import assignmentService from '../../services/assignmentService';

function AssignmentList({ onBackToDashboard }) {
  const [view, setView] = useState('list'); // 'list', 'create', 'progress'
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAssignments();
  }, []);

  const loadAssignments = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Loading assignments...');
      const data = await assignmentService.getTeacherAssignments();
      console.log('Assignments loaded:', data);
      console.log('Is array?', Array.isArray(data));
      // Ensure we always have an array
      setAssignments(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error loading assignments:', error);
      setError(error.message || 'Failed to load assignments');
      setAssignments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAssignment = async (assignmentId) => {
    if (!confirm('Are you sure you want to delete this assignment? This action cannot be undone.')) {
      return;
    }

    try {
      await assignmentService.deleteAssignment(assignmentId);
      alert('Assignment deleted successfully');
      loadAssignments();
    } catch (error) {
      console.error('Error deleting assignment:', error);
      alert('Failed to delete assignment');
    }
  };

  const viewProgress = (assignment) => {
    setSelectedAssignment(assignment);
    setView('progress');
  };

  if (view === 'create') {
    return (
      <CreateAssignment
        onBack={() => {
          setView('list');
          loadAssignments();
        }}
        onAssignmentCreated={() => {
          setView('list');
          loadAssignments();
        }}
      />
    );
  }

  if (view === 'progress' && selectedAssignment) {
    return (
      <AssignmentProgress
        assignment={selectedAssignment}
        onBack={() => {
          setView('list');
          setSelectedAssignment(null);
        }}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold text-gray-900">Word Assignments</h1>
            {onBackToDashboard && (
              <button
                onClick={onBackToDashboard}
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors text-sm"
              >
                <Home className="w-4 h-4 mr-1" />
                Dashboard
              </button>
            )}
          </div>
          <button
            onClick={() => setView('create')}
            className="btn-primary flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Assignment
          </button>
        </div>

        {error && (
          <div className="card bg-red-50 border-red-200 mb-6">
            <div className="flex items-center text-red-800">
              <AlertCircle className="w-5 h-5 mr-2" />
              <div>
                <p className="font-medium">Error loading assignments</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            </div>
            <button
              onClick={loadAssignments}
              className="mt-4 btn-secondary text-sm"
            >
              Try Again
            </button>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading assignments...</p>
          </div>
        ) : assignments.length === 0 && !error ? (
          <div className="card text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No assignments yet</h3>
            <p className="text-gray-600 mb-6">
              Create your first word assignment to help students practice pronunciation
            </p>
            <button
              onClick={() => setView('create')}
              className="btn-primary inline-flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create First Assignment
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {assignments.map((assignment) => {
              const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;
              const isOverdue = dueDate && dueDate < new Date();

              return (
                <div key={assignment.id} className="card hover:shadow-lg transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900">
                          {assignment.title}
                        </h3>
                        {isOverdue && (
                          <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full flex items-center">
                            <AlertCircle className="w-3 h-3 mr-1" />
                            Overdue
                          </span>
                        )}
                      </div>

                      {assignment.description && (
                        <p className="text-gray-600 mb-4">{assignment.description}</p>
                      )}

                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        {assignment.word_database_name && (
                          <div className="flex items-center">
                            <BookOpen className="w-4 h-4 mr-1" />
                            {assignment.word_database_name}
                          </div>
                        )}
                        <div className="flex items-center">
                          <BookOpen className="w-4 h-4 mr-1" />
                          {assignment.word_count} words
                        </div>
                        <div className="flex items-center">
                          <Users className="w-4 h-4 mr-1" />
                          {assignment.student_count} student{assignment.student_count !== 1 ? 's' : ''}
                        </div>
                        {dueDate && (
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            Due: {dueDate.toLocaleDateString()}
                          </div>
                        )}
                      </div>

                      <div className="mt-4 text-xs text-gray-500">
                        Created: {new Date(assignment.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => viewProgress(assignment)}
                        className="btn-secondary flex items-center text-sm"
                        title="View Progress"
                      >
                        <BarChart3 className="w-4 h-4 mr-1" />
                        Progress
                      </button>
                      <button
                        onClick={() => handleDeleteAssignment(assignment.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete Assignment"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {/* Word Preview */}
                  {assignment.words && assignment.words.length > 0 && (
                    <div className="mt-4 pt-4 border-t">
                      <p className="text-sm text-gray-600 mb-2">Words in this assignment:</p>
                      <div className="flex flex-wrap gap-2">
                        {assignment.words.slice(0, 10).map((word) => (
                          <span
                            key={word.id}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded"
                          >
                            {word.word_text}
                          </span>
                        ))}
                        {assignment.words.length > 10 && (
                          <span className="px-2 py-1 bg-gray-200 text-gray-600 text-sm rounded">
                            +{assignment.words.length - 10} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default AssignmentList;
