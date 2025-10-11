# app/services/llm_service.py
import os
import httpx
from typing import Dict, Any, List, Optional
import json
from app.config.settings import settings


class LLMService:
    """Service for interacting with Groq API for AI-powered financial advice"""
    
    BASE_URL = "https://api.groq.com/openai/v1"
    
    @staticmethod
    def _get_headers() -> Dict[str, str]:
        """Get headers for Groq API requests"""
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in settings")
        
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    async def generate_credit_advice(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
        """Generate credit improvement advice using Groq API"""
        
        system_prompt = """You are a knowledgeable and helpful financial advisor specializing in Indian banking and finance. 
        Provide practical, actionable advice.
        Be specific with numbers, timelines, and steps.
        Focus on realistic expectations and proven strategies.
        Keep advice encouraging but honest about the time and effort required.
        When providing loan recommendations, use current 2025 Indian market rates and real bank names."""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{LLMService.BASE_URL}/chat/completions",
                    headers=LLMService._get_headers(),
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 3000,
                        "top_p": 0.9
                    }
                )
                
                if response.status_code != 200:
                    print(f"Groq API Error Response: {response.text}")
                    raise Exception(f"Groq API error: {response.status_code}")
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            print(f"LLM Service error: {type(e).__name__}: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    @staticmethod
    async def generate_loan_recommendations(
        loan_type: str,
        amount: float,
        user_debt_data: Dict[str, Any],
        scraped_bank_data: str
    ) -> str:
        """Generate comprehensive loan recommendations using REAL scraped bank data"""
        
        total_debt = user_debt_data.get('total_debt', 0)
        monthly_obligations = user_debt_data.get('total_minimum_payment', 0)
        debt_count = user_debt_data.get('debt_count', 0)
        
        prompt = f"""
LOAN RECOMMENDATION REQUEST - USING REAL BANK DATA

USER PROFILE:
- Requested Loan Type: {loan_type.upper()} LOAN
- Requested Amount: ₹{amount:,.0f} ({amount/100000:.2f} Lakhs)
- Existing Total Debt: ₹{total_debt:,.0f}
- Monthly Debt Obligations: ₹{monthly_obligations:,.0f}
- Number of Existing Debts: {debt_count}
- Debt Burden Level: {'HIGH - May affect eligibility' if total_debt > 500000 else 'MODERATE - Manageable' if total_debt > 200000 else 'LOW - Good standing'}

REAL-TIME BANK DATA (SCRAPED FROM WEBSITES):
{scraped_bank_data}

CRITICAL INSTRUCTIONS:
1. Use ONLY the scraped bank data provided above - these are REAL current rates
2. Do NOT make up or hallucinate any interest rates or fees
3. If data says "Check website" or "Contact bank", mention that in your response
4. Include the actual scraped rates in your comparison

YOUR TASK:
Provide a comprehensive loan recommendation analysis.

RESPONSE FORMAT:

1. ELIGIBILITY ASSESSMENT
==================
Analyze if the user can afford this loan given their current debt situation.
- Can they realistically take this loan? YES/NO and why
- Recommended loan amount (may differ from requested)
- Monthly EMI they can afford (calculate based on ₹{amount:,.0f})
- Key concerns or red flags
- Credit score implications

2. TOP 5 BANK RECOMMENDATIONS
==================
For each bank in the scraped data, provide:

BANK: [Bank Name from scraped data]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Interest Rate: [EXACT rate from scraped data]
Processing Fee: [EXACT fee from scraped data]
Max Loan Amount: [EXACT amount from scraped data]
Loan Tenure: [EXACT tenure from scraped data]
Monthly EMI (approx): ₹[Calculate using the scraped interest rate]
Why This Bank:
  • [Specific reason based on scraped data]
  • [Another reason]
Eligibility:
  • [Based on bank's typical criteria]
Best For: [Type of customer]
Data Source: [Mention if scraped or fallback]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. COMPARISON TABLE
==================
Create a detailed comparison using the EXACT scraped data:

| Bank Name | Interest Rate | Processing Fee | Max Amount | EMI* | Data Source |
|-----------|---------------|----------------|------------|------|-------------|
[Use actual scraped data for each bank]

*EMI calculated for ₹{amount:,.0f} at average tenure

4. PERSONALIZED RECOMMENDATION
==================
Based on the user's financial situation AND the scraped bank data:
- **BEST CHOICE**: [Bank with lowest rate/best terms from scraped data] - [Why]
- **RUNNER UP**: [Second best option] - [When to choose this]
- **BUDGET OPTION**: [Lowest processing fee option] - [For cost-conscious]

5. REQUIRED DOCUMENTS
==================
Typical documents for {loan_type} loan:
  • Identity Proof (Aadhaar, PAN, Passport)
  • Address Proof
  • Income Proof (Salary slips/ITR)
  • Bank statements (6 months)
  • [Add loan-type specific documents]

6. PRO TIPS FOR BETTER LOAN TERMS
==================
  • Maintain credit score above 750 for best rates
  • Compare multiple banks before deciding
  • Negotiate processing fee waiver
  • Check for pre-approved offers
  • Consider co-applicant to increase eligibility

7. WARNINGS & CONSIDERATIONS
==================
  ⚠️ Current debt: ₹{total_debt:,.0f} - New loan will {'significantly increase' if total_debt > 300000 else 'moderately increase'} your debt burden
  ⚠️ Ensure total EMI (existing + new) doesn't exceed 50% of monthly income
  ⚠️ Verify all rates directly with banks before applying
  ⚠️ {'Some data may be approximate - check bank websites' if 'fallback' in scraped_bank_data.lower() else 'Data scraped from bank websites - verify before applying'}

8. NEXT STEPS
==================
1. Verify your credit score
2. Compare offers from 3-4 banks
3. Negotiate for best terms
4. Read all terms and conditions
5. Apply only after final verification

IMPORTANT: 
- Base ALL recommendations on the scraped bank data provided
- Do NOT invent or assume any interest rates
- If data is missing, explicitly say "Contact bank for details"
- Calculate EMIs using actual scraped interest rates
"""
        
        return await LLMService.generate_credit_advice(prompt, model="llama-3.3-70b-versatile")
    
    @staticmethod
    async def analyze_debt_for_credit_impact(debts: List[Dict], user_profile: Dict) -> str:
        """Analyze how specific debts impact credit score"""
        
        debt_summary = []
        for debt in debts:
            debt_info = f"- {debt.get('name', 'Unnamed')}: ₹{debt.get('total_amount', 0):,.0f} at {debt.get('interest_rate', 0):.1f}% APR"
            if debt.get('limit'):
                utilization = (debt.get('total_amount', 0) / debt.get('limit', 1)) * 100
                debt_info += f" (Utilization: {utilization:.1f}%)"
            debt_summary.append(debt_info)
        
        prompt = f"""
        Analyze how these specific debts impact the user's credit score:
        
        **Current Debts:**
        {chr(10).join(debt_summary)}
        
        **User Profile:**
        - Monthly Income: ₹{user_profile.get('monthly_income', 0):,.0f}
        - Monthly Expenses: ₹{user_profile.get('monthly_expenses', 0):,.0f}
        
        Please provide:
        1. **Credit Score Impact Analysis** - which debts hurt the score most
        2. **Prioritized Paydown Strategy** - which debts to tackle first for credit improvement
        3. **Utilization Optimization** - specific target balances for each revolving account
        4. **Timeline and Milestones** - when to expect credit score improvements
        
        Be specific with numbers and actionable steps.
        """
        
        return await LLMService.generate_credit_advice(prompt)
    
    @staticmethod
    async def generate_personalized_tips(
        user_context: Dict[str, Any], 
        focus_areas: Optional[List[str]] = None
    ) -> List[str]:
        """Generate personalized credit tips based on user context"""
        
        focus_text = f"Focus especially on: {', '.join(focus_areas)}" if focus_areas else ""
        
        prompt = f"""
        Generate 5-7 personalized credit improvement tips for this user:
        
        **User Context:**
        - Current Score: {user_context.get('current_score', 'Unknown')}
        - Target Score: {user_context.get('target_score', 750)}
        - Utilization: {user_context.get('utilization_percent', 0):.1f}%
        - Payment History: {user_context.get('payment_history', 'Good')}
        - Account Age: {user_context.get('account_age_years', 3)} years
        - New Accounts: {user_context.get('new_accounts', 0)} in last 2 years
        
        {focus_text}
        
        Provide specific, actionable tips. Each tip should be:
        - One clear sentence
        - Include specific numbers when relevant
        - Be immediately actionable
        - Focus on highest impact items first
        
        Format as a simple list, one tip per line.
        """
        
        try:
            response = await LLMService.generate_credit_advice(prompt)
            tips = [line.strip() for line in response.split('\n') if line.strip() and not line.startswith('#')]
            return [tip.lstrip('- ').lstrip('• ').lstrip('1234567890. ') for tip in tips if tip][:7]
        except:
            return [
                "Pay down credit card balances to under 30% of limits for immediate score improvement",
                "Set up automatic minimum payments to ensure perfect payment history going forward", 
                "Check your credit reports for errors - dispute any inaccuracies you find",
                "Keep old credit cards open to maintain credit history length",
                "Avoid applying for new credit cards for the next 6-12 months",
                "Pay balances before statement closing dates to reduce reported utilization",
                "Request credit limit increases on existing cards to improve your utilization ratio"
            ]
    
    @staticmethod
    async def test_api_connection() -> Dict[str, Any]:
        """Test Groq API connection and return status"""
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{LLMService.BASE_URL}/chat/completions",
                    headers=LLMService._get_headers(),
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 10
                    }
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "api_key_present": bool(settings.GROQ_API_KEY),
                    "api_key_format": settings.GROQ_API_KEY.startswith('gsk_') if settings.GROQ_API_KEY else False,
                    "response_text": response.text[:200] if response.status_code != 200 else "OK"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "api_key_present": bool(settings.GROQ_API_KEY),
                "api_key_format": settings.GROQ_API_KEY.startswith('gsk_') if settings.GROQ_API_KEY else False
            }