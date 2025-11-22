# Remis 构建流水线架构文档 (Build Pipeline Architecture)

**版本**: 1.0
**日期**: 2025-11-23
**状态**: 已实施

## 1. 概述 (Overview)

Project Remis 采用 **Tauri + React + Python (FastAPI)** 的混合架构。为了将 Python 后端与 Tauri 桌面应用无缝集成，我们采用了 **Sidecar (边车)** 模式。本构建流水线旨在自动化处理从源码清理、后端冻结、资源整合到最终安装包生成的全过程。

## 2. 架构设计 (Architecture Design)

构建流程分为两个主要阶段：**后端冻结 (Backend Freezing)** 和 **前端/应用打包 (Frontend/App Bundling)**。

```mermaid
graph TD
    A[开始构建] --> B{环境清理}
    B --> C[后端构建 (Python)]
    C --> D[Sidecar 适配]
    D --> E[前端构建 (React)]
    E --> F[Tauri 打包 (Rust)]
    F --> G[最终安装包 (.msi/.exe)]

    subgraph "后端构建"
    C1[web_server.py] -->|PyInstaller| C2[web_server.exe]
    end

    subgraph "Sidecar 适配"
    C2 -->|重命名| D1[web_server-<target-triple>.exe]
    D1 -->|移动| D2[src-tauri/binaries/]
    end
```

## 3. 详细构建步骤 (Detailed Steps)

构建逻辑由 `scripts/build_pipeline.py` 统一编排。

### 3.1 环境清理 (Clean & Init)
为了防止旧构建产物的干扰，脚本首先执行清理操作：
-   删除 `dist/` (PyInstaller 产物)
-   删除 `build/` (PyInstaller 临时文件)
-   删除 `scripts/react-ui/src-tauri/binaries/` (旧的 Sidecar 文件)
-   重建 `binaries/` 目录以确保目标路径存在。

### 3.2 后端冻结 (Backend Freezing)
使用 **PyInstaller** 将 Python 源码打包为独立可执行文件。
-   **入口文件**: `scripts/web_server.py`
-   **关键参数**:
    -   `--onefile`: 生成单文件 exe。
    -   `--noconsole`: 运行时不显示控制台窗口 (后台运行)。
    -   `--name web_server`: 指定输出文件名。
    -   `--hidden-import`: 显式包含 `uvicorn`, `fastapi`, `pydantic` 等动态加载的库。

### 3.3 Sidecar 适配 (Sidecar Compliance)
Tauri 要求 Sidecar 二进制文件必须包含目标平台的 **Target Triple** 后缀。
-   **检测**: 脚本自动检测当前操作系统和 CPU 架构 (例如 `x86_64-pc-windows-msvc`)。
-   **重命名**: 将 `web_server.exe` 重命名为 `web_server-x86_64-pc-windows-msvc.exe`。
-   **部署**: 将重命名后的文件移动到 `src-tauri/binaries/` 目录。

### 3.4 前端构建 (Frontend Build)
调用 Vite 进行 React 前端构建。
-   命令: `npm install` && `npm run build`
-   输出: `scripts/react-ui/dist/`

### 3.5 Tauri 打包 (Tauri Build)
调用 Tauri CLI 生成最终安装包。
-   命令: `npm run tauri build`
-   配置: `tauri.conf.json` 中的 `externalBin` 字段必须包含 `"web_server"`，以便 Tauri 在打包时自动包含 Sidecar 并处理路径映射。

## 4. 配置说明 (Configuration)

### 4.1 Tauri 配置 (`tauri.conf.json`)
必须在 `bundle` -> `externalBin` 中注册 Sidecar 名称（不带后缀）：

```json
"bundle": {
  "active": true,
  "targets": "all",
  "externalBin": [
    "web_server"
  ],
  ...
}
```

### 4.2 依赖管理
-   **Python**: `requirements.txt` 定义了后端依赖。
-   **Node.js**: `package.json` 定义了前端依赖。
-   **Rust**: `Cargo.toml` 定义了 Tauri 核心依赖。

## 5. 使用指南 (Usage)

### 5.1 运行构建
在项目根目录下运行批处理文件：
```batch
build_app.bat
```
或者直接运行 Python 脚本：
```bash
python scripts/build_pipeline.py
```

### 5.2 前置要求
-   Python 3.x (已安装 pip 依赖)
-   Node.js & npm
-   Rust & Cargo (必须配置在 PATH 中)

## 6. 故障排除 (Troubleshooting)

-   **找不到 Cargo**: 确保安装了 Rust 并重启了终端。
-   **Sidecar 启动失败**: 检查 PyInstaller 的 `--hidden-import` 是否遗漏了库。
-   **构建卡住**: 检查网络连接 (npm/pip/cargo 拉取依赖)。
