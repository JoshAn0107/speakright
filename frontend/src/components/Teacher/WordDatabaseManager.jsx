import { useState, useEffect, useRef } from 'react';
import { Database, Plus, Trash2, X, Lock, Upload, Clock, CheckCircle, XCircle, Download, RotateCcw, Recycle } from 'lucide-react';
import assignmentService from '../../services/assignmentService';

function WordDatabaseManager() {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState(null);
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newDbName, setNewDbName] = useState('');
  const [newDbDesc, setNewDbDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const [bulkText, setBulkText] = useState('');
  const [bulkUnit, setBulkUnit] = useState('');
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState(null);
  const [uploads, setUploads] = useState([]);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadTargetName, setUploadTargetName] = useState('');
  const [uploadNote, setUploadNote] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);
  const [trash, setTrash] = useState([]);
  const [showTrash, setShowTrash] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadDatabases();
    loadUploads();
    loadTrash();
  }, []);

  const loadTrash = async () => {
    try {
      const data = await assignmentService.getTrashedDatabases();
      setTrash(data);
    } catch (error) {
      console.error('Error loading trash:', error);
    }
  };

  const handleRestore = async (database) => {
    try {
      await assignmentService.restoreDatabase(database.id);
      await Promise.all([loadTrash(), loadDatabases()]);
    } catch (error) {
      alert(error.response?.data?.detail || '恢复失败');
    }
  };

  const handlePurge = async (database) => {
    if (!window.confirm(`确定彻底删除词库「${database.name}」及其全部单词吗？此操作无法撤销！`)) return;
    try {
      await assignmentService.purgeDatabase(database.id);
      await loadTrash();
    } catch (error) {
      alert(error.response?.data?.detail || '删除失败');
    }
  };

  const handleEmptyTrash = async () => {
    if (!window.confirm(`确定清空回收站吗？${trash.length} 个词库将被彻底删除，无法撤销！`)) return;
    try {
      await assignmentService.emptyTrash();
      await loadTrash();
    } catch (error) {
      alert(error.response?.data?.detail || '清空失败');
    }
  };

  const loadUploads = async () => {
    try {
      const data = await assignmentService.getWordlistUploads();
      setUploads(data);
    } catch (error) {
      console.error('Error loading uploads:', error);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;
    setUploading(true);
    setUploadMessage(null);
    try {
      const result = await assignmentService.uploadWordlistFile(
        uploadFile,
        uploadTargetName.trim() || null,
        uploadNote.trim() || null
      );
      setUploadMessage({ type: 'success', text: result.message });
      setUploadFile(null);
      setUploadTargetName('');
      setUploadNote('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      await loadUploads();
    } catch (error) {
      setUploadMessage({
        type: 'error',
        text: error.response?.data?.detail || '上传失败，请重试',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteUpload = async (upload) => {
    if (!window.confirm(`确定删除「${upload.original_filename}」吗？`)) return;
    try {
      await assignmentService.deleteWordlistUpload(upload.id);
      await loadUploads();
    } catch (error) {
      alert(error.response?.data?.detail || '删除失败');
    }
  };

  const loadDatabases = async () => {
    try {
      const data = await assignmentService.getWordDatabases();
      setDatabases(data);
    } catch (error) {
      console.error('Error loading databases:', error);
    }
  };

  const openDatabase = async (database) => {
    setSelectedDb(database);
    setMessage(null);
    setLoading(true);
    try {
      const data = await assignmentService.getDatabaseWords(database.id);
      setWords(data);
    } catch (error) {
      console.error('Error loading words:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDatabase = async (e) => {
    e.preventDefault();
    if (!newDbName.trim()) return;
    setCreating(true);
    try {
      const created = await assignmentService.createWordDatabase(
        newDbName.trim(),
        newDbDesc.trim() || null
      );
      setNewDbName('');
      setNewDbDesc('');
      await loadDatabases();
      openDatabase(created);
    } catch (error) {
      alert(error.response?.data?.detail || '创建词库失败');
    } finally {
      setCreating(false);
    }
  };

  const handleAddWords = async (e) => {
    e.preventDefault();
    if (!selectedDb || !bulkText.trim()) return;

    // One entry per line: "word" or "word|释义" or "word|释义|例句"
    const wordItems = bulkText
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [wordText, definition, example] = line.split('|').map((p) => p.trim());
        return {
          word_text: wordText,
          definition: definition || null,
          example_sentence: example || null,
          unit: bulkUnit.trim() || null,
        };
      })
      .filter((item) => item.word_text);

    if (wordItems.length === 0) return;

    setAdding(true);
    setMessage(null);
    try {
      const result = await assignmentService.addWordsToDatabase(selectedDb.id, wordItems);
      setMessage({ type: 'success', text: result.message });
      setBulkText('');
      setBulkUnit('');
      const data = await assignmentService.getDatabaseWords(selectedDb.id);
      setWords(data);
      await loadDatabases();
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '添加单词失败' });
    } finally {
      setAdding(false);
    }
  };

  const handleDeleteWord = async (wordId) => {
    try {
      await assignmentService.deleteDatabaseWord(selectedDb.id, wordId);
      setWords(words.filter((w) => w.id !== wordId));
      await loadDatabases();
    } catch (error) {
      alert(error.response?.data?.detail || '删除单词失败');
    }
  };

  const handleDeleteDatabase = async (database) => {
    if (!window.confirm(`将词库「${database.name}」放入回收站？可随时恢复。`)) return;
    try {
      await assignmentService.deleteWordDatabase(database.id);
      if (selectedDb?.id === database.id) {
        setSelectedDb(null);
        setWords([]);
      }
      await Promise.all([loadDatabases(), loadTrash()]);
    } catch (error) {
      alert(error.response?.data?.detail || '删除词库失败');
    }
  };

  const handleExport = async (e, database) => {
    e.stopPropagation();
    try {
      await assignmentService.exportDatabaseExcel(database.id, database.name);
    } catch (error) {
      alert('导出失败，请重试');
    }
  };

  const isOwn = (database) => database.created_by != null;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">词库管理</h2>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowTrash(!showTrash)}
            className={`flex items-center px-3 py-1.5 text-sm rounded-lg border transition-colors ${
              showTrash
                ? 'border-primary-600 text-primary-600 bg-primary-50'
                : 'border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Recycle className="w-4 h-4 mr-1" />
            回收站{trash.length > 0 && `（${trash.length}）`}
          </button>
          <span className="text-sm text-gray-600">共 {databases.length} 个词库</span>
        </div>
      </div>

      {showTrash && (
        <div className="card mb-6 border-2 border-dashed border-gray-300">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold flex items-center">
              <Recycle className="w-5 h-5 mr-2 text-gray-500" />
              回收站
            </h3>
            {trash.length > 0 && (
              <button
                onClick={handleEmptyTrash}
                className="px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50"
              >
                清空回收站
              </button>
            )}
          </div>
          {trash.length === 0 ? (
            <p className="text-sm text-gray-500 py-4 text-center">回收站是空的</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {trash.map((database) => (
                <div key={database.id} className="py-2 flex justify-between items-center">
                  <div>
                    <span className="font-medium text-gray-900">{database.name}</span>
                    <span className="ml-3 text-sm text-gray-500">
                      {database.word_count} 个单词 · 删除于 {new Date(database.deleted_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleRestore(database)}
                      className="flex items-center px-3 py-1 text-sm text-primary-600 hover:bg-primary-50 rounded-lg"
                      title="恢复"
                    >
                      <RotateCcw className="w-4 h-4 mr-1" />
                      恢复
                    </button>
                    <button
                      onClick={() => handlePurge(database)}
                      className="flex items-center px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-lg"
                      title="彻底删除"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      彻底删除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create database */}
      <form onSubmit={handleCreateDatabase} className="card mb-6">
        <h3 className="text-lg font-semibold mb-4">创建自定义词库</h3>
        <div className="flex flex-col md:flex-row gap-3">
          <input
            type="text"
            value={newDbName}
            onChange={(e) => setNewDbName(e.target.value)}
            placeholder="词库名称（如：上海新教材六年级上）"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
          <input
            type="text"
            value={newDbDesc}
            onChange={(e) => setNewDbDesc(e.target.value)}
            placeholder="描述（可选）"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={creating}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center"
          >
            <Plus className="w-4 h-4 mr-1" />
            {creating ? '创建中...' : '创建词库'}
          </button>
        </div>
      </form>

      {/* Upload wordlist file for adaptation */}
      <div className="card mb-6">
        <h3 className="text-lg font-semibold mb-1 flex items-center">
          <Upload className="w-5 h-5 mr-2 text-primary-600" />
          上传词表文件适配
        </h3>
        <p className="text-sm text-gray-500 mb-4">
          有现成的词汇表文件（txt、Excel、Word、PDF 或课本照片）？上传后我们会人工适配成词库，完成后自动出现在词库列表中。
        </p>
        <form onSubmit={handleUpload} className="flex flex-col md:flex-row gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
            accept=".txt,.csv,.md,.xlsx,.xls,.docx,.doc,.pdf,.png,.jpg,.jpeg,.webp"
            className="flex-1 text-sm text-gray-600 file:mr-3 file:px-4 file:py-2 file:border-0 file:rounded-lg file:bg-primary-50 file:text-primary-700 file:cursor-pointer hover:file:bg-primary-100"
          />
          <input
            type="text"
            value={uploadTargetName}
            onChange={(e) => setUploadTargetName(e.target.value)}
            placeholder="目标词库名称（如：上海新教材六年级上）"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <input
            type="text"
            value={uploadNote}
            onChange={(e) => setUploadNote(e.target.value)}
            placeholder="备注（可选）"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={uploading || !uploadFile}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {uploading ? '上传中...' : '上传'}
          </button>
        </form>
        {uploadMessage && (
          <p
            className={`mt-2 text-sm ${
              uploadMessage.type === 'success' ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {uploadMessage.text}
          </p>
        )}

        {uploads.length > 0 && (
          <div className="mt-4 divide-y divide-gray-100">
            {uploads.map((upload) => (
              <div key={upload.id} className="py-2 flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900 truncate">
                    {upload.original_filename}
                    {upload.target_name && (
                      <span className="ml-2 text-sm font-normal text-gray-500">
                        → {upload.target_name}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {new Date(upload.created_at).toLocaleString()}
                    {upload.result_message && ` · ${upload.result_message}`}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-3">
                  {upload.status === 'pending' && (
                    <span className="inline-flex items-center px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                      <Clock className="w-3 h-3 mr-1" />
                      等待适配
                    </span>
                  )}
                  {upload.status === 'done' && (
                    <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      已适配
                    </span>
                  )}
                  {upload.status === 'failed' && (
                    <span className="inline-flex items-center px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                      <XCircle className="w-3 h-3 mr-1" />
                      适配失败
                    </span>
                  )}
                  {upload.status === 'pending' && (
                    <button
                      onClick={() => handleDeleteUpload(upload)}
                      className="p-1 text-gray-400 hover:text-red-600"
                      title="删除"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Database list */}
        <div className="space-y-3">
          {databases.map((database) => (
            <div
              key={database.id}
              onClick={() => openDatabase(database)}
              className={`card cursor-pointer transition-shadow hover:shadow-lg ${
                selectedDb?.id === database.id ? 'ring-2 ring-primary-500' : ''
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex items-start">
                  <Database className="w-5 h-5 text-primary-600 mr-2 mt-0.5" />
                  <div>
                    <div className="font-semibold text-gray-900">{database.name}</div>
                    <div className="text-sm text-gray-500 mt-1">
                      {database.word_count} 个单词
                      {!isOwn(database) && (
                        <span className="inline-flex items-center ml-2 text-xs text-gray-400">
                          <Lock className="w-3 h-3 mr-0.5" />
                          内置
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center">
                  <button
                    onClick={(e) => handleExport(e, database)}
                    className="p-1 text-gray-400 hover:text-primary-600"
                    title="下载Excel"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  {isOwn(database) && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteDatabase(database);
                      }}
                      className="p-1 text-gray-400 hover:text-red-600"
                      title="删除词库"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Words panel */}
        <div className="lg:col-span-2">
          {!selectedDb ? (
            <div className="card text-center py-12">
              <Database className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">选择左侧词库查看单词，或创建自己的词库</p>
            </div>
          ) : (
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">
                  {selectedDb.name}
                  <span className="ml-2 text-sm font-normal text-gray-500">
                    {words.length} 个单词
                  </span>
                </h3>
              </div>

              {isOwn(selectedDb) && (
                <form onSubmit={handleAddWords} className="mb-4">
                  <textarea
                    value={bulkText}
                    onChange={(e) => setBulkText(e.target.value)}
                    rows={5}
                    placeholder={'批量添加单词，每行一个：\napple\nbanana|香蕉\nlibrary|图书馆|I study in the library.'}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <div className="flex justify-between items-center mt-2 gap-2">
                    <span className="text-xs text-gray-500 flex-1">
                      格式：单词｜释义（可选）｜例句（可选），用 | 分隔
                    </span>
                    <input
                      type="text"
                      value={bulkUnit}
                      onChange={(e) => setBulkUnit(e.target.value)}
                      placeholder="组别（如 Unit 1，可选）"
                      className="w-44 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
                    />
                    <button
                      type="submit"
                      disabled={adding || !bulkText.trim()}
                      className="px-4 py-2 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700 disabled:opacity-50"
                    >
                      {adding ? '添加中...' : '添加单词'}
                    </button>
                  </div>
                  {message && (
                    <p
                      className={`mt-2 text-sm ${
                        message.type === 'success' ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {message.text}
                    </p>
                  )}
                </form>
              )}

              {loading ? (
                <div className="text-center py-8 text-gray-500">加载单词中...</div>
              ) : words.length === 0 ? (
                <div className="text-center py-8 text-gray-500">词库为空</div>
              ) : (
                <div className="max-h-96 overflow-y-auto">
                  {Object.entries(
                    words.reduce((groups, word) => {
                      const key = word.unit || '未分组';
                      (groups[key] = groups[key] || []).push(word);
                      return groups;
                    }, {})
                  ).map(([unit, unitWords]) => (
                    <div key={unit}>
                      <div className="sticky top-0 bg-primary-50 px-3 py-1.5 rounded text-sm font-semibold text-primary-700 mt-2 first:mt-0">
                        {unit}
                        <span className="ml-2 font-normal text-primary-500">
                          {unitWords.length} 个
                        </span>
                      </div>
                      <div className="divide-y divide-gray-100">
                        {unitWords.map((word) => (
                          <div key={word.id} className="py-2 px-1 flex justify-between items-center">
                            <div>
                              <span className="font-medium text-gray-900">{word.word_text}</span>
                              {word.definition && (
                                <span className="ml-3 text-sm text-gray-600">{word.definition}</span>
                              )}
                              {word.example_sentence && (
                                <div className="text-xs text-gray-400 italic mt-0.5">
                                  {word.example_sentence}
                                </div>
                              )}
                            </div>
                            {isOwn(selectedDb) && (
                              <button
                                onClick={() => handleDeleteWord(word.id)}
                                className="p-1 text-gray-400 hover:text-red-600"
                                title="删除单词"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default WordDatabaseManager;
