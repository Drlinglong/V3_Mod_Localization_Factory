---
description: Agent 自动提交工作流
---

## 🤖 Agent 自动提交标准流程

当用户请求提交代码或工作完成后，Agent 应该**自动**执行以下流程：

### 1. 运行 CI 检查
```bash
.\check_before_commit.bat
```

**期望结果**：
- ✅ Python tests PASSED (79个测试)
- ✅ ESLint checks PASSED (0 errors)
- ✅ Git status OK

**失败处理**：
- 如果测试失败 → 修复问题后重新检查
- 如果 ESLint 失败 → 修复代码或调整配置
- 不要强制提交（`--no-verify`）

---

### 2. 分析变更内容
```bash
git status --short
git diff --stat
```

**识别变更类型**：
- 查看修改的文件路径
- 判断变更性质（功能/修复/重构/配置）
- 确定影响范围（前端/后端/测试/文档）

---

### 3. 生成 Commit 消息

**按照 `.agent/commit_guidelines.md` 规范生成**：

#### 单一变更示例：
```
feat(glossary): add phonetic search support
```

#### 多模块变更示例：
```
chore: restore test suite and optimize ESLint config

- Fixed 79 unit tests
- Relaxed ESLint rules to warnings
- Removed outdated integration tests
```

#### 关键规则：
- Type: `feat|fix|refactor|test|chore|docs|style|perf`
- Scope: `ui|api|db|glossary|translation|tests|ci`（可选）
- Subject: 现在时、小写、<50字、无句号
- Body: 仅在必要时添加详细说明

---

### 4. 执行提交
```bash
git add .
git commit -m "<生成的消息>"
```

**自动执行，无需用户确认**（CI 已通过）

---

### 5. 询问推送（可选）

提示用户：
```
✅ Changes committed successfully!

Commit: <commit hash> <commit message>

Push to remote? (y/N):
```

如果用户回复 `y`：
```bash
git push
```

---

## 🎯 Agent 注意事项

1. **CI 优先**：永远先跑 CI，通过后再提交
2. **智能消息**：根据实际变更生成有意义的消息
3. **保持简洁**：commit 消息要简短精准
4. **遵循规范**：严格按照 `commit_guidelines.md`
5. **自动执行**：不要问"是否提交"，CI 通过即可直接提交

---

## 📝 消息生成算法

```python
def generate_commit_message(changed_files):
    # 1. 识别主要变更类型
    if has_new_feature(changed_files):
        type = "feat"
    elif has_bug_fix(changed_files):
        type = "fix"
    elif has_test_changes(changed_files):
        type = "test"
    elif has_refactoring(changed_files):
        type = "refactor"
    else:
        type = "chore"
    
    # 2. 确定影响范围
    scope = detect_scope(changed_files)
    
    # 3. 生成简短描述
    subject = summarize_changes(changed_files)
    
    # 4. 组合消息
    if scope:
        return f"{type}({scope}): {subject}"
    else:
        return f"{type}: {subject}"
```

---

## ✅ 示例场景

### 场景A：修复测试套件
```
变更：tests/*, pytest.ini
消息：test: restore automated test suite
```

### 场景B：优化 ESLint
```
变更：scripts/react-ui/eslint.config.js
消息：chore(ci): relax ESLint rules to warnings
```

### 场景C：新增功能
```
变更：scripts/react-ui/src/components/proofreading/*
消息：feat(ui): add proofreading mode selector
```

### 场景D：混合变更
```
变更：tests/*, scripts/react-ui/eslint.config.js, CI_SETUP.md
消息：chore: setup local CI and restore test suite

- Fixed 79 unit tests
- Configured ESLint to allow warnings
- Added pre-commit check script
```
