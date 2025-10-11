"""
Real-time web scraping service for Indian bank loan data
"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timedelta
from app.models.loan_recommendation import LoanData

class WebScraperService:
    """Scrape loan data from Indian bank websites"""
    
    @staticmethod
    async def scrape_sbi_loans(loan_type: str) -> Optional[Dict[str, Any]]:
        """Scrape SBI loan data"""
        try:
            url_map = {
                "personal": "https://sbi.co.in/web/personal-banking/loans/personal-loans",
                "home": "https://sbi.co.in/web/personal-banking/loans/home-loans",
                "car": "https://sbi.co.in/web/personal-banking/loans/car-loans",
                "education": "https://sbi.co.in/web/personal-banking/loans/education-loans",
                "gold": "https://sbi.co.in/web/personal-banking/loans/gold-loans"
            }
            
            url = url_map.get(loan_type)
            if not url:
                return None
            
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code != 200:
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract interest rate (adapt selectors based on actual HTML)
                rate_text = soup.find(text=re.compile(r'interest rate', re.I))
                rate_match = re.search(r'(\d+\.?\d*)\s*%', str(rate_text)) if rate_text else None
                
                # Extract loan amount
                amount_text = soup.find(text=re.compile(r'loan amount|maximum', re.I))
                amount_match = re.search(r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|crore)?', str(amount_text)) if amount_text else None
                
                return {
                    "lender_name": f"SBI {loan_type.title()} Loan",
                    "loan_type": loan_type,
                    "interest_rate_min": float(rate_match.group(1)) if rate_match else None,
                    "source_url": url,
                    "scraped_at": datetime.utcnow()
                }
                
        except Exception as e:
            print(f"Error scraping SBI: {str(e)}")
            return None
    
    @staticmethod
    async def scrape_all_banks(loan_type: str) -> List[Dict[str, Any]]:
        """Scrape loan data from all banks"""
        scraped_data = []
        
        # Try to scrape SBI
        sbi_data = await WebScraperService.scrape_sbi_loans(loan_type)
        if sbi_data and sbi_data.get("interest_rate_min"):
            scraped_data.append(sbi_data)
        
        # Add more banks here with similar scraping logic
        # For now, if scraping fails, we'll use cached/fallback data
        
        return scraped_data
    
    @staticmethod
    async def get_or_scrape_loan_data(loan_type: str, amount: float) -> List[Dict[str, Any]]:
        """Get loan data from cache or scrape fresh data"""
        
        # Check if we have recent cached data (less than 24 hours old)
        cached_data = await LoanData.find({
            "loan_type": loan_type,
            "is_active": True,
            "scraped_at": {"$gte": datetime.utcnow() - timedelta(hours=24)},
            "min_amount": {"$lte": amount},
            "max_amount": {"$gte": amount}
        }).to_list()
        
        if cached_data and len(cached_data) >= 3:
            # Return cached data if we have enough recent data
            return [loan.to_dict() for loan in cached_data]
        
        # Otherwise scrape fresh data
        print(f"Scraping fresh loan data for {loan_type}...")
        scraped_loans = await WebScraperService.scrape_all_banks(loan_type)
        
        # If scraping successful, save to database
        if scraped_loans:
            for loan_data in scraped_loans:
                if loan_data.get("interest_rate_min"):
                    # Save to database
                    new_loan = LoanData(**loan_data)
                    await new_loan.insert()
        
        # Combine scraped data with fallback realistic data
        from app.services.loan_service import LoanService
        fallback_data = LoanService.get_realistic_indian_loan_data(loan_type)
        
        # Use scraped rates if available, otherwise use fallback
        if scraped_loans and any(loan.get("interest_rate_min") for loan in scraped_loans):
            return scraped_loans + fallback_data[:7]  # Mix scraped with some fallback
        
        return fallback_data  # Use all fallback if scraping failed