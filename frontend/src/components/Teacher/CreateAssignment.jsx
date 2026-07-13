import { useState, useEffect } from 'react';
import { ArrowLeft, Plus, Trash2, Calendar, Users, Book, CheckCircle } from 'lucide-react';
import Navbar from '../Common/Navbar';
import assignmentService from '../../services/assignmentService';
import teacherService from '../../services/teacherService';

function CreateAssignment({ onBack, onAssignmentCreated }) {
  const [step, setStep] = useState(1); // 1: Select Database, 2: 选择单词, 3: 分配学生 & Submit

  // Step 1: Database selection
  const [databases, setDatabases] = useState([]);
  const [selectedDatabase, setSelectedDatabase] = useState(null);

  // Step 2: Word selection
  const [availableWords, setAvailableWords] = useState([]);
  const [selectedWords, setSelectedWords] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  // Step 3: Assignment details
  const [title, setTitle] = useState('');
  const [mode, setMode] = useState('practice');
  const [description, set描述] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [students, setStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [classes, setClasses] = useState([]);
  const [classStudents, setClassStudents] = useState({}); // classId -> [studentId]

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Load databases on mount
  useEffect(() => {
    loadDatabases();
    loadStudents();
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      const classList = await teacherService.getMyClasses();
      setClasses(classList);
      // preload each class's student ids so chips can show live counts
      const mapping = {};
      await Promise.all(
        classList.map(async (c) => {
          try {
            const s = await teacherService.getStudents(c.id);
            mapping[c.id] = s.map((x) => x.id);
          } catch {
            mapping[c.id] = [];
          }
        })
      );
      setClassStudents(mapping);
    } catch (error) {
      console.error('Error loading classes:', error);
    }
  };

  const toggleClassSelection = (classItem) => {
    const ids = classStudents[classItem.id] || [];
    if (ids.length === 0) return;
    const selectedSet = new Set(selectedStudents);
    const allSelected = ids.every((id) => selectedSet.has(id));
    if (allSelected) {
      const idSet = new Set(ids);
      setSelectedStudents(selectedStudents.filter((id) => !idSet.has(id)));
    } else {
      setSelectedStudents([...new Set([...selectedStudents, ...ids])]);
    }
  };

  // Load words when database is selected
  useEffect(() => {
    if (selectedDatabase) {
      loadDatabaseWords(selectedDatabase.id);
    }
  }, [selectedDatabase]);

  const loadDatabases = async () => {
    try {
      setLoading(true);
      const data = await assignmentService.getWordDatabases();
      console.log('Databases loaded:', data);
      setDatabases(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error loading databases:', error);
      alert('Failed to load word databases');
      setDatabases([]);
    } finally {
      setLoading(false);
    }
  };

  const loadDatabaseWords = async (databaseId) => {
    try {
      setLoading(true);
      const data = await assignmentService.getDatabaseWords(databaseId);
      console.log('Words loaded:', data);
      setAvailableWords(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error loading words:', error);
      alert('Failed to load words from database');
      setAvailableWords([]);
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    try {
      console.log('Loading students...');
      const data = await teacherService.getStudents();
      console.log('Students loaded:', data);
      setStudents(data || []);
    } catch (error) {
      console.error('Error loading students:', error);
      // Don't fail silently - set empty array so UI still works
      setStudents([]);
      alert('Warning: Could not load students list. You can still create the assignment.');
    }
  };

  const selectDatabase = (database) => {
    setSelectedDatabase(database);
    setSelectedWords([]);
    setStep(2);
  };

  const toggleWordSelection = (word) => {
    if (selectedWords.find(w => w.word_text === word.word_text)) {
      setSelectedWords(selectedWords.filter(w => w.word_text !== word.word_text));
    } else {
      if (selectedWords.length < 40) {
        setSelectedWords([...selectedWords, word]);
      } else {
        alert('每个作业最多40个单词');
      }
    }
  };

  const toggleStudentSelection = (studentId) => {
    if (selectedStudents.includes(studentId)) {
      setSelectedStudents(selectedStudents.filter(id => id !== studentId));
    } else {
      setSelectedStudents([...selectedStudents, studentId]);
    }
  };

  const selectAllStudents = () => {
    setSelectedStudents(students.map(s => s.id));
  };

  const deselectAllStudents = () => {
    setSelectedStudents([]);
  };

  const filteredWords = availableWords.filter(word =>
    word.word_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (word.definition && word.definition.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (word.unit && word.unit.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Unit quick-select: stats per unit in the current database
  const selectedWordSet = new Set(selectedWords.map(w => w.word_text));
  const unitStats = [];
  {
    const seen = {};
    for (const word of availableWords) {
      const key = word.unit || '未分组';
      if (!seen[key]) {
        seen[key] = { unit: key, total: 0, selected: 0 };
        unitStats.push(seen[key]);
      }
      seen[key].total += 1;
      if (selectedWordSet.has(word.word_text)) seen[key].selected += 1;
    }
  }
  const hasUnits = unitStats.some(u => u.unit !== '未分组');

  const toggleUnitSelection = (unit) => {
    const unitWords = availableWords.filter(w => (w.unit || '未分组') === unit);
    const allSelected = unitWords.every(w => selectedWordSet.has(w.word_text));

    if (allSelected) {
      // deselect the whole unit
      const unitSet = new Set(unitWords.map(w => w.word_text));
      setSelectedWords(selectedWords.filter(w => !unitSet.has(w.word_text)));
      return;
    }

    const toAdd = unitWords.filter(w => !selectedWordSet.has(w.word_text));
    const capacity = 40 - selectedWords.length;
    if (capacity <= 0) {
      alert('已达到40个单词上限，请先取消部分单词');
      return;
    }
    if (toAdd.length > capacity) {
      setSelectedWords([...selectedWords, ...toAdd.slice(0, capacity)]);
      alert(`已选满40个单词上限，${unit} 还有 ${toAdd.length - capacity} 个单词未能加入，可手动调整`);
    } else {
      setSelectedWords([...selectedWords, ...toAdd]);
    }
  };

  const canProceedToStep3 = selectedWords.length >= 20 && selectedWords.length <= 40;

  const handleSubmit = async () => {
    // Validation
    if (!title.trim()) {
      alert('Please enter an assignment title');
      return;
    }

    if (selectedWords.length < 20 || selectedWords.length > 40) {
      alert('Please select between 20 and 40 words');
      return;
    }

    if (selectedStudents.length === 0) {
      alert('请至少选择一名学生');
      return;
    }

    try {
      setSubmitting(true);

      const assignmentData = {
        title: title.trim(),
        mode,
        description: description.trim() || null,
        word_database_id: selectedDatabase.id,
        due_date: dueDate || null,
        words: selectedWords.map(w => w.word_text),
        student_ids: selectedStudents
      };

      await assignmentService.createAssignment(assignmentData);

      alert(`作业创建成功并分配给 ${selectedStudents.length} 名学生！`);

      if (onAssignmentCreated) {
        onAssignmentCreated();
      }
    } catch (error) {
      console.error('创建作业出错：', error);
      alert(error.response?.data?.detail || '创建作业失败');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          返回作业列表
        </button>

        <h1 className="text-3xl font-bold text-gray-900 mb-8">Create New Assignment</h1>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full ${step >= 1 ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
              1
            </div>
            <div className={`w-24 h-1 ${step >= 2 ? 'bg-primary-600' : 'bg-gray-300'}`}></div>
            <div className={`flex items-center justify-center w-10 h-10 rounded-full ${step >= 2 ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
              2
            </div>
            <div className={`w-24 h-1 ${step >= 3 ? 'bg-primary-600' : 'bg-gray-300'}`}></div>
            <div className={`flex items-center justify-center w-10 h-10 rounded-full ${step >= 3 ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
              3
            </div>
          </div>
        </div>

        {/* Step 1: Select Database */}
        {step === 1 && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">选择词库</h2>
              <p className="text-gray-600 mb-6">选择一个词库以挑选单词</p>

              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">加载词库中...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {databases.map((database) => (
                    <button
                      key={database.id}
                      onClick={() => selectDatabase(database)}
                      className="card bg-gradient-to-br from-primary-50 to-primary-100 hover:from-primary-100 hover:to-primary-200 transition-all border-2 border-primary-200 hover:border-primary-400"
                    >
                      <Book className="w-12 h-12 text-primary-600 mb-3" />
                      <h3 className="font-semibold text-lg mb-2">{database.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">{database.description}</p>
                      <p className="text-sm font-medium text-primary-600">
                        {database.word_count} 个可用单词
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 2: 选择单词 */}
        {step === 2 && (
          <div className="space-y-6">
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">
                  选择单词 ({selectedWords.length}/40)
                </h2>
                <span className={`px-3 py-1 rounded-full text-sm ${
                  canProceedToStep3
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {selectedWords.length < 20
                    ? `还需要 ${20 - selectedWords.length} more`
                    : canProceedToStep3
                    ? '可以继续'
                    : '最多40个单词'}
                </span>
              </div>

              <p className="text-gray-600 mb-4">
                来自 <strong>{selectedDatabase?.name}</strong> - 为本作业选择20-40个单词
              </p>

              {/* Unit quick-select */}
              {hasUnits && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-2">
                    按组别一键选择（点击选中整组，再点取消整组）：
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {unitStats.map(({ unit, total, selected }) => {
                      const full = selected === total && total > 0;
                      const partial = selected > 0 && !full;
                      return (
                        <button
                          key={unit}
                          type="button"
                          onClick={() => toggleUnitSelection(unit)}
                          className={`px-3 py-1.5 rounded-full text-sm font-medium border-2 transition-all flex items-center ${
                            full
                              ? 'bg-primary-600 border-primary-600 text-white'
                              : partial
                              ? 'bg-primary-50 border-primary-400 text-primary-700'
                              : 'bg-white border-gray-300 text-gray-700 hover:border-primary-400'
                          }`}
                        >
                          {full && <CheckCircle className="w-4 h-4 mr-1" />}
                          {unit}
                          <span className={`ml-1.5 text-xs ${full ? 'text-primary-100' : 'text-gray-500'}`}>
                            {partial ? `${selected}/${total}` : total}
                          </span>
                        </button>
                      );
                    })}
                    {selectedWords.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setSelectedWords([])}
                        className="px-3 py-1.5 rounded-full text-sm text-red-600 border-2 border-red-200 hover:bg-red-50 transition-all"
                      >
                        清空已选
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Search */}
              <input
                type="text"
                placeholder="搜索单词..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field mb-4"
              />

              {/* Word List */}
              <div className="max-h-96 overflow-y-auto space-y-2 mb-4">
                {filteredWords.map((word) => {
                  const isSelected = selectedWords.find(w => w.word_text === word.word_text);
                  return (
                    <div
                      key={word.id}
                      onClick={() => toggleWordSelection(word)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <span className="font-semibold text-lg">{word.word_text}</span>
                            {word.unit && (
                              <span className="ml-2 px-2 py-0.5 bg-primary-50 text-primary-600 text-xs rounded-full">
                                {word.unit}
                              </span>
                            )}
                            {word.difficulty_level && (
                              <span className="ml-2 px-2 py-0.5 text-xs rounded bg-gray-200 text-gray-700">
                                {word.difficulty_level}
                              </span>
                            )}
                          </div>
                          {word.definition && (
                            <p className="text-sm text-gray-600 mt-1">{word.definition}</p>
                          )}
                        </div>
                        {isSelected && (
                          <CheckCircle className="w-6 h-6 text-primary-600 flex-shrink-0 ml-2" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setStep(1);
                    setSelectedWords([]);
                  }}
                  className="flex-1 btn-secondary"
                >
                  更换词库
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={!canProceedToStep3}
                  className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  下一步：分配学生
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: 作业详情 & Student Selection */}
        {step === 3 && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">作业详情</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    作业模式 *
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => setMode('practice')}
                      className={`p-4 rounded-lg border-2 text-left transition-all ${
                        mode === 'practice'
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-semibold text-gray-900">练习模式</div>
                      <div className="text-sm text-gray-600 mt-1">
                        逐词录音，可反复练习，适合日常作业
                      </div>
                    </button>
                    <button
                      type="button"
                      onClick={() => setMode('continuous')}
                      className={`p-4 rounded-lg border-2 text-left transition-all ${
                        mode === 'continuous'
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-semibold text-gray-900">连读测试</div>
                      <div className="text-sm text-gray-600 mt-1">
                        倒计时后限时一次读完全部单词，防止查词，适合测验
                      </div>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    标题 *
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g., Week 1 IELTS Vocabulary"
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    描述
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => set描述(e.target.value)}
                    placeholder="可选：为学生添加说明或备注"
                    rows="3"
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    截止日期
                  </label>
                  <input
                    type="datetime-local"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="input-field"
                  />
                </div>

                <div className="border-t pt-4">
                  <p className="text-sm text-gray-600">
                    <strong>词库：</strong> {selectedDatabase?.name}<br />
                    <strong>已选单词：</strong> {selectedWords.length} words
                  </p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">
                  Assign to Students ({selectedStudents.length})
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={selectAllStudents}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    全选
                  </button>
                  <span className="text-gray-400">|</span>
                  <button
                    onClick={deselectAllStudents}
                    className="text-sm text-gray-600 hover:text-gray-700"
                  >
                    取消全选
                  </button>
                </div>
              </div>

              {classes.length > 0 && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-2">按班级一键选择：</div>
                  <div className="flex flex-wrap gap-2">
                    {classes.map((classItem) => {
                      const ids = classStudents[classItem.id] || [];
                      const selectedCount = ids.filter((id) =>
                        selectedStudents.includes(id)
                      ).length;
                      const full = ids.length > 0 && selectedCount === ids.length;
                      const partial = selectedCount > 0 && !full;
                      return (
                        <button
                          key={classItem.id}
                          type="button"
                          onClick={() => toggleClassSelection(classItem)}
                          disabled={ids.length === 0}
                          className={`px-3 py-1.5 rounded-full text-sm font-medium border-2 transition-all flex items-center disabled:opacity-40 disabled:cursor-not-allowed ${
                            full
                              ? 'bg-primary-600 border-primary-600 text-white'
                              : partial
                              ? 'bg-primary-50 border-primary-400 text-primary-700'
                              : 'bg-white border-gray-300 text-gray-700 hover:border-primary-400'
                          }`}
                        >
                          {full && <CheckCircle className="w-4 h-4 mr-1" />}
                          {classItem.class_name}
                          <span className={`ml-1.5 text-xs ${full ? 'text-primary-100' : 'text-gray-500'}`}>
                            {partial ? `${selectedCount}/${ids.length}` : `${ids.length}人`}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              <div className="max-h-64 overflow-y-auto space-y-2">
                {students.map((student) => (
                  <label
                    key={student.id}
                    className="flex items-center p-3 rounded-lg border-2 cursor-pointer transition-all hover:bg-gray-50"
                  >
                    <input
                      type="checkbox"
                      checked={selectedStudents.includes(student.id)}
                      onChange={() => toggleStudentSelection(student.id)}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <span className="ml-3 font-medium">{student.username}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(2)}
                className="flex-1 btn-secondary"
              >
                返回单词选择
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting || !title.trim() || selectedStudents.length === 0}
                className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="w-5 h-5 mr-2" />
                    创建作业
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CreateAssignment;
