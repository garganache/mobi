from datetime import datetime
from typing import Optional, List
import json

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
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
from app.vision_model import analyze_property_image, analyze_multiple_images, VisionModelError
from app.models import Listing, ListingImage, ListingSynthesis
from app.models import Base, Listing, ListingImage, ListingSynthesis

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


# Request schemas for save listing endpoint
class ImageDataSchema(BaseModel):
    image_data: str  # base64 encoded
    ai_analysis: Optional[dict] = None
    order_index: int = 0


class SynthesisDataSchema(BaseModel):
    total_rooms: int
    layout_type: str
    unified_description: str
    room_breakdown: dict
    property_overview: dict
    interior_features: list = []
    exterior_features: list = []


class SaveListingRequest(BaseModel):
    # Property data
    property_type: str
    price: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    
    # Location
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Additional form fields (dynamic)
    additional_fields: Optional[dict] = {}
    
    # Images
    images: List[ImageDataSchema] = []
    
    # Synthesis
    synthesis: Optional[SynthesisDataSchema] = None
    
    @validator('property_type', pre=True)
    def validate_property_type(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            raise ValueError('property_type is required')
        return v
    
    @validator('images', pre=True)
    def validate_images(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one image is required')
        return v


class SaveListingResponse(BaseModel):
    success: bool
    listing_id: int
    message: str


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


# Listing management endpoints


@app.post("/api/analyze-step", response_model=AnalyzeStepResponse)
def analyze_step(request: AnalyzeStepRequest, db: Session = Depends(get_db)):
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
    - `vision_analysis`: Optional full AI analysis result (when image is processed)
    """
    
    # Handle different input types
    extracted_data = request.current_data.copy()
    detected_property_type = None  # Track AI-detected property type for default value
    ai_message = None  # AI message to show user
    vision_analysis = None  # Full AI analysis result to return to frontend
    
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
            
            # Store the full vision analysis result
            vision_analysis = vision_result.copy()
            
            # Save vision analysis to database
            # TODO: This needs to be updated to work with the new ListingImage model
            # For now, we'll skip saving to database since we don't have a listing_id yet
            # In the future, this should create a new listing and associate the image with it
            try:
                # For now, just log the analysis
                logger.info(f"Vision analysis completed: {vision_result.get('description', '')}")
                
                # Add a placeholder ID to vision analysis for reference
                vision_analysis["analysis_id"] = "temp_analysis_id"
                
            except Exception as db_error:
                logger.error(f"Failed to save image analysis to database: {db_error}")
                # Continue even if database save fails
                db.rollback()
            
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
            
            # Generate AI message from the vision analysis description
            description = vision_result.get("description", "")
            if description:
                # Use the AI's actual description
                ai_message = f"{description}\n\nPlease confirm the property type below and continue with additional details."
            else:
                # Fallback message if no description
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
        vision_analysis=vision_analysis,
    )


@app.post("/api/analyze-batch")
async def analyze_batch_images(files: List[UploadFile] = File(...)):
    """
    Analyze multiple property images and return correlated results.
    
    Accepts multiple image files and returns both individual analyses
    and a synthesized overview of the entire property.
    
    ## Request
    - `files`: List of image files (JPEG, PNG, etc.)
    
    ## Response
    ```json
    {
        "status": "success",
        "individual_analyses": [...],  # Analysis of each image
        "synthesis": {
            "total_rooms": 6,
            "room_breakdown": {"bedroom": 2, "kitchen": 1, ...},
            "amenities_by_room": {...},
            "unified_description": "This property has 6 rooms...",
            "property_overview": {...}
        }
    }
    ```
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed per batch")
    
    try:
        # Read all image data
        image_data_list = []
        for file in files:
            # Validate file type
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not an image"
                )
            
            image_data = await file.read()
            if len(image_data) == 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is empty"
                )
            
            image_data_list.append(image_data)
        
        # Analyze multiple images
        model_type = "openai" if os.getenv("OPENAI_API_KEY") else "mock"
        result = analyze_multiple_images(
            images=image_data_list,
            model_type=model_type,
            api_key=os.getenv("OPENAI_API_KEY") if model_type == "openai" else None
        )
        
        return {
            "status": "success",
            "individual_analyses": result["individual_analyses"],
            "synthesis": result["synthesis"]
        }
        
    except VisionModelError as e:
        logger.error(f"Vision model error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@app.post("/api/listings", response_model=SaveListingResponse)
def save_listing(request: SaveListingRequest, db: Session = Depends(get_db)):
    """
    Save a complete property listing to the database.
    
    Accepts:
    - Property details (type, price, bedrooms, etc.)
    - Images with AI analysis
    - Synthesis data from multi-image analysis
    
    Returns:
    - Listing ID
    - Success confirmation
    """
    try:
        # Validate required fields
        if not request.property_type:
            raise HTTPException(status_code=400, detail="property_type is required")
        
        if not request.images or len(request.images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required")
        
        # Create listing
        listing = Listing(
            property_type=request.property_type,
            price=request.price,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            square_feet=request.square_feet,
            address=request.address,
            city=request.city,
            state=request.state,
            zip_code=request.zip_code,
            status="draft"  # Default to draft
        )
        
        db.add(listing)
        db.flush()  # Get listing.id
        
        # Save images
        for img_data in request.images:
            listing_image = ListingImage(
                listing_id=listing.id,
                image_data=img_data.image_data,
                order_index=img_data.order_index
            )
            
            # Add AI analysis if present
            if img_data.ai_analysis:
                listing_image.ai_description = img_data.ai_analysis.get("description")
                listing_image.detected_rooms = img_data.ai_analysis.get("rooms")
                listing_image.detected_amenities = img_data.ai_analysis.get("amenities")
                listing_image.property_type = img_data.ai_analysis.get("property_type")
                listing_image.style = img_data.ai_analysis.get("style")
                listing_image.condition = img_data.ai_analysis.get("condition")
            
            db.add(listing_image)
        
        # Save synthesis data
        if request.synthesis:
            synthesis = ListingSynthesis(
                listing_id=listing.id,
                total_rooms=request.synthesis.total_rooms,
                layout_type=request.synthesis.layout_type,
                unified_description=request.synthesis.unified_description,
                room_breakdown=request.synthesis.room_breakdown,
                property_overview=request.synthesis.property_overview,
                interior_features=request.synthesis.interior_features,
                exterior_features=request.synthesis.exterior_features
            )
            db.add(synthesis)
        
        # Commit transaction
        db.commit()
        db.refresh(listing)
        
        logger.info(f"Listing saved successfully: ID={listing.id}")
        
        return SaveListingResponse(
            success=True,
            listing_id=listing.id,
            message="Listing saved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving listing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save listing: {str(e)}")