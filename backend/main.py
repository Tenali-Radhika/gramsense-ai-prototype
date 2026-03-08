from fastapi import FastAPI

from .api import prices, forecast, recommendation
from .aws_integration import get_aws_service

app = FastAPI(title="GramSense AI", description="Rural Market Intelligence Platform")

# include routers
app.include_router(prices.router)
app.include_router(forecast.router)
app.include_router(recommendation.router)

@app.get("/")
def root():
    return {"message": "GramSense AI Prototype Running"}

@app.get("/health")
def health():
    aws_status = "configured" if get_aws_service().s3_client else "not configured"
    return {
        "status": "ok",
        "aws_integration": aws_status,
        "version": "1.0.0"
    }