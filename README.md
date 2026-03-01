# gramsense-ai-prototype
# GramSense AI – Rural Market Intelligence & Decision Support Platform

GramSense AI is an AI-powered rural market intelligence platform designed to help small and marginal farmers make data-driven selling and crop planning decisions.

This prototype is being developed as part of the **AI for Bharat Hackathon – Prototype Phase**.

---

## 🚜 Problem Statement

Small and marginal farmers often lack access to real-time market intelligence, price forecasting, and decision support. This results in:

- Dependency on middlemen  
- Poor selling timing decisions  
- Post-harvest losses  
- Reduced income  

GramSense AI aims to provide explainable, AI-driven recommendations using publicly available agricultural data.

---

## 🧠 What This Prototype Demonstrates

The MVP includes:

- 📊 Real-time mandi price dashboard  
- 📈 7–14 day AI-based price forecasting  
- 💡 Explainable selling recommendations (Sell Now / Wait / Alternate Market)  
- 🌦 Weather-aware advisory logic  
- 📱 Mobile-optimized web interface  
- ☁️ AWS cloud deployment  

---

## 🏗 Architecture Overview

High-Level Flow:

User → Web Interface → Backend API →  
Data Storage (S3/DynamoDB) →  
Forecasting Model →  
Recommendation Engine →  
Bedrock (Explainable Output) → User

---

## ☁️ AWS Services Used

- **Amazon S3** – Raw dataset storage  
- **Amazon DynamoDB** – Structured price and forecast storage  
- **AWS Lambda** – Data ingestion and preprocessing  
- **Amazon SageMaker** – Forecast model execution  
- **Amazon Bedrock (Titan Text)** – Generate simplified explanations  
- **Amazon EC2** – Backend API hosting  
- **CloudWatch** – Monitoring & logs  

---

## 📂 Repository Structure
gramsense-ai-prototype/
│
├── backend/
│ ├── api/
│ ├── forecasting/
│ ├── recommendation/
│ └── data_ingestion/
│
├── frontend/
│
├── .kiro/spec/
│ ├── requirements.md
│ └── design.md
│
└── README.md


---

## 📊 Data Strategy

### Data Sources
- Agmarknet mandi price datasets
- India Meteorological Department (IMD) weather data
- Public crop calendar datasets

### Data Handling
- Raw data stored in S3
- Processed data stored in DynamoDB
- Forecasting executed via SageMaker
- No personal financial data collected
- Advisory-only AI outputs

---

## 🧪 AI Components

### 1️⃣ Price Forecasting
- Time-series forecasting (Prophet/ARIMA)
- 7–14 day predictions
- Confidence indicators

### 2️⃣ Recommendation Engine
- Combines:
  - Price trend
  - Weather signals
  - Seasonal demand
- Outputs:
  - SELL_NOW
  - WAIT
  - CONSIDER_ALTERNATE_MARKET

### 3️⃣ Explainable AI Layer
- Amazon Bedrock (Titan Text)
- Converts structured model outputs into simple advisory language
- Includes confidence and disclaimers

---

## ⚠ Responsible AI Commitments

- Only publicly available datasets
- No personal or financial data
- All recommendations include confidence levels
- Advisory system — not a financial guarantee
- Transparent data sourcing

---

## 🚀 7-Day Prototype Roadmap

Day 1–2: Backend setup and data ingestion  
Day 3–4: Forecast model integration  
Day 5: Recommendation logic  
Day 6: AWS deployment  
Day 7: Demo recording and submission  

---

## 🛠 Local Development Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Frontend
cd frontend
npm install
npm start
