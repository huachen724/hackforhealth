from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Tuple
from pydantic import BaseModel
from datetime import datetime
from database import Database

app = FastAPI()

db = Database()

# Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with the actual front-end domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Class to represent Point and its arguments.
class PointPin(BaseModel):
    symptoms: Tuple[str, ...]  # Change List to Tuple
    diseases: Tuple[str, ...]  # Change List to Tuple
    longitude: float
    latitude: float
    pin: str
    
    
# Class to represent Point and its arguments.
class Point(BaseModel):
    pointId: int
    symptoms: Tuple[str, ...]  # Change List to Tuple
    diseases: Tuple[str, ...]  # Change List to Tuple
    longitude: float
    latitude: float
    date: str  # This should work without any additional installations
    group: int

class Filter(BaseModel):
    symptoms: List[str]
    diseases: List[str]

# GET Route to get all the points and their related data from the database
@app.get("/points", description="Get all the points")
async def get_all_points():
    try:
        # Get all points from the database
        all_points = db.getAllPoints()
        # Convert each point in all_points to a Point instance
        formatted_points = [
            Point(
                pointId = point["ID"],
                symptoms=tuple(point["SYMPTOMS"]),  # Convert list to tuple
                diseases=tuple(point["DISEASES"]),  # Convert list to tuple
                longitude=point["LONGITUDE"],
                latitude=point["LATITUDE"],
                date= point["DATE"],
                group = point["GROUP"]
            )
            for point in all_points
        ]
        print("LENGTH", len(all_points))
        return {"points": formatted_points}
    except Exception as e:
        # Log the exception for debugging
        print(f"Exception: {e}")
        # Raise HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Internal Server Error")


# GET Route to get the all the symptoms and diseases
@app.get("/dropdown")
async def get_dropdown():
    try:
        symptoms = db.getSymptomList()
        diseases = db.getDiseaseList()
        dropdown_data = {"symptomList": symptoms, "diseaseList": diseases}

        return dropdown_data
    except Exception as e:
        # Log the exception for debugging
        print(f"Exception: {e}")
        # Raise HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Internal Server Error")

# POST Route to upload a point and their related data
@app.post("/points", description="Upload a point")
async def upload_point(point: PointPin):
    try:
        print("Received point data:")
        for param_name, param_value in point.dict().items():
            print(f"{param_name}: {param_value}")

        # For debugging purposes, don't call db.addPoint
        db.addPoint(
           username="billy",
           latitude=point.latitude,
           longitude=point.longitude,
           symptoms=point.symptoms,
           diseases=point.diseases,
           pin=point.pin
        )
        
        # after adding point make the cluster
        return {"message": "Point parameters printed for debugging"}
    except Exception as e:
        # Log the exception for debugging
        print(f"Exception: {e}")
        # Raise HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/points/filter", description="Filter points based on symptoms and diseases")
async def filter_points(symptoms: List[str] = Body(..., embed=True), diseases: List[str] = Body(..., embed=True)):
    try:
        points = db.filterPoints(symptoms, diseases)
        formatted_points = [
            Point(
                pointId = point["ID"],
                symptoms=tuple(point["SYMPTOMS"]),
                diseases=tuple(point["DISEASES"]),
                longitude=point["LONGITUDE"],
                latitude=point["LATITUDE"],
                date=point["DATE"],
                group = point["GROUP"]
            )
            for point in points
        ]
        return {"points": formatted_points}
    except Exception as e:
        # Log the exception for debugging
        print(f"Exception: {e}")
        # Raise HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete Route that deletes based on the pin passed
@app.delete("/points/delete/{pointId}/{pin}")
async def delete_point(pin:str , pointId:int):
    try:
        if db.checkPin(pin, pointId):
            return {"message": "Point deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid pin")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")