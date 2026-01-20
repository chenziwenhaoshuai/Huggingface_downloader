# Hugging Face Tools

[English](README.md) | [中文](README_CN.md)

This repository contains a set of interactive command-line tools to manage files on the Hugging Face Hub. These scripts allow you to easily upload, download, and delete files from your Hugging Face repositories (Models, Datasets, or Spaces).

## Prerequisites

Make sure you have Python 3 installed. You will need to install the required dependencies:

```bash
pip install huggingface_hub inquirer tqdm requests
```

## Authentication

Most operations (Upload, Delete, and downloading from private repos) require a Hugging Face User Access Token with **write** permissions.

You can provide the token in three ways:
1.  **CLI Argument**: Pass it via `--token YOUR_TOKEN`.
2.  **Interactive Prompt**: If not provided, the script will ask for it.
3.  **Hugging Face Cache**: If you have logged in via `huggingface-cli login`, the scripts will automatically use the cached token.

## Tools

### 1. Downloader (`hf_downloader.py`)

Interactively select and download files from a Hugging Face repository.

**Usage:**

```bash
# Interactive mode
python3 hf_downloader.py

# Specify repo and type
python3 hf_downloader.py username/repo_id --type model

# Download specific files
python3 hf_downloader.py username/repo_id --files config.json,pytorch_model.bin
```

**Features:**
-   Interactive file selection menu.
-   "ALL (Download all files)" option to download the entire repository.
-   Supports Models and Datasets.
-   Resumable downloads using `huggingface_hub`.

### 2. Uploader (`hf_uploader.py`)

Upload a file or a folder to a Hugging Face repository. It preserves the directory structure when uploading folders.

**Usage:**

```bash
# Interactive mode
python3 hf_uploader.py

# Upload a specific file/folder to a repo
python3 hf_uploader.py path/to/local/folder --repo username/repo_id --type model
```

**Features:**
-   Automatically creates the repository if it doesn't exist (with visibility options).
-   Preserves folder structure (e.g., uploading `my_folder` creates `my_folder/` in the repo).
-   Supports Models, Datasets, and Spaces.

### 3. Deleter (`hf_deleter.py`)

Interactively select and delete files from a Hugging Face repository.

**Usage:**

```bash
# Interactive mode
python3 hf_deleter.py

# Specify repo
python3 hf_deleter.py username/repo_id --type dataset
```

**Features:**
-   Lists files with sizes.
-   Batch deletion (deletes multiple files in a single commit).
-   Safety confirmation prompt before deletion.

## License

MIT
