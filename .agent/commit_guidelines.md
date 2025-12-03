# Commit 消息规范 (Agent 自动化版)

## 📝 Commit 消息格式

```
<type>(<scope>): <subject>

<body>
```

### Type（必须）

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(ui): add dark mode toggle` |
| `fix` | 修复 Bug | `fix(api): resolve translation timeout` |
| `refactor` | 重构代码 | `refactor(glossary): extract search logic` |
| `test` | 测试相关 | `test: restore test suite` |
| `chore` | 工具/配置 | `chore: update ESLint config` |
| `docs` | 文档 | `docs: update API documentation` |
| `style` | 代码格式 | `style: format with prettier` |
| `perf` | 性能优化 | `perf: optimize translation batch size` |

### Scope（可选）

常用 scope：
- `ui` - 前端界面
- `api` - 后端 API
- `db` - 数据库
- `glossary` - 词典系统
- `translation` - 翻译工作流
- `tests` - 测试套件
- `ci` - CI/CD

### Subject（必须）

- 简短描述（50字以内）
- 使用**现在时**：`add` 而非 `added`
- 首字母**小写**
- 结尾**不加句号**

### Body（可选）

详细描述变更内容，仅在必要时添加。

---

## 🤖 Agent 自动化规则

### 规则 1：优先级排序

当有多个变更时，按优先级选择 type：
1. `feat` > `fix` - 新功能和修复优先
2. `refactor` - 重构次之
3. `test` - 测试修复
4. `chore` - 配置调整

### 规则 2：Scope 识别

根据文件路径自动识别：
- `scripts/react-ui/` → `ui`
- `scripts/routers/` → `api`
- `tests/` → `tests`
- `*.md`, `*.txt` → `docs`
- `eslint.config.js`, `pytest.ini` → `ci`

### 规则 3：消息生成逻辑

```
IF 只有一个文件变更:
    <type>(scope): <根据变更内容生成描述>
    
ELIF 多个文件但都在同一模块:
    <type>(scope): <总结性描述>
    
ELSE:
    <type>: <总结所有变更>
```

### 规则 4：示例模板

**单个功能变更**：
```
feat(glossary): add phonetic search support
```

**多个相关文件**：
```
refactor(api): extract translation validation logic

- Move validation to post_process_validator.py
- Update translation.py imports
- Add unit tests
```

**混合变更**：
```
chore: restore test suite and fix ESLint config

- Fixed 79 unit tests
- Adjusted ESLint rules to allow warnings
- Removed outdated integration tests
```

---

## 🚀 Agent 工作流

### 完成工作后的标准流程：

1. **运行 CI 检查**
   ```bash
   .\check_before_commit.bat
   ```

2. **通过后，检查变更**
   ```bash
   git status --short
   git diff --stat
   ```

3. **生成 commit 消息**
   - 分析变更文件
   - 应用上述规则
   - 生成符合规范的消息

4. **执行提交**
   ```bash
   git add .
   git commit -m "<生成的消息>"
   ```

5. **询问是否推送**
   - 提示用户是否 `git push`

---

## 📌 特殊情况

### 紧急修复（Hot Fix）
```
fix!: critical bug in translation engine

BREAKING CHANGE: Updated API response format
```

### 多人协作
```
feat(ui): add project overview sidebar

Co-authored-by: AI Agent <agent@remis.dev>
```

### 实验性功能
```
feat(experimental): add AI-powered glossary suggestions

⚠️ This feature is experimental and may change.
```

---

## ✅ 质量检查清单

生成消息前确认：
- [ ] Type 选择正确
- [ ] Scope 匹配变更范围
- [ ] Subject 简洁明了（<50字）
- [ ] 使用现在时态
- [ ] 首字母小写
- [ ] 无拼写错误

---

**Agent 备忘**：每次提交前，先运行 CI，通过后根据本规范自动生成消息并提交。
