from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, Text, create_engine
from sqlalchemy.orm import declarative_base, Session, sessionmaker
import os

from app.schemas import (
    AnalyzeStepRequest,
    AnalyzeStepResponse,
    UIField,
    FieldOption,
)

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
    
    ## Current Implementation
    This is a stub implementation that returns mock data for testing.
    Real AI analysis logic will be added in subsequent tasks.
    """
    
    # TODO: Implement real AI analysis logic (TASK-008+)
    # For now, return mock data based on input type
    
    if request.input_type == 'image':
        # Mock response for image input
        return AnalyzeStepResponse(
            extracted_data={
                "property_type": "apartment",
                "has_pool": False,
                "bedrooms": 2,
            },
            ui_schema=[
                UIField(
                    id="property_type",
                    component_type="select",
                    label="Property Type",
                    placeholder="Select type",
                    options=[
                        FieldOption(value="apartment", label="Apartment"),
                        FieldOption(value="house", label="House"),
                        FieldOption(value="condo", label="Condo"),
                    ],
                    required=True,
                ),
                UIField(
                    id="bedrooms",
                    component_type="number",
                    label="Number of Bedrooms",
                    min=0,
                    max=20,
                    default=2,
                ),
            ],
            ai_message="I see a modern apartment with what looks like 2 bedrooms. Is this correct?",
            step_number=1,
            completion_percentage=15.0,
        )
    
    elif request.input_type == 'text':
        # Mock response for text input
        return AnalyzeStepResponse(
            extracted_data={
                **request.current_data,
                "description": request.new_input,
            },
            ui_schema=[
                UIField(
                    id="bathrooms",
                    component_type="number",
                    label="Number of Bathrooms",
                    min=0,
                    max=10,
                ),
                UIField(
                    id="has_parking",
                    component_type="toggle",
                    label="Has Parking",
                ),
            ],
            ai_message="Thanks for the description! Could you tell me about the bathrooms and parking?",
            step_number=2,
            completion_percentage=40.0,
        )
    
    else:  # field_update
        # Mock response for field update
        return AnalyzeStepResponse(
            extracted_data=request.current_data,
            ui_schema=[],
            ai_message="Great! I've updated the form with your information.",
            step_number=len(request.current_data),
            completion_percentage=min(100.0, len(request.current_data) * 10),
        )
