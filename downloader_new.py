import argparse
import os
import sys
import time
from huggingface_hub import HfApi, hf_hub_url, hf_hub_download
from huggingface_hub.utils import validate_repo_id, HfHubHTTPError
import inquirer
from tqdm import tqdm
import signal
import requests

def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes is None:
        return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def fetch_files(repo_id, repo_type='model'):
    """Fetch file list from Hugging Face Hub"""
    print(f"Fetching file list for {repo_id} ({repo_type})...")
    api = HfApi()
    try:
        # Use list_repo_tree for better file handling (files vs folders)
        files_info = []
        # Get all files recursively
        tree = api.list_repo_tree(repo_id=repo_id, recursive=True, repo_type=repo_type)
        
        for item in tree:
            if hasattr(item, 'size') and item.size is not None: # Check if it's a file (has size)
                 files_info.append({
                    'name': item.path,
                    'size': item.size,
                    'type': 'file'
                })
        
        return files_info
    except Exception as e:
        print(f"Error fetching file list: {e}")
        return []

def select_files(files_info):
    """Interactive file selection"""
    if not files_info:
        print("No files found.")
        return []

    # Prepare choices for inquirer
    choices = []
    for f in files_info:
        size_str = format_size(f['size'])
        # Padding for alignment
        label = f"{f['name']} ({size_str})"
        choices.append((label, f))

    questions = [
        inquirer.Checkbox('selected_files',
                          message="Select files to download (Space to select, Enter to confirm)",
                          choices=choices,
                          carousel=True)
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        return []
    return answers['selected_files']

def main():
    parser = argparse.ArgumentParser(description="Hugging Face Model Downloader")
    parser.add_argument("repo_id", help="The repository ID (e.g., 'bert-base-uncased')", nargs='?')
    parser.add_argument("--dir", help="Local directory to save files", default="./downloads")
    parser.add_argument("--files", help="Specific files to download (comma separated)", default=None)
    parser.add_argument("--type", help="Repository type: 'model' or 'dataset'", choices=['model', 'dataset'], default=None)
    
    args = parser.parse_args()
    
    repo_type = args.type
    if not repo_type:
        # Ask for repo type if not provided
        type_question = [
            inquirer.List('type',
                          message="What do you want to download?",
                          choices=['Model', 'Dataset'],
                          default='Model')
        ]
        type_answer = inquirer.prompt(type_question)
        if not type_answer:
            return
        repo_type = type_answer['type'].lower()

    if not args.repo_id:
        questions = [
            inquirer.Text('repo_id', message=f"Please enter the Hugging Face {repo_type.capitalize()} ID (e.g., {'bert-base-uncased' if repo_type == 'model' else 'glue'})")
        ]
        answers = inquirer.prompt(questions)
        if not answers or not answers['repo_id']:
            print("Repo ID is required.")
            return
        args.repo_id = answers['repo_id']

    print(f"Target Repo: {args.repo_id} ({repo_type})")
    
    # Fetch files
    files_info = fetch_files(args.repo_id, repo_type=repo_type)
    if not files_info:
        print("Could not retrieve file list. Please check the Repo ID and your internet connection.")
        return

    selected_files = []
    if args.files:
        # If files specified in CLI, filter them
        requested_files = [f.strip() for f in args.files.split(',')]
        for f_info in files_info:
            if f_info['name'] in requested_files:
                selected_files.append(f_info)
        
        # Check if all requested files were found
        found_names = [f['name'] for f in selected_files]
        missing = [req for req in requested_files if req not in found_names]
        if missing:
            print(f"Warning: The following files were not found in the repo: {', '.join(missing)}")
    else:
        # Interactive selection
        selected_files = select_files(files_info)

    if not selected_files:
        print("No files selected. Exiting.")
        return

    print(f"\nSelected {len(selected_files)} files to download.")
    
    # Construct download directory with Repo ID to preserve structure
    download_dir = os.path.join(args.dir, args.repo_id)
    print(f"Download Directory: {download_dir}")
    
    # Create directory if it doesn't exist
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
            print(f"Created directory: {download_dir}")
        except OSError as e:
            print(f"Error creating directory {download_dir}: {e}")
            return

    # Download files loop
    print(f"\nStarting download of {len(selected_files)} files...\n")
    
    success_count = 0
    fail_count = 0
    
    for i, file_info in enumerate(selected_files):
        filename = file_info['name']
        print(f"[{i+1}/{len(selected_files)}] Downloading {filename}...")
        
        try:
            # hf_hub_download handles resume, progress bar, and validation
            file_path = hf_hub_download(
                repo_id=args.repo_id,
                filename=filename,
                local_dir=download_dir,
                repo_type=repo_type
            )
            print(f"Successfully downloaded: {filename}")
            success_count += 1
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            fail_count += 1
            
    print(f"\nDownload completed.")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    main()
