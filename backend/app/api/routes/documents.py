# app/api/routes/documents.py
import time
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form

from app.services.document_service import DocumentService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/supported-types")
async def get_supported_file_types():
    """Get information about supported file types and limits"""
    return {
        "supported_types": [".pdf", ".txt", ".csv", ".xlsx", ".xls"],
        "max_file_size_mb": 10,
        "max_files_per_request": 5
    }

@router.post("/summarize")
async def summarize_documents(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Generate AI summary of uploaded financial documents"""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed per request")
    
    # Initialize document service
    try:
        document_service = DocumentService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Validate files
    for file in files:
        if not document_service.validate_file_type(file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.filename}"
            )
        
        content = await file.read()
        await file.seek(0)
        
        if not document_service.validate_file_size(len(content)):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds maximum size of 10MB"
            )
    
    start_time = time.time()
    
    try:
        summary = await document_service.summarize_documents(files)
        processing_time = time.time() - start_time
        
        return {
            "summary": summary,
            "files_processed": [file.filename for file in files],
            "processing_time": processing_time,
            "user_id": current_user.id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@router.post("/analyze")
async def analyze_documents(
    files: List[UploadFile] = File(...),
    analysis_type: str = Form(default="General Summary"),
    focus_areas: Optional[str] = Form(default=None),
    current_user: User = Depends(get_current_user)
):
    """Perform focused analysis on uploaded financial documents"""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed per request")
    
    # Initialize document service
    try:
        document_service = DocumentService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Parse focus areas
    focus_areas_list = []
    if focus_areas:
        focus_areas_list = [area.strip() for area in focus_areas.split(",") if area.strip()]
    
    # Validate analysis type
    valid_analysis_types = [
        "General Summary",
        "Expense Categorization", 
        "Cash Flow Analysis",
        "Debt Account Detection",
        "Investment Portfolio Review"
    ]
    
    if analysis_type not in valid_analysis_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid analysis type. Valid types: {valid_analysis_types}"
        )
    
    # Validate files
    for file in files:
        if not document_service.validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}"
            )
        
        content = await file.read()
        await file.seek(0)
        
        if not document_service.validate_file_size(len(content)):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds maximum size"
            )
    
    try:
        analysis_result = await document_service.analyze_documents(
            files=files,
            analysis_type=analysis_type,
            focus_areas=focus_areas_list
        )
        
        # Add user context to response
        analysis_result["user_id"] = current_user.id
        
        return analysis_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing documents: {str(e)}")

@router.get("/analysis-types")
async def get_analysis_types():
    """Get available analysis types and focus areas"""
    return {
        "analysis_types": [
            {
                "value": "General Summary",
                "label": "General Summary",
                "description": "Overall summary of financial documents"
            },
            {
                "value": "Expense Categorization",
                "label": "Expense Categorization", 
                "description": "Categorize and analyze spending patterns"
            },
            {
                "value": "Cash Flow Analysis",
                "label": "Cash Flow Analysis",
                "description": "Analyze income vs expenses and cash flow trends"
            },
            {
                "value": "Debt Account Detection",
                "label": "Debt Account Detection",
                "description": "Identify and analyze debt accounts and obligations"
            },
            {
                "value": "Investment Portfolio Review",
                "label": "Investment Portfolio Review",
                "description": "Review investment holdings and performance"
            }
        ],
        "focus_areas": [
            "Monthly Spending Patterns",
            "High-Interest Charges",
            "Fee Analysis",
            "Credit Utilization",
            "Payment History",
            "Budget Recommendations"
        ]
    }

@router.get("/health")
async def document_service_health():
    """Check if document service is properly configured"""
    try:
        document_service = DocumentService()
        return {
            "status": "healthy",
            "supported_types": document_service.get_supported_file_types(),
            "groq_configured": True
        }
    except ValueError as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "groq_configured": False
        }