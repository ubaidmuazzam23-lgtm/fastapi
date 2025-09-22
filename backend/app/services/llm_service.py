# # app/services/llm_service.py
# import os
# import httpx
# from typing import Dict, Any, List, Optional
# import json
# from app.config.settings import settings

# class LLMService:
#     """Service for interacting with Groq API for AI-powered financial advice"""
    
#     BASE_URL = "https://api.groq.com/openai/v1"
    
#     @staticmethod
#     def _get_headers() -> Dict[str, str]:
#         """Get headers for Groq API requests"""
#         api_key = os.getenv("GROQ_API_KEY")
#         if not api_key:
#             raise ValueError("GROQ_API_KEY environment variable not set")
        
#         return {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         }
    
#     @staticmethod
#     async def generate_credit_advice(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
#         """Generate credit improvement advice using Groq API"""
        
#         system_prompt = """You are a knowledgeable and helpful credit counselor. 
#         Provide practical, actionable advice for improving credit scores.
#         Be specific with numbers, timelines, and steps.
#         Focus on realistic expectations and proven strategies.
#         Keep advice encouraging but honest about the time and effort required.
#         Structure your response clearly with headers and bullet points."""
        
#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     f"{LLMService.BASE_URL}/chat/completions",
#                     headers=LLMService._get_headers(),
#                     json={
#                         "model": model,
#                         "messages": [
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": prompt}
#                         ],
#                         "temperature": 0.7,
#                         "max_tokens": 2000,
#                         "top_p": 0.9
#                     }
#                 )
                
#                 if response.status_code != 200:
#                     raise Exception(f"Groq API error: {response.status_code} - {response.text}")
                
#                 result = response.json()
#                 return result["choices"][0]["message"]["content"]
                
#         except Exception as e:
#             print(f"Error calling Groq API: {e}")
#             # Fallback response
#             return f"""
#             **Credit Improvement Plan**
            
#             Based on your profile, here are the key recommendations:
            
#             **Priority Actions:**
#             1. **Reduce Credit Utilization**: Pay down balances to under 30% of limits
#             2. **Maintain Payment History**: Set up autopay for all minimum payments  
#             3. **Monitor Credit Reports**: Check for errors and dispute if found
            
#             **Timeline:**
#             - **Months 1-3**: Focus on utilization reduction and payment setup
#             - **Months 4-6**: Continue payments and monitor score improvements
#             - **Months 7-12**: Maintain good habits and reassess strategy
            
#             **Expected Impact:**
#             With consistent effort, you could see 50-100 point improvement over 6-12 months.
            
#             **Red Flags to Avoid:**
#             - Don't close old credit cards
#             - Avoid new credit applications
#             - Never miss payments
#             - Don't max out credit limits
            
#             Note: AI service temporarily unavailable, showing fallback recommendations.
#             """
    
#     @staticmethod
#     async def analyze_debt_for_credit_impact(debts: List[Dict], user_profile: Dict) -> str:
#         """Analyze how specific debts impact credit score"""
        
#         debt_summary = []
#         for debt in debts:
#             debt_info = f"- {debt.get('name', 'Unnamed')}: ₹{debt.get('total_amount', 0):,.0f} at {debt.get('interest_rate', 0):.1f}% APR"
#             if debt.get('limit'):
#                 utilization = (debt.get('total_amount', 0) / debt.get('limit', 1)) * 100
#                 debt_info += f" (Utilization: {utilization:.1f}%)"
#             debt_summary.append(debt_info)
        
#         prompt = f"""
#         Analyze how these specific debts impact the user's credit score:
        
#         **Current Debts:**
#         {chr(10).join(debt_summary)}
        
#         **User Profile:**
#         - Monthly Income: ₹{user_profile.get('monthly_income', 0):,.0f}
#         - Monthly Expenses: ₹{user_profile.get('monthly_expenses', 0):,.0f}
        
#         Please provide:
#         1. **Credit Score Impact Analysis** - which debts hurt the score most
#         2. **Prioritized Paydown Strategy** - which debts to tackle first for credit improvement
#         3. **Utilization Optimization** - specific target balances for each revolving account
#         4. **Timeline and Milestones** - when to expect credit score improvements
        
#         Be specific with numbers and actionable steps.
#         """
        
#         return await LLMService.generate_credit_advice(prompt)
    
#     @staticmethod
#     async def generate_personalized_tips(
#         user_context: Dict[str, Any], 
#         focus_areas: Optional[List[str]] = None
#     ) -> List[str]:
#         """Generate personalized credit tips based on user context"""
        
#         focus_text = f"Focus especially on: {', '.join(focus_areas)}" if focus_areas else ""
        
#         prompt = f"""
#         Generate 5-7 personalized credit improvement tips for this user:
        
#         **User Context:**
#         - Current Score: {user_context.get('current_score', 'Unknown')}
#         - Target Score: {user_context.get('target_score', 750)}
#         - Utilization: {user_context.get('utilization_percent', 0):.1f}%
#         - Payment History: {user_context.get('payment_history', 'Good')}
#         - Account Age: {user_context.get('account_age_years', 3)} years
#         - New Accounts: {user_context.get('new_accounts', 0)} in last 2 years
        
#         {focus_text}
        
#         Provide specific, actionable tips. Each tip should be:
#         - One clear sentence
#         - Include specific numbers when relevant
#         - Be immediately actionable
#         - Focus on highest impact items first
        
