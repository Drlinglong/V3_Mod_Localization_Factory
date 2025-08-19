# ❓ 常见问题

> 问题解决方案和故障排除指南

## 🚨 常见错误和解决方案

### 1. 环境配置问题

#### 问题：Python命令未找到
**错误信息**: `'python' 不是内部或外部命令，也不是可运行的程序或批处理文件。`

**解决方案**:
1. 检查Python是否正确安装
2. 验证PATH环境变量设置
3. 重启命令行窗口
4. 尝试使用 `python3` 命令

**详细步骤**:
```bash
# 检查Python版本
python --version
python3 --version

# 如果都失败，重新安装Python并勾选"Add Python to PATH"
```

#### 问题：pip命令未找到
**错误信息**: `'pip' 不是内部或外部命令`

**解决方案**:
```bash
# 使用Python模块方式运行pip
python -m pip install package_name

# 或者重新安装Python，确保pip被正确安装
```

#### 问题：依赖库安装失败
**错误信息**: `ERROR: Could not find a version that satisfies the requirement`

**解决方案**:
```bash
# 更新pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 或者使用conda安装
conda install package_name
```

### 2. API配置问题

#### 问题：API密钥无效
**错误信息**: `Invalid API key` 或 `Authentication failed`

**解决方案**:
1. 检查环境变量设置
2. 验证API密钥是否正确
3. 确认API服务是否可用
4. 检查网络连接

**环境变量设置**:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_actual_api_key"
$env:OPENAI_API_KEY="your_actual_api_key"

# Windows CMD
set GEMINI_API_KEY=your_actual_api_key
set OPENAI_API_KEY=your_actual_api_key

# 永久设置（推荐）
# 系统属性 → 环境变量 → 新建
```

#### 问题：API调用超时
**错误信息**: `Request timeout` 或 `Connection timeout`

**解决方案**:
1. 检查网络连接
2. 增加超时时间
3. 使用代理服务器
4. 分批处理减少单次请求大小

**配置调整**:
```python
# 在config.py中调整超时设置
API_TIMEOUT = 60  # 增加到60秒
RETRY_ATTEMPTS = 5  # 增加重试次数
```

#### 问题：API配额不足
**错误信息**: `Rate limit exceeded` 或 `Quota exceeded`

**解决方案**:
1. 检查API使用量
2. 升级API套餐
3. 降低并发请求数
4. 使用多个API密钥轮换

### 3. 文件处理问题

#### 问题：文件解析失败
**错误信息**: `Failed to parse file` 或 `Invalid file format`

**解决方案**:
1. 检查文件编码（推荐UTF-8）
2. 验证文件格式是否正确
3. 检查文件是否损坏
4. 尝试手动修复文件

**文件检查**:
```bash
# 检查文件编码
file -i your_file.yml

# 检查文件内容
head -20 your_file.yml
```

#### 问题：输出文件为空
**错误信息**: 输出文件存在但内容为空

**解决方案**:
1. 检查源文件是否有可翻译内容
2. 验证API调用是否成功
3. 检查日志文件中的错误信息
4. 确认目标语言设置正确

#### 问题：文件权限错误
**错误信息**: `Permission denied` 或 `Access denied`

**解决方案**:
1. 以管理员身份运行程序
2. 检查文件夹权限设置
3. 关闭可能占用文件的程序
4. 检查防病毒软件设置

### 4. 性能问题

#### 问题：翻译速度慢
**现象**: 处理大量文件时速度很慢

**解决方案**:
1. 启用并行处理
2. 调整批处理大小
3. 使用更快的API服务
4. 优化网络连接

**性能调优**:
```python
# 调整并行处理参数
RECOMMENDED_MAX_WORKERS = min(32, cpu_count * 3)  # 增加工作线程
CHUNK_SIZE = 50  # 增加批处理大小
```

#### 问题：内存占用过高
**现象**: 程序运行时内存使用量激增

**解决方案**:
1. 减少并行处理线程数
2. 降低批处理大小
3. 及时清理临时文件
4. 使用流式处理大文件

#### 问题：CPU使用率过高
**现象**: 程序运行时CPU使用率接近100%

**解决方案**:
1. 降低并行处理线程数
2. 使用异步处理替代多线程
3. 优化算法效率
4. 添加处理间隔

### 5. 词典系统问题

#### 问题：词典加载失败
**错误信息**: `Failed to load glossary` 或 `Glossary file not found`

**解决方案**:
1. 检查词典文件路径
2. 验证词典文件格式
3. 确认文件编码正确
4. 检查词典文件权限

**词典文件检查**:
```bash
# 检查词典文件是否存在
ls -la data/glossary/

