# LO2 Grading Checklist - 对标评分标准

## 📋 LO2 的 4 个子项到底在看什么？

| 子项 | 核心问题 | 你的文档位置 | 分数关键 |
|-----|---------|------------|---------|
| **2.1** | 你的测试计划是什么？ | `LO2_Test_Plan.md` § 1-6 | 有没有 evolution story |
| **2.2** | 这个计划好不好？有什么问题？ | `LO2_Test_Plan.md` § 7 | 能不能看出缺点 |
| **2.3** | 你为了测试，对代码做了什么改造？ | `LO2_Instrumentation_Report.md` § 1 | 改造够不够实质 |
| **2.4** | 这些改造够不够？哪里还能更好？ | `LO2_Instrumentation_Report.md` § 4 | 批判性反思 |

---

## ✅ LO2.1 - Test Plan (测试计划)

### 评分标准

| 分数 | 标准 | 你的体现 |
|-----|------|---------|
| **1-2** | 只有简单的测试类型列表 | ❌ |
| **3** | 有计划，但缺乏细节或理由 | ❌ |
| **4** | 清晰计划 + 需求映射 + **evolution story** | ✅ § 4 "Evolution of Test Plan" |

### 关键检查点

**必须包含**：
- [ ] 三种测试类型（Unit/Integration/System）
- [ ] 每种类型的具体范围和数量
- [ ] 需求到测试的映射表
- [ ] **测试计划如何演进**（最重要！）

**你的文档位置**：
```
LO2_Test_Plan.md
├── § 1: Planned Test Types          ✅ 三种类型
├── § 2: Mapping to Requirements     ✅ 完整映射
├── § 4: Evolution of Test Plan      ✅ 4 phases with rationale
└── § 6: Testing Priorities          ✅ Risk-based prioritization
```

**高分亮点**：
> § 4.1-4.4 详细描述了测试计划如何从 Unit → Integration → System 演进
> 每个阶段都说明了：Focus, Rationale, Challenges, Adaptations

**典型扣分点**（你已避免）：
- ❌ 没有说明测试计划如何变化
- ❌ 只有测试类型，没有数量估计
- ❌ 没有需求映射

---

## ⚠️ LO2.2 - Critical Evaluation of Test Plan (评价计划)

### 评分标准

| 分数 | 标准 | 你的体现 |
|-----|------|---------|
| **1-2** | 只说优点，看不出缺点 | ❌ |
| **3** | 提到缺点，但分析不深 | ❌ |
| **4** | **诚实指出缺点 + 分析原因 + 说明影响 + 未来改进** | ✅ § 7 "Known Limitations" |

### 关键检查点

**必须包含**：
- [ ] **至少 2-3 个明确的缺点**
- [ ] 每个缺点的影响分析
- [ ] 为什么存在这个缺点（时间/成本/技术限制）
- [ ] 未来如何改进

**你的文档位置**：
```
LO2_Test_Plan.md § 7
├── 7.1 Current Gaps
│   ├── Concurrent Operation Testing    ✅ Gap + Risk + Mitigation + Future
│   ├── Performance Testing             ✅ 完整分析
│   └── Frontend E2E Coverage           ✅ 诚实承认
└── 7.2 Planned Improvements            ✅ 具体改进方案
```

**高分话术示例**（你的文档）：
```markdown
**Concurrent Operation Testing** (L01 Requirement 1.m)
- **Gap**: No stress tests for simultaneous submissions
- **Risk**: Race conditions in file uploads or database writes
- **Mitigation**: Database transactions provide some safety
- **Future Work**: Add pytest-xdist for parallel test execution
```

**典型扣分点**（你已避免）：
- ❌ "我的测试计划很完美"
- ❌ 只说缺点，不说影响或改进
- ❌ 找一些无关紧要的"缺点"敷衍

**Auditor 想看到的态度**：
> "我知道我没测所有东西，这是为什么，这是影响，这是我如果有时间会怎么改进。"

---

## ✅ LO2.3 - Instrumentation (代码改造)

### 评分标准

