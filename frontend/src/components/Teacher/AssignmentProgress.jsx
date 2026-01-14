import { useState, useEffect } from 'react';
import { ArrowLeft, Users, CheckCircle, Clock, TrendingUp, Volume2, Eye, MessageSquare, Award, ChevronRight } from 'lucide-react';
import Navbar from '../Common/Navbar';
import assignmentService from '../../services/assignmentService';
import teacherService from '../../services/teacherService';

function AssignmentProgress({ assignment, onBack }) {
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentDetails, setStudentDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    loadProgress();
  }, [assignment.id]);

  const loadProgress = async () => {
    try {
      setLoading(true);
      const data = await assignmentService.getAssignmentProgress(assignment.id);
      setProgress(data);
    } catch (error) {
      console.error('Error loading progress:', error);
      alert('Failed to load assignment progress');
    } finally {
      setLoading(false);
    }
  };

  const loadStudentDetails = async (studentId) => {
    try {
      setLoadingDetails(true);
      // Get student's assignment progress with all word submissions (using teacher endpoint)
      const progressData = await assignmentService.getStudentProgressForTeacher(assignment.id, studentId);

      // Get all submissions for this student (to get recording details with feedback)
      const submissions = await teacherService.getSubmissions();
      const studentSubmissions = submissions.filter(
        sub => sub.student_id === studentId &&
        progressData.words.map(w => w.word_text).includes(sub.word_text)
      );

      setStudentDetails({
        progress: progressData,
        submissions: studentSubmissions,
        studentInfo: progress.find(p => p.student_id === studentId)
      });
    } catch (error) {
      console.error('Error loading student details:', error);
      alert('Failed to load student details');
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleViewStudent = (studentProgress) => {
    setSelectedStudent(studentProgress.student_id);
    loadStudentDetails(studentProgress.student_id);
  };

  const handleBackToProgress = () => {
    setSelectedStudent(null);
    setStudentDetails(null);
    loadProgress(); // Reload to get updated progress
  };

  const handleFeedbackSubmitted = () => {
    loadStudentDetails(selectedStudent);
  };

  // If viewing student details
  if (selectedStudent && studentDetails) {
    return (
      <StudentDetailView
        assignment={assignment}
        studentDetails={studentDetails}
        onBack={handleBackToProgress}
        onFeedbackSubmitted={handleFeedbackSubmitted}
      />
    );
  }

  if (loadingDetails) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading student details...</p>
          </div>
        </div>
      </div>
    );
  }

  const averageCompletion = progress.length > 0
    ? Math.round(progress.reduce((sum, p) => sum + p.completion_percentage, 0) / progress.length)
    : 0;

  const completedStudents = progress.filter(p => p.completion_percentage === 100).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Assignments
        </button>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{assignment.title}</h1>
          {assignment.description && (
            <p className="text-gray-600">{assignment.description}</p>
          )}
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
            <Users className="w-8 h-8 text-blue-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">{progress.length}</div>
            <div className="text-sm text-gray-600">Total Students</div>
          </div>

          <div className="card bg-gradient-to-br from-green-50 to-green-100">
            <CheckCircle className="w-8 h-8 text-green-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">{completedStudents}</div>
            <div className="text-sm text-gray-600">Completed</div>
          </div>

          <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
            <Clock className="w-8 h-8 text-yellow-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">
              {progress.length - completedStudents}
            </div>
            <div className="text-sm text-gray-600">In Progress</div>
          </div>

          <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
            <TrendingUp className="w-8 h-8 text-purple-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">{averageCompletion}%</div>
            <div className="text-sm text-gray-600">Avg. Completion</div>
          </div>
        </div>

        {/* Student Progress Table */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Student Progress</h2>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading progress...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Progress
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Completed Words
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Assigned Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {progress.map((studentProgress) => (
                    <tr key={studentProgress.student_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">
                          {studentProgress.student_name}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="flex-1">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full transition-all ${
                                  studentProgress.completion_percentage === 100
                                    ? 'bg-green-600'
                                    : studentProgress.completion_percentage >= 50
                                    ? 'bg-blue-600'
                                    : 'bg-yellow-600'
                                }`}
                                style={{ width: `${studentProgress.completion_percentage}%` }}
                              ></div>
                            </div>
                          </div>
                          <span className="ml-3 text-sm font-medium text-gray-700">
                            {studentProgress.completion_percentage.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {studentProgress.completed_words} / {studentProgress.total_words}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(studentProgress.assigned_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {studentProgress.completed_at ? (
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Completed
                          </span>
                        ) : (
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                            <Clock className="w-3 h-3 mr-1" />
                            In Progress
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => handleViewStudent(studentProgress)}
                          className="flex items-center text-primary-600 hover:text-primary-700 font-medium"
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          View & Review
                          <ChevronRight className="w-4 h-4 ml-1" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Student Detail View Component
function StudentDetailView({ assignment, studentDetails, onBack, onFeedbackSubmitted }) {
  const [selectedWord, setSelectedWord] = useState(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [grade, setGrade] = useState('');
  const [flagForPractice, setFlagForPractice] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const { progress, submissions, studentInfo } = studentDetails;

  const getSubmissionForWord = (wordText) => {
    return submissions.find(sub => sub.word_text === wordText);
  };

  const handleSelectWord = (word) => {
    const submission = getSubmissionForWord(word.word_text);
    setSelectedWord(word);
    if (submission) {
      setFeedbackText(submission.teacher_feedback || submission.automated_feedback || '');
      setGrade(submission.teacher_grade || submission.automated_grade || '');
      setFlagForPractice(submission.flag_for_practice || false);
    } else {
      setFeedbackText('');
      setGrade('');
      setFlagForPractice(false);
    }
  };

  const playAudio = (audioPath) => {
    if (audioPath) {
      const audioUrl = `/${audioPath}`;
      const audio = new Audio(audioUrl);
      audio.play().catch(err => {
        console.error('Error playing audio:', err);
        alert('Could not play audio file');
      });
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    const submission = getSubmissionForWord(selectedWord.word_text);
    if (!submission) {
      alert('No recording found for this word');
      return;
    }

    setSubmitting(true);
    try {
      await teacherService.submitFeedback(
        submission.id,
        feedbackText,
        grade,
        flagForPractice
      );
      alert('Feedback submitted successfully!');
      onFeedbackSubmitted();
      setSelectedWord(null);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const gradeOptions = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F'];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Progress
        </button>

        {/* Student Header */}
        <div className="card mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {studentInfo?.student_name}
              </h1>
              <p className="text-gray-600 mb-2">Assignment: {assignment.title}</p>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>
                  Progress: <strong>{progress.completed_words}/{progress.total_words} words</strong>
                </span>
                <span>•</span>
                <span>
                  <strong>{progress.completion_percentage.toFixed(0)}%</strong> complete
                </span>
              </div>
            </div>
            {studentInfo?.completed_at && (
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                Completed
              </span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Word List */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <MessageSquare className="w-5 h-5 mr-2" />
              Words & Recordings
            </h2>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {progress.words?.map((word) => {
                const submission = getSubmissionForWord(word.word_text);
                const hasReview = submission && submission.teacher_feedback;

                return (
                  <button
                    key={word.word_text}
                    onClick={() => handleSelectWord(word)}
                    className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                      selectedWord?.word_text === word.word_text
                        ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                        : word.submitted
                        ? 'border-green-300 bg-green-50 hover:border-green-400'
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{word.word_text}</span>
                          {word.submitted && <CheckCircle className="w-4 h-4 text-green-600" />}
                          {hasReview && <Award className="w-4 h-4 text-blue-600" />}
                        </div>
                        {word.score && (
                          <p className="text-sm text-gray-600 mt-1">
                            Score: <span className="font-medium">{word.score}</span>
                          </p>
                        )}
                      </div>
                      {word.submitted && submission && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            playAudio(submission.audio_file_path);
                          }}
                          className="p-2 text-purple-600 hover:bg-purple-100 rounded-lg transition-colors"
                        >
                          <Volume2 className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Review Panel */}
          <div className="card">
            {selectedWord ? (
              <>
                <h2 className="text-xl font-semibold mb-4">
                  Review: {selectedWord.word_text}
                </h2>

                {!selectedWord.submitted ? (
                  <div className="text-center py-12 text-gray-500">
                    <Clock className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                    <p>Student hasn't recorded this word yet</p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmitFeedback} className="space-y-6">
                    {/* Audio Player */}
                    <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                      <h3 className="font-semibold mb-3">Student Recording</h3>
                      <button
                        type="button"
                        onClick={() => playAudio(getSubmissionForWord(selectedWord.word_text)?.audio_file_path)}
                        className="btn-primary flex items-center"
                      >
                        <Volume2 className="w-5 h-5 mr-2" />
                        Play Recording
                      </button>
                    </div>

                    {/* Automated Scores */}
                    {getSubmissionForWord(selectedWord.word_text)?.automated_scores && (
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <h3 className="font-semibold mb-2">AI Assessment</h3>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div>
                            <span className="text-gray-600">Pronunciation:</span>
                            <span className="ml-2 font-semibold">
                              {getSubmissionForWord(selectedWord.word_text)?.automated_scores?.pronunciation_score || 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600">Accuracy:</span>
                            <span className="ml-2 font-semibold">
                              {getSubmissionForWord(selectedWord.word_text)?.automated_scores?.accuracy_score || 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600">Fluency:</span>
                            <span className="ml-2 font-semibold">
                              {getSubmissionForWord(selectedWord.word_text)?.automated_scores?.fluency_score || 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600">Completeness:</span>
                            <span className="ml-2 font-semibold">
                              {getSubmissionForWord(selectedWord.word_text)?.automated_scores?.completeness_score || 'N/A'}
                            </span>
                          </div>
                        </div>
                        {getSubmissionForWord(selectedWord.word_text)?.automated_feedback && (
                          <p className="mt-3 text-sm text-gray-700 p-2 bg-white rounded">
                            {getSubmissionForWord(selectedWord.word_text)?.automated_feedback}
                          </p>
                        )}
                      </div>
                    )}

                    {/* Feedback Form */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Your Feedback
                      </label>
                      <textarea
                        value={feedbackText}
                        onChange={(e) => setFeedbackText(e.target.value)}
                        rows="4"
                        className="input-field"
                        placeholder="Provide feedback to the student..."
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Grade
                      </label>
                      <select
                        value={grade}
                        onChange={(e) => setGrade(e.target.value)}
                        className="input-field"
                        required
                      >
                        <option value="">Select Grade</option>
                        {gradeOptions.map((g) => (
                          <option key={g} value={g}>{g}</option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="flagForPractice"
                        checked={flagForPractice}
                        onChange={(e) => setFlagForPractice(e.target.checked)}
                        className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                      />
                      <label htmlFor="flagForPractice" className="ml-2 text-sm text-gray-700">
                        Flag for additional practice
                      </label>
                    </div>

                    <button
                      type="submit"
                      disabled={submitting}
                      className="w-full btn-primary disabled:opacity-50 flex items-center justify-center"
                    >
                      {submitting ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Submitting...
                        </>
                      ) : (
                        'Submit Feedback'
                      )}
                    </button>
                  </form>
                )}
              </>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <Eye className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p>Select a word to review and provide feedback</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AssignmentProgress;
