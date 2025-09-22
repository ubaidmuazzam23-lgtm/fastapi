# app/services/document_service.py (complete updated implementation)
import io
import os
import tempfile
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import pdfplumber
from fastapi import UploadFile, HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

# Import your settings
from app.config.settings import settings

class DocumentService:
    def __init__(self):
        # Use settings instead of os.getenv()
        self.groq_api_key = settings.GROQ_API_KEY
        self.llm_model = settings.llm_model
        
        if not self.groq_api_key or self.groq_api_key == "test_groq_key":
            raise ValueError("Valid GROQ_API_KEY is required in settings")
    
    def _get_llm(self):
        """Initialize and return LLM"""
        return ChatGroq(
            model=self.llm_model,
            groq_api_key=self.groq_api_key,
            temperature=0.2
        )
    
    def _extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text from uploaded file based on file type"""
        name = filename.lower()
        
        try:
            if name.endswith(".pdf"):
                return self._extract_pdf_text(file_content)
            elif name.endswith(".txt"):
                return file_content.decode("utf-8", errors="ignore")
            elif name.endswith(".csv"):
                return self._extract_csv_text(file_content)
            elif name.endswith((".xlsx", ".xls")):
                return self._extract_excel_text(file_content)
            else:
                return file_content.decode("utf-8", errors="ignore")
        except Exception as e:
            return f"Error reading {filename}: {str(e)}"
    
    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                return "\n".join(text)
        except Exception as e:
            return f"PDF read error: {str(e)}"
    
    def _extract_csv_text(self, file_content: bytes) -> str:
        """Extract text from CSV file"""
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            return df.to_string(index=False)
        except Exception as e:
            return f"CSV read error: {str(e)}"
    
    def _extract_excel_text(self, file_content: bytes) -> str:
        """Extract text from Excel file"""
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            return df.to_string(index=False)
        except Exception as e:
            return f"Excel read error: {str(e)}"
    
    def _chunk_text(self, text: str, chunk_size: int = 2000, chunk_overlap: int = 200) -> List[str]:
        """Split text into chunks for processing"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return splitter.split_text(text)
    
    async def summarize_documents(self, files: List[UploadFile]) -> str:
        """Generate AI summary of uploaded documents"""
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        texts = []
        for file in files:
            try:
                content = await file.read()
                text = self._extract_text_from_file(content, file.filename)
                texts.append(f"=== {file.filename} ===\n{text}")
                await file.seek(0)
            except Exception as e:
                texts.append(f"Error reading {file.filename}: {str(e)}")
        
        all_text = "\n\n".join(texts)
        
        if not all_text.strip():
            return "No text could be extracted from the uploaded files."
        
        chunks = self._chunk_text(all_text)
        llm = self._get_llm()
        system_prompt = "You are a concise financial document summarizer. Extract key numbers, dates, and action items."
        
        if len(chunks) == 1:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Summarize this financial document:\n\n{chunks[0]}")
            ]
            try:
                response = llm.invoke(messages)
                return response.content
            except Exception as e:
                return f"LLM error: {str(e)}"
        else:
            partial_summaries = []
            for chunk in chunks:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Summarize this part:\n\n{chunk}")
                ]
                try:
                    response = llm.invoke(messages)
                    partial_summaries.append(response.content)
                except Exception as e:
                    partial_summaries.append(f"LLM error: {str(e)}")
            
            combined_text = "\n\n".join(partial_summaries)
            final_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Combine these partial summaries into one concise summary:\n\n{combined_text}")
            ]
            
            try:
                final_response = llm.invoke(final_messages)
                return final_response.content
            except Exception as e:
                return f"LLM error combining summaries: {str(e)}"
    
    async def analyze_documents(
        self, 
        files: List[UploadFile], 
        analysis_type: str,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform focused analysis on documents"""
        
        summary = await self.summarize_documents(files)
        
        focus_prompt = f"""
        Based on the document summary provided, perform a {analysis_type.lower()} analysis.
        """
        
        if focus_areas:
            focus_prompt += f"\nPay special attention to: {', '.join(focus_areas)}"
        
        focus_prompt += f"""
        
        Document Summary:
        {summary}
        
        Please provide:
        1. Key findings specific to {analysis_type.lower()}
        2. Actionable recommendations
        3. Any red flags or opportunities identified
        4. Specific numbers and dates when available
        
        Keep the analysis practical and actionable for debt management.
        """
        
        llm = self._get_llm()
        
        try:
            analysis_response = llm.invoke([HumanMessage(content=focus_prompt)])
            focused_analysis = analysis_response.content
        except Exception as e:
            focused_analysis = f"Enhanced analysis unavailable: {str(e)}"
        
        action_prompt = f"""
        Based on this financial document analysis, suggest 3-5 specific, actionable steps the user should take:
        
        {summary}
        
        Focus on:
        - Debt reduction opportunities
        - Fee avoidance
        - Credit score improvement
        - Budget optimization
        
        Format as a numbered list with brief explanations.
        """
        
        try:
            action_response = llm.invoke([HumanMessage(content=action_prompt)])
            action_items = action_response.content
        except Exception as e:
            action_items = f"Action items unavailable: {str(e)}"
        
        return {
            "summary": summary,
            "focused_analysis": focused_analysis,
            "action_items": action_items,
            "analysis_type": analysis_type,
            "focus_areas": focus_areas or [],
            "files_analyzed": [file.filename for file in files]
        }
    
    def get_supported_file_types(self) -> List[str]:
        """Return list of supported file types"""
        return [".pdf", ".txt", ".csv", ".xlsx", ".xls"]
    
    def validate_file_type(self, filename: str) -> bool:
        """Validate if file type is supported"""
        return any(filename.lower().endswith(ext) for ext in self.get_supported_file_types())
    
    def validate_file_size(self, file_size: int, max_size_mb: int = 10) -> bool:
        """Validate file size (default max 10MB)"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes