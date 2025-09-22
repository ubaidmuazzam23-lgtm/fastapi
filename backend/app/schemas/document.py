# app/schemas/document.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentAnalysisRequest(BaseModel):
    analysis_type: str = Field(
        default="General Summary",
        description="Type of analysis to perform"
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on in the analysis"
    )

class DocumentSummaryResponse(BaseModel):
    summary: str = Field(description="AI-generated summary of the documents")
    files_processed: List[str] = Field(description="List of processed file names")
    processing_time: Optional[float] = Field(description="Time taken to process in seconds")
    created_at: datetime = Field(default_factory=datetime.now)

class DocumentAnalysisResponse(BaseModel):
    summary: str = Field(description="Document summary")
    focused_analysis: str = Field(description="Focused analysis based on type and areas")
    action_items: str = Field(description="Actionable recommendations")
    analysis_type: str = Field(description="Type of analysis performed")
    focus_areas: List[str] = Field(description="Areas that were focused on")
    files_analyzed: List[str] = Field(description="List of analyzed file names")
    created_at: datetime = Field(default_factory=datetime.now)

class ExtractedFinancialData(BaseModel):
    accounts: List[Dict[str, Any]] = Field(default_factory=list)
    transactions: List[Dict[str, Any]] = Field(default_factory=list)
    balances: Dict[str, Any] = Field(default_factory=dict)
    fees: List[Dict[str, Any]] = Field(default_factory=list)
    interest_charges: List[Dict[str, Any]] = Field(default_factory=list)
    raw_extractions: Optional[List[Dict[str, str]]] = Field(default=None)
    errors: Optional[List[str]] = Field(default=None)

class SupportedFileTypesResponse(BaseModel):
    supported_types: List[str] = Field(description="List of supported file extensions")
    max_file_size_mb: int = Field(description="Maximum file size in MB")
    max_files_per_request: int = Field(description="Maximum number of files per request")

class FileValidationResponse(BaseModel):
    is_valid: bool = Field(description="Whether the file is valid")
    filename: str = Field(description="Name of the validated file")
    file_size: int = Field(description="Size of the file in bytes")
    errors: Optional[List[str]] = Field(default=None, description="Validation errors if any")