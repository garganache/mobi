import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db, Base
from app.models import Listing, ListingImage, ListingSynthesis

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def test_client():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)


def test_save_listing_success(test_client):
    """Test successful listing save with all data."""
    
    # Test data
    payload = {
        "property_type": "apartment",
        "price": 350000,
        "bedrooms": 2,
        "bathrooms": 1.5,
        "square_feet": 1200,
        "address": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94102",
        "additional_fields": {
            "has_pool": True,
            "has_fireplace": False
        },
        "images": [
            {
                "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "order_index": 0,
                "ai_analysis": {
                    "description": "Beautiful living room",
                    "rooms": {"living_room": 1},
                    "amenities": ["hardwood_floors"],
                    "property_type": "apartment",
                    "style": "modern",
                    "condition": "good"
                }
            }
        ],
        "synthesis": {
            "total_rooms": 5,
            "layout_type": "open_concept",
            "unified_description": "Beautiful modern apartment",
            "room_breakdown": {"bedroom": 2, "bathroom": 1, "kitchen": 1, "living_room": 1},
            "property_overview": {"style": "modern", "condition": "good"},
            "interior_features": ["hardwood_floors", "granite_counters"],
            "exterior_features": ["balcony"]
        }
    }
    
    response = test_client.post("/api/listings", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["listing_id"] > 0
    assert data["message"] == "Listing saved successfully"
    
    # Verify database state
    db = TestingSessionLocal()
    listing = db.query(Listing).filter(Listing.id == data["listing_id"]).first()
    assert listing is not None
    assert listing.property_type == "apartment"
    assert listing.price == 350000
    assert listing.bedrooms == 2
    assert listing.bathrooms == 1.5
    assert listing.square_feet == 1200
    assert listing.address == "123 Main St"
    assert listing.city == "San Francisco"
    assert listing.state == "CA"
    assert listing.zip_code == "94102"
    assert listing.status == "draft"
    
    # Verify images
    assert len(listing.images) == 1
    image = listing.images[0]
    assert image.order_index == 0
    assert image.ai_description == "Beautiful living room"
    assert image.property_type == "apartment"
    assert image.style == "modern"
    assert image.condition == "good"
    
    # Verify synthesis
    assert listing.synthesis is not None
    assert listing.synthesis.total_rooms == 5
    assert listing.synthesis.layout_type == "open_concept"
    assert listing.synthesis.unified_description == "Beautiful modern apartment"
    assert len(listing.synthesis.interior_features) == 2
    assert len(listing.synthesis.exterior_features) == 1


def test_save_listing_minimal(test_client):
    """Test saving a listing with minimal required data."""
    
    payload = {
        "property_type": "house",
        "images": [
            {
                "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "order_index": 0
            }
        ]
    }
    
    response = test_client.post("/api/listings", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["listing_id"] > 0
    
    # Verify database state
    db = TestingSessionLocal()
    listing = db.query(Listing).filter(Listing.id == data["listing_id"]).first()
    assert listing is not None
    assert listing.property_type == "house"
    assert listing.price is None
    assert listing.bedrooms is None
    assert listing.bathrooms is None
    assert listing.square_feet is None
    assert len(listing.images) == 1
    assert listing.synthesis is None


def test_save_listing_missing_property_type(test_client):
    """Test that property_type is required."""
    
    payload = {
        "images": [
            {
                "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "order_index": 0
            }
        ]
    }
    
    response = test_client.post("/api/listings", json=payload)
    
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "property_type" in str(data).lower() or "field required" in str(data).lower()


def test_save_listing_no_images(test_client):
    """Test that at least one image is required."""
    
    payload = {
        "property_type": "apartment",
        "images": []
    }
    
    response = test_client.post("/api/listings", json=payload)
    
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "at least one image" in str(data).lower() or "images" in str(data).lower()


def test_save_listing_missing_images(test_client):
    """Test that images field is required."""
    
    payload = {
        "property_type": "apartment"
    }
    
    response = test_client.post("/api/listings", json=payload)
    
    assert response.status_code == 400  # My validation returns 400 for missing images
    data = response.json()
    assert "at least one image" in str(data).lower() or "images" in str(data).lower()


def test_save_listing_multiple_images(test_client):
    """Test saving a listing with multiple images."""
    
    payload = {
        "property_type": "condo",
        "images": [
            {
                "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "order_index": 0,
                "ai_analysis": {
                    "description": "Living room",
                    "rooms": {"living_room": 1}
                }
            },
            {
                "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "order_index": 1,
                "ai_analysis": {
                    "description": "Kitchen",
                    "rooms": {"kitchen": 1}
                }
            }
        ]
    }
    
    response = test_client.post("/api/listings", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["listing_id"] > 0
    
    # Verify database state
    db = TestingSessionLocal()
    listing = db.query(Listing).filter(Listing.id == data["listing_id"]).first()
    assert listing is not None
    assert len(listing.images) == 2
    assert listing.images[0].order_index == 0
    assert listing.images[1].order_index == 1