"""
Test utilities and fixtures for feature extraction testing.

This module provides helper functions and mock data for testing
the feature extraction functionality.
"""

from typing import Dict, Any, List
import pytest


class MockVisionOutput:
    """Mock vision model outputs for testing feature extraction."""
    
    @staticmethod
    def house_description() -> str:
        """Return a mock vision output describing a house."""
        return """
        This beautiful 2-story house sits on a quarter-acre lot with mature trees.
        The 4-bedroom, 3-bathroom home features a modern kitchen with granite countertops
        and stainless steel appliances. Hardwood floors flow throughout the main living areas.
        Additional amenities include a swimming pool, 2-car garage, and outdoor fireplace.
        The architectural style is traditional with contemporary updates.
        """
    
    @staticmethod
    def apartment_description() -> str:
        """Return a mock vision output describing an apartment."""
        return """
        This modern apartment is located on the 8th floor of a luxury high-rise building.
        The 2-bedroom, 2-bathroom unit features floor-to-ceiling windows with city views.
        The kitchen has granite countertops and stainless steel appliances.
        Building amenities include a fitness center, pool, and 24-hour concierge.
        The contemporary design features an open-concept living space.
        """
    
    @staticmethod
    def condo_description() -> str:
        """Return a mock vision output describing a condo."""
        return """
        This spacious condominium unit features 3 bedrooms and 2.5 bathrooms.
        The condo has been recently updated with hardwood floors throughout.
        The kitchen features granite countertops and modern appliances.
        A private balcony off the living room provides outdoor space.
        The unit includes a designated parking space in the garage.
        """
    
    @staticmethod
    def ambiguous_description() -> str:
        """Return a mock vision output with ambiguous information."""
        return """
        This property has some interesting characteristics and features.
        The space could be used for various purposes depending on needs.
        Some areas are well-maintained while others may require attention.
        The overall condition appears to be average.
        """
    
    @staticmethod
    def luxury_estate_description() -> str:
        """Return a mock vision output describing a luxury estate."""
        return """
        This magnificent 6-bedroom, 5.5-bathroom estate sits on 3 acres of landscaped grounds.
        The property features a gourmet kitchen with professional-grade appliances,
        granite countertops, and custom cabinetry. Additional amenities include a home theater,
        wine cellar, fitness room, and library. Outdoor features include an infinity pool,
        tennis court, outdoor kitchen, and 4-car garage. The architectural style is 
        contemporary with traditional elements and high-end finishes throughout.
        """


def assert_valid_extraction_result(result: Any) -> None:
    """
    Assert that a feature extraction result has the expected structure.
    
    Args:
        result: The result object from feature extraction
    """
    # TODO: Update this when the actual result structure is implemented
    # For now, just assert that result is not None
    assert result is not None


def assert_confidence_scores_valid(confidence_scores: Dict[str, float]) -> None:
    """
    Assert that confidence scores are valid (between 0.0 and 1.0).
    
    Args:
        confidence_scores: Dictionary mapping feature names to confidence scores
    """
    for feature, score in confidence_scores.items():
        assert 0.0 <= score <= 1.0, f"Confidence score for {feature} must be between 0.0 and 1.0"


@pytest.fixture
def mock_vision_outputs() -> MockVisionOutput:
    """Pytest fixture providing mock vision outputs."""
    return MockVisionOutput()


@pytest.fixture
def sample_property_descriptions() -> List[str]:
    """Pytest fixture providing sample property descriptions."""
    return [
        MockVisionOutput.house_description(),
        MockVisionOutput.apartment_description(),
        MockVisionOutput.condo_description(),
        MockVisionOutput.luxury_estate_description(),
        MockVisionOutput.ambiguous_description()
    ]