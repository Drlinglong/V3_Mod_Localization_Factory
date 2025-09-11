# Commit Message

## 更新 run.bat 支持虚拟环境启动和环境检查

### 主要变更
- 更新 `run.bat` 脚本以支持 conda 虚拟环境启动
- 添加了完整的环境检查机制，包括 Python、API 库和密钥验证
- 实现了虚拟环境检测和自动激活功能
- 当检测到 conda 环境时优先使用，否则回退到系统默认环境
- 简化了输出信息，提供更清晰的用户反馈

### 技术细节
- 虚拟环境路径目前硬编码为 `J:\miniconda\condabin\conda.bat`
- 支持检测 OpenAI、Google Gemini、Qwen 三种 API 库
- 检查对应的环境变量：`OPENAI_API_KEY`、`GEMINI_API_KEY`、`DASHSCOPE_API_KEY`
- 添加了详细的错误处理和用户指导信息

### 未来改进
- 考虑实现动态虚拟环境路径检测
- 可能添加对其他虚拟环境管理器的支持（如 venv、pipenv 等）

### 文件变更
- `run.bat` - 主要脚本更新
- `banner.txt` - 恢复 ASCII 艺术字显示