# Twitter/X Video Downloader (Local, Tanpa Deploy)

Aplikasi lokal untuk download video dari URL status Twitter/X.
Tidak perlu deploy ke server, cukup jalankan di komputer sendiri.

## Fitur
- UI browser sederhana di `GET /`
- Endpoint download di `POST /download`
- Health check di `GET /health`
- File temporary dibersihkan otomatis setelah respons selesai

## Tech Stack
- Python + FastAPI
- `yt-dlp` untuk mengambil media
- `ffmpeg` untuk proses merge/convert

## Prasyarat
- Python `3.10+`
- `ffmpeg` terpasang dan bisa diakses

Cek versi:
```bash
python --version
ffmpeg -version
```

## Install ffmpeg
Pilih sesuai OS:

Windows (winget):
```powershell
winget install --id yt-dlp.FFmpeg --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
```

macOS (Homebrew):
```bash
brew install ffmpeg
```

Ubuntu/Debian:
```bash
sudo apt update && sudo apt install -y ffmpeg
```

## Setup Project
Clone repo lalu masuk folder project:
```bash
git clone <repo-url>
cd ai-twitter-vid-downloader
```

## Instalasi Dependency
### Opsi 1: PowerShell (Windows)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Opsi 2: Bash (Git Bash/WSL/macOS/Linux)
```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash di Windows
# source .venv/bin/activate     # WSL/Linux/macOS
pip install -r requirements.txt
```

## Menjalankan Aplikasi
```bash
python main.py
```

Buka browser:
- `http://127.0.0.1:8000`

## Cara Pakai
1. Buka `http://127.0.0.1:8000`
2. Paste URL tweet/status yang berisi video
3. Klik `Download Video`

## Contoh API
### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Download dengan curl (direkomendasikan)
```bash
curl -X POST -F "url=https://x.com/username/status/1234567890" \
  "http://127.0.0.1:8000/download" \
  -o video.mp4
```

### Download dengan PowerShell (`Invoke-WebRequest`)
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/download" `
  -Method Post `
  -Form @{ url = "https://x.com/username/status/1234567890" } `
  -OutFile "video.mp4"
```

Jika PowerShell kamu tidak support `-Form`, gunakan `curl.exe`:
```powershell
curl.exe -X POST -F "url=https://x.com/username/status/1234567890" "http://127.0.0.1:8000/download" -o "video.mp4"
```

## Troubleshooting
- `ffmpeg is not recognized`: install `ffmpeg`, lalu buka terminal baru.
- `Unable to connect 127.0.0.1:8000`: pastikan server sudah jalan (`python main.py`).
- `400 URL bukan link status...`: URL harus format `https://x.com/<user>/status/<id>`.
- `Video tidak ditemukan`: tweet tidak berisi video atau konten private/protected.

## Catatan Legal
- Gunakan hanya untuk konten yang kamu punya hak/izin untuk diunduh.
- Patuhi ToS platform Twitter/X dan hukum hak cipta yang berlaku.
