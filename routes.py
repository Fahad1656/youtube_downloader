

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import unquote
import os
import uuid
import yt_dlp
import subprocess

router = APIRouter()


@router.get("/available_resolutions")
async def get_available_resolutions(url: str, timestamp: str = ""):
    print(f"🔍 Received request for resolutions: {url} at {timestamp}")
    try:
        decoded_url = unquote(url)

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,  # 👈 Add this line
            "extract_flat": "discard"  # 👈 Optional but recommended
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(decoded_url, download=False)
            formats = info_dict.get("formats", [])

        resolutions = [{"itag": fmt["format_id"], "label": fmt["format"]}
                      for fmt in formats if fmt.get("vcodec") != "none"]

        print(f"✅ Available resolutions ({len(resolutions)} found)")
        return {"resolutions": resolutions}
    except Exception as e:
        print(f"❌ Error fetching resolutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching resolutions: {str(e)}")




@router.get("/download")
async def download_video(url: str, itag: str):
    try:
        decoded_url = unquote(url)
        unique_id = uuid.uuid4().hex
        output_filename = f"video_{unique_id}.mp4"

        ydl_opts = {
            "format": f"{itag}+bestaudio/best",
            "outtmpl": f"{unique_id}.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": False,
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"  # Ensure final format is MP4 with audio
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(decoded_url, download=True)
            downloaded_video = ydl.prepare_filename(info_dict).replace(".webm", ".mp4")

        # Verify the downloaded file
        if not os.path.exists(downloaded_video) or os.path.getsize(downloaded_video) == 0:
            raise HTTPException(status_code=500, detail="Download failed: File missing or empty.")

        # Stream the file to the client
        def iter_file():
            with open(downloaded_video, "rb") as file:
                yield from file
            os.remove(downloaded_video)  # Clean up the file after streaming

        headers = {
            "Content-Disposition": f'attachment; filename="{os.path.basename(downloaded_video)}"'
        }

        return StreamingResponse(iter_file(), media_type="video/mp4", headers=headers)

    except Exception as e:
        print(f"❌ Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")
