import os
import zipfile
import urllib.request
import platform
import tarfile

def download_ffmpeg_if_needed():
    # Thư mục ffmpeg_bin sẽ nằm cùng cấp với thư mục cha của file .py
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dest_folder = os.path.join(base_dir, "ffmpeg_bin")
    
    system = platform.system()
    ffmpeg_exe = os.path.join(dest_folder, "ffmpeg.exe" if system == "Windows" else "ffmpeg")

    # ✅ Nếu đã tồn tại, trả về luôn
    if os.path.exists(ffmpeg_exe):
        print("✅ ffmpeg exists, skip download.")
        return dest_folder

    os.makedirs(dest_folder, exist_ok=True)

    if system == "Windows":
        print("📥 Downloading ffmpeg for Windows...")
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(dest_folder, "ffmpeg.zip")

        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)

        for root, dirs, files in os.walk(dest_folder):
            if "ffmpeg.exe" in files:
                src = os.path.join(root, "ffmpeg.exe")
                if src != ffmpeg_exe:
                    with open(src, 'rb') as fsrc, open(ffmpeg_exe, 'wb') as fdest:
                        fdest.write(fsrc.read())
                break

        os.remove(zip_path)
        print("✅ Download ffmpeg successfully (Windows).")

    elif system == "Linux":
        print("Downloading ffmpeg for Linux...")
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        tar_path = os.path.join(dest_folder, "ffmpeg.tar.xz")

        urllib.request.urlretrieve(url, tar_path)

        with tarfile.open(tar_path, "r:xz") as tar_ref:
            tar_ref.extractall(dest_folder)

        for root, dirs, files in os.walk(dest_folder):
            if "ffmpeg" in files and "ffmpeg.exe" not in files:
                src = os.path.join(root, "ffmpeg")
                if src != ffmpeg_exe:
                    with open(src, 'rb') as fsrc, open(ffmpeg_exe, 'wb') as fdest:
                        fdest.write(fsrc.read())
                os.chmod(ffmpeg_exe, 0o755)
                break

        os.remove(tar_path)
        print("✅ Download ffmpeg successfully (Linux).")

    else:
        print("⚠️ Haven't supported auto-download ffmpeg for:", system)
        return None

    return dest_folder