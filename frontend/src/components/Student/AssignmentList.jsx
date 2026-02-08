import { useState, useEffect } from 'react';
import { BookOpen, Calendar, CheckCircle, Clock, AlertCircle, ChevronRight, Home } from 'lucide-react';
import Navbar from '../Common/Navbar';
import AssignmentPractice from './AssignmentPractice';
import assignmentService from '../../services/assignmentService';

function AssignmentList({ onBackToDashboard }) {
  const [view, setView] = useState('list'); // 'list' or 'practice'
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAssignments();
  }, []);

  const loadAssignments = async () => {
    try {
      setLoading(true);
      const data = await assignmentService.getStudentAssignments();
      setAssignments(data);
    } catch (error) {
      console.error('Error loading assignments:', error);
      alert('加载作业失败');
    } finally {
      setLoading(false);
    }
  };

  const startPractice = (assignment) => {
    setSelectedAssignment(assignment);
    setView('practice');
  };

  if (view === 'practice' && selectedAssignment) {
    return (
      <AssignmentPractice
        assignment={selectedAssignment}
        onBack={() => {
          setView('list');
          setSelectedAssignment(null);
          loadAssignments(); // Reload to get updated progress
        }}
      />
    );
  }

  // Separate assignments by status
  const activeAssignments = assignments.filter(a => !a.completed_at && !a.is_overdue);
  const completedAssignments = assignments.filter(a => a.completed_at);
  const overdueAssignments = assignments.filter(a => !a.completed_at && a.is_overdue);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">我的作业</h1>
          {onBackToDashboard && (
            <button
              onClick={onBackToDashboard}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <Home className="w-5 h-5 mr-2" />
              返回仪表盘
            </button>
          )}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">正在加载作业...</p>
          </div>
        ) : assignments.length === 0 ? (
          <div className="card text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">目前没有作业</h3>
            <p className="text-gray-600">
              你的老师还没有布置单词练习作业。
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Overdue Assignments */}
            {overdueAssignments.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-red-700 mb-4 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  已逾期（{overdueAssignments.length}）
                </h2>
                <div className="grid grid-cols-1 gap-4">
                  {overdueAssignments.map((assignment) => (
                    <AssignmentCard
                      key={assignment.id}
                      assignment={assignment}
                      onStartPractice={startPractice}
                      variant="overdue"
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Active Assignments */}
            {activeAssignments.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  进行中（{activeAssignments.length}）
                </h2>
                <div className="grid grid-cols-1 gap-4">
                  {activeAssignments.map((assignment) => (
                    <AssignmentCard
                      key={assignment.id}
                      assignment={assignment}
                      onStartPractice={startPractice}
                      variant="active"
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Completed Assignments */}
            {completedAssignments.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-green-700 mb-4 flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  已完成（{completedAssignments.length}）
                </h2>
                <div className="grid grid-cols-1 gap-4">
                  {completedAssignments.map((assignment) => (
                    <AssignmentCard
                      key={assignment.id}
                      assignment={assignment}
                      onStartPractice={startPractice}
                      variant="completed"
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function AssignmentCard({ assignment, onStartPractice, variant }) {
  const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;

  const variantStyles = {
    overdue: 'border-red-300 bg-red-50',
    active: 'border-gray-200 bg-white hover:shadow-lg',
    completed: 'border-green-300 bg-green-50'
  };

  return (
    <div className={`card ${variantStyles[variant]} transition-shadow cursor-pointer`}
         onClick={() => onStartPractice(assignment)}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-xl font-semibold text-gray-900">{assignment.title}</h3>
            {variant === 'overdue' && (
              <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full flex items-center">
                <AlertCircle className="w-3 h-3 mr-1" />
                已逾期
              </span>
            )}
            {variant === 'completed' && (
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full flex items-center">
                <CheckCircle className="w-3 h-3 mr-1" />
                已完成
              </span>
            )}
          </div>

          {assignment.description && (
            <p className="text-gray-600 mb-4">{assignment.description}</p>
          )}

          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            {assignment.teacher_name && (
              <div>教师：<span className="font-medium">{assignment.teacher_name}</span></div>
            )}
            {assignment.word_database_name && (
              <div className="flex items-center">
                <BookOpen className="w-4 h-4 mr-1" />
                {assignment.word_database_name}
              </div>
            )}
            <div className="flex items-center">
              <BookOpen className="w-4 h-4 mr-1" />
              {assignment.total_words} 个单词
            </div>
            {dueDate && (
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                截止：{dueDate.toLocaleDateString()}
              </div>
            )}
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">进度</span>
              <span className="text-sm font-semibold text-primary-600">
                {assignment.completed_words}/{assignment.total_words} 个单词
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  assignment.completion_percentage === 100
                    ? 'bg-green-600'
                    : assignment.completion_percentage >= 50
                    ? 'bg-blue-600'
                    : 'bg-yellow-600'
                }`}
                style={{ width: `${assignment.completion_percentage}%` }}
              ></div>
            </div>
            <div className="text-right mt-1">
              <span className="text-sm text-gray-600">{assignment.completion_percentage.toFixed(0)}%</span>
            </div>
          </div>
        </div>

        <ChevronRight className="w-6 h-6 text-gray-400 ml-4 flex-shrink-0" />
      </div>
    </div>
  );
}

export default AssignmentList;
