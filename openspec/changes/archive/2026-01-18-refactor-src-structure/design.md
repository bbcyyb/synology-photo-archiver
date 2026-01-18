## 背景
当前代码所有功能耦合在 `archiver.py` 中。为了支持未来的 1-N 功能开发，需要一个更清晰的模块化架构。

## 目标 / 非目标
- **目标**:
    - 将关注点分离（Separation of Concerns）。
    - 提高代码可读性。
    - 方便单元测试独立模块。
- **非目标**:
    - 改变现有程序的运行时行为（功能应保持一致）。
    - 修改配置文件格式。

## 架构设计

### 模块划分

1.  **`src/config.py`**
    - `load_config(path) -> ConfigParser`

2.  **`src/state.py`**
    - `load_state(path) -> dict`
    - `save_state(path, state) -> None`

3.  **`src/scanner.py`**
    - `scan_for_new_and_modified_files(source_dir, processed_files) -> list[Path]`

4.  **`src/compression.py`**
    - `create_archive(...) -> bool`
    - 封装 `subprocess` 调用 7z 的逻辑。

5.  **`src/main.py`**

    - `main()`: 编排上述模块。

## 决策
- **入口文件命名**: 将 `src/archiver.py` 重命名为 `src/main.py` 作为新的入口点。
  > [!WARNING]
  > 这是一个 **Breaking Change**。因为没有代码自动管理 cron job，用户必须**手动更新**群晖 NAS 任务计划程序中的脚本路径（从 `src/archiver.py` 改为 `src/main.py`）。

## 风险
- **导入错误**: 拆分后需确保模块间循环引用（虽然目前看似无循环依赖）。
- **路径问题**: 确保 `sys.path` 或相对导入在拆分后仍能正常工作。
