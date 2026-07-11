import { useState, useEffect } from 'react';
import { Users, BarChart3, BookOpen, GraduationCap, Copy, Check, Plus, Pencil, Trash2, Database, UserMinus, MessageSquare, Award } from 'lucide-react';
import Navbar from '../Common/Navbar';
import AssignmentList from './AssignmentList';
import WordDatabaseManager from './WordDatabaseManager';
import teacherService from '../../services/teacherService';

function TeacherDashboard() {
  const [activeTab, setActiveTab] = useState('students');
  const [students, setStudents] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState('');
  const [newClassName, setNewClassName] = useState('');
  const [newClassDesc, setNewClassDesc] = useState('');
  const [creatingClass, setCreatingClass] = useState(false);
  const [copiedCode, setCopiedCode] = useState(null);
  const [editingClass, setEditingClass] = useState(null); // { id, class_name, description }
  const [suggestions, setSuggestions] = useState([]);
  const [suggestionText, setSuggestionText] = useState('');
  const [sendingSuggestion, setSendingSuggestion] = useState(false);
  const [suggestionMessage, setSuggestionMessage] = useState(null);

  useEffect(() => {
    if (activeTab === 'students') {
      loadStudents(selectedClassId);
      loadClasses();
    } else if (activeTab === 'analytics') {
      loadAnalytics();
    } else if (activeTab === 'classes') {
      loadClasses();
    } else if (activeTab === 'feedback') {
      loadSuggestions();
    }
  }, [activeTab, selectedClassId]);

  const loadSuggestions = async () => {
    try {
      const data = await teacherService.getMySuggestions();
      setSuggestions(data);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const handleSendSuggestion = async (e) => {
    e.preventDefault();
    if (!suggestionText.trim()) return;
    setSendingSuggestion(true);
    setSuggestionMessage(null);
    try {
      const result = await teacherService.createSuggestion(suggestionText.trim());
      setSuggestionMessage({ type: 'success', text: result.message });
      setSuggestionText('');
      await loadSuggestions();
    } catch (error) {
      setSuggestionMessage({
        type: 'error',
        text: error.response?.data?.detail || '提交失败，请重试',
      });
    } finally {
      setSendingSuggestion(false);
    }
  };

  const loadStudents = async (classId = '') => {
    setLoading(true);
    try {
      const data = await teacherService.getStudents(classId || null);
      setStudents(data);
    } catch (error) {
      console.error('Error loading students:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadClasses = async () => {
    try {
      const data = await teacherService.getMyClasses();
      setClasses(data);
    } catch (error) {
      console.error('Error loading classes:', error);
    }
  };

  const handleCreateClass = async (e) => {
    e.preventDefault();
    if (!newClassName.trim()) return;
    setCreatingClass(true);
    try {
      await teacherService.createClass(newClassName.trim(), newClassDesc.trim() || null);
      setNewClassName('');
      setNewClassDesc('');
      await loadClasses();
    } catch (error) {
      console.error('Error creating class:', error);
      alert(error.response?.data?.detail || '创建班级失败');
    } finally {
      setCreatingClass(false);
    }
  };

  const handleUpdateClass = async (e) => {
    e.preventDefault();
    if (!editingClass || !editingClass.class_name.trim()) return;
    try {
      await teacherService.updateClass(
        editingClass.id,
        editingClass.class_name.trim(),
        editingClass.description ?? ''
      );
      setEditingClass(null);
      await loadClasses();
    } catch (error) {
      alert(error.response?.data?.detail || '更新班级失败');
    }
  };

  const handleDeleteClass = async (classItem) => {
    if (!window.confirm(`确定删除班级「${classItem.class_name}」吗？学生账号会保留，但会退出该班级。`)) return;
    try {
      await teacherService.deleteClass(classItem.id);
      if (String(classItem.id) === selectedClassId) setSelectedClassId('');
      await loadClasses();
    } catch (error) {
      alert(error.response?.data?.detail || '删除班级失败');
    }
  };

  const handleRemoveStudent = async (student) => {
    if (!selectedClassId) return;
    if (!window.confirm(`确定将 ${student.username} 移出该班级吗？`)) return;
    try {
      await teacherService.removeStudentFromClass(selectedClassId, student.id);
      await loadStudents(selectedClassId);
      await loadClasses();
    } catch (error) {
      alert(error.response?.data?.detail || '移出学生失败');
    }
  };

  const handleCopyCode = async (code) => {
    try {
      await navigator.clipboard.writeText(code);
    } catch {
      // Clipboard API unavailable (e.g. http) — fall back to a prompt
      window.prompt('复制班级码：', code);
    }
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
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

  // Render Assignments tab as full component
  if (activeTab === 'assignments') {
    return <AssignmentList onBackToDashboard={() => setActiveTab('students')} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('students')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors flex items-center ${
              activeTab === 'students'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="w-4 h-4 mr-2" />
            学生
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
            作业
          </button>
          <button
            onClick={() => setActiveTab('classes')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors flex items-center ${
              activeTab === 'classes'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <GraduationCap className="w-4 h-4 mr-2" />
            班级
          </button>
          <button
            onClick={() => setActiveTab('databases')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors flex items-center ${
              activeTab === 'databases'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Database className="w-4 h-4 mr-2" />
            词库
          </button>
          <button
            onClick={() => setActiveTab('feedback')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors flex items-center ${
              activeTab === 'feedback'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            反馈
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
            数据分析
          </button>
        </div>

        {/* Students Tab */}
        {activeTab === 'students' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">学生</h2>
              <div className="flex items-center gap-3">
                <select
                  value={selectedClassId}
                  onChange={(e) => setSelectedClassId(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">全部学生</option>
                  {classes.map((classItem) => (
                    <option key={classItem.id} value={classItem.id}>
                      {classItem.class_name}
                    </option>
                  ))}
                </select>
                <span className="text-sm text-gray-600">
                  共 {students.length} 人
                </span>
                {(() => {
                  const scored = students.filter((st) => st.total_recordings > 0);
                  if (scored.length === 0) return null;
                  const avg = scored.reduce((a, st) => a + st.average_score, 0) / scored.length;
                  return (
                    <span className="flex items-center px-3 py-1.5 bg-primary-50 rounded-lg text-sm font-medium text-primary-700">
                      <Award className="w-4 h-4 mr-1" />
                      {selectedClassId ? '班级平均分' : '平均分'}：{avg.toFixed(1)}
                    </span>
                  );
                })()}
              </div>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="text-gray-500">加载学生中...</div>
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
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">
                          {student.username}
                        </div>
                        <div className="text-sm text-gray-500">{student.email}</div>
                      </div>
                      {selectedClassId && (
                        <button
                          onClick={() => handleRemoveStudent(student)}
                          className="p-2 text-gray-400 hover:text-red-600"
                          title="移出班级"
                        >
                          <UserMinus className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">录音数：</span>
                        <span className="font-medium">{student.total_recordings}</span>
                      </div>
                      <div className="flex justify-between text-sm mt-2">
                        <span className="text-gray-600">平均分：</span>
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

        {/* Word Databases Tab */}
        {activeTab === 'databases' && <WordDatabaseManager />}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <div>
            <h2 className="text-2xl font-bold mb-2">意见反馈</h2>
            <p className="text-sm text-gray-500 mb-6">
              希望平台增加什么功能？使用中遇到什么问题？在这里留言，我们会查看并回复。
            </p>

            <form onSubmit={handleSendSuggestion} className="card mb-6">
              <textarea
                value={suggestionText}
                onChange={(e) => setSuggestionText(e.target.value)}
                rows={4}
                maxLength={2000}
                placeholder="写下你的功能需求或建议，例如：希望能给学生布置跟读课文的作业……"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <div className="flex justify-between items-center mt-3">
                <span className="text-xs text-gray-400">{suggestionText.length}/2000</span>
                <button
                  type="submit"
                  disabled={sendingSuggestion || !suggestionText.trim()}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {sendingSuggestion ? '提交中...' : '提交反馈'}
                </button>
              </div>
              {suggestionMessage && (
                <p
                  className={`mt-2 text-sm ${
                    suggestionMessage.type === 'success' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {suggestionMessage.text}
                </p>
              )}
            </form>

            {suggestions.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">我的反馈记录</h3>
                {suggestions.map((item) => (
                  <div key={item.id} className="card">
                    <div className="flex justify-between items-start">
                      <p className="text-gray-800 flex-1 whitespace-pre-wrap">{item.content}</p>
                      {item.status === 'done' ? (
                        <span className="ml-3 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full whitespace-nowrap">
                          已处理
                        </span>
                      ) : (
                        <span className="ml-3 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full whitespace-nowrap">
                          待处理
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                      {new Date(item.created_at).toLocaleString()}
                    </div>
                    {item.reply && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <div className="text-xs font-medium text-blue-700 mb-1">平台回复：</div>
                        <p className="text-sm text-gray-700 whitespace-pre-wrap">{item.reply}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Classes Tab */}
        {activeTab === 'classes' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">班级管理</h2>
              <span className="text-sm text-gray-600">
                共 {classes.length} 个班级
              </span>
            </div>

            {/* Create class */}
            <form onSubmit={handleCreateClass} className="card mb-6">
              <h3 className="text-lg font-semibold mb-4">创建新班级</h3>
              <div className="flex flex-col md:flex-row gap-3">
                <input
                  type="text"
                  value={newClassName}
                  onChange={(e) => setNewClassName(e.target.value)}
                  placeholder="班级名称（如：初三2班）"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                />
                <input
                  type="text"
                  value={newClassDesc}
                  onChange={(e) => setNewClassDesc(e.target.value)}
                  placeholder="描述（可选）"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  disabled={creatingClass}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  {creatingClass ? '创建中...' : '创建班级'}
                </button>
              </div>
            </form>

            {classes.length === 0 ? (
              <div className="card text-center py-12">
                <GraduationCap className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">还没有班级，创建一个班级并把班级码告诉学生吧</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {classes.map((classItem) => (
                  <div key={classItem.id} className="card">
                    {editingClass?.id === classItem.id ? (
                      <form onSubmit={handleUpdateClass} className="space-y-2 mb-2">
                        <input
                          type="text"
                          value={editingClass.class_name}
                          onChange={(e) =>
                            setEditingClass({ ...editingClass, class_name: e.target.value })
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
                          placeholder="班级名称"
                          required
                        />
                        <input
                          type="text"
                          value={editingClass.description || ''}
                          onChange={(e) =>
                            setEditingClass({ ...editingClass, description: e.target.value })
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
                          placeholder="备注（可选）"
                        />
                        <div className="flex gap-2">
                          <button
                            type="submit"
                            className="flex-1 px-3 py-1.5 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700"
                          >
                            保存
                          </button>
                          <button
                            type="button"
                            onClick={() => setEditingClass(null)}
                            className="flex-1 px-3 py-1.5 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200"
                          >
                            取消
                          </button>
                        </div>
                      </form>
                    ) : (
                      <>
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {classItem.class_name}
                          </h3>
                          <div className="flex items-center gap-1">
                            <span className="text-sm text-gray-600 flex items-center mr-1">
                              <Users className="w-4 h-4 mr-1" />
                              {classItem.student_count} 人
                            </span>
                            <button
                              onClick={() =>
                                setEditingClass({
                                  id: classItem.id,
                                  class_name: classItem.class_name,
                                  description: classItem.description || '',
                                })
                              }
                              className="p-1 text-gray-400 hover:text-primary-600"
                              title="编辑班级"
                            >
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteClass(classItem)}
                              className="p-1 text-gray-400 hover:text-red-600"
                              title="删除班级"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        {classItem.description && (
                          <p className="text-sm text-gray-600 mb-3">{classItem.description}</p>
                        )}
                      </>
                    )}
                    <div className="mt-3 p-3 bg-primary-50 rounded-lg flex items-center justify-between">
                      <div>
                        <div className="text-xs text-gray-600 mb-1">班级码</div>
                        <div className="text-xl font-mono font-bold tracking-widest text-primary-700">
                          {classItem.class_code}
                        </div>
                      </div>
                      <button
                        onClick={() => handleCopyCode(classItem.class_code)}
                        className="p-2 rounded-lg hover:bg-primary-100 text-primary-600"
                        title="复制班级码"
                      >
                        {copiedCode === classItem.class_code ? (
                          <Check className="w-5 h-5 text-green-600" />
                        ) : (
                          <Copy className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedClassId(String(classItem.id));
                        setActiveTab('students');
                      }}
                      className="mt-3 w-full text-sm text-primary-600 hover:text-primary-700 font-medium"
                    >
                      查看学生 →
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && analytics && (
          <div>
            <h2 className="text-2xl font-bold mb-6">数据分析</h2>

            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
                <h3 className="text-sm font-medium text-gray-600 mb-2">
                  总录音数
                </h3>
                <p className="text-4xl font-bold text-gray-900">
                  {analytics.total_recordings}
                </p>
              </div>
              <div className="card bg-gradient-to-br from-green-50 to-green-100">
                <h3 className="text-sm font-medium text-gray-600 mb-2">
                  平均分
                </h3>
                <p className="text-4xl font-bold text-gray-900">
                  {analytics.average_score}%
                </p>
              </div>
              <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
                <h3 className="text-sm font-medium text-gray-600 mb-2">
                  待评审
                </h3>
                <p className="text-4xl font-bold text-gray-900">
                  {analytics.pending_reviews}
                </p>
              </div>
            </div>

            {/* Most Practiced Words */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">练习最多的单词</h3>
                <div className="space-y-3">
                  {analytics.most_practiced_words.map((item, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                    >
                      <span className="font-medium text-gray-900">{item.word}</span>
                      <span className="text-sm text-gray-600">{item.count} 次</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Challenging Words */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">较难单词</h3>
                <div className="space-y-3">
                  {analytics.challenging_words.map((item, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center p-3 bg-red-50 rounded-lg"
                    >
                      <span className="font-medium text-gray-900">{item.word}</span>
                      <span className="text-sm text-red-600">
                        {item.average_score}% 平均
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
