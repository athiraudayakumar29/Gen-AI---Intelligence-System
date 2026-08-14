from fastapi import APIRouter, UploadFile, File
from backend.services.storage_service import StorageService
from rag.indexing import index_document
from tools.pdf import extract_text_from_pdf
import pypdf
import io

router = APIRouter()
storage_service = StorageService()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


@router.post("")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()

    # 1. Save to Blob Storage
    blob_url = storage_service.upload_file(file.filename, contents)

    # 2. Extract text based on file type
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(contents)
    else:
        text = contents.decode("utf-8", errors="ignore")

    # 3. Chunk + embed + index into Azure AI Search
    chunks_indexed = index_document(text, file.filename)

    return {
        "filename": file.filename,
        "size_bytes": len(contents),
        "blob_url": blob_url,
        "chunks_indexed": chunks_indexed,
        "status": "uploaded and indexed"
    }