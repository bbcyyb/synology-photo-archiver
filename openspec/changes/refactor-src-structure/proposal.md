# 变更：Refactor Source Code Structure

## 为什么
目前的 `src/archiver.py` 是一个单文件脚本，包含了配置读取、状态管理、文件扫描和压缩逻辑。随着功能增加（例如后续可能添加的日志、通知等），这种结构难以维护和扩展。

## 变更内容
- 将 `src/archiver.py` 拆分为多个模块：
    - `src/config.py`: 处理配置加载
    - `src/state.py`: 处理状态文件读写
    - `src/scanner.py`: 处理文件扫描逻辑
    - `src/compression.py`: 处理 7z 压缩逻辑
    - `src/main.py`: 作为新的程序入口点
- 更新 `tests/` 以适应新的模块结构

## 影响
- **受影响的代码**: `src/archiver.py` 将被重写/拆分。
- **受影响的测试**: `tests/test_archiver.py` 需要更新导入路径。
- **配置兼容性**: 此次重构不改变 `config.ini` 格式，保持向后兼容。
