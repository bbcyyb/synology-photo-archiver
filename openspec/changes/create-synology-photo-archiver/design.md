# 设计: 照片归档器

## 1. 架构决策
- **核心架构**: 采用模块化的 Python 脚本架构。一个主入口点 (`archiver.py`) 调用不同的模块来处理特定任务。
- **配置管理**:
  - 使用标准的 `configparser` 模块读取 `config.ini` 文件。
  - 配置文件将包含 `[Paths]`、`[Archive]` 和 `[State]` 等部分，用于定义源目录、目标目录、7z 路径、压缩包密码和状态文件位置。
- **状态管理与幂等性**:
  - 幂等性通过一个 JSON 格式的状态文件 (`processed_files.json`) 来保证。
  - 该文件将存储一个字典，键为已处理文件的相对路径，值为文件的最后修改时间戳。
  - **工作流程**:
    1.  程序启动时读取 `processed_files.json`。
    2.  遍历照片源目录，对每个文件：
        a. 如果文件路径不在状态文件中，则为新文件。
        b. 如果文件路径在状态文件中，但其当前修改时间戳与记录的不符，则为已修改文件。
    3.  将所有新文件和已修改文件添加到一个待处理列表中。
    4.  调用 7z 子进程，将待处理列表中的文件进行打包和加密。
    5.  如果打包成功，则更新 `processed_files.json`，将新处理的文件的信息添加或更新进去。
- **外部依赖调用**:
  - 使用 Python 的 `subprocess` 模块安全地调用 `7z` 命令行工具。
  - 命令和参数将被清晰地构建，密码将通过 `-p` 参数传递。

## 2. 风险与权衡
- **密码安全**: 密码明文存储在 `config.ini` 中，这是一个安全风险。
  - **缓解措施**: 在项目初期，我们将接受这个风险，但在文档中明确指出，`config.ini` 文件应具有严格的文件权限（例如 `600`），只有运行脚本的用户可以读取。未来可以考虑使用更安全的凭据管理方式（如环境变量或加密的凭据存储）。
- **7z 可用性**: 程序强依赖于环境中 `7z` 命令的可用性。
  - **缓解措施**: 程序启动时会检查 `7z` 路径是否有效，如果无效则会提前失败并给出明确的错误信息。

## 3. 数据模型
- **config.ini**:
  ```ini
  [Paths]
  source_dir = /path/to/photos
  destination_dir = /path/to/archives
  7z_executable = /usr/bin/7z

  [Archive]
  password = YOUR_SECRET_PASSWORD
  volume_size = 1g

  [State]
  file = /path/to/state/processed_files.json
  ```
- **processed_files.json**:
  ```json
  {
    "photos/2023/vacation/IMG_001.jpg": 1672531200.0,
    "photos/2024/birthday/IMG_002.png": 1704067200.0
  }
  ```
