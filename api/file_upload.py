"""
File Upload Handler - Support for files, images, videos, audio
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
import os
import shutil
from pathlib import Path
import mimetypes

router = APIRouter(prefix="/api/v1", tags=["File Upload"])

# Upload directory
UPLOAD_DIR = Path("/tmp/superagent_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload any file (documents, code, data files)
    Supported: .txt, .md, .pdf, .doc, .docx, .json, .csv, .xlsx, .py, .js, etc.
    """
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        saved_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / saved_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Extract content based on file type
        content = None
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        # Text files - read content
        if file_extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.csv']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                content = "[Binary file - content not readable as text]"
        
        # PDF files - extract text (basic)
        elif file_extension == '.pdf':
            content = "[PDF file uploaded - content extraction requires additional processing]"
        
        # Other files
        else:
            content = f"[{file_extension} file uploaded]"
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "saved_as": saved_filename,
            "size": file_size,
            "size_human": format_file_size(file_size),
            "type": content_type,
            "extension": file_extension,
            "content": content[:1000] if content else None,  # First 1000 chars
            "content_preview": content[:200] if content else None,  # Preview
            "path": str(file_path)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload image files
    Supported: .jpg, .jpeg, .png, .gif, .webp, .svg
    """
    try:
        # Validate image type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        saved_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / saved_filename
        
        # Save image
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Get image dimensions (if possible)
        dimensions = None
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                dimensions = {"width": img.width, "height": img.height}
        except:
            pass
        
        return {
            "success": True,
            "image_id": file_id,
            "filename": file.filename,
            "saved_as": saved_filename,
            "size": file_size,
            "size_human": format_file_size(file_size),
            "type": file.content_type,
            "extension": file_extension,
            "dimensions": dimensions,
            "url": f"/uploads/{saved_filename}",
            "path": str(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload video files
    Supported: .mp4, .webm, .mov, .avi
    """
    try:
        # Validate video type
        allowed_extensions = ['.mp4', '.webm', '.mov', '.avi']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid video type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        saved_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / saved_filename
        
        # Save video
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return {
            "success": True,
            "video_id": file_id,
            "filename": file.filename,
            "saved_as": saved_filename,
            "size": file_size,
            "size_human": format_file_size(file_size),
            "type": file.content_type,
            "extension": file_extension,
            "url": f"/uploads/{saved_filename}",
            "path": str(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video upload failed: {str(e)}")

@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload audio files and optionally transcribe
    Supported: .mp3, .wav, .m4a, .ogg, .webm
    """
    try:
        # Validate audio type
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.webm']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audio type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        saved_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / saved_filename
        
        # Save audio
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Try to transcribe using manus-speech-to-text
        transcript = None
        try:
            import subprocess
            result = subprocess.run(
                ['manus-speech-to-text', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                transcript = result.stdout.strip()
        except:
            transcript = "[Transcription not available]"
        
        return {
            "success": True,
            "audio_id": file_id,
            "filename": file.filename,
            "saved_as": saved_filename,
            "size": file_size,
            "size_human": format_file_size(file_size),
            "type": file.content_type,
            "extension": file_extension,
            "transcript": transcript,
            "url": f"/uploads/{saved_filename}",
            "path": str(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio upload failed: {str(e)}")

@router.post("/upload-multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    """Upload multiple files at once"""
    results = []
    
    for file in files:
        try:
            # Determine file type and route to appropriate handler
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                result = await upload_image(file)
            elif file_extension in ['.mp4', '.webm', '.mov', '.avi']:
                result = await upload_video(file)
            elif file_extension in ['.mp3', '.wav', '.m4a', '.ogg']:
                result = await upload_audio(file)
            else:
                result = await upload_file(file)
            
            results.append(result)
            
        except Exception as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": True,
        "total": len(files),
        "uploaded": len([r for r in results if r.get("success")]),
        "failed": len([r for r in results if not r.get("success")]),
        "results": results
    }

@router.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """Serve uploaded files"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(file_path)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
