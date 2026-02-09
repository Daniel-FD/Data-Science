from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from services.numbeo_service import NumbeoService
from services.fx_service import FXService
from models.schemas import BasicConversionResponse, AdvancedConversionRequest, AdvancedConversionResponse, CityResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cost of Living Comparison API",
    description="API for comparing salaries across cities worldwide",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
numbeo_service = NumbeoService()
fx_service = FXService()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Cost of Living Comparison API", "version": "1.0.0"}


@app.get("/api/cities")
async def get_cities():
    """Get list of available cities"""
    try:
        cities = numbeo_service.get_available_cities()
        return {"cities": cities}
    except Exception as e:
        logger.error(f"Error fetching cities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/convert_basic", response_model=BasicConversionResponse)
async def convert_basic(
    salary: float = Query(..., description="Annual salary in source city"),
    source_city: str = Query(..., description="Source city name"),
    currency: str = Query(default="USD", description="Currency code")
):
    """
    Basic Mode: Convert salary to equivalent in other cities
    
    Args:
        salary: Annual salary in source city
        source_city: Name of the source city
        currency: Currency code (default: USD)
    
    Returns:
        List of cities with equivalent salaries and GeoJSON data
    """
    try:
        logger.info(f"Basic conversion: {salary} {currency} from {source_city}")
        
        # Get source city index
        source_index = numbeo_service.get_city_index(source_city)
        if not source_index:
            raise HTTPException(status_code=404, detail=f"City '{source_city}' not found")
        
        # Get all target cities
        target_cities = numbeo_service.get_available_cities()
        
        results = []
        geojson_features = []
        
        for target_city in target_cities:
            if target_city == source_city:
                continue
                
            target_index = numbeo_service.get_city_index(target_city)
            if not target_index:
                continue
            
            # Basic calculation: equiv = salary × (index_target / index_source)
            multiplier = target_index['overall_index'] / source_index['overall_index']
            equivalent_salary = salary * multiplier
            
            city_result = CityResult(
                city=target_city,
                country=target_index.get('country', 'Unknown'),
                equivalent_salary=round(equivalent_salary, 2),
                cost_index=target_index['overall_index'],
                latitude=target_index.get('latitude'),
                longitude=target_index.get('longitude')
            )
            
            results.append(city_result)
            
            # Create GeoJSON feature
            if city_result.latitude and city_result.longitude:
                geojson_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [city_result.longitude, city_result.latitude]
                    },
                    "properties": {
                        "city": city_result.city,
                        "country": city_result.country,
                        "equivalent_salary": city_result.equivalent_salary,
                        "cost_index": city_result.cost_index
                    }
                })
        
        # Sort by equivalent salary
        results.sort(key=lambda x: x.equivalent_salary)
        
        geojson = {
            "type": "FeatureCollection",
            "features": geojson_features
        }
        
        return BasicConversionResponse(
            source_city=source_city,
            source_salary=salary,
            currency=currency,
            results=results,
            geojson=geojson
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in basic conversion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/convert_advanced", response_model=AdvancedConversionResponse)
async def convert_advanced(request: AdvancedConversionRequest):
    """
    Advanced Mode: Convert salary using personalized expense breakdown
    
    Args:
        request: Contains salary, source_city, currency, and expense breakdown
    
    Returns:
        List of cities with personalized equivalent salaries
    """
    try:
        logger.info(f"Advanced conversion: {request.salary} {request.currency} from {request.source_city}")
        
        # Get source city data
        source_data = numbeo_service.get_city_detailed_data(request.source_city)
        if not source_data:
            raise HTTPException(status_code=404, detail=f"City '{request.source_city}' not found")
        
        # Calculate expense weights
        total_expenses = sum(request.expenses.values())
        if total_expenses == 0:
            raise HTTPException(status_code=400, detail="Total expenses cannot be zero")
        
        weights = {k: v / total_expenses for k, v in request.expenses.items()}
        
        # Get all target cities
        target_cities = numbeo_service.get_available_cities()
        
        results = []
        geojson_features = []
        
        for target_city in target_cities:
            if target_city == request.source_city:
                continue
                
            target_data = numbeo_service.get_city_detailed_data(target_city)
            if not target_data:
                continue
            
            # Advanced calculation with weighted categories
            multiplier = 0.0
            for category, weight in weights.items():
                source_cat_index = source_data['categories'].get(category, source_data['overall_index'])
                target_cat_index = target_data['categories'].get(category, target_data['overall_index'])
                
                ratio = target_cat_index / source_cat_index if source_cat_index > 0 else 1.0
                multiplier += weight * ratio
            
            equivalent_salary = request.salary * multiplier
            
            city_result = CityResult(
                city=target_city,
                country=target_data.get('country', 'Unknown'),
                equivalent_salary=round(equivalent_salary, 2),
                cost_index=target_data['overall_index'],
                latitude=target_data.get('latitude'),
                longitude=target_data.get('longitude')
            )
            
            results.append(city_result)
            
            # Create GeoJSON feature
            if city_result.latitude and city_result.longitude:
                geojson_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [city_result.longitude, city_result.latitude]
                    },
                    "properties": {
                        "city": city_result.city,
                        "country": city_result.country,
                        "equivalent_salary": city_result.equivalent_salary,
                        "cost_index": city_result.cost_index
                    }
                })
        
        # Sort by equivalent salary
        results.sort(key=lambda x: x.equivalent_salary)
        
        geojson = {
            "type": "FeatureCollection",
            "features": geojson_features
        }
        
        return AdvancedConversionResponse(
            source_city=request.source_city,
            source_salary=request.salary,
            currency=request.currency,
            expense_breakdown=request.expenses,
            results=results,
            geojson=geojson
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in advanced conversion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
