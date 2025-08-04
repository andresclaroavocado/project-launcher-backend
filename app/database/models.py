"""
Database models for Web-Based Project Architect
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func

from .database import Base


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    project_idea = Column(Text, nullable=False)
    architecture = Column(JSON)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    phase = Column(String(100), default="project_idea")
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text)
    doc_type = Column(String(100))  # architecture, api_spec, deployment, etc.
    file_path = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Repository(Base):
    """Repository model"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repo_type = Column(String(100))  # backend, frontend, docs, infrastructure
    github_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now()) 