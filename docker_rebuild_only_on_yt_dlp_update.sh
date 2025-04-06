#! /bin/bash -eu

YT_DLP_VERSION_FILE="yt_dlp_version.txt"

# rebuild the docker image if the yt-dlp version has changed

# check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip could not be found" >&2
    exit
fi

# create YT_DLP_VERSION_FILE if it does not exist
if [ ! -f "$YT_DLP_VERSION_FILE" ]; then
    echo "-1" > "$YT_DLP_VERSION_FILE"
fi

# check if YT_DLP_VERSION_FILE is writable
if [ ! -w "$YT_DLP_VERSION_FILE" ]; then
    echo "YT_DLP_VERSION_FILE is not writable" >&2
    exit 1
fi

pip_index_yt_dlp=$(pip index versions yt-dlp 2>/dev/null)
yt_dlp_version_line=$(echo "$pip_index_yt_dlp" |head -n1)
echo "yt-dlp version in pip index: $yt_dlp_version_line" >&2

installed_yt_dlp_version_line=$(cat "$YT_DLP_VERSION_FILE")
echo "installed yt-dlp version: $installed_yt_dlp_version_line" >&2

if [ "$yt_dlp_version_line" == "$installed_yt_dlp_version_line" ]; then
    echo "yt-dlp version has not changed, not rebuilding docker image" >&2
    exit 0
fi

echo "yt-dlp version has changed, rebuilding docker image" >&2
./docker_rebuild.sh
echo "rebuilding docker image done" >&2.

echo "$yt_dlp_version_line" > "$YT_DLP_VERSION_FILE"

exit 0
