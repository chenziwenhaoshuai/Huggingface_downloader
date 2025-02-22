import os
import huggingface_hub
import concurrent.futures

# 设置环境变量
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 登录 Hugging Face
huggingface_hub.login("hf_###")

# 导入下载函数
from huggingface_hub import snapshot_download, HfApi
api = HfApi()

continue_download = False  # 设置为 True 表示继续下载之前失败的文件

if not continue_download:
    # 获取数据集文件列表, 适用于第一次下载
    dataset_repo = "Maple728/Time-300B"  # 或者你感兴趣的特定数据集repo
    filtered_repo_files = api.list_repo_files(dataset_repo, repo_type="dataset")
else:
    # 读取下载失败的文件列表，适用于第一次失败后的查缺补漏
    with open(r'./error.txt', 'r') as f:
        filtered_repo_files = eval(f.read())

# 下载的错误列表
err = []

# 定义下载函数
def download_snapshot(file):
    try:
        st = snapshot_download(
            repo_id="Maple728/Time-300B",
            repo_type="dataset",
            cache_dir="D:/time300b/",
            local_dir_use_symlinks=False,
            force_download=True,
            resume_download=True,
            max_workers=64,
            token='hf_###',
            allow_patterns=[file]  # 单个文件名传给 snapshot_download
        )
    except Exception as e:
        print(f"Error downloading {file}: {e}")
        return file  # 返回出错的文件名
    return None  # 成功则返回 None

# 设置线程池最大工作线程数为 8
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = []
    batch_size = 8  # 修改为批处理大小 8

    # 遍历所有文件，每 8 个文件启动一个线程池
    for i in range(0, len(filtered_repo_files), batch_size):
        batch = filtered_repo_files[i:i + batch_size]
        # 为每个文件提交一个下载任务
        for file in batch:
            futures.append(executor.submit(download_snapshot, file))

    # 获取所有任务的执行结果，处理失败的文件
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            err.append(result)

# 将错误文件写入文件
with open(r'./error.txt', 'a') as f:
    f.write(str(err))

print('done')
