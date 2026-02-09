from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class CityResult(BaseModel):
    """Result for a single city"""
    city: str
    country: str
    equivalent_salary: float
    cost_index: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BasicConversionResponse(BaseModel):
    """Response for basic conversion"""
    source_city: str
    source_salary: float
    currency: str
    results: List[CityResult]
    geojson: Dict


class ExpenseBreakdown(BaseModel):
    """Expense breakdown by category"""
    rent: float = Field(ge=0, description="Monthly rent expenses")
    food: float = Field(ge=0, description="Monthly food expenses")
    transport: float = Field(ge=0, description="Monthly transport expenses")
    utilities: float = Field(ge=0, description="Monthly utilities expenses")
    entertainment: float = Field(ge=0, description="Monthly entertainment expenses")


class AdvancedConversionRequest(BaseModel):
    """Request for advanced conversion"""
    salary: float = Field(gt=0, description="Annual salary in source city")
    source_city: str = Field(description="Source city name")
    currency: str = Field(default="USD", description="Currency code")
    expenses: ExpenseBreakdown


class AdvancedConversionResponse(BaseModel):
    """Response for advanced conversion"""
    source_city: str
    source_salary: float
    currency: str
    expense_breakdown: ExpenseBreakdown
    results: List[CityResult]
    geojson: Dict
