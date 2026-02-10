import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Listing, ListingImage, ListingSynthesis


# Test database setup
@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_listing_creation(db_session):
    """Test creating a basic listing."""
    listing = Listing(
        property_type="apartment",
        price=150000,
        bedrooms=2,
        bathrooms=1.5,
        square_feet=800,
        address="123 Main St",
        city="New York",
        state="NY",
        zip_code="10001"
    )
    
    db_session.add(listing)
    db_session.commit()
    
    assert listing.id is not None
    assert listing.property_type == "apartment"
    assert listing.price == 150000
    assert listing.bedrooms == 2
    assert listing.bathrooms == 1.5
    assert listing.square_feet == 800
    assert listing.status == "draft"
    assert listing.created_at is not None
    assert listing.updated_at is not None


def test_listing_image_creation(db_session):
    """Test creating a listing image."""
    # First create a listing
    listing = Listing(property_type="house", price=300000)
    db_session.add(listing)
    db_session.commit()
    
    # Create an image for the listing
    image = ListingImage(
        listing_id=listing.id,
        image_data="base64_encoded_image_data",
        ai_description="A beautiful living room with hardwood floors",
        detected_rooms={"living_room": 1, "bedroom": 2},
        detected_amenities=["hardwood_floors", "fireplace"],
        property_type="house",
        style="colonial",
        condition="good",
        order_index=0
    )
    
    db_session.add(image)
    db_session.commit()
    
    assert image.id is not None
    assert image.listing_id == listing.id
    assert image.image_data == "base64_encoded_image_data"
    assert image.ai_description == "A beautiful living room with hardwood floors"
    assert image.detected_rooms == {"living_room": 1, "bedroom": 2}
    assert image.detected_amenities == ["hardwood_floors", "fireplace"]
    assert image.property_type == "house"
    assert image.style == "colonial"
    assert image.condition == "good"
    assert image.order_index == 0


def test_listing_synthesis_creation(db_session):
    """Test creating a listing synthesis."""
    # First create a listing
    listing = Listing(property_type="condo", price=250000)
    db_session.add(listing)
    db_session.commit()
    
    # Create synthesis for the listing
    synthesis = ListingSynthesis(
        listing_id=listing.id,
        total_rooms=5,
        layout_type="open_concept",
        unified_description="A modern condo with open concept design",
        room_breakdown={"bedroom": 2, "bathroom": 2, "kitchen": 1},
        property_overview={"type": "condo", "size": "1200 sqft", "year_built": 2020},
        interior_features=["granite_counters", "stainless_appliances"],
        exterior_features=["balcony", "parking"]
    )
    
    db_session.add(synthesis)
    db_session.commit()
    
    assert synthesis.id is not None
    assert synthesis.listing_id == listing.id
    assert synthesis.total_rooms == 5
    assert synthesis.layout_type == "open_concept"
    assert synthesis.unified_description == "A modern condo with open concept design"
    assert synthesis.room_breakdown == {"bedroom": 2, "bathroom": 2, "kitchen": 1}
    assert synthesis.property_overview == {"type": "condo", "size": "1200 sqft", "year_built": 2020}
    assert synthesis.interior_features == ["granite_counters", "stainless_appliances"]
    assert synthesis.exterior_features == ["balcony", "parking"]


def test_listing_relationships(db_session):
    """Test relationships between listing, images, and synthesis."""
    # Create a listing with images and synthesis
    listing = Listing(property_type="townhouse", price=400000)
    db_session.add(listing)
    db_session.commit()
    
    # Add images
    image1 = ListingImage(
        listing_id=listing.id,
        image_data="image1_data",
        order_index=0
    )
    image2 = ListingImage(
        listing_id=listing.id,
        image_data="image2_data",
        order_index=1
    )
    db_session.add_all([image1, image2])
    
    # Add synthesis
    synthesis = ListingSynthesis(
        listing_id=listing.id,
        total_rooms=6,
        layout_type="traditional"
    )
    db_session.add(synthesis)
    db_session.commit()
    
    # Test relationships
    assert len(listing.images) == 2
    assert listing.synthesis is not None
    assert listing.synthesis.total_rooms == 6
    assert listing.synthesis.layout_type == "traditional"
    
    # Test that images are ordered correctly
    images = sorted(listing.images, key=lambda x: x.order_index)
    assert images[0].order_index == 0
    assert images[1].order_index == 1


def test_listing_status_default(db_session):
    """Test that listing status defaults to 'draft'."""
    listing = Listing(property_type="apartment")
    db_session.add(listing)
    db_session.commit()
    
    assert listing.status == "draft"


def test_listing_timestamps(db_session):
    """Test that created_at and updated_at are set correctly."""
    before_creation = datetime.utcnow()
    
    listing = Listing(property_type="house")
    db_session.add(listing)
    db_session.commit()
    
    after_creation = datetime.utcnow()
    
    assert listing.created_at is not None
    assert listing.updated_at is not None
    assert before_creation <= listing.created_at <= after_creation
    assert before_creation <= listing.updated_at <= after_creation