| 分数 | 标准 | 你的体现 |
|-----|------|---------|
| **1-2** | 没有实质性改造，或只有琐碎改变 | ❌ |
| **3** | 有一些改造，但没说清楚为什么 | ❌ |
| **4** | **实质性改造 + Before/After 对比 + 测试收益说明** | ✅ 6 个改造 |

### 关键检查点

**必须展示**：
- [ ] **至少 1-2 个实质性改造**（不是改个变量名）
- [ ] Before/After 代码对比
- [ ] 为什么这个改造让测试更容易
- [ ] 有多少测试因此受益

**你的 6 个改造**：

| 改造 | 实质性？ | Before/After？ | 测试收益？ |
|-----|---------|---------------|-----------|
| 1. 提取纯函数 | ✅ 高 | ✅ 有 | 80+ tests |
| 2. Mock seam | ✅ 高 | ✅ 有 | All recording tests |
| 3. Database fixtures | ✅ 高 | ✅ 有 | All integration tests |
| 4. 异常返回值 | ✅ 中 | ✅ 有 | System tests |
| 5. 状态可观察 | ✅ 中 | ✅ 有 | Integration tests |
| 6. 测试数据生成 | ✅ 中 | ✅ 有 | System tests |

**高分示例**（你的文档 § 1.1）：
```markdown
### 1.1 Extracting Pure Functions

**Problem**: Feedback generation logic was embedded in API route...

**Before**: [Code showing mixed concerns]
**After**: [Code showing pure function]

**Benefits for Testing**:
- ✅ Can test `_calculate_grade()` with 15+ boundary value tests
- ✅ Fast execution (no database or HTTP overhead)

**Evidence**: See `tests/unit/test_feedback_service.py::TestCalculateGrade`
```

**典型扣分点**（你已避免）：
- ❌ "我改了一些变量名"（不算 instrumentation）
- ❌ 只说做了什么，不说为什么
- ❌ 没有 Before/After 对比

**Auditor 想看到**：
- 你理解什么是 testability
- 你能识别哪些代码结构妨碍测试
- 你能通过重构改善 testability

---

## ⚠️ LO2.4 - Evaluate Instrumentation (评价改造)

### 评分标准

| 分数 | 标准 | 你的体现 |
|-----|------|---------|
| **1-2** | 只说改造很好，没有批判 | ❌ |
| **3** | 提到不足，但分析浅显 | ❌ |
| **4** | **具体不足 + 量化影响 + 改进方案 + 成本分析** | ✅ § 4 |

### 关键检查点

**必须包含**：
- [ ] **至少 2-3 个改造的不足**
- [ ] 具体说明哪里不够好
- [ ] 如果改进，会怎么做
- [ ] 为什么现在没做（成本/收益分析）

**你的 3 个批判点**：

```
LO2_Instrumentation_Report.md § 4.2
├── Limited Observability         ✅ 具体 gap + 改进代码示例
├── No Timing Metrics             ✅ 影响分析 + 简单实现方案
└── Shallow Mock Behavior         ✅ 真实案例 + 改进思路
```

**高分示例**（你的文档 § 4.2）：
```markdown
⚠️ **Limited Observability**
- **Gap**: No logging instrumentation for debugging failed tests
- **Impact**: When integration tests fail, hard to see intermediate state
- **Example**: Multi-table transaction failures don't log which table failed
- **Improvement**: Add structured logging with debug level
  [Code example provided]
```

**典型扣分点**（你已避免）：
- ❌ "我的改造完美无缺"
- ❌ 只说"可以加日志"，不说为什么需要、如何实现
- ❌ 找一些无关紧要的"不足"

**Cost-Benefit 表格**（你的 § 4.3）：
```markdown
| Instrumentation | Implementation Cost | Testing Benefit | Verdict |
|----------------|---------------------|----------------|---------|
| Pure functions | Low (1 hour) | Very High (80+ tests) | ✅ Excellent ROI |
| Timing metrics | Low (1 hour) | Medium | ⚠️ Should add |
| Contract testing | High (8+ hours) | Medium | ❌ Not justified yet |
```

**Auditor 想看到的态度**：
> "我的改造整体很好，但有些地方确实不够完善。如果我有更多时间/资源，我会优先改进 X 和 Y，因为它们 ROI 高。Z 暂时不做，因为成本太高。"

