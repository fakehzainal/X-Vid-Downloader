from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from starlette.background import BackgroundTask
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

app = FastAPI(title="Twitter/X Video Downloader", version="1.0.0")

TWITTER_URL_PATTERN = re.compile(
    r"^https?://(www\.)?(twitter\.com|x\.com)/[^/]+/status/\d+",
    re.IGNORECASE,
)


HTML_INDEX = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Twitter/X Video Downloader</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Archivo+Black&display=swap\" rel=\"stylesheet\">
  <style>
    :root {
      --bg: #f2f5f7;
      --ink: #101820;
      --muted: #4e5d6c;
      --card: rgba(255, 255, 255, 0.9);
      --edge: rgba(16, 24, 32, 0.11);
      --cta: #ef4444;
      --accent: #0ea5e9;
      --shadow: 0 24px 50px rgba(13, 30, 41, 0.18);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Space Grotesk", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1100px 600px at 5% -10%, rgba(14, 165, 233, 0.22), transparent 65%),
        radial-gradient(850px 450px at 100% 0%, rgba(239, 68, 68, 0.18), transparent 60%),
        linear-gradient(150deg, #eff3f6 0%, #f8fafc 60%, #e9f3f7 100%);
      display: grid;
      place-items: center;
      padding: 20px;
    }
    .orb {
      position: fixed;
      width: 260px;
      height: 260px;
      border-radius: 999px;
      filter: blur(40px);
      opacity: .6;
      z-index: 0;
      animation: drift 8s ease-in-out infinite alternate;
    }
    .orb.one { top: -50px; right: -40px; background: rgba(14, 165, 233, .35); }
    .orb.two { bottom: -60px; left: -50px; background: rgba(239, 68, 68, .25); animation-delay: .5s; }
    @keyframes drift { from { transform: translateY(0); } to { transform: translateY(18px); } }
    .wrap {
      width: min(760px, 100%);
      position: relative;
      z-index: 1;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--edge);
      border-radius: 20px;
      padding: 28px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
      animation: rise .5s ease-out both;
    }
    @keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .tag {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid var(--edge);
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      color: var(--muted);
      background: rgba(255, 255, 255, .7);
      margin-bottom: 14px;
    }
    h1 {
      margin: 0;
      font-family: "Archivo Black", "Arial Black", sans-serif;
      letter-spacing: .2px;
      line-height: 1.1;
      font-size: clamp(28px, 4.8vw, 46px);
      text-wrap: balance;
    }
    p {
      margin: 14px 0 20px;
      color: var(--muted);
      line-height: 1.6;
      font-size: 15px;
    }
    form {
      display: grid;
      gap: 10px;
    }
    input {
      width: 100%;
      padding: 14px;
      border: 1px solid #c6d3dd;
      border-radius: 12px;
      font-size: 14px;
      background: #ffffff;
      transition: border-color .2s, box-shadow .2s;
    }
    input:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 4px rgba(14, 165, 233, .2);
    }
    button {
      margin-top: 2px;
      border: 0;
      padding: 14px 16px;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--cta), #fb7185);
      color: white;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
      transition: transform .14s ease, filter .14s ease;
    }
    button:hover { transform: translateY(-1px); filter: brightness(1.03); }
    button:active { transform: translateY(0); }
    .row {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
      margin-top: 12px;
      font-size: 12px;
      color: var(--muted);
    }
    .pill {
      border: 1px solid var(--edge);
      border-radius: 999px;
      padding: 5px 10px;
      background: rgba(255, 255, 255, .8);
    }
    .note {
      margin-top: 16px;
      font-size: 12px;
      color: #6b7280;
      border-top: 1px dashed rgba(16, 24, 32, 0.15);
      padding-top: 12px;
    }
    @media (max-width: 560px) {
      .card { padding: 20px; border-radius: 16px; }
      input, button { padding: 13px; }
    }
  </style>
</head>
<body>
  <div class=\"orb one\"></div>
  <div class=\"orb two\"></div>
  <div class=\"wrap\">
    <div class=\"card\">
      <div class=\"tag\">Local Mode • No Deploy</div>
      <h1>Twitter/X Video Downloader</h1>
      <p>Paste URL tweet yang berisi video, lalu ambil file MP4 langsung dari browser kamu.</p>
      <form method=\"post\" action=\"/download\">
        <input name=\"url\" placeholder=\"https://x.com/username/status/1234567890\" required />
        <button type=\"submit\">Download Video</button>
      </form>
      <div class=\"row\">
        <span class=\"pill\">FastAPI</span>
        <span class=\"pill\">yt-dlp</span>
        <span class=\"pill\">Local File Output</span>
      </div>
      <div class=\"note\">Gunakan hanya untuk konten yang kamu punya hak untuk mengunduh.</div>
    </div>
  </div>
</body>
</html>
"""


def _normalize_tweet_url(url: str) -> str:
    value = url.strip()
    if not TWITTER_URL_PATTERN.match(value):
        raise HTTPException(status_code=400, detail="URL bukan link status Twitter/X yang valid.")
    return value


def _pick_downloaded_file(target_dir: Path) -> Optional[Path]:
    files = [p for p in target_dir.iterdir() if p.is_file() and p.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}]
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_size, reverse=True)
    return files[0]


def _detect_ffmpeg_location() -> Optional[str]:
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        return str(Path(ffmpeg_bin).parent)

    winget_packages = Path(os.getenv("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    if not winget_packages.exists():
        return None

    candidates = sorted(winget_packages.glob("yt-dlp.FFmpeg*"), key=lambda p: p.stat().st_mtime, reverse=True)
    for pkg in candidates:
        matches = list(pkg.rglob("ffmpeg.exe"))
        if matches:
            return str(matches[0].parent)
    return None


def _download_video(tweet_url: str) -> Path:
    output_dir = Path(tempfile.mkdtemp(prefix="xdl_"))
    output_template = str(output_dir / "video.%(ext)s")
    ffmpeg_location = os.getenv("FFMPEG_LOCATION") or _detect_ffmpeg_location()

    ydl_opts = {
        "outtmpl": output_template,
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    if ffmpeg_location:
        ydl_opts["ffmpeg_location"] = ffmpeg_location

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([tweet_url])
    except DownloadError as exc:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"Gagal download video: {exc}") from exc
    except Exception as exc:  # noqa: BLE001
        shutil.rmtree(output_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail="Terjadi error saat memproses video.") from exc

    video_file = _pick_downloaded_file(output_dir)
    if video_file is None:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise HTTPException(status_code=404, detail="Video tidak ditemukan di tweet tersebut.")

    return video_file


def _cleanup_file_and_parent(file_path: Path) -> None:
    parent = file_path.parent
    try:
        if file_path.exists():
            file_path.unlink(missing_ok=True)
    finally:
        shutil.rmtree(parent, ignore_errors=True)


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return HTML_INDEX


@app.post("/download")
def download(url: str = Form(...)):
    tweet_url = _normalize_tweet_url(url)
    video_path = _download_video(tweet_url)

    file_name = f"twitter-video{video_path.suffix}"
    background_task = BackgroundTask(_cleanup_file_and_parent, video_path)
    return FileResponse(
        path=video_path,
        filename=file_name,
        media_type="application/octet-stream",
        background=background_task,
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False)
