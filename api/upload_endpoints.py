"""
SuperAgent v2.0 - Upload API Endpoints
Handles file uploads, URL imports, and microphone recording
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
import asyncio
import logging
from api.multimodal_processor import multimodal_processor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/upload", tags=["upload"])

class UploadResponse(BaseModel):
    """Response model for upload operations"""
    success: bool
    file_id: str
    filename: str
    file_type: str
    metadata: dict
    extracted_data: dict
    actions: List[dict]
    processing_time: float
    message: str

class URLImportRequest(BaseModel):
    """Request model for URL import"""
    url: HttpUrl
    file_type: Optional[str] = None

@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    process_options: Optional[str] = Form(None)
):
    """
    Upload a file (drag & drop or click upload)
    
    Supports:
    - Video: .mp4, .mov, .avi, .webm
    - Image: .png, .jpg, .jpeg, .gif, .webp
    - Audio: .mp3, .wav, .m4a, .ogg
    - Document: .pdf, .docx, .txt, .md
    - Archive: .zip, .tar.gz
    """
    try:
        logger.info(f"Received file upload: {file.filename} ({file.content_type})")
        
        # Read file content
        file_content = await file.read()
        
        # Process options (JSON string if provided)
        options = None
        if process_options:
            import json
            try:
                options = json.loads(process_options)
            except:
                pass
        
        # Process the upload
        result = await multimodal_processor.process_upload(
            file_data=file_content,
            filename=file.filename,
            process_options=options
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
        
        return UploadResponse(
            success=True,
            file_id=result.get("file_path", "").split("/")[-1],
            filename=result["filename"],
            file_type=result["file_type"],
            metadata=result.get("metadata", {}),
            extracted_data=result.get("extracted_data", {}),
            actions=result.get("actions", []),
            processing_time=result.get("processing_time", 0),
            message=f"Successfully processed {result['file_type']} file"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/url")
async def import_from_url(request: URLImportRequest):
    """
    Import file from URL
    
    Supports:
    - Direct file URLs
    - YouTube videos
    - Image URLs
    - Document URLs
    """
    try:
        logger.info(f"Importing from URL: {request.url}")
        
        import httpx
        import tempfile
        from pathlib import Path
        
        # Download file
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(str(request.url))
            response.raise_for_status()
            
            # Determine filename from URL or Content-Disposition
            filename = Path(str(request.url)).name
            if 'content-disposition' in response.headers:
                import re
                cd = response.headers['content-disposition']
                fname_match = re.findall('filename="(.+)"', cd)
                if fname_match:
                    filename = fname_match[0]
            
            # Process the downloaded file
            result = await multimodal_processor.process_upload(
                file_data=response.content,
                filename=filename,
                process_options={"source": "url", "url": str(request.url)}
            )
            
            if not result.get("success", False):
                raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
            
            return {
                "success": True,
                "file_id": result.get("file_path", "").split("/")[-1],
                "filename": result["filename"],
                "file_type": result["file_type"],
                "metadata": result.get("metadata", {}),
                "extracted_data": result.get("extracted_data", {}),
                "actions": result.get("actions", []),
                "processing_time": result.get("processing_time", 0),
                "message": f"Successfully imported {result['file_type']} from URL"
            }
        
    except httpx.HTTPError as e:
        logger.error(f"Error downloading from URL: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download from URL: {str(e)}")
    except Exception as e:
        logger.error(f"Error in import_from_url: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/microphone")
async def upload_microphone_recording(
    audio_data: UploadFile = File(...),
    duration: Optional[float] = Form(None)
):
    """
    Upload microphone recording
    
    Accepts:
    - WebM audio (browser recording)
    - WAV audio
    - MP3 audio
    """
    try:
        logger.info(f"Received microphone recording: {audio_data.filename}")
        
        # Read audio content
        audio_content = await audio_data.read()
        
        # Process the audio
        result = await multimodal_processor.process_upload(
            file_data=audio_content,
            filename=audio_data.filename or "recording.webm",
            process_options={"source": "microphone", "duration": duration}
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
        
        return {
            "success": True,
            "file_id": result.get("file_path", "").split("/")[-1],
            "filename": result["filename"],
            "file_type": result["file_type"],
            "metadata": result.get("metadata", {}),
            "extracted_data": result.get("extracted_data", {}),
            "actions": result.get("actions", []),
            "processing_time": result.get("processing_time", 0),
            "message": "Successfully processed microphone recording"
        }
        
    except Exception as e:
        logger.error(f"Error in upload_microphone_recording: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
async def upload_multiple_files(
    files: List[UploadFile] = File(...)
):
    """
    Upload multiple files at once
    
    Processes all files in parallel
    Returns array of results
    """
    try:
        logger.info(f"Received batch upload: {len(files)} files")
        
        # Process all files in parallel
        tasks = []
        for file in files:
            file_content = await file.read()
            task = multimodal_processor.process_upload(
                file_data=file_content,
                filename=file.filename,
                process_options={"batch": True}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Count successes and failures
        successes = sum(1 for r in results if r.get("success", False))
        failures = len(results) - successes
        
        return {
            "success": failures == 0,
            "total": len(results),
            "successes": successes,
            "failures": failures,
            "results": results,
            "message": f"Processed {successes}/{len(results)} files successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in upload_multiple_files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of all supported file formats"""
    return {
        "success": True,
        "formats": multimodal_processor.SUPPORTED_FORMATS,
        "total_formats": sum(len(exts) for exts in multimodal_processor.SUPPORTED_FORMATS.values())
    }

@router.delete("/file/{file_id}")
async def delete_uploaded_file(file_id: str):
    """Delete an uploaded file"""
    try:
        from pathlib import Path
        
        # Find and delete file
        upload_dir = Path("/tmp/superagent_uploads")
        matching_files = list(upload_dir.glob(f"*{file_id}*"))
        
        if not matching_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        for file_path in matching_files:
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
        
        return {
            "success": True,
            "message": f"Deleted {len(matching_files)} file(s)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Export router
upload_router = router
