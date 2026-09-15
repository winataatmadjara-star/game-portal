import subprocess
import os

def run_git_command(command_list, cwd=None):
    """
    Menjalankan perintah Git secara aman menggunakan subprocess.
    Mengembalikan (success: bool, output: str)
    """
    try:
        # Jika working directory tidak diset, gunakan direktori root project
        if not cwd:
            cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

        # Jalankan proses terminal
        result = subprocess.run(
            command_list,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30 # Batasi waktu eksekusi agar tidak menggantung (hung)
        )

        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            return True, output.strip()
        else:
            return False, output.strip()

    except subprocess.TimeoutExpired:
        return False, "❌ Error: Proses Git melebihi batas waktu (timeout 30 detik)."
    except Exception as e:
        return False, f"❌ Terjadi kesalahan sistem: {str(e)}"