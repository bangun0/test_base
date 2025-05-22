"""
Tests for the Pydantic models (schemas) in the TodayPickup client library.

This module contains unit tests to ensure that the DTOs defined in
`app.today_pickup_client.schemas` behave as expected. This includes
testing for correct instantiation, field validation (implicitly by Pydantic),
and serialization (e.g., via `model_dump()`).
"""
from app.today_pickup_client.schemas import GoodsReturnRequestDTO

def test_goods_return_request_dto() -> None:
    """
    Tests the instantiation and serialization of the GoodsReturnRequestDTO.

    Verifies that:
    - The DTO can be created with valid data.
    - The `invoiceNumber` field is correctly assigned.
    - `model_dump()` produces a dictionary matching the input data.
    """
    data = {"invoiceNumber": "INV123456789"}
    
    # Instantiate the DTO with the test data
    dto = GoodsReturnRequestDTO(**data)
    
    # Assert that the field was correctly assigned
    assert dto.invoiceNumber == "INV123456789"
    
    # Assert that model_dump() returns the original data structure
    # This also implicitly tests that no unexpected fields are present
    # and that required fields are correctly handled by Pydantic.
    assert dto.model_dump() == data

# Add more tests here for other DTOs as they are implemented and used.
# For example:
# def test_another_dto_valid_data():
#     ...
#
# def test_another_dto_missing_required_field():
#     with pytest.raises(ValidationError):
#         AnotherDTO(...) # Data missing a required field
