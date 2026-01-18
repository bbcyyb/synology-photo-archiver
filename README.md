# 群晖照片归档器

[![Python application](https://github.com/bbcyyb/synology-photo-archiver/actions/workflows/python-app.yml/badge.svg)](https://github.com/bbcyyb/synology-photo-archiver/actions/workflows/python-app.yml)

这是一个 Python 脚本，用于自动查找目录中新增和修改过的照片，将其打包成加密、分卷的 7z 归档文件，并移动到目标目录。此脚本设计为在群晖 NAS 上作为定时任务运行。

## 功能特性

-   **幂等性**: 脚本会跟踪已处理的文件，并仅归档新增或修改过的文件。
-   **可配置**: 所有路径、归档密码和分卷大小都可以在配置文件中设置。
-   **安全**: 创建受密码保护的 7z 归档文件。
-   **分卷归档**: 将大型归档文件分割成更小的卷，以便于管理。

## 前提条件

1.  **Python 3**: 您的群晖 NAS 必须安装 Python 3。您可以通过套件中心安装。
2.  **7-Zip**: 必须安装 `7z` 命令行工具。您可能需要通过群晖社区套件源或其他方式安装。

## 设置

1.  **复制文件**: 将 `synology-photo-archiver` 目录复制到群晖 NAS 上的某个位置（例如，`/volume1/scripts/`）。
2.  **创建 `config.ini`**:
    -   导航到 `synology-photo-archiver` 目录。
    -   复制 `config.ini.template` 并将其命名为 `config.ini`。
    -   编辑 `config.ini`，配置您所需的设置：
        ```ini
        [Paths]
        ; 存放原始照片的目录。
        source_dir = /volume1/photo
        
        ; 7z 归档文件将保存的目录。
        destination_dir = /volume1/backups/photo_archives
        
        ; 7z 可执行文件的完整路径。可以使用 'which 7z' 或 'find / -name 7z' 查找。
        7z_executable = /usr/local/bin/7z

        [Archive]
        ; 加密归档文件的密码。请使用强密码。
        password = YOUR_SECRET_PASSWORD
        
        ; 每个分卷的大小（例如，1g = 1 GB, 500m = 500 MB）。
        volume_size = 1g

        [State]
        ; 用于存储已处理文件状态的文件。
        ; 建议将其放置在脚本目录内。
        file = /volume1/scripts/synology-photo-archiver/processed_files.json
        ```
3.  **权限**: 确保运行脚本的用户对 `source_dir` 具有读取权限，对 `destination_dir` 和脚本目录（用于状态文件）具有读写权限。

## 手动运行脚本

您可以手动运行脚本以测试您的配置。

1.  通过 SSH 连接到您的群晖 NAS。
2.  导航到脚本目录：
    ```bash
    cd /volume1/scripts/synology-photo-archiver
    ```
3.  运行脚本：
    ```bash
    python3 src/archiver.py
    ```
    脚本会将其进度打印到控制台。

## 使用群晖任务计划程序进行定时

要自动运行脚本，请使用群晖控制面板中的任务计划程序。

1.  前往 **控制面板 > 任务计划程序**。
2.  点击 **创建 > 计划的任务 > 用户定义的脚本**。
3.  **常规** 选项卡:
    -   **任务**: 为您的任务命名（例如，“照片归档器”）。
    -   **用户**: 选择运行脚本的用户（例如，`root` 或管理员用户）。
4.  **计划** 选项卡:
    -   设置脚本的运行频率（例如，每天凌晨 2:00）。
5.  **任务设置** 选项卡:
    -   在 **用户定义的脚本** 下，输入以下命令，请务必调整脚本的路径：
        ```bash
        cd /volume1/scripts/synology-photo-archiver && python3 src/archiver.py
        ```
    -   建议将输出结果重定向到日志文件以便于调试。您可以通过勾选“将运行结果发送至电子邮件”或在脚本命令中重定向输出来实现：
        ```bash
        cd /volume1/scripts/synology-photo-archiver && python3 src/archiver.py >> /volume1/scripts/synology-photo-archiver/archiver.log 2>&1
        ```
6.  点击 **确定** 保存任务。您可以从任务计划程序中手动运行它以进行测试。