#         Format as a simple list, one tip per line.
#         """
        
#         try:
#             response = await LLMService.generate_credit_advice(prompt)
#             # Parse response into list
#             tips = [line.strip() for line in response.split('\n') if line.strip() and not line.startswith('#')]
#             return [tip.lstrip('- ').lstrip('• ').lstrip('1234567890. ') for tip in tips if tip][:7]
#         except:
#             # Fallback tips
#             return [
#                 "Pay down credit card balances to under 30% of limits for immediate score improvement",
#                 "Set up automatic minimum payments to ensure perfect payment history going forward", 
#                 "Check your credit reports for errors - dispute any inaccuracies you find",
#                 "Keep old credit cards open to maintain credit history length",
#                 "Avoid applying for new credit cards for the next 6-12 months",
#                 "Pay balances before statement closing dates to reduce reported utilization",
#                 "Request credit limit increases on existing cards to improve your utilization ratio"
#             ]


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
        api_key = settings.GROQ_API_KEY  # Use settings instead of os.getenv
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in settings")
        
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    async def generate_credit_advice(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
        """Generate credit improvement advice using Groq API"""
        
        system_prompt = """You are a knowledgeable and helpful credit counselor. 
        Provide practical, actionable advice for improving credit scores.
        Be specific with numbers, timelines, and steps.
        Focus on realistic expectations and proven strategies.
        Keep advice encouraging but honest about the time and effort required.
        Structure your response clearly with headers and bullet points."""
        
        # Debug logging
        print(f"Using API key: {settings.GROQ_API_KEY[:10]}..." if settings.GROQ_API_KEY else "No API key found")
        
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
                        "max_tokens": 2000,
                        "top_p": 0.9
                    }
                )
                
                print(f"Groq API Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"Groq API Error Response: {response.text}")
                    raise Exception(f"Groq API error: {response.status_code} - {response.text}")
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            print(f"Full exception details: {type(e).__name__}: {str(e)}")
            if hasattr(e, 'response'):
                print(f"HTTP Response: {e.response.status_code} - {e.response.text}")
            
            # Fallback response
            return f"""
**Credit Improvement Plan**

Based on your profile, here are the key recommendations:

**Priority Actions:**
1. **Reduce Credit Utilization**: Pay down balances to under 30% of limits
2. **Maintain Payment History**: Set up autopay for all minimum payments 
3. **Monitor Credit Reports**: Check for errors and dispute if found

**Timeline:**
- **Months 1-3**: Focus on utilization reduction and payment setup
- **Months 4-6**: Continue payments and monitor score improvements
- **Months 7-12**: Maintain good habits and reassess strategy

**Expected Impact:**
With consistent effort, you could see 50-100 point improvement over 6-12 months.

**Red Flags to Avoid:**
- Don't close old credit cards
- Avoid new credit applications
- Never miss payments
- Don't max out credit limits

Note: AI service temporarily unavailable, showing fallback recommendations.
"""
    
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
            # Parse response into list
            tips = [line.strip() for line in response.split('\n') if line.strip() and not line.startswith('#')]
            return [tip.lstrip('- ').lstrip('• ').lstrip('1234567890. ') for tip in tips if tip][:7]
        except:
            # Fallback tips
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
    async def generate_debt_plan_explanation(plan_data: Dict[str, Any]) -> str:
        """Generate AI explanation for debt repayment plan"""
        
        prompt = f"""
        Explain this debt repayment plan in simple, encouraging terms:
        
        **Plan Details:**
        - Strategy: {plan_data.get('strategy', 'Unknown')}
        - Total Debt: ₹{plan_data.get('total_debt', 0):,.0f}
        - Monthly Payment: ₹{plan_data.get('monthly_payment', 0):,.0f}
        - Payoff Time: {plan_data.get('payoff_months', 0)} months
        - Total Interest: ₹{plan_data.get('total_interest', 0):,.0f}
        - Interest Saved vs Minimum: ₹{plan_data.get('interest_saved', 0):,.0f}
        
        Provide:
        1. **Why this strategy works** - brief explanation
        2. **Key benefits** - what they'll achieve
        3. **Stay motivated tips** - how to stick with it
        4. **Milestones to celebrate** - progress markers
        
        Keep it encouraging and actionable, under 300 words.
        """
        
        return await LLMService.generate_credit_advice(prompt)
    
    @staticmethod
    async def generate_scenario_analysis(scenario_data: Dict[str, Any]) -> str:
        """Generate AI analysis for what-if scenarios"""
        
        prompt = f"""
        Analyze this financial what-if scenario:
        
        **Scenario:**
        {scenario_data.get('description', 'Financial scenario analysis')}
        
        **Key Numbers:**
        - Current Monthly Payment: ₹{scenario_data.get('current_payment', 0):,.0f}
        - New Monthly Payment: ₹{scenario_data.get('new_payment', 0):,.0f}
        - Time Difference: {scenario_data.get('time_difference', 0)} months
        - Interest Difference: ₹{scenario_data.get('interest_difference', 0):,.0f}
        
        Provide:
        1. **Impact Summary** - what this change means
        2. **Pros and Cons** - benefits and drawbacks
        3. **Recommendation** - should they do it?
        4. **Action Steps** - how to implement if beneficial
        
        Be objective and practical, under 250 words.
        """
        
        return await LLMService.generate_credit_advice(prompt)
    
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