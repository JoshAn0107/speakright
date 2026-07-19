import { useState, useRef, useEffect } from 'react';
import { ArrowLeft, Square, Trophy, AlertTriangle, Timer, Play } from 'lucide-react';
import Navbar from '../Common/Navbar';
import assignmentService from '../../services/assignmentService';

// 连读测试：倒计时后单词才出现并自动开始录音，限时朗读，停止即自动评分。
// 单词在开始前不可见、结束后立即提交——不给查词的时间窗口。
function ContinuousTest({ assignment, onBack }) {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [phase, setPhase] = useState('ready'); // ready | countdown | recording | scoring | done
  const [countdown, setCountdown] = useState(3);
  const [timeLeft, setTimeLeft] = useState(0);
  const [result, setResult] = useState(null);

  const audioContextRef = useRef(null);
  const streamRef = useRef(null);
  const processorRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const stoppedRef = useRef(false);

  useEffect(() => {
    assignmentService
      .getStudentAssignment(assignment.id)
      .then(setDetails)
      .catch(() => alert('加载作业失败'))
      .finally(() => setLoading(false));
    // 有历史成绩就先展示（比如上次提交后没等评分离开了）
    assignmentService.getContinuousResult(assignment.id).then((r) => {
      if (r.status === 'done') { setResult(r); setPhase('done'); }
      else if (r.status === 'scoring') { setPhase('submitted'); }
      else if (r.status === 'failed') { setResult({ failed: true, message: r.message }); setPhase('done'); }
    }).catch(() => {});
    return () => cleanup();
  }, [assignment.id]);

  const words = (details?.words || []).slice().sort((a, b) => a.order_index - b.order_index);
  const timeLimit = Math.max(30, words.length * 4); // 每词4秒，至少30秒

  const cleanup = () => {
    if (processorRef.current) { processorRef.current.disconnect(); processorRef.current = null; }
    if (audioContextRef.current) { audioContextRef.current.close(); audioContextRef.current = null; }
    if (streamRef.current) { streamRef.current.getTracks().forEach((t) => t.stop()); streamRef.current = null; }
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
  };

  const convertToWav = (audioData, sampleRate) => {
    const buffer = new ArrayBuffer(44 + audioData.length * 2);
    const view = new DataView(buffer);
    const writeString = (offset, str) => {
      for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
    };
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + audioData.length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, audioData.length * 2, true);
    let offset = 44;
    for (let i = 0; i < audioData.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, audioData[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }
    return new Blob([view], { type: 'audio/wav' });
  };

  const startTest = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true },
      });
      streamRef.current = stream;
    } catch {
      alert('无法访问麦克风，请授予权限。');
      return;
    }
    stoppedRef.current = false;
    setPhase('countdown');
    setCountdown(3);
    let n = 3;
    const tick = setInterval(() => {
      n -= 1;
      if (n <= 0) {
        clearInterval(tick);
        beginRecording();
      } else {
        setCountdown(n);
      }
    }, 1000);
  };

  const beginRecording = () => {
    const ctx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    audioContextRef.current = ctx;
    const source = ctx.createMediaStreamSource(streamRef.current);
    const processor = ctx.createScriptProcessor(4096, 1, 1);
    processorRef.current = processor;
    chunksRef.current = [];
    processor.onaudioprocess = (e) => {
      chunksRef.current.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    };
    source.connect(processor);
    processor.connect(ctx.destination);

    setPhase('recording');
    setTimeLeft(timeLimit);
    timerRef.current = setInterval(() => {
      setTimeLeft((v) => {
        if (v <= 1) {
          finishRecording();
          return 0;
        }
        return v - 1;
      });
    }, 1000);
  };

  const finishRecording = async () => {
    if (stoppedRef.current) return;
    stoppedRef.current = true;
    cleanup();

    if (chunksRef.current.length === 0) {
      setPhase('ready');
      return;
    }
    const total = chunksRef.current.reduce((a, c) => a + c.length, 0);
    const combined = new Float32Array(total);
    let off = 0;
    for (const c of chunksRef.current) { combined.set(c, off); off += c.length; }
    const blob = convertToWav(combined, 16000);

    setPhase('scoring');
    try {
      const data = await assignmentService.submitContinuous(assignment.id, blob);
      setResult(data);
      setPhase('done');
    } catch (error) {
      alert(error.response?.data?.detail || '提交失败，请重新测试');
      setPhase('ready');
    }
  };

  const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  const timePct = timeLimit ? (timeLeft / timeLimit) * 100 : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="text-center py-16 text-gray-500">正在加载...</div>
      </div>
    );
  }

  if (phase === 'done' && result) {
    if (result.failed) {
      return (
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <div className="max-w-xl mx-auto px-4 py-20 text-center">
            <div className="card">
              <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-900 mb-2">这次没评好</h2>
              <p className="text-gray-600 text-sm mb-6">{result.message || '可以重新测试，或等老师人工评分'}</p>
              <div className="flex gap-3">
                <button onClick={() => { setResult(null); setPhase('ready'); }} className="flex-1 btn-secondary">
                  重新测试
                </button>
                <button onClick={onBack} className="flex-1 btn-primary">
                  返回作业列表
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }
    const missed = (result.per_word || []).filter((w) => w.error === '漏读');
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-8">
          <div className="card bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 mb-6 text-center">
            <Trophy className="w-14 h-14 text-green-600 mx-auto mb-3" />
            <h2 className="text-2xl font-bold text-gray-900 mb-1">连读测试完成</h2>
            <p className="text-4xl font-bold text-primary-700 my-2">
              {Number(result.pronunciation_score ?? 0).toFixed(0)}
              <span className="text-lg text-gray-500 ml-1">分（{result.grade}）</span>
            </p>
            <p className="text-gray-700">
              读到 {result.words_read}/{result.words_total} 个单词
              · 完整度 {result.completeness_score?.toFixed(0)}%
              · 流利度 {result.fluency_score?.toFixed(0)}
            </p>
          </div>

          {missed.length > 0 && (
            <div className="card bg-red-50 border border-red-200 mb-4">
              <div className="flex items-center text-red-700 font-medium mb-1">
                <AlertTriangle className="w-4 h-4 mr-2" />
                漏读了 {missed.length} 个单词
              </div>
              <p className="text-sm text-red-600">{missed.map((w) => w.word).join('、')}</p>
            </div>
          )}

          <div className="card">
            <h3 className="font-semibold text-lg mb-4">逐词得分</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
              {(result.per_word || []).map((w) => (
                <div
                  key={w.word}
                  className={`p-2 rounded-lg border text-center ${
                    w.error === '漏读'
                      ? 'bg-red-50 border-red-200'
                      : w.score >= 80
                      ? 'bg-green-50 border-green-200'
                      : w.score >= 60
                      ? 'bg-yellow-50 border-yellow-200'
                      : 'bg-orange-50 border-orange-200'
                  }`}
                >
                  <div className="font-medium text-gray-900 truncate">{w.word}</div>
                  <div className={`text-sm font-bold ${w.error === '漏读' ? 'text-red-600' : 'text-gray-700'}`}>
                    {w.error === '漏读' ? '漏读' : `${Number(w.score ?? 0).toFixed(0)}分`}
                    {w.teacher_grade && <span className="ml-1 text-blue-600">{w.teacher_grade}</span>}
                  </div>
                  {w.teacher_feedback && (
                    <div className="text-xs text-blue-700 mt-1 text-left bg-blue-50 rounded px-1.5 py-0.5">
                      💬 {w.teacher_feedback}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => { setResult(null); setPhase('ready'); }}
              className="flex-1 btn-secondary"
            >
              再测一次
            </button>
            <button onClick={onBack} className="flex-1 btn-primary">
              返回作业列表
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (phase === 'scoring') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-xl mx-auto px-4 py-20 text-center">
          <div className="card">
            <div className="animate-spin rounded-full h-14 w-14 border-b-2 border-primary-600 mx-auto mb-6"></div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">正在提交录音...</h2>
          </div>
        </div>
      </div>
    );
  }

  if (phase === 'submitted') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-xl mx-auto px-4 py-20 text-center">
          <div className="card">
            <div className="text-5xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">连读测试完成</h2>
            <div className="flex flex-col gap-3 max-w-xs mx-auto">
              <button onClick={viewResult} className="btn-primary py-3">
                查看成绩
              </button>
              <button
                onClick={() => { setResult(null); setPhase('ready'); }}
                className="btn-secondary py-3"
              >
                重做
              </button>
              <button
                onClick={onBack}
                className="py-3 text-gray-600 hover:text-gray-900 font-medium"
              >
                返回作业列表
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (phase === 'checking') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-xl mx-auto px-4 py-20 text-center">
          <div className="card">
            <div className="animate-spin rounded-full h-14 w-14 border-b-2 border-primary-600 mx-auto mb-6"></div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">正在评分整段朗读...</h2>
            <p className="text-gray-600 text-sm mb-6">大约需要 10–20 秒，评好自动显示成绩</p>
            <button onClick={onBack} className="text-sm text-gray-500 hover:text-gray-700">
              先返回，稍后再看
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (phase === 'countdown') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-xl mx-auto px-4 py-24 text-center">
          <p className="text-gray-600 mb-6 text-lg">准备好，单词马上出现——</p>
          <div className="text-8xl font-bold text-primary-600 animate-pulse">{countdown}</div>
        </div>
      </div>
    );
  }

  if (phase === 'recording') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="card mb-4 sticky top-0 z-10">
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center text-sm font-medium text-gray-700">
                <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></span>
                正在录音，按顺序朗读
              </span>
              <span className={`font-mono text-xl font-bold ${timeLeft <= 10 ? 'text-red-600' : 'text-gray-800'}`}>
                <Timer className="w-4 h-4 inline mr-1" />
                {fmt(timeLeft)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  timePct > 50 ? 'bg-green-500' : timePct > 25 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${timePct}%` }}
              ></div>
            </div>
          </div>

          <div className="card mb-4">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {words.map((w, i) => (
                <div key={w.id} className="p-3 rounded-lg border-2 border-gray-200 bg-white text-center">
                  <span className="text-xs text-gray-400 mr-1">{i + 1}.</span>
                  <span className="text-lg font-semibold text-gray-900">{w.word_text}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={finishRecording}
              className="px-8 py-3 bg-gray-800 hover:bg-gray-900 text-white rounded-full font-medium inline-flex items-center shadow-lg"
            >
              <Square className="w-5 h-5 mr-2" />
              我读完了，提交评分
            </button>
            <p className="text-xs text-gray-500 mt-2">时间到会自动提交</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-12">
        <button onClick={onBack} className="flex items-center text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-5 h-5 mr-2" />
          返回作业列表
        </button>

        <div className="card text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{details?.title}</h1>
          {details?.description && <p className="text-gray-600 mb-4">{details.description}</p>}

          <div className="bg-primary-50 rounded-xl p-6 my-6">
            <p className="text-lg text-gray-800 mb-1">
              连读测试 · 共 <strong>{words.length}</strong> 个单词 · 限时 <strong>{fmt(timeLimit)}</strong>
            </p>
            <p className="text-sm text-gray-600">
              点击开始后倒计时 3 秒，单词出现的同时开始录音。
              <br />
              按顺序大声朗读每个单词，读完点提交，时间到会自动提交。
            </p>
          </div>

          <button
            onClick={startTest}
            className="px-10 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-full text-lg font-bold inline-flex items-center shadow-lg transition-all hover:scale-105"
          >
            <Play className="w-6 h-6 mr-2" />
            开始测试
          </button>
          <p className="text-xs text-gray-400 mt-4">开始前请确认周围安静、麦克风可用</p>
        </div>
      </div>
    </div>
  );
}

export default ContinuousTest;
