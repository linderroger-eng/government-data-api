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
    
    def add_metrics(self, metrics: RevenueMetrics):
        """Add daily metrics"""
        self.data["metrics"].append(asdict(metrics))
        self._save_data()
    
    def calculate_projections(self) -> Dict:
        """Calculate revenue projections based on growth"""
        if not self.data["metrics"]:
            return self._default_projections()
        
        # Get recent growth trends
        recent_metrics = self.data["metrics"][-30:]  # Last 30 days
        if len(recent_metrics) < 7:
            return self._default_projections()
        
        # Calculate growth rates
        first_week = recent_metrics[:7]
        last_week = recent_metrics[-7:]
        
        avg_first_revenue = sum(m["monthly_revenue"] for m in first_week) / len(first_week)
        avg_last_revenue = sum(m["monthly_revenue"] for m in last_week) / len(last_week)
        
        weekly_growth = (avg_last_revenue - avg_first_revenue) / avg_first_revenue if avg_first_revenue > 0 else 0.1
        
        # Project next 6 months
        current_revenue = avg_last_revenue
        projections = {}
        
        for month in range(1, 7):
            current_revenue *= (1 + weekly_growth * 4)  # 4 weeks per month
            projections[f"month_{month}"] = round(current_revenue, 2)
        
        return projections
    
    def _default_projections(self) -> Dict:
        """Default projections for new API"""
        return {
            "month_1": 500.00,
            "month_2": 1200.00,
            "month_3": 2500.00,
            "month_4": 4200.00,
            "month_5": 6800.00,
            "month_6": 10000.00
        }
    
    def get_current_status(self) -> Dict:
        """Get current revenue status"""
        if not self.data["metrics"]:
            return {
                "status": "launching",
                "monthly_revenue": 0,
                "total_users": 0,
                "growth_rate": "N/A",
                "last_updated": datetime.now().isoformat()
            }
        
        latest = self.data["metrics"][-1]
        
        # Calculate growth rate
        if len(self.data["metrics"]) >= 30:
            month_ago = self.data["metrics"][-30]
            growth_rate = ((latest["monthly_revenue"] - month_ago["monthly_revenue"]) / month_ago["monthly_revenue"] * 100) if month_ago["monthly_revenue"] > 0 else 0
        else:
            growth_rate = "Insufficient data"
        
        return {
            "status": "active",
            "monthly_revenue": latest["monthly_revenue"],
            "total_users": latest["total_users"],
            "growth_rate": f"{growth_rate:.1f}%" if isinstance(growth_rate, (int, float)) else growth_rate,
            "last_updated": latest["date"],
            "projections": self.calculate_projections()
        }

def generate_revenue_report():
    """Generate daily revenue report"""
    tracker = RevenueTracker()
    
    # Simulate current metrics (in production, this would come from your API analytics)
    today_metrics = RevenueMetrics(
        date=datetime.now().strftime("%Y-%m-%d"),
        total_users=150,          # Total API users
        free_tier_users=120,      # Free tier
        startup_users=25,         # $49/month
        business_users=4,         # $199/month  
        enterprise_users=1,       # $499/month
        monthly_revenue=49*25 + 199*4 + 499*1,  # Calculate revenue
        total_requests=45000,     # Total API requests today
        conversion_rate=20.0      # Free to paid conversion %
    )
    
    tracker.add_metrics(today_metrics)
    status = tracker.get_current_status()
    
    print("🏛️ GOVERNMENT DATA API - REVENUE REPORT")
    print("=" * 50)
    print(f"📅 Date: {today_metrics.date}")
    print(f"💰 Monthly Revenue: ${status['monthly_revenue']:,.2f}")
    print(f"👥 Total Users: {status['total_users']:,}")
    print(f"📈 Growth Rate: {status['growth_rate']}")
    print(f"🔄 Conversion Rate: {today_metrics.conversion_rate}%")
    print()
    print("📊 USER BREAKDOWN:")
    print(f"   🆓 Free Tier: {today_metrics.free_tier_users} users")
    print(f"   🥉 Startup ($49): {today_metrics.startup_users} users")
    print(f"   🥈 Business ($199): {today_metrics.business_users} users") 
    print(f"   🥇 Enterprise ($499): {today_metrics.enterprise_users} users")
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