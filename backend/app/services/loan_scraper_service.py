# app/services/loan_scraper_service.py
import httpx
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import re
from datetime import datetime


class LoanScraperService:
    """Service to scrape real-time loan interest rates from Indian bank websites"""
    
    # Bank websites to scrape
    BANK_URLS = {
        'personal': {
            'SBI': 'https://sbi.co.in/web/personal-banking/loans/personal-loan',
            'HDFC': 'https://www.hdfcbank.com/personal/borrow/popular-loans/personal-loan',
            'ICICI': 'https://www.icicibank.com/personal-banking/loans/personal-loan',
            'Axis': 'https://www.axisbank.com/retail/loans/personal-loan',
            'Kotak': 'https://www.kotak.com/en/personal-banking/loans/personal-loan.html'
        },
        'home': {
            'SBI': 'https://sbi.co.in/web/personal-banking/loans/home-loans',
            'HDFC': 'https://www.hdfcbank.com/personal/borrow/popular-loans/home-loan',
            'ICICI': 'https://www.icicibank.com/personal-banking/loans/home-loan',
            'Axis': 'https://www.axisbank.com/retail/loans/home-loan',
            'Kotak': 'https://www.kotak.com/en/personal-banking/loans/home-loan.html'
        },
        'car': {
            'SBI': 'https://sbi.co.in/web/personal-banking/loans/auto-loans',
            'HDFC': 'https://www.hdfcbank.com/personal/borrow/popular-loans/car-loan',
            'ICICI': 'https://www.icicibank.com/personal-banking/loans/car-loan',
            'Axis': 'https://www.axisbank.com/retail/loans/car-loan',
            'Kotak': 'https://www.kotak.com/en/personal-banking/loans/car-loan.html'
        },
        'education': {
            'SBI': 'https://sbi.co.in/web/personal-banking/loans/education-loans',
            'HDFC': 'https://www.hdfcbank.com/personal/borrow/popular-loans/education-loan',
            'ICICI': 'https://www.icicibank.com/personal-banking/loans/education-loan',
            'Axis': 'https://www.axisbank.com/retail/loans/education-loan',
            'Kotak': 'https://www.kotak.com/en/personal-banking/loans/education-loan.html'
        },
        'business': {
            'SBI': 'https://sbi.co.in/web/business/loans/business-loan',
            'HDFC': 'https://www.hdfcbank.com/sme/borrow/business-loan',
            'ICICI': 'https://www.icicibank.com/business-banking/loans/business-loan',
            'Axis': 'https://www.axisbank.com/corporate/product/loans/business-loan',
            'Kotak': 'https://www.kotak.com/en/business-banking/loans/business-loan.html'
        }
    }
    
    @staticmethod
    async def scrape_bank_rates(loan_type: str) -> List[Dict[str, Any]]:
        """Scrape loan rates from multiple banks"""
        
        if loan_type not in LoanScraperService.BANK_URLS:
            loan_type = 'personal'  # default
        
        banks_to_scrape = LoanScraperService.BANK_URLS[loan_type]
        scraped_data = []
        
        for bank_name, url in banks_to_scrape.items():
            try:
                bank_data = await LoanScraperService._scrape_single_bank(
                    bank_name, 
                    url, 
                    loan_type
                )
                if bank_data:
                    scraped_data.append(bank_data)
            except Exception as e:
                print(f"Error scraping {bank_name}: {e}")
                # Add fallback data if scraping fails
                scraped_data.append(
                    LoanScraperService._get_fallback_data(bank_name, loan_type)
                )
        
        return scraped_data
    
    @staticmethod
    async def _scrape_single_bank(
        bank_name: str, 
        url: str, 
        loan_type: str
    ) -> Optional[Dict[str, Any]]:
        """Scrape a single bank's website for loan information"""
        
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"{bank_name} returned status {response.status_code}")
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract interest rate (look for common patterns)
                interest_rate = LoanScraperService._extract_interest_rate(soup, bank_name)
                
                # Extract processing fee
                processing_fee = LoanScraperService._extract_processing_fee(soup, bank_name)
                
                # Extract max loan amount
                max_amount = LoanScraperService._extract_max_amount(soup, bank_name, loan_type)
                
                # Extract tenure
                tenure = LoanScraperService._extract_tenure(soup, bank_name)
                
                return {
                    'bank_name': bank_name,
                    'interest_rate': interest_rate,
                    'processing_fee': processing_fee,
                    'max_amount': max_amount,
                    'tenure': tenure,
                    'url': url,
                    'scraped_at': datetime.utcnow().isoformat(),
                    'loan_type': loan_type
                }
                
        except Exception as e:
            print(f"Error scraping {bank_name}: {e}")
            return None
    
    @staticmethod
    def _extract_interest_rate(soup: BeautifulSoup, bank_name: str) -> str:
        """Extract interest rate from HTML"""
        
        # Common patterns for interest rates
        patterns = [
            r'(\d+\.?\d*)\s*%\s*(?:p\.?a\.?|per\s+annum|onwards)',
            r'(?:rate|interest|ROI).*?(\d+\.?\d*)\s*%',
            r'(\d+\.?\d*)\s*%\s*-\s*(\d+\.?\d*)\s*%'
        ]
        
        text = soup.get_text()
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Range pattern
                    return f"{match.group(1)}% - {match.group(2)}%"
                else:
                    return f"{match.group(1)}%"
        
        # Look in meta tags
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            for pattern in patterns:
                match = re.search(pattern, meta_desc.get('content', ''), re.IGNORECASE)
                if match:
                    return f"{match.group(1)}%"
        
        return "Rate not found - check website"
    
    @staticmethod
    def _extract_processing_fee(soup: BeautifulSoup, bank_name: str) -> str:
        """Extract processing fee from HTML"""
        
        patterns = [
            r'processing\s+fee.*?₹\s*(\d+(?:,\d+)*)',
            r'processing\s+fee.*?(\d+\.?\d*)\s*%',
            r'₹\s*(\d+(?:,\d+)*)\s*(?:processing|fee)'
        ]
        
        text = soup.get_text()
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Check website"
    
    @staticmethod
    def _extract_max_amount(soup: BeautifulSoup, bank_name: str, loan_type: str) -> str:
        """Extract maximum loan amount"""
        
        patterns = [
            r'(?:up\s+to|upto|maximum).*?₹\s*(\d+(?:,\d+)*)\s*(?:lakh|crore)?',
            r'₹\s*(\d+(?:,\d+)*)\s*(?:lakh|crore)',
            r'(\d+)\s*(?:lakh|crore)'
        ]
        
        text = soup.get_text()
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Defaults based on loan type
        defaults = {
            'personal': '₹25 lakhs',
            'home': '₹5 crores',
            'car': '₹50 lakhs',
            'education': '₹1 crore',
            'business': '₹10 crores'
        }
        return defaults.get(loan_type, 'Check website')
    
    @staticmethod
    def _extract_tenure(soup: BeautifulSoup, bank_name: str) -> str:
        """Extract loan tenure"""
        
        patterns = [
            r'(?:tenure|period).*?(\d+)\s*(?:years?|months?)',
            r'(\d+)\s*(?:years?|months?)\s*(?:tenure|period)',
            r'up\s+to\s+(\d+)\s*years?'
        ]
        
        text = soup.get_text()
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Check website"
    
    @staticmethod
    def _get_fallback_data(bank_name: str, loan_type: str) -> Dict[str, Any]:
        """Fallback data if scraping fails - uses approximate current market rates"""
        
        # Approximate rates as of 2025 (fallback only)
        fallback_rates = {
            'personal': {
                'SBI': {'rate': '10.50% - 15.50%', 'fee': '₹10,000 + GST', 'max': '₹20 lakhs', 'tenure': '6-5 years'},
                'HDFC': {'rate': '10.75% - 21.00%', 'fee': '2.50% of loan amount', 'max': '₹40 lakhs', 'tenure': '1-5 years'},
                'ICICI': {'rate': '10.75% - 19.00%', 'fee': '2.00% of loan amount', 'max': '₹50 lakhs', 'tenure': '1-5 years'},
                'Axis': {'rate': '10.49% onwards', 'fee': '2.00% of loan amount', 'max': '₹40 lakhs', 'tenure': '1-5 years'},
                'Kotak': {'rate': '10.99% onwards', 'fee': '2.50% of loan amount', 'max': '₹35 lakhs', 'tenure': '1-5 years'}
            },
            'home': {
                'SBI': {'rate': '8.50% - 9.65%', 'fee': '₹10,000 + GST', 'max': '₹7.5 crores', 'tenure': '30 years'},
                'HDFC': {'rate': '8.60% - 9.50%', 'fee': '0.50% of loan amount', 'max': '₹10 crores', 'tenure': '30 years'},
                'ICICI': {'rate': '8.75% - 9.45%', 'fee': '0.50% of loan amount', 'max': '₹10 crores', 'tenure': '30 years'},
                'Axis': {'rate': '8.75% - 9.40%', 'fee': '1.00% of loan amount', 'max': '₹5 crores', 'tenure': '30 years'},
                'Kotak': {'rate': '8.70% onwards', 'fee': '0.50% of loan amount', 'max': '₹10 crores', 'tenure': '20 years'}
            },
            'car': {
                'SBI': {'rate': '8.70% - 9.70%', 'fee': '₹5,000 + GST', 'max': '₹1 crore', 'tenure': '7 years'},
                'HDFC': {'rate': '8.75% onwards', 'fee': '2.50% of loan amount', 'max': '₹75 lakhs', 'tenure': '7 years'},
                'ICICI': {'rate': '8.75% onwards', 'fee': '2.00% of loan amount', 'max': '₹1 crore', 'tenure': '7 years'},
                'Axis': {'rate': '8.80% onwards', 'fee': '2.00% of loan amount', 'max': '₹75 lakhs', 'tenure': '7 years'},
                'Kotak': {'rate': '9.00% onwards', 'fee': '2.50% of loan amount', 'max': '₹50 lakhs', 'tenure': '7 years'}
            },
            'education': {
                'SBI': {'rate': '9.55% onwards', 'fee': 'Nil', 'max': '₹1.5 crores', 'tenure': '15 years'},
                'HDFC': {'rate': '9.50% onwards', 'fee': 'Nil', 'max': '₹1 crore', 'tenure': '15 years'},
                'ICICI': {'rate': '10.00% onwards', 'fee': 'Nil', 'max': '₹1 crore', 'tenure': '15 years'},
                'Axis': {'rate': '13.70% onwards', 'fee': '1.00% of loan amount', 'max': '₹75 lakhs', 'tenure': '15 years'},
                'Kotak': {'rate': '10.00% onwards', 'fee': 'Nil', 'max': '₹75 lakhs', 'tenure': '10 years'}
            },
            'business': {
                'SBI': {'rate': '9.00% - 12.00%', 'fee': '1.00% of loan amount', 'max': '₹10 crores', 'tenure': '10 years'},
                'HDFC': {'rate': '11.00% onwards', 'fee': '2.00% of loan amount', 'max': '₹50 lakhs', 'tenure': '5 years'},
                'ICICI': {'rate': '11.25% onwards', 'fee': '2.00% of loan amount', 'max': '₹1 crore', 'tenure': '5 years'},
                'Axis': {'rate': '11.00% onwards', 'fee': '2.00% of loan amount', 'max': '₹75 lakhs', 'tenure': '5 years'},
                'Kotak': {'rate': '11.50% onwards', 'fee': '2.50% of loan amount', 'max': '₹1 crore', 'tenure': '5 years'}
            }
        }
        
        data = fallback_rates.get(loan_type, {}).get(bank_name, {})
        
        return {
            'bank_name': bank_name,
            'interest_rate': data.get('rate', 'Contact bank'),
            'processing_fee': data.get('fee', 'Contact bank'),
            'max_amount': data.get('max', 'Contact bank'),
            'tenure': data.get('tenure', 'Contact bank'),
            'url': LoanScraperService.BANK_URLS.get(loan_type, {}).get(bank_name, ''),
            'scraped_at': datetime.utcnow().isoformat(),
            'loan_type': loan_type,
            'is_fallback': True
        }
    
    @staticmethod
    def format_scraped_data_for_llm(scraped_data: List[Dict[str, Any]]) -> str:
        """Format scraped data into text for LLM"""
        
        if not scraped_data:
            return "No bank data available"
        
        formatted = "REAL-TIME BANK LOAN RATES (Scraped from bank websites):\n\n"
        
        for idx, bank in enumerate(scraped_data, 1):
            formatted += f"{idx}. {bank['bank_name']}:\n"
            formatted += f"   - Interest Rate: {bank['interest_rate']}\n"
            formatted += f"   - Processing Fee: {bank['processing_fee']}\n"
            formatted += f"   - Max Loan Amount: {bank['max_amount']}\n"
            formatted += f"   - Tenure: {bank['tenure']}\n"
            
            if bank.get('is_fallback'):
                formatted += f"   - Note: Using approximate rates (website scraping failed)\n"
            else:
                formatted += f"   - Data Source: Scraped from {bank['url']}\n"
            
            formatted += f"   - Last Updated: {bank['scraped_at']}\n\n"
        
        return formatted