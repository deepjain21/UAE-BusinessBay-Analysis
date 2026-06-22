from typing import Optional
from pydantic import BaseModel, Field


class PropertyListing(BaseModel):
    listing_type: Optional[str] = Field(None, description="'buy' or 'rent'")
    property_type: Optional[str] = Field(None, description="Apartment / Villa / Townhouse / Penthouse / etc.")

    price_aed: Optional[float] = Field(None, description="Listed price in AED as a number, no commas or currency symbol")
    price_frequency: Optional[str] = Field(None, description="For rentals: yearly / monthly / weekly / daily. Null for buy.")
    price_per_sqft_aed: Optional[float] = None
    mortgage_monthly_aed: Optional[float] = Field(None, description="Estimated monthly mortgage in AED if shown")

    bedrooms: Optional[str] = Field(None, description="Number of bedrooms; 'Studio' if studio; include '+Maid' suffix if present")
    bathrooms: Optional[float] = None
    size_sqft: Optional[float] = None
    size_sqm: Optional[float] = None
    parking_slots: Optional[int] = None
    furnishing: Optional[str] = Field(None, description="Furnished / Unfurnished / Partially furnished")
    status: Optional[str] = Field(None, description="Vacant / Tenanted / Off-plan / Ready / etc.")
    floor: Optional[str] = Field(None, description="e.g. 'Mid Floor', 'High Floor', or a number")

    building: Optional[str] = None
    community: Optional[str] = None
    area: Optional[str] = Field(None, description="Neighborhood / district")
    city: Optional[str] = None
    zone: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = Field(None, description="Full listing description text")
    features: Optional[list[str]] = Field(None, description="Property-level features list")
    amenities: Optional[list[str]] = Field(None, description="Building/community amenities list")

    listed_on: Optional[str] = Field(None, description="Listed date or relative time string ('8 days ago')")
    permit_number: Optional[str] = Field(None, description="RERA / DLD permit number if shown")

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_count: Optional[int] = None


CSV_COLUMNS = list(PropertyListing.model_fields.keys())
