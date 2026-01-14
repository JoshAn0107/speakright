import { useState } from 'react';
import { ArrowLeft, Save, Flag, Volume2 } from 'lucide-react';
import Navbar from '../Common/Navbar';
import teacherService from '../../services/teacherService';

function ReviewSubmission({ submission, onBack, onFeedbackSubmitted }) {
  const [feedbackText, setFeedbackText] = useState(submission.teacher_feedback || '');
  const [grade, setGrade] = useState(submission.teacher_grade || '');
  const [flagForPractice, setFlagForPractice] = useState(submission.flag_for_practice || false);
  const [submitting, setSubmitting] = useState(false);

  const playAudio = () => {
    if (submission.audio_file_path) {
      // Use relative path - Vite proxy will handle routing to backend
      const audioUrl = `/${submission.audio_file_path}`;
      const audio = new Audio(audioUrl);
      audio.play().catch(err => {
        console.error('Error playing audio:', err);
        alert('Could not play audio file');
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await teacherService.submitFeedback(
        submission.id,
        feedbackText,
        grade,
        flagForPractice
      );
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted();
      }
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

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Submissions
        </button>

        {/* Student Info & Word */}
        <div className="card mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {submission.word_text}
              </h1>
              <p className="text-gray-600">
                Student: <span className="font-medium">{submission.student_name}</span>
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Submitted: {new Date(submission.created_at).toLocaleString()}
              </p>
            </div>
            <div>
              {submission.is_automated_feedback ? (
                <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                  AI-Generated Feedback
                </span>
              ) : (
                <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                  Manually Reviewed
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Audio Player */}
        <div className="card mb-6 bg-gradient-to-br from-purple-50 to-purple-100">
          <h3 className="font-semibold mb-4">Student Recording</h3>
          <button
            onClick={playAudio}
            className="btn-primary flex items-center"
          >
            <Volume2 className="w-5 h-5 mr-2" />
            Play Recording
          </button>
        </div>

        {/* Automated Scores */}
        <div className="card mb-6">
          <h3 className="font-semibold text-lg mb-4">Automated Assessment</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Pronunciation</div>
              <div className="text-3xl font-bold text-primary-600">
                {submission.automated_scores?.pronunciation_score?.toFixed(0) || 0}%
              </div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Accuracy</div>
              <div className="text-3xl font-bold text-green-600">
                {submission.automated_scores?.accuracy_score?.toFixed(0) || 0}%
              </div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Fluency</div>
              <div className="text-3xl font-bold text-yellow-600">
                {submission.automated_scores?.fluency_score?.toFixed(0) || 0}%
              </div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Completeness</div>
              <div className="text-3xl font-bold text-purple-600">
                {submission.automated_scores?.completeness_score?.toFixed(0) || 0}%
              </div>
            </div>
          </div>

          {/* Phoneme Breakdown */}
          {submission.automated_scores?.words?.[0]?.phonemes && (
            <div className="mt-6">
              <h4 className="font-medium mb-3">Phoneme Analysis</h4>
              <div className="flex flex-wrap gap-2">
                {submission.automated_scores.words[0].phonemes.map((phoneme, index) => (
                  <div
                    key={index}
                    className={`px-3 py-2 rounded-lg ${
                      phoneme.accuracy_score >= 80
                        ? 'bg-green-100 text-green-800'
                        : phoneme.accuracy_score >= 60
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    <div className="font-mono font-medium">{phoneme.phoneme}</div>
                    <div className="text-xs">{phoneme.accuracy_score}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Current AI Feedback */}
        {submission.teacher_feedback && submission.is_automated_feedback && (
          <div className="card mb-6 bg-blue-50 border border-blue-200">
            <h3 className="font-semibold mb-3">Current AI Feedback</h3>
            <p className="text-gray-700 whitespace-pre-line">{submission.teacher_feedback}</p>
            {submission.teacher_grade && (
              <p className="mt-2 text-sm">
                <strong>Grade:</strong> {submission.teacher_grade}
              </p>
            )}
          </div>
        )}

        {/* Teacher Feedback Form */}
        <form onSubmit={handleSubmit} className="card">
          <h3 className="font-semibold text-lg mb-4">
            {submission.is_automated_feedback ? 'Modify or Add Feedback' : 'Your Feedback'}
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Feedback Text
              </label>
              <textarea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                className="input-field"
                rows="6"
                placeholder={
                  submission.is_automated_feedback
                    ? 'Add your personal comments to the AI-generated feedback...'
                    : 'Enter your feedback for the student...'
                }
              />
              <p className="mt-1 text-xs text-gray-500">
                {submission.is_automated_feedback
                  ? 'Your feedback will replace the AI-generated feedback'
                  : 'Provide constructive feedback to help the student improve'}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Grade
                </label>
                <select
                  value={grade}
                  onChange={(e) => setGrade(e.target.value)}
                  className="input-field"
                >
                  <option value="">Select grade...</option>
                  {gradeOptions.map((g) => (
                    <option key={g} value={g}>
                      {g}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center pt-6">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={flagForPractice}
                    onChange={(e) => setFlagForPractice(e.target.checked)}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <Flag className="w-5 h-5 ml-2 mr-1 text-orange-500" />
                  <span className="text-sm font-medium text-gray-700">
                    Flag for Additional Practice
                  </span>
                </label>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onBack}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 btn-primary disabled:opacity-50 flex items-center justify-center"
              >
                <Save className="w-5 h-5 mr-2" />
                {submitting ? 'Saving...' : 'Save Feedback'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ReviewSubmission;
