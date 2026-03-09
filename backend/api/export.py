"""
Data export API endpoints.
Allows users to export price data, forecasts, and recommendations in various formats.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import csv
import json
import io
from datetime import datetime

from models import Location
from data_ingestion import fetch_mandi_prices, fetch_historical_prices
from forecasting.engine import generate_price_forecast
from recommendation.engine import generate_selling_recommendation

router = APIRouter()


def generate_csv(data: list, headers: list) -> str:
    """Generate CSV string from data."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data)
    return output.getvalue()


@router.get("/export/prices/csv")
def export_prices_csv(crop: str, lat: float, lon: float, days: int = 30):
    """Export price data as CSV file."""
    try:
        loc = Location(latitude=lat, longitude=lon)
        prices = fetch_historical_prices(crop, loc, days=days)
        
        # Prepare data for CSV
        headers = ["Date", "Crop", "Market", "Price (INR/quintal)", "Quality", "Source"]
        rows = [
            [
                p.timestamp.strftime("%Y-%m-%d"),
                p.crop,
                p.market,
                p.price,
                p.quality,
                p.source
            ]
            for p in prices
        ]
        
        csv_content = generate_csv(rows, headers)
        
        # Create filename
        filename = f"gramsense_prices_{crop}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/prices/json")
def export_prices_json(crop: str, lat: float, lon: float, days: int = 30):
    """Export price data as JSON file."""
    try:
        loc = Location(latitude=lat, longitude=lon)
        prices = fetch_historical_prices(crop, loc, days=days)
        
        # Convert to JSON-serializable format
        data = {
            "crop": crop,
            "location": {"latitude": lat, "longitude": lon},
            "export_date": datetime.now().isoformat(),
            "data_points": len(prices),
            "prices": [
                {
                    "date": p.timestamp.isoformat(),
                    "crop": p.crop,
                    "market": p.market,
                    "price": p.price,
                    "unit": p.unit,
                    "quality": p.quality,
                    "source": p.source
                }
                for p in prices
            ]
        }
        
        json_content = json.dumps(data, indent=2)
        filename = f"gramsense_prices_{crop}_{datetime.now().strftime('%Y%m%d')}.json"
        
        return StreamingResponse(
            iter([json_content]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/forecast/csv")
def export_forecast_csv(crop: str, lat: float, lon: float, horizon: int = 30):
    """Export forecast data as CSV file."""
    try:
        loc = Location(latitude=lat, longitude=lon)
        forecast = generate_price_forecast(crop, loc, horizon_days=horizon)
        
        # Prepare data for CSV
        headers = ["Date", "Predicted Price (INR/quintal)", "Confidence", "Lower Bound", "Upper Bound"]
        rows = [
            [
                p.date.strftime("%Y-%m-%d"),
                p.price,
                f"{p.confidence * 100:.1f}%" if p.confidence else "N/A",
                p.price * 0.95,  # Approximate bounds
                p.price * 1.05
            ]
            for p in forecast.predictions
        ]
        
        csv_content = generate_csv(rows, headers)
        filename = f"gramsense_forecast_{crop}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/forecast/json")
def export_forecast_json(crop: str, lat: float, lon: float, horizon: int = 30):
    """Export forecast data as JSON file."""
    try:
        loc = Location(latitude=lat, longitude=lon)
        forecast = generate_price_forecast(crop, loc, horizon_days=horizon)
        
        # Convert to JSON-serializable format
        data = {
            "crop": crop,
            "location": {"latitude": lat, "longitude": lon},
            "export_date": datetime.now().isoformat(),
            "forecast_horizon_days": horizon,
            "confidence_level": forecast.confidenceLevel,
            "methodology": forecast.methodology,
            "predictions": [
                {
                    "date": p.date.isoformat(),
                    "price": p.price,
                    "confidence": p.confidence
                }
                for p in forecast.predictions
            ],
            "factors": [
                {
                    "name": f.name,
                    "impact": f.impact,
                    "description": f.description
                }
                for f in forecast.factors
            ]
        }
        
        json_content = json.dumps(data, indent=2)
        filename = f"gramsense_forecast_{crop}_{datetime.now().strftime('%Y%m%d')}.json"
        
        return StreamingResponse(
            iter([json_content]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/recommendation/json")
def export_recommendation_json(crop: str, lat: float, lon: float, quantity: float):
    """Export recommendation as JSON file."""
    try:
        loc = Location(latitude=lat, longitude=lon)
        rec = generate_selling_recommendation(crop, loc, quantity)
        
        # Convert to JSON-serializable format
        data = {
            "crop": crop,
            "location": {"latitude": lat, "longitude": lon},
            "quantity": quantity,
            "export_date": datetime.now().isoformat(),
            "recommendation": {
                "type": rec.type,
                "priority": rec.priority,
                "explanation": rec.explanation,
                "confidence": rec.confidence,
                "supporting_data": rec.supportingData,
                "disclaimers": rec.disclaimers
            }
        }
        
        json_content = json.dumps(data, indent=2)
        filename = f"gramsense_recommendation_{crop}_{datetime.now().strftime('%Y%m%d')}.json"
        
        return StreamingResponse(
            iter([json_content]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/report/json")
def export_full_report_json(crop: str, lat: float, lon: float, quantity: float = 100):
    """Export complete market intelligence report as JSON."""
    try:
        loc = Location(latitude=lat, longitude=lon)
        
        # Gather all data
        prices = fetch_historical_prices(crop, loc, days=30)
        forecast = generate_price_forecast(crop, loc, horizon_days=30)
        recommendation = generate_selling_recommendation(crop, loc, quantity)
        
        # Create comprehensive report
        data = {
            "report_title": "GramSense AI Market Intelligence Report",
            "crop": crop,
            "location": {"latitude": lat, "longitude": lon},
            "quantity": quantity,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "current_price": prices[0].price if prices else None,
                "30_day_average": sum(p.price for p in prices) / len(prices) if prices else None,
                "forecast_trend": "increasing" if forecast.predictions[-1].price > prices[0].price else "decreasing",
                "recommendation": recommendation.type
            },
            "historical_prices": {
                "data_points": len(prices),
                "prices": [
                    {
                        "date": p.timestamp.isoformat(),
                        "price": p.price,
                        "market": p.market
                    }
                    for p in prices[:10]  # Last 10 days
                ]
            },
            "forecast": {
                "horizon_days": 30,
                "confidence": forecast.confidenceLevel,
                "predictions": [
                    {
                        "date": p.date.isoformat(),
                        "price": p.price
                    }
                    for p in forecast.predictions[:7]  # Next 7 days
                ]
            },
            "recommendation": {
                "action": recommendation.type,
                "priority": recommendation.priority,
                "explanation": recommendation.explanation,
                "confidence": recommendation.confidence
            },
            "disclaimers": [
                "This report is for informational purposes only",
                "Actual market prices may vary",
                "Consult local market experts before making decisions",
                "GramSense AI is not responsible for financial losses"
            ]
        }
        
        json_content = json.dumps(data, indent=2)
        filename = f"gramsense_report_{crop}_{datetime.now().strftime('%Y%m%d')}.json"
        
        return StreamingResponse(
            iter([json_content]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
