# Government Contracts & Grants API

![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![Version](https://img.shields.io/badge/version-2.0.0-blue) ![License](https://img.shields.io/badge/license-MIT-green) [![RapidAPI](https://img.shields.io/badge/RapidAPI-Subscribe-orange?logo=rapid)](https://rapidapi.com/linderroger-eng/api/government-contracts-grants-api1)

**Live U.S. federal contracts and grants data sourced directly from USASpending.gov — search by agency, keyword, or funding type.**

## ✨ Key Features

- 🏛️ **Real Federal Contract Data** — Up-to-date awards from DOD, NASA, DHS, and 200+ federal agencies sourced from USASpending.gov
- 💡 **Keyword-Powered Grant Search** — Find active grant opportunities by topic (AI, climate, infrastructure, and more)
- 🏢 **Agency Directory** — Browse all federal agencies issuing contracts and grants with metadata
- ⚡ **Pagination & Filtering** — Limit results, filter by agency code, and drill into specific award details

## 🚀 Quick Start

```bash
# 1. Health check — verify the API is live
curl -s https://government-data-api.onrender.com/health

# 2. Get recent DOD contracts (limit 10)
curl -s "https://government-data-api.onrender.com/contracts?agency=DOD&limit=10"

# 3. Search for AI-related grants
curl -s "https://government-data-api.onrender.com/grants?keyword=AI&limit=10"

# 4. List all federal agencies
curl -s "https://government-data-api.onrender.com/agencies"
```

> **With RapidAPI key** — add `-H "X-RapidAPI-Key: YOUR_KEY"` to each request.

## 📡 All Endpoints

| Method | Path | Description | Example Params |
|--------|------|-------------|----------------|
| GET | `/health` | API status and uptime check | — |
| GET | `/contracts` | Federal contract awards, filterable by agency | `?agency=DOD&limit=10` |
| GET | `/grants` | Federal grant awards, searchable by keyword | `?keyword=AI&limit=10` |
| GET | `/agencies` | Directory of all federal contracting agencies | — |

> **Note:** All endpoints return JSON. Use `limit` (max 100) and `offset` for pagination. Agency codes follow USASpending.gov conventions (e.g., `DOD`, `NASA`, `DHS`, `HHS`).

## 🐍 Python Example

```python
import requests

BASE_URL = "https://government-data-api.onrender.com"
HEADERS = {"X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY"}

# Search for AI-related grants
grants = requests.get(
    f"{BASE_URL}/grants",
    params={"keyword": "artificial intelligence", "limit": 5},
    headers=HEADERS
)
for grant in grants.json().get("results", []):
    print(grant.get("Award ID"), "-", grant.get("Recipient Name"), "-", grant.get("Award Amount"))

# Get recent Department of Defense contracts
contracts = requests.get(
    f"{BASE_URL}/contracts",
    params={"agency": "DOD", "limit": 5},
    headers=HEADERS
)
for contract in contracts.json().get("results", []):
    print(contract.get("Award ID"), "-", contract.get("Description"))

# List all agencies
agencies = requests.get(f"{BASE_URL}/agencies", headers=HEADERS)
print(f"Total agencies: {len(agencies.json())}")
```

## 💳 Pricing Tiers

| Plan | Price | Requests / Month | Features |
|------|-------|-----------------|----------|
| **BASIC** | Free | Unlimited* | All endpoints, no credit card |
| **PRO** | $49 / mo | High volume | Priority support, faster response |
| **ULTRA** | $149 / mo | Bulk access | SLA, bulk filtering, custom params |
| **MEGA** | $499 / mo | Enterprise | Dedicated support, max throughput |

*Fair use policy applies on free tier.

## 🔗 RapidAPI Listing

Subscribe and manage your API key at:
👉 **[https://rapidapi.com/linderroger-eng/api/government-contracts-grants-api1](https://rapidapi.com/linderroger-eng/api/government-contracts-grants-api1)**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push and open a Pull Request

Bug reports and feature requests are welcome via [GitHub Issues](https://github.com/linderroger-eng/government-data-api/issues).

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ by [linderroger-eng](https://github.com/linderroger-eng) · Powered by [USASpending.gov](https://www.usaspending.gov/) public data*
