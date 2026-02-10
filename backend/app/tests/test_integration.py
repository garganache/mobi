import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Listing, ListingImage, ListingSynthesis
from app.main import SaveListingRequest, ImageDataSchema, SynthesisDataSchema


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_save_listing_request_schemas():
    """Test that the request schemas work correctly."""
    # Test ImageDataSchema
    image_data = ImageDataSchema(
        image_data="base64_image_data",
        ai_analysis={
            "description": "Beautiful living room",
            "rooms": {"living_room": 1, "bedroom": 2},
            "amenities": ["fireplace", "hardwood_floors"],
            "property_type": "house",
            "style": "colonial",
            "condition": "good"
        },
        order_index=0
    )
    
    assert image_data.image_data == "base64_image_data"
    assert image_data.ai_analysis["description"] == "Beautiful living room"
    assert image_data.order_index == 0
    
    # Test SynthesisDataSchema
    synthesis_data = SynthesisDataSchema(
        total_rooms=5,
        layout_type="open_concept",
        unified_description="A beautiful open concept home",
        room_breakdown={"bedroom": 2, "bathroom": 2, "kitchen": 1},
        property_overview={"type": "house", "size": "2000 sqft"},
        interior_features=["granite_counters", "hardwood_floors"],
        exterior_features=["garage", "patio"]
    )
    
    assert synthesis_data.total_rooms == 5
    assert synthesis_data.layout_type == "open_concept"
    assert synthesis_data.unified_description == "A beautiful open concept home"
    assert synthesis_data.room_breakdown == {"bedroom": 2, "bathroom": 2, "kitchen": 1}
    
    # Test SaveListingRequest
    request = SaveListingRequest(
        property_type="house",
        price=350000,
        bedrooms=3,
        bathrooms=2.5,
        square_feet=2000,
        address="456 Oak Ave",
        city="Los Angeles",
        state="CA",
        zip_code="90210",
        additional_fields={"has_pool": True, "has_garage": True},
        images=[image_data],
        synthesis=synthesis_data
    )
    
    assert request.property_type == "house"
    assert request.price == 350000
    assert request.bedrooms == 3
    assert request.bathrooms == 2.5
    assert request.square_feet == 2000
    assert request.address == "456 Oak Ave"
    assert request.city == "Los Angeles"
    assert request.state == "CA"
    assert request.zip_code == "90210"
    assert len(request.images) == 1
    assert request.synthesis.total_rooms == 5


def test_model_imports():
    """Test that all models can be imported correctly."""
    from app.models import Listing, ListingImage, ListingSynthesis, Base
    
    # Test that all models are available
    assert Listing is not None
    assert ListingImage is not None
    assert ListingSynthesis is not None
    assert Base is not None
    
    # Test that they have the expected attributes
    assert hasattr(Listing, '__tablename__')
    assert hasattr(ListingImage, '__tablename__')
    assert hasattr(ListingSynthesis, '__tablename__')
    
    assert Listing.__tablename__ == "listings"
    assert ListingImage.__tablename__ == "listing_images"
    assert ListingSynthesis.__tablename__ == "listing_synthesis"