# Hugging Face 命令行工具

[English](README.md) | [中文](README_CN.md)

本仓库包含一套交互式命令行工具，用于管理 Hugging Face Hub 上的文件。这些脚本允许你轻松地上传、下载和删除 Hugging Face 仓库（模型、数据集或 Spaces）中的文件。

## 前置条件

请确保你已安装 Python 3。你需要安装以下依赖：

```bash
pip install huggingface_hub inquirer tqdm requests
```

## 身份验证

大多数操作（上传、删除以及从私有仓库下载）都需要一个具有 **write（写入）** 权限的 Hugging Face User Access Token。

你可以通过以下三种方式提供 Token：
1.  **命令行参数**：通过 `--token YOUR_TOKEN` 传递。
2.  **交互式提示**：如果未提供，脚本会询问你输入。
3.  **Hugging Face 缓存**：如果你已经使用 `huggingface-cli login` 登录过，脚本会自动使用缓存的 Token。

## 工具列表

### 1. 下载器 (`hf_downloader.py`)

交互式地选择并从 Hugging Face 仓库下载文件。

**用法：**

```bash
# 交互模式
python3 hf_downloader.py

# 指定仓库和类型
python3 hf_downloader.py username/repo_id --type model

# 下载特定文件
python3 hf_downloader.py username/repo_id --files config.json,pytorch_model.bin
```

**功能：**
-   交互式文件选择菜单。
-   “ALL (Download all files)” 选项可下载整个仓库。
-   支持模型（Models）和数据集（Datasets）。
-   使用 `huggingface_hub` 支持断点续传。

### 2. 上传器 (`hf_uploader.py`)

上传文件或文件夹到 Hugging Face 仓库。上传文件夹时会保留目录结构。

**用法：**

```bash
# 交互模式
python3 hf_uploader.py

# 上传特定文件/文件夹到仓库
python3 hf_uploader.py path/to/local/folder --repo username/repo_id --type model
```

**功能：**
-   如果仓库不存在，会自动创建（提供可见性选项）。
-   保留文件夹结构（例如，上传 `my_folder` 会在仓库中创建 `my_folder/`）。
-   支持模型（Models）、数据集（Datasets）和 Spaces。

### 3. 删除器 (`hf_deleter.py`)

交互式地选择并删除 Hugging Face 仓库中的文件。

**用法：**

```bash
# 交互模式
python3 hf_deleter.py

# 指定仓库
python3 hf_deleter.py username/repo_id --type dataset
```

**功能：**
-   列出文件及其大小。
-   批量删除（在一次提交中删除多个文件）。
-   删除前的安全确认提示。

## 许可证

MIT
