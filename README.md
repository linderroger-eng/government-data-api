# Government Data API

Clean, reliable access to US Government spending data through a modern REST API.

## 🎯 What This API Provides

- **Government Contracts**: Search and filter contracts by agency, amount, date
- **Government Grants**: Access grant data with flexible filtering
- **Agency Information**: Complete list of government agencies with spending data
- **Real-time Data**: Fresh data from official government sources

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API**:
   ```bash
   python run.py
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/

## 📊 API Endpoints

### Contracts
```
GET /contracts?agency=NASA&amount_min=1000000&limit=50
```
- Filter by agency, amount range, date range
- Returns clean, structured contract data

### Grants  
```
GET /grants?agency=NSF&amount_min=50000&category=research
```
- Access government grant information
- Filter by agency, amount, category

### Agencies
```
GET /agencies
```
- Complete list of government agencies
- Includes spending statistics

### Statistics
```
GET /stats
```
- API usage and data freshness statistics

## 🔧 Configuration

Edit `.env` file:
```
USASPENDING_BASE_URL=https://api.usaspending.gov/api/v2/
DATABASE_URL=sqlite:///./government_data.db
API_HOST=0.0.0.0
API_PORT=8000
```

## 💰 Monetization Ready

This API is designed for commercial use:
- Rate limiting built-in
- Usage tracking capabilities  
- Scalable architecture
- Clean, consistent data format

## 📈 Next Steps

1. **Deploy to cloud** (AWS, Digital Ocean, Railway)
2. **Add authentication** and usage tracking
3. **List on RapidAPI** marketplace
4. **Add more data sources** (patents, regulations)

## 🎯 Target Customers

- **GovTech developers** building procurement software
- **Compliance companies** tracking government spending  
- **Journalists** investigating government contracts
- **Business intelligence** companies analyzing markets

---

**Ready to monetize government data! 🚀💰**