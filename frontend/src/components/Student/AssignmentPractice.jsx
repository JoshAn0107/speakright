import { useState, useEffect, useRef } from 'react';
import { ArrowLeft, ChevronLeft, ChevronRight, Trophy, BookOpen, CheckCircle, Circle } from 'lucide-react';
import Navbar from '../Common/Navbar';
import RecordingInterface from './RecordingInterface';
import assignmentService from '../../services/assignmentService';
import studentService from '../../services/studentService';

function AssignmentPractice({ assignment, onBack }) {
  const [assignmentDetails, setAssignmentDetails] = useState(null);
  const [progress, set进度] = useState(null);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  // background scoring: judge each word while the student keeps recording
  const [wordStatus, setWordStatus] = useState({}); // word -> {status: queued|scoring|scored|error, score, grade, feedback, error}
  const [phase, setPhase] = useState('practice'); // practice | submitting | done
  const jobsRef = useRef({ queue: [], active: 0, versions: {} });

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
      set进度(progressData);

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

  const pumpQueue = () => {
    const jobs = jobsRef.current;
    while (jobs.active < 2 && jobs.queue.length > 0) {
      const job = jobs.queue.shift();
      // student re-recorded this word after it was queued — skip the stale job
      if (jobs.versions[job.word] !== job.version) continue;
      jobs.active += 1;
      (async () => {
        try {
          const resp = await studentService.submitRecording(job.word, job.blob);
          await assignmentService.submitAssignmentWord(assignment.id, job.word, resp.recording_id);
          if (jobsRef.current.versions[job.word] === job.version) {
            setWordStatus((prev) => ({
              ...prev,
              [job.word]: {
                status: 'scored',
                score: resp.automated_scores?.pronunciation_score,
                grade: resp.feedback?.grade,
                feedback: resp.feedback?.text,
              },
            }));
          }
        } catch (error) {
          if (jobsRef.current.versions[job.word] === job.version) {
            setWordStatus((prev) => ({
              ...prev,
              [job.word]: { status: 'error', error: error.response?.data?.detail || '评分失败' },
            }));
          }
        } finally {
          jobsRef.current.active -= 1;
          pumpQueue();
        }
      })();
    }
  };

  const handleAudioSaved = (blob) => {
    const words = progress?.words || [];
    const word = words[currentWordIndex];
    if (!word) return;
    const jobs = jobsRef.current;
    jobs.versions[word.word_text] = (jobs.versions[word.word_text] || 0) + 1;
    jobs.queue.push({ word: word.word_text, blob, version: jobs.versions[word.word_text] });
    setWordStatus((prev) => ({ ...prev, [word.word_text]: { status: 'scoring' } }));
    pumpQueue();
    // auto-advance to the next word not yet recorded or submitted
    for (let step = 1; step <= words.length; step++) {
      const idx = (currentWordIndex + step) % words.length;
      const w = words[idx];
      if (!w.submitted && !wordStatus[w.word_text] && w.word_text !== word.word_text) {
        setCurrentWordIndex(idx);
        return;
      }
    }
  };

  const handleFinish = () => {
    const recordedCount = Object.keys(wordStatus).length;
    if (recordedCount === 0) return;
    const words = progress?.words || [];
    const notRecorded = words.filter((w) => !w.submitted && !wordStatus[w.word_text]).length;
    if (notRecorded > 0) {
      if (!window.confirm(`还有 ${notRecorded} 个单词没有录音，确定完成吗？`)) return;
    }
    setPhase('submitting');
  };

  // while on the waiting screen, move to the report as soon as all scoring finishes
  useEffect(() => {
    if (phase !== 'submitting') return;
    const pending = Object.values(wordStatus).filter((v) => v.status === 'scoring' || v.status === 'queued').length;
    if (pending === 0 && jobsRef.current.active === 0 && jobsRef.current.queue.length === 0) {
      setPhase('done');
      assignmentService.getStudentAssignmentProgress(assignment.id)
        .then(set进度)
        .catch(() => {});
    }
  }, [phase, wordStatus]);

  const goTo上一个 = () => {
    if (currentWordIndex > 0) {
      setCurrentWordIndex(currentWordIndex - 1);
    }
  };

  const goTo下一个 = () => {
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
            <p className="mt-4 text-gray-600">正在加载作业...</p>
          </div>
        </div>
      </div>
    );
  }

  const words = progress?.words || [];
  const currentWord = words[currentWordIndex];
  const isCompleted = progress && progress.completed_words >= progress.total_words;

  if (phase === 'submitting') {
    const all = Object.values(wordStatus);
    const doneCount = all.filter((v) => v.status === 'scored' || v.status === 'error').length;
    const pct = all.length ? Math.round((doneCount / all.length) * 100) : 0;
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 py-16">
          <div className="card text-center">
            <div className="animate-spin rounded-full h-14 w-14 border-b-2 border-primary-600 mx-auto mb-6"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">马上就好...</h2>
            <p className="text-gray-600 mb-6">
              大部分单词在你朗读时已经评完分了，正在等最后 {all.length - doneCount} 个
            </p>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div className="h-3 rounded-full bg-primary-600 transition-all" style={{ width: `${pct}%` }}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (phase === 'done') {
    const order = (progress?.words || []).map((w) => w.word_text);
    const batchResults = Object.entries(wordStatus)
      .map(([word, v]) => ({ word, ...v }))
      .sort((a, b) => order.indexOf(a.word) - order.indexOf(b.word));
    const scored = batchResults.filter((r) => r.score != null);
    const avg = scored.length ? scored.reduce((a, r) => a + r.score, 0) / scored.length : 0;
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-8">
          <div className="card bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 mb-6 text-center">
            <Trophy className="w-14 h-14 text-green-600 mx-auto mb-3" />
            <h2 className="text-2xl font-bold text-gray-900 mb-1">评分完成！</h2>
            <p className="text-gray-700">
              本次提交 {batchResults.length} 个单词，平均分{' '}
              <span className="font-bold text-primary-700">{avg.toFixed(0)}</span>
            </p>
          </div>

          <div className="card">
            <h3 className="font-semibold text-lg mb-4">本次成绩单</h3>
            <div className="divide-y divide-gray-100">
              {batchResults.map((r) => (
                <div key={r.word} className="py-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">{r.word}</span>
                    {r.error ? (
                      <span className="text-sm text-red-600">{r.error}</span>
                    ) : (
                      <span className={`text-lg font-bold ${r.score >= 80 ? 'text-green-600' : r.score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {r.score?.toFixed(0)} 分{r.grade ? `（${r.grade}）` : ''}
                      </span>
                    )}
                  </div>
                  {r.feedback && (
                    <p className="text-sm text-gray-600 mt-1">{r.feedback}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <button onClick={() => setPhase('practice')} className="flex-1 btn-secondary">
              继续练习
            </button>
            <button onClick={onBack} className="flex-1 btn-primary">
              返回作业列表
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          返回作业列表
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

          {/* 进度 Bar */}
          {progress && (
            <div className="mt-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">进度</span>
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
              <h2 className="text-2xl font-bold text-gray-900 mb-2">恭喜！</h2>
              <p className="text-gray-700">
                你已完成本次作业的全部单词！
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
                  onClick={goTo上一个}
                  disabled={currentWordIndex === 0}
                  className="flex items-center px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5 mr-1" />
                  上一个
                </button>

                <div className="text-center flex-1">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <h2 className="text-3xl font-bold text-gray-900">{currentWord.word_text}</h2>
                    {currentWord.submitted && (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600">
                    第 {currentWordIndex + 1} / {words.length} 个单词
                  </p>
                  {currentWord.submitted && currentWord.score && (
                    <p className="text-sm text-green-600 font-medium mt-1">
                      上次得分： {currentWord.score}
                    </p>
                  )}
                </div>

                <button
                  onClick={goTo下一个}
                  disabled={currentWordIndex === words.length - 1}
                  className="flex items-center px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  下一个
                  <ChevronRight className="w-5 h-5 ml-1" />
                </button>
              </div>

              {/* Word 进度 Dots */}
              <div className="flex justify-center gap-2 mt-4 flex-wrap">
                {words.map((word, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentWordIndex(index)}
                    className={`w-3 h-3 rounded-full transition-all ${
                      index === currentWordIndex
                        ? 'w-8 bg-primary-600'
                        : wordStatus[word.word_text]?.status === 'scored' || word.submitted
                        ? 'bg-green-500'
                        : wordStatus[word.word_text]?.status === 'scoring'
                        ? 'bg-blue-400 animate-pulse'
                        : wordStatus[word.word_text]?.status === 'error'
                        ? 'bg-red-400'
                        : 'bg-gray-300'
                    }`}
                    title={`${word.word_text}${word.submitted || wordStatus[word.word_text]?.status === 'scored' ? '（已评分）' : wordStatus[word.word_text]?.status === 'scoring' ? '（评分中）' : wordStatus[word.word_text]?.status === 'error' ? '（失败，请重录）' : ''}`}
                  />
                ))}
              </div>
            </div>

            {/* Recording Interface (batch: save locally, judge all at the end) */}
            {wordStatus[currentWord.word_text] && (
              <div className="card bg-blue-50 border border-blue-200 text-sm text-blue-800">
                {wordStatus[currentWord.word_text].status === 'scoring' && '这个单词已保存，正在后台评分…重新录音会覆盖。'}
                {wordStatus[currentWord.word_text].status === 'scored' && '这个单词已评分完成 ✓ 重新录音会覆盖成绩。'}
                {wordStatus[currentWord.word_text].status === 'error' && '⚠️ 这个单词评分失败，请重新录音提交。'}
              </div>
            )}
            <RecordingInterface
              word={currentWord.word_text}
              wordData={null}
              batchMode={true}
              onAudioSaved={handleAudioSaved}
            />

            {/* Finish bar: scoring happens in the background while recording */}
            <div className="card border-2 border-primary-200 bg-primary-50">
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div className="text-sm text-gray-700">
                  已录 <span className="font-bold text-primary-700">{Object.keys(wordStatus).length}</span> 个
                  · 已评分 <span className="font-bold text-green-700">{Object.values(wordStatus).filter((v) => v.status === 'scored').length}</span> 个
                  {progress && (
                    <span className="text-gray-500">
                      · 还剩 {words.filter((w) => !w.submitted && !wordStatus[w.word_text]).length} 个未录
                    </span>
                  )}
                </div>
                <button
                  onClick={handleFinish}
                  disabled={Object.keys(wordStatus).length === 0}
                  className="btn-primary disabled:opacity-50 px-6"
                >
                  完成作业，查看成绩单
                </button>
              </div>
            </div>

            {/* Quick Navigation Grid */}
            <div className="card">
              <h3 className="font-semibold text-lg mb-4 flex items-center">
                <BookOpen className="w-5 h-5 mr-2" />
                全部单词
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
