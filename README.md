# HuggingFace 下载器

该项目提供一个脚本，用于从 Hugging Face 下载超大的，难下载的，老报错的数据集。脚本支持错误处理，并允许恢复下载失败的文件。

## 功能

- **首次下载**：下载指定数据集中的所有文件。
- **错误处理**：如果下载失败，脚本会记录失败的文件，并允许仅重新下载失败的文件。
- **并行下载**：脚本使用多线程来加速下载过程，支持同时下载多个文件。
- **可定制**：你可以修改脚本，下载其他 Hugging Face 数据集。

## 环境要求

- Python 3.x
- `huggingface_hub` 库
- `concurrent.futures` 用于并行下载
- `os`、`json` 等标准 Python 库

可以通过以下命令安装所需的库：

```bash
pip install huggingface_hub
```

## 配置说明

- **Hugging Face 登录**：脚本需要你使用 API Token 登录 Hugging Face，确保你的 token 是有效的并已正确设置。
- **环境变量**：你可以通过设置 `HF_ENDPOINT` 环境变量来指定 Hugging Face 的端点，默认值为 `'https://hf-mirror.com'`。

## 脚本使用

1. **首次下载**：
   默认情况下，脚本会下载 `repo/id` 数据集中的所有文件。它会获取数据集文件列表并开始下载。

2. **错误处理与重试**：
   如果某个文件下载失败，脚本会将失败的文件记录到 `error.txt` 文件中。你可以将 `continue_download` 标志设置为 `True`，只重新下载失败的文件。

3. **并行下载**：
   脚本使用 `ThreadPoolExecutor` 来并行下载多个文件，下载的最大并发数由 `max_workers` 参数控制，默认值为 8。

## 脚本结构

- **登录**：使用 API Token 登录 Hugging Face。
- **下载文件**：通过 `snapshot_download` 方法下载数据集中的文件。
- **错误记录**：下载失败的文件会被记录在 `error.txt` 文件中，以便后续重试。
- **多线程**：通过并行下载提高下载速度。

## 如何运行

1. 克隆此项目到本地机器：
   ```bash
   git clone https://github.com/yourusername/huggingface_downloader.git
   cd huggingface_downloader
   ```

2. 运行脚本：
   ```bash
   python download_dataset.py
   ```

3. 如果某个下载失败，脚本会将失败的文件记录到 `error.txt` 中。你可以将 `continue_download = True` 设置为 `True`，然后重新运行脚本来下载失败的文件。

## 问题排查

- 确保你的 Hugging Face API Token 是有效的，并且正确配置。
- 检查本地的存储空间，确保有足够的空间来存储下载的文件。
- 如果下载遇到问题，检查你的网络连接是否稳定。

## 许可证

该项目采用 MIT 许可证，具体内容请见 [LICENSE](LICENSE) 文件。
```

### 说明：
- 该 **README** 中已经隐藏了敏感信息（如 API Token），你需要在自己的代码中插入正确的值。
- 文件中详细说明了项目的功能、使用方法、配置说明和排查问题的建议，确保其他用户能够理解如何使用这个下载器。
- 在 **如何运行** 部分，提供了从 GitHub 克隆项目并运行脚本的具体步骤。

你可以将这个内容放到你的项目的 `README.md` 文件中。如果以后需要更改或添加更多说明，可以根据实际情况进行调整。