---

## 🎯 快速自检（提交前）

### LO2.1 Checklist

```
LO2_Test_Plan.md
├── [ ] 有三种测试类型（Unit/Integration/System）
├── [ ] 每种类型有数量估计
├── [ ] 有需求映射表
├── [ ] 有 evolution story（4-5 个阶段）
│       └── 每个阶段：Focus + Rationale + Challenges + Adaptations
├── [ ] 有测试环境说明
└── [ ] 有成功标准
```

### LO2.2 Checklist

```
LO2_Test_Plan.md § 7
├── [ ] 至少 2-3 个明确缺点
├── [ ] 每个缺点都说明了：Gap + Risk + Mitigation + Future
├── [ ] 有诚实的自我评估
└── [ ] 有具体改进计划
```

### LO2.3 Checklist

```
LO2_Instrumentation_Report.md § 1
├── [ ] 至少 1-2 个实质性改造
├── [ ] 每个改造有 Before/After 对比
├── [ ] 说明了测试收益（有多少测试因此受益）
├── [ ] 有 Evidence 指向实际测试文件
└── [ ] 有总结表格
```

### LO2.4 Checklist

```
LO2_Instrumentation_Report.md § 4
├── [ ] 至少 2-3 个改造不足
├── [ ] 每个不足都有：Gap + Impact + Improvement
├── [ ] 有成本收益分析（Cost-Benefit table）
├── [ ] 有自我评分（X/10）并说明理由
└── [ ] 有 Lessons Learned
```

---

## 🗣️ 答辩准备（Viva Questions）

### Q1: "你的测试计划怎么制定的？"

**❌ 错误回答**：
> "我一开始就决定写 150 个测试，分成三类..."

**✅ 正确回答**：
> "我的测试计划是演进式的。最开始（Week 1-2）我专注于单元测试，建立业务逻辑的基础验证。然后（Week 3）我发现集成问题，所以加了 integration tests。最后（Week 4）我做了端到端系统测试。
>
> 这个过程不是预先设计好的，而是根据发现的问题不断调整。比如在 Week 2，我意识到 feedback logic 需要重构才能测试，所以提取了纯函数。
>
> 详见 LO2_Test_Plan.md § 4 Evolution of Test Plan。"

### Q2: "你的测试计划有什么问题？"

**❌ 错误回答**：
> "我觉得我的计划很好，没什么问题。"

**✅ 正确回答**：
> "有三个明显的缺点：
>
> 1. **Concurrent testing 缺失**：我没测并发提交场景，可能有 race conditions。不过数据库事务提供了一定保护。如果有时间，我会用 pytest-xdist 加压力测试。
>
> 2. **Performance testing 不足**：虽然需求说 API 要在 3 秒内响应，但我没加性能基准测试。这是个明显疏漏。
>
> 3. **Frontend E2E 覆盖有限**：只有 smoke tests，没有全面的 UI 自动化。这是权衡的结果——UI 测试成本高、易碎，我选择用 manual exploratory testing 替代。
>
> 详见 LO2_Test_Plan.md § 7。"

### Q3: "你做了哪些 instrumentation？"

**❌ 错误回答**：
> "我改了一些代码让它更好测..."

**✅ 正确回答**：
> "主要做了 6 个改造，其中 3 个是高影响的：
>
> 1. **提取纯函数**：把 feedback logic 从 route handler 拆出来，变成可独立测试的纯函数。这使得我能写 80+ 单元测试覆盖所有评分边界。
>
> 2. **Mock seam**：在 PronunciationService 加了 Azure API 的 fallback，测试时不需要真实的 Azure 凭证。这让所有测试都能离线运行，而且快很多。
>
> 3. **Database fixtures**：设计了 per-test 的 in-memory database，每个测试都有干净的数据库。这保证了测试隔离和速度。
>
> 详见 LO2_Instrumentation_Report.md § 1，有 Before/After 代码对比。"

### Q4: "你的 instrumentation 够不够？"

**❌ 错误回答**：
> "够了，我觉得很好。"

