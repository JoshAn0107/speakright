import { useState, useEffect } from 'react';
import { Users, BarChart3, FileText, AlertCircle, BookOpen } from 'lucide-react';
import Navbar from '../Common/Navbar';
import ReviewSubmission from './ReviewSubmission';
import AssignmentList from './AssignmentList';
import teacherService from '../../services/teacherService';

function TeacherDashboard() {
  const [activeTab, setActiveTab] = useState('submissions');
  const [submissions, setSubmissions] = useState([]);
  const [students, setStudents] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);

  useEffect(() => {
    if (activeTab === 'submissions') {
      loadSubmissions();
    } else if (activeTab === 'students') {
      loadStudents();
    } else if (activeTab === 'analytics') {
      loadAnalytics();
    }
  }, [activeTab]);

  const loadSubmissions = async () => {
    setLoading(true);
    try {
      const data = await teacherService.getSubmissions();
      setSubmissions(data);
    } catch (error) {
      console.error('Error loading submissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    setLoading(true);
    try {
      const data = await teacherService.getStudents();
      setStudents(data);
    } catch (error) {
      console.error('Error loading students:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const data = await teacherService.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmitted = () => {
    setSelectedSubmission(null);
    loadSubmissions();
  };

  if (selectedSubmission) {
    return (
      <ReviewSubmission
        submission={selectedSubmission}
        onBack={() => setSelectedSubmission(null)}
        onFeedbackSubmitted={handleFeedbackSubmitted}
      />
    );
  }

  // Render Assignments tab as full component
  if (activeTab === 'assignments') {
    return <AssignmentList onBackToDashboard={() => setActiveTab('submissions')} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('submissions')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors flex items-center ${
              activeTab === 'submissions'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <FileText className="w-4 h-4 mr-2" />
            Submissions
          </button>
          <button
            onClick={() => setActiveTab('students')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors flex items-center ${
              activeTab === 'students'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="w-4 h-4 mr-2" />
            Students
          </button>
          <button
            onClick={() => setActiveTab('assignments')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors flex items-center ${
              activeTab === 'assignments'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <BookOpen className="w-4 h-4 mr-2" />
            Assignments
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors flex items-center ${
              activeTab === 'analytics'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Analytics
          </button>
        </div>

        {/* Submissions Tab */}
        {activeTab === 'submissions' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Student Submissions</h2>
              <span className="text-sm text-gray-600">
                {submissions.length} total
              </span>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="text-gray-500">Loading submissions...</div>
              </div>
            ) : submissions.length === 0 ? (
              <div className="card text-center py-12">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No submissions yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {submissions.map((submission) => (
                  <div
                    key={submission.id}
                    className="card hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedSubmission(submission)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-xl font-semibold text-gray-900">
                            {submission.word_text}
                          </h3>
                          {submission.is_automated_feedback && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                              AI Feedback
                            </span>
                          )}
                          {!submission.is_automated_feedback && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                              Manually Reviewed
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600">
                          Student: <span className="font-medium">{submission.student_name}</span>
                        </p>
                        <p className="text-sm text-gray-500 mt-1">
                          {new Date(submission.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-primary-600">
                          {submission.automated_scores?.pronunciation_score?.toFixed(0) || 'N/A'}%
                        </div>
                        {submission.teacher_grade && (
                          <div className="text-lg font-medium text-gray-900 mt-1">
                            Grade: {submission.teacher_grade}
                          </div>
                        )}
                      </div>
                    </div>

                    {submission.teacher_feedback && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-gray-700 line-clamp-2">
                          {submission.teacher_feedback}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Students Tab */}
        {activeTab === 'students' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Students</h2>
              <span className="text-sm text-gray-600">
                {students.length} total
              </span>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="text-gray-500">Loading students...</div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {students.map((student) => (
                  <div key={student.id} className="card">
                    <div className="flex items-center mb-3">
                      <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                        <span className="text-xl font-bold text-primary-600">
                          {student.username[0].toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">
                          {student.username}
                        </div>
                        <div className="text-sm text-gray-500">{student.email}</div>
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Recordings:</span>
                        <span className="font-medium">{student.total_recordings}</span>
                      </div>
                      <div className="flex justify-between text-sm mt-2">
                        <span className="text-gray-600">Avg Score:</span>
                        <span className="font-medium text-primary-600">
                          {student.average_score}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && analytics && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Analytics</h2>

            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
                <h3 className="text-sm font-medium text-gray-600 mb-2">
                  Total Recordings
                </h3>
                <p className="text-4xl font-bold text-gray-900">
                  {analytics.total_recordings}
                </p>
              </div>
              <div className="card bg-gradient-to-br from-green-50 to-green-100">
                <h3 className="text-sm font-medium text-gray-600 mb-2">
                  Average Score
                </h3>
                <p className="text-4xl font-bold text-gray-900">
                  {analytics.average_score}%
                </p>
              </div>
              <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
                <h3 className="text-sm font-medium text-gray-600 mb-2">
                  Pending Reviews
                </h3>
                <p className="text-4xl font-bold text-gray-900">
                  {analytics.pending_reviews}
                </p>
              </div>
            </div>

            {/* Most Practiced Words */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Most Practiced Words</h3>
                <div className="space-y-3">
                  {analytics.most_practiced_words.map((item, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                    >
                      <span className="font-medium text-gray-900">{item.word}</span>
                      <span className="text-sm text-gray-600">{item.count} times</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Challenging Words */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Challenging Words</h3>
                <div className="space-y-3">
                  {analytics.challenging_words.map((item, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center p-3 bg-red-50 rounded-lg"
                    >
                      <span className="font-medium text-gray-900">{item.word}</span>
                      <span className="text-sm text-red-600">
                        {item.average_score}% avg
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default TeacherDashboard;
