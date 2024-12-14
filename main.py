from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
from typing import List, Optional

# Load CSV data
data = pd.read_csv("data/house_pricing.csv")

# Initialize FastAPI app
app = FastAPI()

# In-memory "database"
data["id"] = data.index  # Add an 'id' column for unique identifiers
data_records = data.to_dict(orient="records")


# Pydantic model for a house record
class House(BaseModel):
    id: Optional[int]  # Auto-assigned on creation
    date: str
    price: float
    bedrooms: float
    bathrooms: float
    sqft_living: int
    sqft_lot: int
    floors: float
    waterfront: int
    view: int
    condition: int
    sqft_above: int
    sqft_basement: int
    yr_built: int
    yr_renovated: int
    street: str
    city: str
    statezip: str
    country: str


@app.get("/houses", response_model=List[House])
def get_houses(
    page: int = Query(1, gt=0),
    size: int = Query(10, le=100),
    city: Optional[str] = None,
    statezip: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
):
    """
    Retrieve paginated and filtered house records.
    """
    filtered_data = data_records

    # Apply filters
    if city:
        filtered_data = [d for d in filtered_data if d["city"].lower() == city.lower()]
    if statezip:
        filtered_data = [
            d for d in filtered_data if d["statezip"].lower() == statezip.lower()
        ]
    if price_min is not None:
        filtered_data = [d for d in filtered_data if d["price"] >= price_min]
    if price_max is not None:
        filtered_data = [d for d in filtered_data if d["price"] <= price_max]

    # Pagination
    start = (page - 1) * size
    end = start + size
    return filtered_data[start:end]


@app.post("/houses", response_model=House)
def create_house(house: House):
    """
    Create a new house record.
    """
    new_id = max([d["id"] for d in data_records]) + 1
    house_data = house.dict()
    house_data["id"] = new_id
    data_records.append(house_data)
    return house_data


@app.get("/houses/{house_id}", response_model=House)
def get_house(house_id: int):
    """
    Retrieve a house record by ID.
    """
    house = next((d for d in data_records if d["id"] == house_id), None)
    if house is None:
        raise HTTPException(status_code=404, detail="House not found")
    return house


@app.put("/houses/{house_id}", response_model=House)
def update_house(house_id: int, updated_house: House):
    """
    Update a house record by ID.
    """
    for i, house in enumerate(data_records):
        if house["id"] == house_id:
            updated_data = updated_house.dict()
            updated_data["id"] = house_id
            data_records[i] = updated_data
            return updated_data
    raise HTTPException(status_code=404, detail="House not found")


@app.delete("/houses/{house_id}")
def delete_house(house_id: int):
    """
    Delete a house record by ID.
    """
    for i, house in enumerate(data_records):
        if house["id"] == house_id:
            del data_records[i]
            return {"message": "House deleted"}
    raise HTTPException(status_code=404, detail="House not found")