**✅ 正确回答**：
> "整体还不错，但有明显的改进空间。我给自己打 7.5/10。
>
> **不足之处**：
> 1. **缺少 logging**：测试失败时很难调试，因为没有中间状态日志。应该加 structured logging。
> 2. **Mock 太简单**：Mock Azure API 只是随机生成分数，不能模拟真实的错误模式。应该用录制的真实响应。
> 3. **没有性能度量**：无法验证 '3 秒响应' 这个需求。应该加简单的 timing assertion。
>
> 这些改进都是 low cost, medium benefit，理应做。但由于时间限制，优先保证了核心测试功能。
>
> 详见 LO2_Instrumentation_Report.md § 4。"

### Q5: "如果重新做，会改什么？"

**❌ 错误回答**：
> "都很好，不用改。"

**✅ 正确回答**：
> "核心策略不变，但会优先加这两个：
>
> 1. **从一开始就加 logging**：现在回头加 logging 要改很多文件，如果一开始就有，调试会容易很多。
>
> 2. **建立性能 baseline**：应该在早期就加 timing tests，这样能追踪性能变化。现在没有 baseline，不知道是否有 regression。
>
> 但我**不会**改变测试分配（backend 多，frontend 少）——这个决策是对的。
>
> 详见 LO2_Instrumentation_Report.md § 5 Recommendations。"

---

## 💯 高分要素总结

### LO2.1（Test Plan）- 要点

✅ **Evolution story** - 测试计划如何演进
✅ **Requirement mapping** - 每个需求对应哪些测试
✅ **Concrete numbers** - 不是"一些测试"，而是"50+ unit tests"

### LO2.2（Evaluate Plan）- 要点

✅ **Honest gaps** - 诚实指出 2-3 个缺点
✅ **Impact analysis** - 每个缺点的影响是什么
✅ **Future work** - 如果有时间会怎么改进

### LO2.3（Instrumentation）- 要点

✅ **Substantial changes** - 实质性改造（不是改变量名）
✅ **Before/After** - 对比代码展示改进
✅ **Evidence** - 指向受益的测试文件

### LO2.4（Evaluate Instrumentation）- 要点

✅ **Specific weaknesses** - 具体不足（不是泛泛而谈）
✅ **Improvement proposals** - 有代码示例的改进方案
✅ **Cost-benefit** - 为什么有些改进没做

---

## 📚 文档使用指南

### 在 Portfolio 中的组织

```
/root/ilp/
├── docs/
│   ├── LO2_Test_Plan.md                    # 主文档（10 页）
│   ├── LO2_Instrumentation_Report.md       # 主文档（8 页）
│   └── LO2_Grading_Checklist.md           # 你的备战手册（不提交）
├── tests/
│   └── ... 150+ tests (LO3 的证据，但也是 LO2 的证据)
└── L01_Testing_Requirements.md
```

### 答辩时的使用

**被问到 LO2.1**：
> "请看 LO2_Test_Plan.md 第 4 节，我详细记录了测试计划的演进过程..."

**被问到 LO2.2**：
> "我在 LO2_Test_Plan.md 第 7 节诚实指出了 3 个缺点，每个都分析了 Gap-Risk-Mitigation-Future..."

**被问到 LO2.3**：
> "请看 LO2_Instrumentation_Report.md 第 1 节，我做了 6 个改造，有 Before/After 代码对比..."

**被问到 LO2.4**：
> "我在第 4 节批判性评估了这些改造，给自己打 7.5/10，因为..."

---

## ✨ 最后的话

**LO2 的精髓**：

1. **Planning** ≠ 完美的计划
   - 而是：有思考过程的计划

2. **Reflection** ≠ 说自己很好
   - 而是：诚实指出不足，分析原因

3. **Instrumentation** ≠ 高深技术
   - 而是：实质性改造 + 清楚说明为什么

4. **Evaluation** ≠ 找无关紧要的缺点
   - 而是：真实问题 + 改进方案 + 成本分析

**你的两个文档完美体现了这 4 点** ✅

Marker 会看到：
- 一个会思考的工程师（不是机械写代码）
- 一个会反思的学习者（不是盲目自信）
- 一个会权衡的专业人士（不是完美主义者）

**这正是 LO2 想要的！** 🎯
