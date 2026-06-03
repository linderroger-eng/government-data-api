#!/usr/bin/env python3
"""
Government Data API - Revenue Tracking & Analytics
"""
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

@dataclass
class RevenueMetrics:
    date: str
    total_users: int
    free_tier_users: int
    startup_users: int
    business_users: int
    enterprise_users: int
    monthly_revenue: float
    total_requests: int
    conversion_rate: float


class RevenueTracker:
    def __init__(self, data_file="revenue_data.json"):
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """Load existing revenue data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {"metrics": [], "projections": {}}

    def _save_data(self):
        """Save revenue data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def _deduplicate(self):
        """Remove duplicate entries for the same date, keeping the latest."""
        seen = {}
        for entry in self.data["metrics"]:
            seen[entry["date"]] = entry  # last write wins
        self.data["metrics"] = sorted(seen.values(), key=lambda x: x["date"])

    def add_metrics(self, metrics: RevenueMetrics):
        """Add or update daily metrics (upsert by date)."""
        self.data["metrics"].append(asdict(metrics))
        self._deduplicate()
        self._save_data()

    def _calc_mrr(self, entry: Dict) -> float:
        """True MRR: (startup × $49) + (business × $199) + (enterprise × $499)"""
        return (
            entry.get("startup_users", 0) * 49 +
            entry.get("business_users", 0) * 199 +
            entry.get("enterprise_users", 0) * 499
        )

    def _rolling_growth_7d(self) -> Optional[float]:
        """7-day rolling revenue growth rate (%)."""
        metrics = self.data["metrics"]
        if len(metrics) < 8:
            return None
        recent = [self._calc_mrr(m) for m in metrics[-7:]]
        prior  = [self._calc_mrr(m) for m in metrics[-14:-7]]
        avg_recent = sum(recent) / len(recent)
        avg_prior  = sum(prior)  / len(prior)
        if avg_prior == 0:
            return None
        return round((avg_recent - avg_prior) / avg_prior * 100, 2)

    def calculate_projections(self) -> Dict:
        """Project next 6 months based on 7-day rolling growth."""
        metrics = self.data["metrics"]
        if len(metrics) < 7:
            return self._default_projections()

        growth_pct = self._rolling_growth_7d()
        if growth_pct is None:
            return self._default_projections()

        weekly_growth = growth_pct / 100
        current_revenue = self._calc_mrr(metrics[-1])
        projections = {}
        for month in range(1, 7):
            current_revenue *= (1 + weekly_growth * 4)
            projections[f"month_{month}"] = round(current_revenue, 2)
        return projections

    def _default_projections(self) -> Dict:
        return {
            "month_1": 500.00,
            "month_2": 1_200.00,
            "month_3": 2_500.00,
            "month_4": 4_200.00,
            "month_5": 6_800.00,
            "month_6": 10_000.00,
        }

    def get_current_status(self) -> Dict:
        """Get current revenue status with correct MRR and rolling growth."""
        if not self.data["metrics"]:
            return {
                "status": "launching",
                "monthly_revenue": 0,
                "total_users": 0,
                "growth_rate_7d": "N/A",
                "last_updated": datetime.now().isoformat(),
            }

        latest = self.data["metrics"][-1]
        true_mrr = self._calc_mrr(latest)
        rolling_growth = self._rolling_growth_7d()

        return {
            "status": "active",
            "monthly_revenue": true_mrr,
            "total_users": latest["total_users"],
            "growth_rate_7d": f"{rolling_growth:+.1f}%" if rolling_growth is not None else "Insufficient data",
            "last_updated": latest["date"],
            "projections": self.calculate_projections(),
        }


def generate_revenue_report():
    """Generate daily revenue report"""
    tracker = RevenueTracker()

    today = datetime.now().strftime("%Y-%m-%d")

    # Simulate realistic metrics (replace with real analytics when available)
    startup_users  = 25
    business_users = 4
    enterprise_users = 1
    free_users = 120

    today_metrics = RevenueMetrics(
        date=today,
        total_users=free_users + startup_users + business_users + enterprise_users,
        free_tier_users=free_users,
        startup_users=startup_users,
        business_users=business_users,
        enterprise_users=enterprise_users,
        monthly_revenue=startup_users * 49 + business_users * 199 + enterprise_users * 499,
        total_requests=45_000,
        conversion_rate=round((startup_users + business_users + enterprise_users) /
                               (free_users + startup_users + business_users + enterprise_users) * 100, 1)
    )

    tracker.add_metrics(today_metrics)
    status = tracker.get_current_status()

    print("🏛️ GOVERNMENT DATA API - REVENUE REPORT")
    print("=" * 50)
    print(f"📅 Date: {today}")
    print(f"💰 True MRR: ${status['monthly_revenue']:,.2f}")
    print(f"👥 Total Users: {status['total_users']:,}")
    print(f"📈 7-Day Rolling Growth: {status['growth_rate_7d']}")
    print(f"🔄 Conversion Rate: {today_metrics.conversion_rate}%")
    print()
    print("📊 USER BREAKDOWN:")
    print(f"   🆓 Free Tier:          {today_metrics.free_tier_users} users")
    print(f"   🥉 Startup   ($49):    {today_metrics.startup_users} users  → ${today_metrics.startup_users * 49:,}")
    print(f"   🥈 Business  ($199):   {today_metrics.business_users} users  → ${today_metrics.business_users * 199:,}")
    print(f"   🥇 Enterprise($499):   {today_metrics.enterprise_users} user  → ${today_metrics.enterprise_users * 499:,}")
    print()
    print("🎯 6-MONTH PROJECTIONS:")
    for month, revenue in status["projections"].items():
        month_num = month.split("_")[1]
        print(f"   Month {month_num}: ${revenue:,.2f}")
    print()
    print(f"🚀 Target: $5,000/month by Month 3")
    print(f"💎 Stretch Goal: $15,000/month by Month 6")


if __name__ == "__main__":
    generate_revenue_report()
