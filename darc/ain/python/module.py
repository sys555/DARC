import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Actor(Base):
    __tablename__ = 'actor'
    
    uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    graph_id = Column(UUID(as_uuid=True), nullable=False)
    inserted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    outgoing_edges = relationship("Edge", back_populates="from_actor", foreign_keys='Edge.from_uid')
    incoming_edges = relationship("Edge", back_populates="to_actor", foreign_keys='Edge.to_uid')

class Edge(Base):
    __tablename__ = 'edge'
    
    uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    since = Column(Integer, nullable=False)
    graph_id = Column(UUID(as_uuid=True), nullable=False)
    from_uid = Column(UUID(as_uuid=True), ForeignKey('actor.uid'), nullable=False)
    to_uid = Column(UUID(as_uuid=True), ForeignKey('actor.uid'), nullable=False)
    inserted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    from_actor = relationship("Actor", foreign_keys=[from_uid], back_populates="outgoing_edges")
    to_actor = relationship("Actor", foreign_keys=[to_uid], back_populates="incoming_edges")