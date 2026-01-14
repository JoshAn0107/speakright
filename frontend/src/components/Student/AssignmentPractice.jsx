import { useState, useEffect } from 'react';
import { ArrowLeft, ChevronLeft, ChevronRight, Trophy, BookOpen, CheckCircle, Circle } from 'lucide-react';
import Navbar from '../Common/Navbar';
import RecordingInterface from './RecordingInterface';
import assignmentService from '../../services/assignmentService';

function AssignmentPractice({ assignment, onBack }) {
  const [assignmentDetails, setAssignmentDetails] = useState(null);
  const [progress, setProgress] = useState(null);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAssignmentDetails();
  }, [assignment.id]);

  const loadAssignmentDetails = async () => {
    try {
      setLoading(true);
      const [details, progressData] = await Promise.all([
        assignmentService.getStudentAssignment(assignment.id),
        assignmentService.getStudentAssignmentProgress(assignment.id)
      ]);
      setAssignmentDetails(details);
      setProgress(progressData);

      // Find first uncompleted word or start at beginning
      if (progressData && progressData.words) {
        const firstUncompletedIndex = progressData.words.findIndex(w => !w.submitted);
        if (firstUncompletedIndex !== -1) {
          setCurrentWordIndex(firstUncompletedIndex);
        }
      }
    } catch (error) {
      console.error('Error loading assignment details:', error);
      alert('Failed to load assignment details');
    } finally {
      setLoading(false);
    }
  };

  const handleRecordingComplete = async (result) => {
    try {
      // Submit to assignment with the recording ID
      await assignmentService.submitAssignmentWord(
        assignment.id,
        currentWord.word_text,
        result.recording_id
      );

      // Reload progress
      const updatedProgress = await assignmentService.getStudentAssignmentProgress(assignment.id);
      setProgress(updatedProgress);

      // Auto-move to next word if not the last one
      if (currentWordIndex < words.length - 1) {
        setCurrentWordIndex(currentWordIndex + 1);
      }
    } catch (error) {
      console.error('Error submitting word:', error);
      alert('Failed to submit word. Please try again.');
    }
  };

  const goToPrevious = () => {
    if (currentWordIndex > 0) {
      setCurrentWordIndex(currentWordIndex - 1);
    }
  };

  const goToNext = () => {
    if (currentWordIndex < words.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading assignment...</p>
          </div>
        </div>
      </div>
    );
  }

  const words = progress?.words || [];
  const currentWord = words[currentWordIndex];
  const isCompleted = progress && progress.completed_words >= progress.total_words;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Assignments
        </button>

        {/* Assignment Header */}
        <div className="card mb-6">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{assignmentDetails?.title}</h1>
              {assignmentDetails?.description && (
                <p className="text-gray-600">{assignmentDetails.description}</p>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          {progress && (
            <div className="mt-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Progress</span>
                <span className="text-sm font-semibold text-primary-600">
                  {progress.completed_words}/{progress.total_words} words
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    progress.completion_percentage === 100
                      ? 'bg-green-600'
                      : progress.completion_percentage >= 50
                      ? 'bg-blue-600'
                      : 'bg-yellow-600'
                  }`}
                  style={{ width: `${progress.completion_percentage}%` }}
                ></div>
              </div>
              <div className="text-right mt-1">
                <span className="text-sm text-gray-600">{progress.completion_percentage.toFixed(0)}%</span>
              </div>
            </div>
          )}
        </div>

        {/* Completion Celebration */}
        {isCompleted && (
          <div className="card bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 mb-6">
            <div className="text-center">
              <Trophy className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Congratulations!</h2>
              <p className="text-gray-700">
                You've completed all words in this assignment!
              </p>
            </div>
          </div>
        )}

        {/* Word Navigation and Practice */}
        {currentWord && (
          <div className="space-y-6">
            {/* Word Navigation Header */}
            <div className="card">
              <div className="flex items-center justify-between">
                <button
                  onClick={goToPrevious}
                  disabled={currentWordIndex === 0}
                  className="flex items-center px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5 mr-1" />
                  Previous
                </button>

                <div className="text-center flex-1">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <h2 className="text-3xl font-bold text-gray-900">{currentWord.word_text}</h2>
                    {currentWord.submitted && (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600">
                    Word {currentWordIndex + 1} of {words.length}
                  </p>
                  {currentWord.submitted && currentWord.score && (
                    <p className="text-sm text-green-600 font-medium mt-1">
                      Previous score: {currentWord.score}
                    </p>
                  )}
                </div>

                <button
                  onClick={goToNext}
                  disabled={currentWordIndex === words.length - 1}
                  className="flex items-center px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  Next
                  <ChevronRight className="w-5 h-5 ml-1" />
                </button>
              </div>

              {/* Word Progress Dots */}
              <div className="flex justify-center gap-2 mt-4 flex-wrap">
                {words.map((word, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentWordIndex(index)}
                    className={`w-3 h-3 rounded-full transition-all ${
                      index === currentWordIndex
                        ? 'w-8 bg-primary-600'
                        : word.submitted
                        ? 'bg-green-500'
                        : 'bg-gray-300'
                    }`}
                    title={`${word.word_text}${word.submitted ? ' (completed)' : ''}`}
                  />
                ))}
              </div>
            </div>

            {/* Recording Interface */}
            <RecordingInterface
              word={currentWord.word_text}
              wordData={null}
              onRecordingComplete={handleRecordingComplete}
            />

            {/* Quick Navigation Grid */}
            <div className="card">
              <h3 className="font-semibold text-lg mb-4 flex items-center">
                <BookOpen className="w-5 h-5 mr-2" />
                All Words
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {words.map((word, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentWordIndex(index)}
                    className={`p-3 rounded-lg border-2 text-left transition-all ${
                      index === currentWordIndex
                        ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                        : word.submitted
                        ? 'border-green-300 bg-green-50 hover:border-green-400'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{word.word_text}</span>
                      {word.submitted ? (
                        <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                      ) : (
                        <Circle className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AssignmentPractice;
