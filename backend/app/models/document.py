# app/models/document.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # File metadata
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    file_hash = Column(String, nullable=True)
    
    # Analysis metadata
    analysis_type = Column(String, nullable=True)
    focus_areas = Column(JSON, default=list)
    
    # Analysis results
    summary = Column(Text, nullable=True)
    focused_analysis = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    
    # Processing metadata
    processing_time = Column(Float, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Extracted financial data
    extracted_accounts = Column(JSON, default=list)
    extracted_transactions = Column(JSON, default=list)
    extracted_balances = Column(JSON, default=dict)
    extracted_fees = Column(JSON, default=list)
    extracted_interest_charges = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")