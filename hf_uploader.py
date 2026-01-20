import argparse
import os
import sys
from huggingface_hub import HfApi, get_token
from huggingface_hub.utils import RepositoryNotFoundError
import inquirer

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
    
    # Optionally save the token? For now, just return it.
    # HfFolder.save_token(answers['token']) 
    return answers['token']

def upload(api, args):
    path = args.path
    repo_id = args.repo_id
    repo_type = args.repo_type
    commit_message = args.message
    
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return

    # Check if repo exists, if not ask to create
    try:
        api.repo_info(repo_id=repo_id, repo_type=repo_type)
        print(f"Repository {repo_id} ({repo_type}) exists.")
    except RepositoryNotFoundError:
        print(f"Repository {repo_id} ({repo_type}) does not exist.")
        if not args.yes:
            confirm = inquirer.confirm(f"Do you want to create {repo_type} repository '{repo_id}'?", default=True)
            if not confirm:
                print("Aborted.")
                return
        
        # Ask for visibility
        private = False
        if not args.yes:
            visibility_q = [
                inquirer.List('visibility', message="Repository Visibility", choices=['Public', 'Private'], default='Public')
            ]
            ans = inquirer.prompt(visibility_q)
            if ans and ans['visibility'] == 'Private':
                private = True
        
        try:
            api.create_repo(repo_id=repo_id, repo_type=repo_type, exist_ok=True, private=private)
            print(f"Created {'private' if private else 'public'} repository {repo_id}.")
        except Exception as e:
            print(f"Error creating repository: {e}")
            return
    except Exception as e:
        print(f"Error checking repository: {e}")
        return

    print(f"\nUploading '{path}' to {repo_id} ({repo_type})...")
    
    try:
        if os.path.isdir(path):
            # Upload folder
            folder_name = os.path.basename(os.path.abspath(path))
            api.upload_folder(
                folder_path=path,
                path_in_repo=folder_name,
                repo_id=repo_id,
                repo_type=repo_type,
                commit_message=commit_message
            )
        else:
            # Upload file
            # path_in_repo defaults to filename
            filename = os.path.basename(path)
            api.upload_file(
                path_or_fileobj=path,
                path_in_repo=filename,
                repo_id=repo_id,
                repo_type=repo_type,
                commit_message=commit_message
            )
        print("Upload completed successfully!")
        
    except Exception as e:
        print(f"Upload failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Hugging Face File/Folder Uploader")
    parser.add_argument("path", help="Local file or folder path to upload", nargs='?')
    parser.add_argument("--repo", help="Target Repo ID (e.g. username/repo)", dest="repo_id")
    parser.add_argument("--token", help="Hugging Face Write Token", default=None)
    parser.add_argument("--type", help="Repo type: 'model', 'dataset', 'space'", choices=['model', 'dataset', 'space'], default=None, dest="repo_type")
    parser.add_argument("-m", "--message", help="Commit message", default="Upload via hf_uploader")
    parser.add_argument("-y", "--yes", help="Skip confirmation for repo creation", action="store_true")
    
    args = parser.parse_args()
    
    # 1. Authentication
    token = args.token
    if not token:
        token = get_hf_token()
    
    if not token:
        print("Authentication required to upload.")
        return
    
    api = HfApi(token=token)
    
    # 2. Interactive Prompts if args missing
    if not args.path:
        questions = [
            inquirer.Path('path', message="Path to file or folder to upload", exists=True)
        ]
        answers = inquirer.prompt(questions)
        if not answers: return
        args.path = answers['path']

    # REMOVED default repo prompt for public version

    if not args.repo_type:
        questions = [
            inquirer.List('type', message="Repository Type", choices=['model', 'dataset', 'space'], default='model')
        ]
        answers = inquirer.prompt(questions)
        if not answers: return
        args.repo_type = answers['type']
        
    if not args.repo_id:
        questions = [
            inquirer.Text('repo_id', message=f"Target {args.repo_type.capitalize()} ID (e.g. username/my-bert)")
        ]
        answers = inquirer.prompt(questions)
        if not answers or not answers['repo_id']: return
        args.repo_id = answers['repo_id']

    # 3. Perform Upload
    upload(api, args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
