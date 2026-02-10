from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Property details
    property_type = Column(String, nullable=False)  # apartment, house, etc.
    price = Column(Integer)  # in cents or dollars
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    square_feet = Column(Integer)
    
    # Location
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    
    # Status
    status = Column(String, default="draft")  # draft, published, archived
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = relationship("ListingImage", back_populates="listing", cascade="all, delete-orphan")
    synthesis = relationship("ListingSynthesis", back_populates="listing", uselist=False, cascade="all, delete-orphan")


class ListingImage(Base):
    __tablename__ = "listing_images"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    
    # Image data (base64 or URL)
    image_data = Column(Text)  # Base64 encoded for MVP
    image_url = Column(String)  # Optional URL if using external storage
    
    # AI analysis results
    ai_description = Column(Text)
    detected_rooms = Column(JSON)  # e.g., {"bedroom": 1, "kitchen": 1}
    detected_amenities = Column(JSON)  # e.g., ["hardwood_floors", "granite"]
    property_type = Column(String)
    style = Column(String)
    condition = Column(String)
    
    # Order
    order_index = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    listing = relationship("Listing", back_populates="images")


class ListingSynthesis(Base):
    __tablename__ = "listing_synthesis"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False, unique=True)
    
    # Synthesis data
    total_rooms = Column(Integer)
    layout_type = Column(String)  # open_concept, traditional
    unified_description = Column(Text)
    room_breakdown = Column(JSON)  # e.g., {"bedroom": 2, "kitchen": 1}
    property_overview = Column(JSON)  # Full overview object
    interior_features = Column(JSON)  # List of interior amenities
    exterior_features = Column(JSON)  # List of exterior features
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    listing = relationship("Listing", back_populates="synthesis")