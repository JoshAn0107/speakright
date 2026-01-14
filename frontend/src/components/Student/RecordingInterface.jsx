import { useState, useRef } from 'react';
import { Mic, Square, Play, Upload, Volume2, Loader } from 'lucide-react';
import studentService from '../../services/studentService';

function RecordingInterface({ word, wordData, onRecordingComplete }) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const audioContextRef = useRef(null);
  const streamRef = useRef(null);
  const processorRef = useRef(null);
  const audioChunksRef = useRef([]);

  const convertToWav = (audioData, sampleRate) => {
    // Convert Float32Array to 16-bit PCM
    const buffer = new ArrayBuffer(44 + audioData.length * 2);
    const view = new DataView(buffer);

    // Write WAV header
    const writeString = (offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, 36 + audioData.length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true); // fmt chunk size
    view.setUint16(20, 1, true); // PCM format
    view.setUint16(22, 1, true); // mono
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true); // byte rate
    view.setUint16(32, 2, true); // block align
    view.setUint16(34, 16, true); // bits per sample
    writeString(36, 'data');
    view.setUint32(40, audioData.length * 2, true);

    // Write PCM samples
    let offset = 44;
    for (let i = 0; i < audioData.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, audioData[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    return new Blob([view], { type: 'audio/wav' });
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        }
      });

      streamRef.current = stream;
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      audioChunksRef.current = [];

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        audioChunksRef.current.push(new Float32Array(inputData));
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please grant permission.');
    }
  };

  const stopRecording = () => {
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Combine all chunks and convert to WAV
    if (audioChunksRef.current.length > 0) {
      const totalLength = audioChunksRef.current.reduce((acc, chunk) => acc + chunk.length, 0);
      const combined = new Float32Array(totalLength);
      let offset = 0;

      for (const chunk of audioChunksRef.current) {
        combined.set(chunk, offset);
        offset += chunk.length;
      }

      const wavBlob = convertToWav(combined, 16000);
      setAudioBlob(wavBlob);
      setAudioUrl(URL.createObjectURL(wavBlob));
    }

    setIsRecording(false);
  };

  const submitRecording = async () => {
    if (!audioBlob) return;

    setSubmitting(true);
    try {
      const response = await studentService.submitRecording(word, audioBlob);
      setResult(response);
      if (onRecordingComplete) {
        onRecordingComplete(response);
      }
    } catch (error) {
      console.error('Error submitting recording:', error);
      alert('Failed to submit recording. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const playModelAudio = () => {
    if (wordData?.audio_url) {
      const audio = new Audio(wordData.audio_url);
      audio.play();
    }
  };

  const playRecording = () => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.play();
    }
  };

  if (result) {
    return (
      <div className="space-y-6">
        <div className="card bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500 rounded-full mb-4">
              <span className="text-2xl font-bold text-white">
                {result.feedback?.grade || 'N/A'}
              </span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Recording Submitted!
            </h3>
            <p className="text-gray-700">
              Score: {result.automated_scores?.pronunciation_score?.toFixed(0) || 'N/A'}/100
            </p>
          </div>
        </div>

        <div className="card">
          <h4 className="font-semibold text-lg mb-3">Detailed Scores</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-600">Pronunciation</div>
              <div className="text-2xl font-bold text-primary-600">
                {result.automated_scores?.pronunciation_score?.toFixed(0) || 0}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Accuracy</div>
              <div className="text-2xl font-bold text-primary-600">
                {result.automated_scores?.accuracy_score?.toFixed(0) || 0}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Fluency</div>
              <div className="text-2xl font-bold text-primary-600">
                {result.automated_scores?.fluency_score?.toFixed(0) || 0}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Completeness</div>
              <div className="text-2xl font-bold text-primary-600">
                {result.automated_scores?.completeness_score?.toFixed(0) || 0}%
              </div>
            </div>
          </div>
        </div>

        <div className="card bg-blue-50 border border-blue-200">
          <h4 className="font-semibold text-lg mb-3 flex items-center">
            <span className="mr-2">💬</span>
            AI Feedback
          </h4>
          <p className="text-gray-800 whitespace-pre-line">
            {result.feedback?.text || 'No feedback available'}
          </p>
          {result.feedback?.is_automated && (
            <p className="text-xs text-gray-500 mt-3 italic">
              This feedback was generated automatically. Your teacher may review and provide additional comments.
            </p>
          )}
        </div>

        <button
          onClick={() => {
            setResult(null);
            setAudioBlob(null);
            setAudioUrl(null);
          }}
          className="w-full btn-primary"
        >
          Practice Another Word
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Model Pronunciation */}
      {wordData?.audio_url && (
        <div className="card bg-gray-50">
          <h4 className="font-semibold mb-3">Model Pronunciation</h4>
          <button
            onClick={playModelAudio}
            className="btn-secondary w-full flex items-center justify-center"
          >
            <Volume2 className="w-5 h-5 mr-2" />
            Listen to Pronunciation
          </button>
        </div>
      )}

      {/* Recording Controls */}
      <div className="card">
        <h4 className="font-semibold mb-4">Your Recording</h4>

        <div className="flex flex-col items-center space-y-4">
          {!isRecording && !audioBlob && (
            <button
              onClick={startRecording}
              className="w-32 h-32 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center shadow-lg transition-all hover:scale-105"
            >
              <Mic className="w-12 h-12 text-white" />
            </button>
          )}

          {isRecording && (
            <button
              onClick={stopRecording}
              className="w-32 h-32 rounded-full bg-gray-800 hover:bg-gray-900 flex items-center justify-center shadow-lg animate-pulse"
            >
              <Square className="w-12 h-12 text-white" />
            </button>
          )}

          {audioBlob && !isRecording && (
            <button
              onClick={playRecording}
              className="w-32 h-32 rounded-full bg-green-500 hover:bg-green-600 flex items-center justify-center shadow-lg transition-all hover:scale-105"
            >
              <Play className="w-12 h-12 text-white" />
            </button>
          )}

          <div className="text-center">
            {isRecording && (
              <p className="text-sm text-red-600 font-medium">Recording... Click to stop</p>
            )}
            {!isRecording && !audioBlob && (
              <p className="text-sm text-gray-600">Click to start recording</p>
            )}
            {audioBlob && !isRecording && (
              <p className="text-sm text-green-600 font-medium">Recording ready! Click to play</p>
            )}
          </div>
        </div>

        {audioBlob && (
          <div className="mt-6 flex gap-3">
            <button
              onClick={() => {
                setAudioBlob(null);
                setAudioUrl(null);
              }}
              className="flex-1 btn-secondary"
            >
              Re-record
            </button>
            <button
              onClick={submitRecording}
              disabled={submitting}
              className="flex-1 btn-primary disabled:opacity-50 flex items-center justify-center"
            >
              {submitting ? (
                <>
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5 mr-2" />
                  Submit
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {isRecording && (
        <div className="card bg-yellow-50 border border-yellow-200">
          <p className="text-sm text-yellow-800">
            <strong>Tip:</strong> Speak clearly and pronounce the word as accurately as possible.
            Take your time!
          </p>
        </div>
      )}
    </div>
  );
}

export default RecordingInterface;
