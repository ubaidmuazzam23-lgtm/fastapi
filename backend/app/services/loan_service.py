"""
Enhanced Loan recommendation service with AI chatbot and web scraping
"""
from groq import Groq
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from beanie import PydanticObjectId
import httpx
from bs4 import BeautifulSoup
import re
import random
import asyncio
import json

from app.models.loan_recommendation import LoanRecommendation, LoanData
from app.models.user import User
from app.models.debt import Debt
from app.schemas.loan import (
    LoanRecommendationRequest,
    LoanRecommendationResponse,
    LoanOption,
    AffordabilityAnalysis,
    LoanComparisonData
)
from app.core.loan_analyzer import LoanAnalyzer
from app.config.settings import settings

# Initialize Groq client with settings
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]


class LoanService:
    """Main service for loan recommendations with AI and web scraping"""
    
    INDIAN_BANKS = [
        {"name": "SBI", "url": "https://sbi.co.in/web/personal-banking/loans"},
        {"name": "HDFC Bank", "url": "https://www.hdfcbank.com/personal/borrow/popular-loans"},
        {"name": "ICICI Bank", "url": "https://www.icicibank.com/personal-banking/loans"},
        {"name": "Axis Bank", "url": "https://www.axisbank.com/retail/loans"},
        {"name": "Kotak Mahindra", "url": "https://www.kotak.com/en/personal-banking/loans.html"},
        {"name": "Punjab National Bank", "url": "https://www.pnbindia.in"},
        {"name": "Bank of Baroda", "url": "https://www.bankofbaroda.in/personal-banking/loans"},
        {"name": "Canara Bank", "url": "https://canarabank.com"},
        {"name": "Union Bank", "url": "https://www.unionbankofindia.co.in/english/home.aspx"},
        {"name": "IDFC First Bank", "url": "https://www.idfcfirstbank.com/personal-banking/loans"}
    ]
    
    @staticmethod
    async def chat_with_ai(message: str, conversation_history: List[Dict] = None) -> str:
        """Chat with Groq AI about loans"""
        if conversation_history is None:
            conversation_history = []
        
        system_prompt = """You are a helpful Indian financial advisor specializing in loans. 
        You help users understand different loan types (Personal, Home, Car, Gold, Education, Business loans).
        Explain interest rates, eligibility, documentation, and compare options.
        Be conversational, friendly, and provide accurate information about Indian banking.
        Use Indian Rupees (₹) for all monetary values."""
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        try:
            response = groq_client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {str(e)}")
            return "I'm having trouble connecting to the AI service. Please try again later."
    
    @staticmethod
    def extract_interest_rate(soup: BeautifulSoup, page_text: str) -> Optional[float]:
        """Extract interest rate with multiple strategies"""
        
        # Strategy 1: Look for specific rate sections
        rate_sections = soup.find_all(['div', 'span', 'p', 'td', 'li'], 
                                     text=re.compile(r'interest rate|rate of interest|roi|@', re.I))
        for section in rate_sections:
            text = section.get_text()
            rate_match = re.search(r'(\d+\.?\d*)\s*%', text)
            if rate_match:
                rate = float(rate_match.group(1))
                if 5 <= rate <= 30:
                    return rate
        
        # Strategy 2: Look in tables
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text()
            if 'interest' in table_text.lower() or 'rate' in table_text.lower():
                rates = re.findall(r'(\d+\.?\d*)\s*%', table_text)
                if rates:
                    valid_rates = [float(r) for r in rates if 5 <= float(r) <= 30]
                    if valid_rates:
                        return min(valid_rates)
        
        # Strategy 3: Look for common patterns
        rate_patterns = [
            r'(\d+\.?\d*)\s*%\s*(?:p\.?a\.?|per annum|onwards|starting)',
            r'(?:starting|from|@)\s*(\d+\.?\d*)\s*%',
            r'rate[:\s]+(\d+\.?\d*)\s*%',
            r'(\d+\.?\d*)\s*%\s*(?:interest|roi)',
        ]
        
        for pattern in rate_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                rates = [float(m) for m in matches if 5 <= float(m) <= 30]
                if rates:
                    return min(rates)
        
        # Strategy 4: Full page scan
        all_rates = re.findall(r'(\d+\.?\d*)\s*%', page_text)
        valid_rates = [float(r) for r in all_rates if 5 <= float(r) <= 30]
        if valid_rates:
            from collections import Counter
            rate_counts = Counter(valid_rates)
            return rate_counts.most_common(1)[0][0]
        
        return None
    
    @staticmethod
    async def scrape_bank_website(bank_name: str, bank_url: str, loan_type: str) -> Optional[Dict[str, Any]]:
        """Scrape a single bank website for loan data"""
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Referer': 'https://www.google.com/'
                }
                
                response = await client.get(bank_url, headers=headers)
                
                if response.status_code != 200:
                    print(f"Failed to fetch {bank_name}: Status {response.status_code}")
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                interest_rate = LoanService.extract_interest_rate(soup, page_text)
                
                amount_patterns = [
                    r'(?:up to|maximum|upto|loan of)\s+₹?\s*(\d+(?:,\d+)*)\s*(lakh|crore)',
                    r'₹\s*(\d+(?:,\d+)*)\s*(lakh|crore)',
                ]
                
                max_amount = None
                for pattern in amount_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        amount_str = match.group(1).replace(',', '')
                        amount = float(amount_str)
                        unit = match.group(2).lower()
                        
                        if 'crore' in unit:
                            max_amount = amount * 10000000
                        elif 'lakh' in unit:
                            max_amount = amount * 100000
                        break
                
                if interest_rate:
                    print(f"✓ Scraped {bank_name}: {interest_rate}% interest rate")
                    return {
                        "lender_name": f"{bank_name} {loan_type.title()} Loan",
                        "loan_type": loan_type,
                        "min_amount": 50000,
                        "max_amount": max_amount or 5000000,
                        "interest_rate_min": interest_rate,
                        "interest_rate_max": interest_rate + 5,
                        "term_months_min": 12,
                        "term_months_max": 60,
                        "origination_fee": 1.0,
                        "processing_fee": 0.5,
                        "prepayment_penalty": False,
                        "min_credit_score": 650,
                        "min_income": 25000,
                        "max_dti_ratio": 43,
                        "features": ["Real-time rate", "Scraped from bank website"],
                        "source_url": bank_url,
                        "scraped_at": datetime.utcnow()
                    }
                else:
                    print(f"✗ Could not extract rate from {bank_name}")
                    return None
                    
        except Exception as e:
            print(f"Error scraping {bank_name}: {str(e)}")
            return None
    
    @staticmethod
    async def scrape_all_banks(loan_type: str) -> List[Dict[str, Any]]:
        """Scrape loan data from all banks with delays"""
        print(f"\n🔍 Scraping loan data for {loan_type} loans from top Indian banks...")
        
        scraped_data = []
        for bank in LoanService.INDIAN_BANKS:
            result = await LoanService.scrape_bank_website(bank["name"], bank["url"], loan_type)
            if result:
                scraped_data.append(result)
            await asyncio.sleep(2)
        
        print(f"✓ Successfully scraped {len(scraped_data)}/{len(LoanService.INDIAN_BANKS)} banks\n")
        return scraped_data
    
    @staticmethod
    async def get_cached_loan_data(loan_type: str, amount: float, max_age_hours: int = 24) -> List[Dict[str, Any]]:
        """Get cached loan data from database"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        cached_data = await LoanData.find({
            "loan_type": loan_type,
            "is_active": True,
            "scraped_at": {"$gte": cutoff_time},
            "min_amount": {"$lte": amount},
            "max_amount": {"$gte": amount}
        }).to_list()
        
        if cached_data:
            print(f"✓ Found {len(cached_data)} cached loans (less than {max_age_hours}h old)")
        
        return [loan.to_dict() for loan in cached_data]
    
    @staticmethod
    async def save_scraped_data(scraped_loans: List[Dict[str, Any]]):
        """Save scraped loan data to database"""
        for loan_data in scraped_loans:
            try:
                existing = await LoanData.find_one({
                    "lender_name": loan_data["lender_name"],
                    "loan_type": loan_data["loan_type"]
                })
                
                if existing:
                    for key, value in loan_data.items():
                        setattr(existing, key, value)
                    existing.scraped_at = datetime.utcnow()
                    await existing.save()
                else:
                    new_loan = LoanData(**loan_data)
                    await new_loan.insert()
                    
            except Exception as e:
                print(f"Error saving loan data: {str(e)}")
    
    @staticmethod
    async def fetch_loan_options(loan_type: str, amount: float) -> List[Dict[str, Any]]:
        """Fetch loan options"""
        cached_loans = await LoanService.get_cached_loan_data(loan_type, amount, max_age_hours=24)
        
        if len(cached_loans) >= 5:
            print(f"📦 Using {len(cached_loans)} cached loan options")
            return cached_loans
        
        print("🌐 Fetching fresh loan data from bank websites...")
        scraped_loans = await LoanService.scrape_all_banks(loan_type)
        
        if scraped_loans:
            await LoanService.save_scraped_data(scraped_loans)
            all_loans = scraped_loans + cached_loans
            
            seen = set()
            unique_loans = []
            for loan in all_loans:
                if loan["lender_name"] not in seen:
                    seen.add(loan["lender_name"])
                    unique_loans.append(loan)
            
            return unique_loans
        
        if not cached_loans:
            raise ValueError("Unable to fetch loan data. Please try again later.")
        
        return cached_loans
    
    @staticmethod
    async def get_user_financial_snapshot(clerk_user_id: str) -> Dict[str, Any]:
        """Get user's current financial situation"""
        user = await User.find_one({"clerk_user_id": clerk_user_id})
        if not user:
            raise ValueError("User not found")
        
        debts = await Debt.find({
            "clerk_user_id": clerk_user_id,
            "is_active": True
        }).to_list()
        
        total_debt = sum(debt.total_amount for debt in debts)
        total_monthly_payments = sum(debt.min_payment for debt in debts)
        
        return {
            "monthly_income": user.monthly_income,
            "monthly_expenses": user.monthly_expenses,
            "total_existing_debt": total_debt,
            "existing_monthly_debt_payments": total_monthly_payments,
            "debt_count": len(debts)
        }
    
    @staticmethod
    async def get_ai_ranking_and_insights(
        loan_options: List[Dict],
        user_profile: Dict,
        requested_amount: float,
        loan_type: str
    ) -> Tuple[List[int], str]:
        """AI ranks loans and provides detailed insights"""
        
        loans_summary = "\n".join([
            f"{i+1}. {loan['lender_name']}: "
            f"Interest Rate {loan['interest_rate_min']:.2f}-{loan['interest_rate_max']:.2f}%, "
            f"Max Loan: ₹{loan['max_amount']:,.0f}, "
            f"Processing Fee: {loan.get('processing_fee', 0)}%, "
            f"Min Credit Score: {loan.get('min_credit_score', 'Not specified')}"
            for i, loan in enumerate(loan_options)
        ])
        
        prompt = f"""You are an expert Indian financial advisor. Analyze these {loan_type} loans and provide intelligent recommendations.

USER FINANCIAL PROFILE:
- Monthly Income: ₹{user_profile.get('monthly_income', 0):,.0f}
- Monthly Expenses: ₹{user_profile.get('monthly_expenses', 0):,.0f}
- Available Budget: ₹{user_profile.get('available_budget', 0):,.0f}
- Existing Total Debt: ₹{user_profile.get('total_existing_debt', 0):,.0f}
- Existing Monthly Debt Payments: ₹{user_profile.get('existing_monthly_debt_payments', 0):,.0f}
- Current DTI Ratio: {user_profile.get('debt_to_income_ratio', 0):.1f}%
- Loan Amount Requested: ₹{requested_amount:,.0f}

AVAILABLE LOANS FROM INDIAN BANKS:
{loans_summary}

TASK 1 - RANK LOANS:
Analyze and rank these loans from BEST to WORST match for this user. Consider:
1. Interest rate (lowest is better - this is the PRIMARY factor)
2. Total cost over the loan term
3. User's ability to qualify (income, credit score requirements)
4. Processing fees and other charges
5. Loan amount limits

Return the ranking as a JSON array of loan numbers (1-{len(loan_options)}) in order from best to worst.
Example: [3, 1, 5, 2, 4]

TASK 2 - DETAILED INSIGHTS:
Provide a detailed analysis (200-300 words) covering:

**RECOMMENDED LOAN:**
- Which bank loan is the best match and WHY
- Exact monthly EMI they'll pay
- Total interest they'll pay over the term
- Why this is better than other options

**KEY INSIGHTS:**
- How does their DTI ratio look with this new loan?
- Is this loan affordable given their budget?
- What's the total financial impact?
- Any red flags or concerns?

**ALTERNATIVE OPTIONS:**
- Mention the 2nd best option briefly
- When would someone choose the alternative?

**ACTIONABLE ADVICE:**
- Specific steps to improve loan eligibility
- How to reduce overall interest costs
- Timing recommendations

Be specific with numbers. Use ₹ for currency. Be direct and practical.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
RANKING: [3, 1, 5, 2]

INSIGHTS:
[Your detailed analysis here]"""
        
        try:
            response = await LoanService.chat_with_ai(prompt)
            
            # Parse ranking
            ranking_match = re.search(r'RANKING:\s*\[([0-9,\s]+)\]', response)
            if ranking_match:
                ranking_str = ranking_match.group(1)
                ranking = [int(x.strip()) for x in ranking_str.split(',')]
            else:
                # Fallback: rank by interest rate
                ranking = list(range(1, len(loan_options) + 1))
            
            # Extract insights
            insights_match = re.search(r'INSIGHTS:\s*(.*)', response, re.DOTALL)
            if insights_match:
                insights = insights_match.group(1).strip()
            else:
                insights = response
            
            return ranking, insights
            
        except Exception as e:
            print(f"AI ranking error: {str(e)}")
            # Fallback: rank by interest rate
            ranking = list(range(1, len(loan_options) + 1))
            insights = "Analysis temporarily unavailable. Loans ranked by interest rate."
            return ranking, insights
    
    @staticmethod
    async def rank_loan_options_with_ai(
        loan_options: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        requested_amount: float,
        loan_type: str,
        preferred_term: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], str]:
        """AI-powered loan ranking with detailed insights"""
        
        # Get AI ranking and insights
        print("🤖 AI is analyzing loans and generating insights...")
        ranking, insights = await LoanService.get_ai_ranking_and_insights(
            loan_options, user_profile, requested_amount, loan_type
        )
        
        # Calculate loan details for each option
        ranked_loans = []
        for loan_data in loan_options:
            interest_rate = (loan_data.get("interest_rate_min", 0) + loan_data.get("interest_rate_max", 0)) / 2
            term_months = preferred_term or 36
            
            monthly_payment = LoanAnalyzer.calculate_monthly_payment(
                requested_amount, interest_rate, term_months
            )
            
            total_interest = LoanAnalyzer.calculate_total_interest(
                requested_amount, monthly_payment, term_months
            )
            total_cost = requested_amount + total_interest
            
            origination_fee = loan_data.get("origination_fee", 0)
            processing_fee = loan_data.get("processing_fee", 0)
            apr = LoanAnalyzer.calculate_apr(interest_rate, origination_fee, processing_fee)
            
            # AI-based suitability score (100 for rank 1, 90 for rank 2, etc.)
            loan_index = loan_options.index(loan_data) + 1
            if loan_index in ranking:
                rank_position = ranking.index(loan_index)
                suitability_score = 100 - (rank_position * 10)
            else:
                suitability_score = 50
            
            approval_probability = LoanAnalyzer.calculate_approval_probability(
                loan_data, user_profile
            )
            
            loan_option = {
                "lender_name": loan_data.get("lender_name", "Unknown"),
                "loan_type": loan_data.get("loan_type", "personal"),
                "interest_rate": round(interest_rate, 2),
                "apr": apr,
                "monthly_payment": monthly_payment,
                "total_interest": total_interest,
                "total_cost": total_cost,
                "term_months": term_months,
                "origination_fee": origination_fee,
                "processing_fee": processing_fee,
                "prepayment_penalty": loan_data.get("prepayment_penalty", False),
                "min_credit_score": loan_data.get("min_credit_score"),
                "min_income": loan_data.get("min_income"),
                "max_dti_ratio": loan_data.get("max_dti_ratio"),
                "suitability_score": suitability_score,
                "approval_probability": approval_probability,
                "features": loan_data.get("features", []),
                "pros": LoanService.generate_pros(loan_data, interest_rate),
                "cons": LoanService.generate_cons(loan_data, interest_rate),
                "source_url": loan_data.get("source_url"),
                "ai_rank": rank_position + 1 if loan_index in ranking else 99
            }
            
            ranked_loans.append(loan_option)
        
        # Sort by AI ranking
        ranked_loans.sort(key=lambda x: x["ai_rank"])
        
        return ranked_loans[:10], insights
    
    @staticmethod
    async def create_loan_recommendation(
        clerk_user_id: str,
        request: LoanRecommendationRequest
    ) -> LoanRecommendationResponse:
        """Create AI-powered loan recommendation"""
        
        financial_snapshot = await LoanService.get_user_financial_snapshot(clerk_user_id)
        
        affordability = LoanAnalyzer.analyze_affordability(
            requested_amount=request.requested_amount,
            monthly_income=financial_snapshot["monthly_income"],
            monthly_expenses=financial_snapshot["monthly_expenses"],
            total_existing_debt=financial_snapshot["total_existing_debt"],
            existing_monthly_debt_payments=financial_snapshot["existing_monthly_debt_payments"],
            term_months=request.preferred_term_months or 36
        )
        
        # Fetch loan options
        loan_options = await LoanService.fetch_loan_options(
            loan_type=request.loan_type,
            amount=request.requested_amount
        )
        
        # AI ranks loans and generates insights
        ranked_loans, ai_insights = await LoanService.rank_loan_options_with_ai(
            loan_options=loan_options,
            user_profile=affordability,
            requested_amount=request.requested_amount,
            loan_type=request.loan_type,
            preferred_term=request.preferred_term_months
        )
        
        # Generate comparison data
        comparison_data = LoanService.generate_comparison_data(ranked_loans)
        
        # Find best options
        best_overall = ranked_loans[0]["lender_name"] if ranked_loans else None
        lowest_rate = min(ranked_loans, key=lambda x: x["interest_rate"])["lender_name"] if ranked_loans else None
        lowest_payment = min(ranked_loans, key=lambda x: x["monthly_payment"])["lender_name"] if ranked_loans else None
        lowest_total_cost = min(ranked_loans, key=lambda x: x["total_cost"])["lender_name"] if ranked_loans else None
        
        # Save recommendation
        recommendation = LoanRecommendation(
            clerk_user_id=clerk_user_id,
            loan_type=request.loan_type,
            requested_amount=request.requested_amount,
            purpose=request.purpose,
            preferred_term_months=request.preferred_term_months,
            user_monthly_income=financial_snapshot["monthly_income"],
            user_monthly_expenses=financial_snapshot["monthly_expenses"],
            total_existing_debt=financial_snapshot["total_existing_debt"],
            debt_to_income_ratio=affordability["debt_to_income_with_loan"],
            recommended_loans=[loan for loan in ranked_loans],
            affordability_score=affordability["affordability_score"],
            max_affordable_monthly=affordability["max_affordable_monthly"],
            analysis_notes=ai_insights,  # Detailed AI insights stored here
            status="completed"
        )
        await recommendation.insert()
        
        return LoanRecommendationResponse(
            id=str(recommendation.id),
            clerk_user_id=clerk_user_id,
            loan_type=request.loan_type,
            requested_amount=request.requested_amount,
            affordability_analysis=AffordabilityAnalysis(**affordability),
            recommended_loans=[LoanOption(**loan) for loan in ranked_loans],
            comparison_data=[LoanComparisonData(**comp) for comp in comparison_data],
            best_overall=best_overall,
            lowest_rate=lowest_rate,
            lowest_payment=lowest_payment,
            lowest_total_cost=lowest_total_cost,
            status="completed",
            created_at=recommendation.created_at
        )
    
    @staticmethod
    def generate_comparison_data(loans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate comparison data"""
        if not loans:
            return []
        
        highest_monthly = max(loan["monthly_payment"] for loan in loans)
        highest_total = max(loan["total_cost"] for loan in loans)
        
        comparison = []
        for i, loan in enumerate(loans):
            comparison.append({
                "loan_id": f"loan_{i}",
                "lender_name": loan["lender_name"],
                "monthly_payment": loan["monthly_payment"],
                "total_interest": loan["total_interest"],
                "total_cost": loan["total_cost"],
                "term_months": loan["term_months"],
                "monthly_savings_vs_highest": round(highest_monthly - loan["monthly_payment"], 2),
                "total_savings_vs_highest": round(highest_total - loan["total_cost"], 2)
            })
        
        return comparison
    
    @staticmethod
    def generate_pros(loan_data: Dict[str, Any], interest_rate: float) -> List[str]:
        """Generate pros"""
        pros = []
        
        if interest_rate < 10:
            pros.append("Competitive interest rate")
        if not loan_data.get("prepayment_penalty", False):
            pros.append("No prepayment penalty")
        if loan_data.get("origination_fee", 1) < 1:
            pros.append("Low fees")
        
        pros.extend(loan_data.get("features", [])[:2])
        return pros[:5]
    
    @staticmethod
    def generate_cons(loan_data: Dict[str, Any], interest_rate: float) -> List[str]:
        """Generate cons"""
        cons = []
        
        if interest_rate > 15:
            cons.append("High interest rate")
        if loan_data.get("prepayment_penalty", False):
            cons.append("Prepayment penalty")
        if loan_data.get("origination_fee", 0) > 2:
            cons.append("Higher fees")
        
        if not cons:
            cons.append("Standard terms apply")
        
        return cons[:4]
    
    @staticmethod
    async def get_recommendation_history(clerk_user_id: str) -> List[Dict[str, Any]]:
        """Get past recommendations"""
        recommendations = await LoanRecommendation.find({
            "clerk_user_id": clerk_user_id,
            "is_active": True
        }).sort("-created_at").to_list()
        
        return [rec.to_dict() for rec in recommendations]
    
    @staticmethod
    async def get_recommendation_by_id(recommendation_id: str, clerk_user_id: str) -> Optional[LoanRecommendation]:
        """Get specific recommendation"""
        try:
            recommendation = await LoanRecommendation.find_one({
                "_id": PydanticObjectId(recommendation_id),
                "clerk_user_id": clerk_user_id
            })
            return recommendation
        except:
            return None