# 检查文件内容
head -10 data/glossary/glossary.json
```

#### 问题：词典匹配效果差
**现象**: 词典术语匹配率低

**解决方案**:
1. 调整模糊匹配阈值
2. 扩充词典内容
3. 优化匹配算法
4. 使用同义词词典

**匹配参数调整**:
```python
# 调整模糊匹配设置
FUZZY_MATCH_THRESHOLD = 0.7  # 降低阈值提高匹配率
FUZZY_MATCH_MODE = "loose"   # 使用宽松模式
```

### 6. 国际化问题

#### 问题：界面显示乱码
**现象**: 中文界面显示为乱码

**解决方案**:
1. 检查终端编码设置
2. 确认语言文件编码为UTF-8
3. 设置正确的环境变量
4. 使用支持中文的终端

**编码设置**:
```bash
# Windows CMD
chcp 65001

# Windows PowerShell
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8
```

#### 问题：语言切换失败
**现象**: 无法切换到目标语言

**解决方案**:
1. 检查语言文件是否存在
2. 验证语言文件格式
3. 确认语言代码正确
4. 重启程序

### 7. 网络问题

#### 问题：网络连接失败
**错误信息**: `Connection failed` 或 `Network unreachable`

**解决方案**:
1. 检查网络连接
2. 配置代理服务器
3. 检查防火墙设置
4. 使用VPN服务

**代理配置**:
```bash
# 设置HTTP代理
set HTTP_PROXY=http://proxy_server:port
set HTTPS_PROXY=http://proxy_server:port

# 或者在代码中配置
import os
os.environ['HTTP_PROXY'] = 'http://proxy_server:port'
os.environ['HTTPS_PROXY'] = 'http://proxy_server:port'
```

#### 问题：DNS解析失败
**错误信息**: `DNS resolution failed`

**解决方案**:
1. 更换DNS服务器
2. 检查hosts文件
3. 使用IP地址替代域名
4. 刷新DNS缓存

## 🔧 调试技巧

### 启用详细日志
```python
# 在config.py中设置
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
VERBOSE_OUTPUT = True
```

### 检查系统信息
```python
# 运行系统信息检查
python scripts/main.py --check-system
```

### 测试API连接
```python
# 测试API连接
python -c "
from scripts.core.api_handler import test_api_connection
test_api_connection('gemini')
"
```

## 📞 获取帮助

### 1. 查看日志文件
日志文件位于 `logs/` 目录，包含详细的错误信息

### 2. 检查项目状态
```bash
# 检查项目完整性
python scripts/main.py --status
```

### 3. 提交Issue
如果问题仍然存在，请在GitHub上提交Issue，包含：
- 错误信息截图
- 系统环境信息
- 复现步骤
- 日志文件内容

### 4. 社区支持
- 查看 [项目文档](docs/)
- 参与 [社区讨论](https://github.com/your-repo/discussions)
- 联系项目维护者

## 📚 预防措施

### 1. 定期备份
- 备份重要的配置文件
- 保存成功的翻译结果
- 记录有效的配置参数

### 2. 环境隔离
- 使用虚拟环境
- 避免全局安装包
- 保持依赖版本一致

### 3. 测试验证
- 先用小文件测试
- 验证API配置
- 检查输出结果

---

> 💡 **提示**: 大多数问题都可以通过仔细阅读错误信息和日志文件来解决。如果遇到新问题，请先搜索现有文档和Issue。
