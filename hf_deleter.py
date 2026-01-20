import argparse
import sys
import signal
from huggingface_hub import HfApi, get_token, CommitOperationDelete
from huggingface_hub.utils import RepositoryNotFoundError
import inquirer

def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes is None:
        return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_hf_token():
    """Get HF token from cache or prompt user"""
    token = get_token()
    if token:
        return token
    
    print("No Hugging Face token found.")
    questions = [
        inquirer.Password('token', message="Please enter your Hugging Face Write Token")
    ]
    answers = inquirer.prompt(questions)
    if not answers or not answers['token']:
        return None
    return answers['token']

def fetch_files(api, repo_id, repo_type='model'):
    """Fetch file list from Hugging Face Hub"""
    print(f"Fetching file list for {repo_id} ({repo_type})...")
    try:
        files_info = []
        tree = api.list_repo_tree(repo_id=repo_id, recursive=True, repo_type=repo_type)
        
        for item in tree:
            if hasattr(item, 'size') and item.size is not None:
                 files_info.append({
                    'name': item.path,
                    'size': item.size,
                    'type': 'file'
                })
        return files_info
    except RepositoryNotFoundError:
        print(f"Repository {repo_id} not found.")
        return []
    except Exception as e:
        print(f"Error fetching file list: {e}")
        return []

def select_files(files_info):
    """Interactive file selection"""
    if not files_info:
        print("No files found in the repository.")
        return []

    choices = []
    for f in files_info:
        size_str = format_size(f['size'])
        label = f"{f['name']} ({size_str})"
        choices.append((label, f))

    questions = [
        inquirer.Checkbox('selected_files',
                          message="Select files to DELETE (Space to select, Enter to confirm)",
                          choices=choices,
                          carousel=True)
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        return []
    return answers['selected_files']

def delete_files(api, repo_id, repo_type, files_to_delete):
    """Delete selected files using a single commit"""
    if not files_to_delete:
        return

    filenames = [f['name'] for f in files_to_delete]
    print(f"\nYou are about to DELETE the following files from {repo_id} ({repo_type}):")
    for name in filenames:
        print(f" - {name}")
    
    confirm_q = [
        inquirer.Confirm('confirm', message="Are you sure? This action CANNOT be undone.", default=False)
    ]
    ans = inquirer.prompt(confirm_q)
    if not ans or not ans['confirm']:
        print("Deletion aborted.")
        return

    print("Deleting files...")
    operations = [CommitOperationDelete(path_in_repo=name) for name in filenames]
    
    try:
        api.create_commit(
            repo_id=repo_id,
            repo_type=repo_type,
            operations=operations,
            commit_message=f"Delete {len(filenames)} files via hf_deleter"
        )
        print("Successfully deleted files.")
    except Exception as e:
        print(f"Error deleting files: {e}")

def main():
    parser = argparse.ArgumentParser(description="Hugging Face File Deleter")
    parser.add_argument("repo_id", help="The repository ID", nargs='?')
    parser.add_argument("--type", help="Repository type: 'model', 'dataset', 'space'", choices=['model', 'dataset', 'space'], default=None)
    parser.add_argument("--token", help="Hugging Face Write Token", default=None)
    
    args = parser.parse_args()
    
    # Authentication
    token = args.token
    if not token:
        token = get_hf_token()
    
    if not token:
        print("Authentication required to delete files.")
        return

    api = HfApi(token=token)

    # Repo Selection Logic
    # REMOVED default repo prompt for public version

    if not args.type:
        questions = [
            inquirer.List('type', message="Repository Type", choices=['model', 'dataset', 'space'], default='model')
        ]
        answers = inquirer.prompt(questions)
        if not answers: return
        args.type = answers['type']
        
    if not args.repo_id:
        questions = [
            inquirer.Text('repo_id', message=f"Target {args.type.capitalize()} ID")
        ]
        answers = inquirer.prompt(questions)
        if not answers or not answers['repo_id']: return
        args.repo_id = answers['repo_id']

    # Fetch and Select
    files_info = fetch_files(api, args.repo_id, args.type)
    if not files_info:
        return

    selected_files = select_files(files_info)
    if not selected_files:
        print("No files selected.")
        return

    # Delete
    delete_files(api, args.repo_id, args.type, selected_files)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    main()
