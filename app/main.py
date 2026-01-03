from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os
import shutil
import uuid

app = FastAPI(title="Enterprise File Manager")

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB Limit
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

# Ensure folders exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
# Isse hum uploaded files ko browser mein dekh payenge
app.mount("/download", StaticFiles(directory=UPLOAD_DIR), name="download")

@app.get("/", response_class=HTMLResponse)
async def main_page():
    return FileResponse("static/index.html")

@app.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    # 1. Check File Size (Memory check)
    file_size = 0
    contents = await file.read() # Read file content
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large! Max limit is 5MB.")

    # 2. Generate Unique Filename (taaki purani file delete na ho)
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Extension not allowed!")
        
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # 3. Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # 4. Return a Shareable Download Link
    base_url = str(request.base_url)
    download_url = f"{base_url}download/{unique_name}"

    return {
        "filename": file.filename,
        "unique_name": unique_name,
        "download_url": download_url,
        "status": "Success"
    }