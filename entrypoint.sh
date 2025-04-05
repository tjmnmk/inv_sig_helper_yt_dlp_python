#! /bin/sh
if [ -d "~/.cache/yt-dlp" ]; then
  rm -rf ~/.cache/yt-dlp
fi
cd /app

python3 inv_sig_helper_yt_dlp_python.py "$@"
