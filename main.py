import os
import subprocess
import requests
from git import Repo
import shutil
import venv
import time
import sys

def print_ascii_art():
    ascii_art = """
    ***********************************************
    *           SUBSCRIBE YOUTUBE:                *
    *            @SHAREITHUB_COM                  *
    ***********************************************
    """
    print(ascii_art)

def check_repo_files(repo_url):
    """Mengambil daftar file dari repositori GitHub menggunakan API."""
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    api_url = f'https://api.github.com/repos/{"/".join(repo_url.split("/")[-2:])}/contents/'
    
    response = requests.get(api_url)
    if response.status_code == 200:
        return [item['name'] for item in response.json()]
    else:
        print(f"Error accessing repository: {response.status_code}")
        return []

def clone_and_install(repo_url):
    # Membuat folder "list-bot" jika belum ada
    list_bot_dir = "list-bot"
    if not os.path.exists(list_bot_dir):
        os.makedirs(list_bot_dir)

    # Mengambil nama repositori dari URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    repo_path = os.path.join(list_bot_dir, repo_name)

    # Mengecek apakah direktori repositori sudah ada
    if os.path.exists(repo_path):
        choice = input(f"Folder '{repo_name}' sudah ada di '{list_bot_dir}'. Apakah Anda ingin (h)apus folder, (t)impa folder, atau (b)atalkan? (h/t/b): ")
        if choice.lower() == 'h':
            try:
                time.sleep(1)  # Delay 1 detik
                shutil.rmtree(repo_path)
                print(f"Folder '{repo_name}' dihapus.")
            except PermissionError as e:
                print(f"PermissionError: {e}. Coba tutup aplikasi yang menggunakan folder ini.")
                return
        elif choice.lower() == 'b':
            print("Clone dibatalkan.")
            return
        elif choice.lower() == 't':
            print(f"Menimpa folder '{repo_name}' dengan konten baru...")
            try:
                time.sleep(1)  # Delay 1 detik
                shutil.rmtree(repo_path)
                print(f"Folder '{repo_name}' dihapus.")
            except PermissionError as e:
                print(f"PermissionError: {e}. Coba tutup aplikasi yang menggunakan folder ini.")
                return
        else:
            print("Pilihan tidak valid. Clone dibatalkan.")
            return

    # Mengecek file yang ada di repositori
    print(f"Memeriksa file di repositori {repo_url}...")
    project_files = check_repo_files(repo_url)

    # Melakukan clone repositori
    print(f"Cloning repository {repo_url} ke '{repo_path}'...")
    Repo.clone_from(repo_url, repo_path)
    print("Clone completed.")

    # Mengecek jenis proyek berdasarkan file yang ada
    requirements_file = 'requirements.txt' in project_files
    package_json_file = 'package.json' in project_files

    # Menanyakan apakah ingin membuat virtual environment
    create_venv = input("Apakah Anda ingin membuat virtual environment untuk proyek Python? (y/n): ").lower()
    if create_venv == 'y' and requirements_file:
        venv_name = input("Masukkan nama untuk virtual environment: ")
        venv_dir = os.path.join(repo_path, venv_name)
        print(f"Membuat virtual environment di '{venv_dir}'...")
        venv.create(venv_dir, with_pip=True)
        print("Virtual environment created.")

        pip_path = os.path.join(venv_dir, 'Scripts', 'pip') if sys.platform == 'win32' else os.path.join(venv_dir, 'bin', 'pip')
        
        print("Installing required modules from requirements.txt...")
        subprocess.check_call([pip_path, 'install', '-r', os.path.join(repo_path, 'requirements.txt')])
        print("Installation completed.")
    elif create_venv == 'y' and not requirements_file:
        print("Tidak ada requirements.txt ditemukan. Virtual environment tidak dibuat.")
    
    if package_json_file:
        print("Menjalankan npm install di direktori repositori...")
        try:
            result = subprocess.run(['npm', 'install'], cwd=repo_path, check=True, capture_output=True, text=True)
            print("Npm install completed.")
            print(result.stdout)  # Menampilkan output dari npm install
        except subprocess.CalledProcessError as e:
            print(f"Error saat menjalankan npm install: {e}\n{e.stderr}")

    if not (requirements_file or package_json_file):
        print("No recognized project files found (requirements.txt or package.json).")

if __name__ == "__main__":
    print_ascii_art()  # Menampilkan ASCII art di atas
    while True:
        url = input("Masukkan link Git repository (atau ketik 'exit' untuk keluar): ")
        if url.lower() == 'exit':
            break
        clone_and_install(url)
