import { useState, useEffect } from 'react';
import { Search, TrendingUp, Award, Flame, BookOpen } from 'lucide-react';
import Navbar from '../Common/Navbar';
import RecordingInterface from './RecordingInterface';
import AssignmentList from './AssignmentList';
import wordService from '../../services/wordService';
import studentService from '../../services/studentService';

function StudentDashboard() {
  const [activeTab, setActiveTab] = useState('practice');
  const [word, setWord] = useState('');
  const [wordData, setWordData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(null);
  const [recentRecordings, setRecentRecordings] = useState([]);

  useEffect(() => {
    loadDailyWord();
    loadProgress();
    loadRecentRecordings();
  }, []);

  const loadDailyWord = async () => {
    try {
      const data = await wordService.getDailyWord();
      setWordData(data);
      setWord(data.word);
    } catch (error) {
      console.error('Error loading daily word:', error);
    }
  };

  const loadProgress = async () => {
    try {
      const data = await studentService.getMyProgress('week');
      setProgress(data);
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  };

  const loadRecentRecordings = async () => {
    try {
      const data = await studentService.getMyRecordings();
      setRecentRecordings(data.slice(0, 5));
    } catch (error) {
      console.error('Error loading recordings:', error);
    }
  };

  const searchWord = async (e) => {
    e.preventDefault();
    if (!word.trim()) return;

    setLoading(true);
    setError('');
    setWordData(null);

    try {
      const data = await wordService.getWord(word);
      setWordData(data);
    } catch (err) {
      setError('Word not found. Please try another word.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecordingComplete = () => {
    loadProgress();
    loadRecentRecordings();
  };

  // Render Assignments tab as full component
  if (activeTab === 'assignments') {
    return <AssignmentList onBackToDashboard={() => setActiveTab('practice')} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('practice')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'practice'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Practice
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
            onClick={() => setActiveTab('progress')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'progress'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            My Progress
          </button>
        </div>

        {activeTab === 'practice' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Word Practice */}
            <div className="lg:col-span-2 space-y-6">
              {/* Search Word */}
              <div className="card">
                <h2 className="text-xl font-bold mb-4">Practice a Word</h2>
                <form onSubmit={searchWord} className="flex gap-2">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={word}
                      onChange={(e) => setWord(e.target.value)}
                      className="input-field pl-10"
                      placeholder="Enter a word to practice..."
                    />
                  </div>
                  <button type="submit" className="btn-primary" disabled={loading}>
                    {loading ? 'Searching...' : 'Search'}
                  </button>
                </form>
                {error && (
                  <p className="mt-2 text-sm text-red-600">{error}</p>
                )}
              </div>

              {/* Word Display */}
              {wordData && (
                <div className="card">
                  <h3 className="text-3xl font-bold text-gray-900 mb-2">
                    {wordData.word}
                  </h3>
                  {wordData.phonetic && (
                    <p className="text-lg text-gray-600 mb-4">{wordData.phonetic}</p>
                  )}

                  {wordData.difficulty_level && (
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-4 ${
                      wordData.difficulty_level === 'beginner'
                        ? 'bg-green-100 text-green-800'
                        : wordData.difficulty_level === 'intermediate'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {wordData.difficulty_level}
                    </span>
                  )}

                  {wordData.meanings && wordData.meanings.length > 0 && (
                    <div className="space-y-3">
                      <div>
                        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded mb-2">
                          {wordData.meanings[0].partOfSpeech}
                        </span>
                        <p className="text-gray-700">
                          <strong>Definition:</strong> {wordData.meanings[0].definition}
                        </p>
                      </div>
                      {wordData.meanings[0].example && (
                        <p className="text-gray-600 italic">
                          <strong>Example:</strong> "{wordData.meanings[0].example}"
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Recording Interface */}
              {wordData && (
                <RecordingInterface
                  word={wordData.word}
                  wordData={wordData}
                  onRecordingComplete={handleRecordingComplete}
                />
              )}
            </div>

            {/* Right: Stats & Recent */}
            <div className="space-y-6">
              {/* Progress Stats */}
              {progress && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">This Week</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <TrendingUp className="w-5 h-5 text-green-500 mr-2" />
                        <span className="text-sm text-gray-600">Words Practiced</span>
                      </div>
                      <span className="text-2xl font-bold text-gray-900">
                        {progress.words_practiced}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Award className="w-5 h-5 text-yellow-500 mr-2" />
                        <span className="text-sm text-gray-600">Avg Score</span>
                      </div>
                      <span className="text-2xl font-bold text-gray-900">
                        {progress.average_score}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Flame className="w-5 h-5 text-orange-500 mr-2" />
                        <span className="text-sm text-gray-600">Streak</span>
                      </div>
                      <span className="text-2xl font-bold text-gray-900">
                        {progress.streak_count} days
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Recent Recordings */}
              {recentRecordings.length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Recent Practice</h3>
                  <div className="space-y-3">
                    {recentRecordings.map((recording) => (
                      <div
                        key={recording.id}
                        className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-gray-900">
                              {recording.word_text}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {new Date(recording.created_at).toLocaleDateString()}
                            </div>
                          </div>
                          {recording.automated_scores && (
                            <div className="text-right">
                              <div className="text-lg font-bold text-primary-600">
                                {recording.automated_scores.pronunciation_score?.toFixed(0)}%
                              </div>
                              {recording.teacher_grade && (
                                <div className="text-sm text-gray-600">
                                  Grade: {recording.teacher_grade}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'progress' && (
          <div className="card">
            <h2 className="text-2xl font-bold mb-6">My Progress</h2>
            {progress && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                  <TrendingUp className="w-12 h-12 text-blue-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-gray-900">
                    {progress.words_practiced}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Words Practiced</div>
                </div>
                <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                  <Award className="w-12 h-12 text-green-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-gray-900">
                    {progress.average_score}%
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Average Score</div>
                </div>
                <div className="text-center p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg">
                  <Flame className="w-12 h-12 text-orange-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-gray-900">
                    {progress.streak_count}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Day Streak</div>
                </div>
              </div>
            )}

            <h3 className="text-xl font-semibold mb-4">All Recordings</h3>
            <div className="space-y-3">
              {recentRecordings.map((recording) => (
                <div
                  key={recording.id}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold text-lg text-gray-900">
                        {recording.word_text}
                      </div>
                      <div className="text-sm text-gray-500 mt-1">
                        {new Date(recording.created_at).toLocaleString()}
                      </div>
                      {recording.teacher_feedback && (
                        <div className="mt-2 text-sm text-gray-700">
                          <strong>Feedback:</strong> {recording.teacher_feedback}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary-600">
                        {recording.automated_scores?.pronunciation_score?.toFixed(0) || 'N/A'}%
                      </div>
                      {recording.teacher_grade && (
                        <div className="text-lg font-medium text-gray-900 mt-1">
                          {recording.teacher_grade}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default StudentDashboard;
