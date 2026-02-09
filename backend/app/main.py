from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, Text, create_engine
from sqlalchemy.orm import declarative_base, Session, sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

from app.schemas import (
    AnalyzeStepRequest,
    AnalyzeStepResponse,
    UIField,
    FieldOption,
)
from app.orchestrator import orchestrator
from app.vision_model import analyze_property_image, VisionModelError

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
  raise RuntimeError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


class Description(Base):
    __tablename__ = "descriptions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


class DescriptionIn(BaseModel):
    text: str


class DescriptionOut(BaseModel):
    id: int
    text: str
    created_at: datetime

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Mobi Backend")

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check for Kubernetes probes."""
    return {"status": "ok"}


@app.post("/description", response_model=DescriptionOut)
def create_description(payload: DescriptionIn, db: Session = Depends(get_db)):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Description cannot be empty")

    desc = Description(text=text)
    db.add(desc)
    db.commit()
    db.refresh(desc)
    return desc


@app.get("/description/latest", response_model=Optional[DescriptionOut])
def get_latest_description(db: Session = Depends(get_db)):
    desc = db.query(Description).order_by(Description.created_at.desc()).first()
    if desc is None:
        raise HTTPException(status_code=404, detail="No description found")
    return desc


@app.get("/description", response_model=list[DescriptionOut])
def list_descriptions(limit: int = 10, db: Session = Depends(get_db)):
    """Return the most recent descriptions, newest first."""
    q = db.query(Description).order_by(Description.created_at.desc()).limit(limit)
    return q.all()


@app.post("/analyze-step", response_model=AnalyzeStepResponse)
def analyze_step(request: AnalyzeStepRequest):
    """
    Core orchestrator endpoint for AI-guided listing creation.
    
    Accepts the current form state and new input (image, text, or field update),
    then returns a UI manifest telling the frontend what to display next.
    
    ## Request Body
    - `current_data`: Dictionary of current form values (field_id: value)
    - `new_input`: Optional new input (base64 image or text)
    - `input_type`: Type of input ('image', 'text', or 'field_update')
    - `image_url`: Optional URL to an uploaded image
    
    ## Response
    Returns a UI Manifest containing:
    - `extracted_data`: Data extracted/inferred by AI
    - `ui_schema`: Array of field definitions to render
    - `ai_message`: Conversational guidance for the user
    - `step_number`: Current step in the flow
    - `completion_percentage`: Estimated progress
    """
    
    # Handle different input types
    extracted_data = request.current_data.copy()
    detected_property_type = None  # Track AI-detected property type for default value
    ai_message = None  # AI message to show user
    
    if request.input_type == 'image':
        try:
            # Decode base64 image data
            import base64
            # Handle potential base64 padding issues
            image_b64 = request.new_input
            if image_b64:
                # Add padding if needed
                missing_padding = len(image_b64) % 4
                if missing_padding:
                    image_b64 += '=' * (4 - missing_padding)
                image_data = base64.b64decode(image_b64)
            else:
                # Fallback for testing - create a simple test image
                from PIL import Image
                import io
                img = Image.new('RGB', (800, 600), color='blue')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG')
                image_data = img_bytes.getvalue()
            
            # Analyze the image using vision model
            # Use OpenAI if API key is available, otherwise use mock
            model_type = "openai" if os.getenv("OPENAI_API_KEY") else "mock"
            vision_result = analyze_property_image(
                image_data, 
                model_type=model_type,
                api_key=os.getenv("OPENAI_API_KEY") if model_type == "openai" else None
            )
            
            # Store property_type as a suggestion, not as extracted data
            # This ensures the user sees and confirms the detected property type
            detected_property_type = vision_result.get("property_type") or "apartment"
            
            if vision_result.get("rooms"):
                for room_type, count in vision_result["rooms"].items():
                    if room_type == "bedroom":
                        extracted_data["bedrooms"] = count
                    elif room_type == "bathroom":
                        extracted_data["bathrooms"] = count
            else:
                # Default rooms if not detected
                extracted_data["bedrooms"] = 2
            
            if vision_result.get("amenities"):
                # Convert amenities to boolean flags
                amenities = vision_result["amenities"]
                extracted_data["has_pool"] = "pool" in amenities
                extracted_data["has_fireplace"] = "fireplace" in amenities
                extracted_data["has_balcony"] = "balcony" in amenities
                extracted_data["has_garage"] = "garage" in amenities
                extracted_data["has_hardwood_floors"] = "hardwood_floors" in amenities
                extracted_data["has_granite_counters"] = "granite_counters" in amenities
            else:
                # Default amenities if not detected
                extracted_data["has_pool"] = False
            
            # Generate AI message based on what was detected
            bedrooms_count = extracted_data.get('bedrooms', 2)
            if detected_property_type == "apartment":
                ai_message = f"I see what looks like an apartment with {bedrooms_count} bedrooms. Please confirm the property type below."
            else:
                ai_message = f"I see what looks like a {detected_property_type} with {bedrooms_count} bedrooms. Please confirm the property type below."
                
        except Exception as e:
            logger.error(f"Vision model analysis failed: {e}")
            # Fallback to basic defaults (don't set property_type)
            detected_property_type = "apartment"
            if "bedrooms" not in extracted_data:
                extracted_data["bedrooms"] = 2
            if "has_pool" not in extracted_data:
                extracted_data["has_pool"] = False
                
            ai_message = "I see what looks like an apartment with 2 bedrooms. Please confirm the property type below."
        
    elif request.input_type == 'text':
        # For text input, we might extract some basic info
        # This is a simplified implementation
        if request.new_input and len(request.new_input) > 10:
            extracted_data["description"] = request.new_input
    
    # Use orchestrator to determine next fields (after processing input)
    next_fields = orchestrator.get_next_fields(extracted_data)
    
    # If we detected a property type from an image and property_type field is shown,
    # set it as the default value so user can confirm/modify
    if detected_property_type:
        for field in next_fields:
            if field.id == "property_type":
                field.default = detected_property_type
                break
    
    # Generate AI message if not already set (e.g., from image analysis)
    if ai_message is None:
        ai_message = orchestrator.generate_ai_message(extracted_data, next_fields)
    
    completion_percentage = orchestrator.calculate_completion_percentage(extracted_data)
    
    return AnalyzeStepResponse(
        extracted_data=extracted_data,
        ui_schema=next_fields,
        ai_message=ai_message,
        step_number=len(extracted_data),
        completion_percentage=completion_percentage,
    )