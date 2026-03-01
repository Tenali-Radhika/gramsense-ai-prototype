from fastapi import FastAPI

from .api import prices, forecast, recommendation

app = FastAPI()

# include routers
app.include_router(prices.router)
app.include_router(forecast.router)
app.include_router(recommendation.router)

@app.get("/")
def root():
    return {"message": "GramSense AI Prototype Running"}

@app.get("/health")
def health():
    return {"status": "ok"}