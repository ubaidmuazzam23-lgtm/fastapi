# from typing import List, Dict, Any, Optional
# from datetime import datetime
# from app.services.llm_service import LLMService
# from app.services.debt_service import DebtService
# from app.services.plan_service import PlanService
# from app.services.scenario_service import ScenarioService
# from app.services.loan_scraper_service import LoanScraperService
# from app.models.user import User
# import re

# class EducationService:
    
#     @staticmethod
#     def _check_inappropriate_content(message: str) -> bool:
#         """Check if message contains inappropriate content"""
#         inappropriate_words = [
#             'fuck', 'shit', 'damn', 'bitch', 'ass', 'hell', 'crap',
#             'stupid', 'idiot', 'moron', 'hate'
#         ]
#         message_lower = message.lower()
#         return any(word in message_lower for word in inappropriate_words)
    
#     @staticmethod
#     def _detect_loan_request(message: str) -> Dict[str, Any]:
#         """Detect if user is requesting loan recommendations"""
#         message_lower = message.lower()
        
#         # Loan keywords
#         loan_keywords = ['loan', 'borrow', 'finance', 'credit']
#         loan_types = {
#             'personal': ['personal loan', 'personal', 'quick loan'],
#             'home': ['home loan', 'housing loan', 'mortgage', 'property loan'],
#             'car': ['car loan', 'auto loan', 'vehicle loan'],
#             'education': ['education loan', 'student loan', 'study loan'],
#             'business': ['business loan', 'commercial loan', 'msme loan']
#         }
        
#         # Check if it's a loan request
#         is_loan_request = any(keyword in message_lower for keyword in loan_keywords)
        
#         # Determine loan type
#         loan_type = None
#         for ltype, keywords in loan_types.items():
#             if any(keyword in message_lower for keyword in keywords):
#                 loan_type = ltype
#                 break
        
#         # Extract amount (simple regex pattern)
#         amount_patterns = [
#             r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lakhs|cr|crore)?',
#             r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lakhs|cr|crore)',
#             r'(\d+(?:,\d+)*)'
#         ]
        
#         amount = None
#         for pattern in amount_patterns:
#             match = re.search(pattern, message_lower)
#             if match:
#                 amount_str = match.group(1).replace(',', '')
#                 amount = float(amount_str)
#                 # Check for lakh/crore
#                 if 'lakh' in message_lower:
#                     amount *= 100000
#                 elif 'cr' in message_lower or 'crore' in message_lower:
#                     amount *= 10000000
#                 break
        
#         return {
#             'is_loan_request': is_loan_request,
#             'loan_type': loan_type or 'personal',
#             'amount': amount
#         }
    
#     @staticmethod
#     def _detect_data_request(message: str) -> Dict[str, bool]:
#         """Detect what type of user data is being requested"""
#         message_lower = message.lower()
        
#         # Keywords for different data types
#         debt_keywords = [
#             'debt', 'debts', 'owe', 'outstanding', 'borrowed', 
#             'my debt', 'current debt', 'मेरा कर्ज', 'कर्ज', 
#             'माझे कर्ज', 'എന്റെ കടം', 'నా అప్పు'
#         ]
        
#         plan_keywords = [
#             'repayment plan', 'payment plan', 'strategy', 'payoff plan', 
#             'debt plan', 'my plan', 'current plan', 'repayment',
#             'चुकौती योजना', 'योजना', 'रणनीति',
#             'పరిహార ప్రణాళిక', 'തിരിച്ചടവ് പദ്ധതി'
#         ]
        
#         scenario_keywords = [
#             'what if', 'scenario', 'scenarios', 'simulation', 'compare', 
#             'different plan', 'my scenario', 'extra payment',
#             'अगर', 'परिदृश्य', 'तुलना',
#             'ఏమైతే', 'സാഹചര്യം'
#         ]
        
#         # NEW: Voice-related keywords that indicate user wants debt info
#         voice_debt_phrases = [
#             'what are my', 'show my', 'tell me my', 'give me my',
#             'मेरे', 'माझे', 'എന്റെ', 'నా',
#             'current', 'existing', 'have', 'got'
#         ]
        
#         # Check if message is asking about their debt data
#         needs_debt = any(keyword in message_lower for keyword in debt_keywords)
        
#         # ENHANCED: Also detect when voice users ask "what are my debts" style questions
#         if not needs_debt:
#             # Check for patterns like "what are my debts", "show my debts"
#             for phrase in voice_debt_phrases:
#                 if phrase in message_lower:
#                     for debt_word in ['debt', 'debts', 'loan', 'loans', 'कर्ज', 'കടം', 'అప్పు']:
#                         if debt_word in message_lower:
#                             needs_debt = True
#                             break
#                 if needs_debt:
#                     break
        
#         return {
#             'needs_debt_data': needs_debt,
#             'needs_plan_data': any(keyword in message_lower for keyword in plan_keywords),
#             'needs_scenario_data': any(keyword in message_lower for keyword in scenario_keywords)
#         }
    
#     @staticmethod
#     async def _fetch_user_financial_data(clerk_user_id: str, data_needs: Dict[str, bool]) -> Dict[str, Any]:
#         """Fetch relevant user financial data based on detected needs"""
#         financial_data = {}
        
#         try:
#             if data_needs['needs_debt_data']:
#                 debts = await DebtService.get_user_debts(clerk_user_id)
#                 print(f"DEBUG: Fetched {len(debts)} debts")
                
#                 financial_data['debts'] = debts
                
#                 if debts:
#                     total_debt = 0
#                     total_minimum_payment = 0
                    
#                     for debt in debts:
#                         try:
#                             total_debt += debt.total_amount or 0
#                             min_pay = getattr(debt, 'min_payment', 0) or 0
#                             total_minimum_payment += min_pay
#                         except Exception as e:
#                             print(f"Error processing debt: {e}")
#                             continue
                    
#                     financial_data['debt_summary'] = {
#                         'total_debt': total_debt,
#                         'total_minimum_payment': total_minimum_payment,
#                         'debt_count': len(debts)
#                     }
            
#             if data_needs['needs_plan_data']:
#                 try:
#                     debt_summary = await PlanService.get_user_debt_summary(clerk_user_id)
                    
#                     if debt_summary["debt_count"] > 0:
#                         plan_info = {
#                             "available_strategies": [
#                                 {
#                                     "name": "Debt Avalanche Strategy",
#                                     "description": "Pay minimums + focus extra on highest APR debt (saves most money)",
#                                     "best_for": "Minimizing total interest paid"
#                                 },
#                                 {
#                                     "name": "Debt Snowball Strategy", 
#                                     "description": "Pay minimums + focus extra on smallest balance (psychological wins)",
#                                     "best_for": "Building momentum and motivation"
#                                 },
#                                 {
#                                     "name": "Mathematical Optimal Strategy",
#                                     "description": "Mathematically optimized allocation for fastest payoff",
#                                     "best_for": "Maximum efficiency"
#                                 }
#                             ],
#                             "total_debt": debt_summary["total_debt"],
#                             "monthly_minimums": debt_summary["monthly_minimums"],
#                             "available_budget": debt_summary["available_budget"]
#                         }
#                         financial_data['plans'] = plan_info
#                     else:
#                         financial_data['plans'] = {"message": "No active debts found for repayment planning"}
                
#                 except Exception as e:
#                     print(f"Error fetching plans: {e}")
#                     financial_data['plans'] = {"error": f"Could not fetch plan information: {str(e)}"}
            
#             if data_needs['needs_scenario_data']:
#                 try:
#                     debt_summary = await PlanService.get_user_debt_summary(clerk_user_id)
                    
#                     if debt_summary["debt_count"] > 0:
#                         scenario_info = {
#                             "available_scenarios": [
#                                 "Extra Payment: See impact of paying extra each month",
#                                 "Windfall: Apply lump sum to debts", 
#                                 "Budget Reduction: What if available budget decreases",
#                                 "Interest Rate Change: Impact of rate changes",
#                                 "Debt Consolidation: Combine debts into single loan"
#                             ],
#                             "current_debt_count": debt_summary["debt_count"],
#                             "total_debt": debt_summary["total_debt"]
#                         }
#                         financial_data['scenarios'] = scenario_info
#                     else:
#                         financial_data['scenarios'] = {"message": "No active debts found for scenario analysis"}
                
#                 except Exception as e:
#                     print(f"Error fetching scenarios: {e}")
#                     financial_data['scenarios'] = {"error": f"Could not fetch scenario information: {str(e)}"}
        
#         except Exception as e:
#             print(f"Error fetching financial data: {e}")
#             financial_data['error'] = f"Could not fetch some financial data: {str(e)}"
        
#         return financial_data
    
#     @staticmethod
#     async def _format_financial_context(financial_data: Dict[str, Any]) -> str:
#         """Format financial data into context for the LLM"""
#         context_parts = []
        
#         if 'debts' in financial_data and financial_data['debts']:
#             context_parts.append("USER'S CURRENT DEBTS:")
#             for i, debt in enumerate(financial_data['debts']):
#                 try:
#                     name = debt.name
#                     total_amount = debt.total_amount
#                     interest_rate = debt.interest_rate
#                     min_payment = getattr(debt, 'min_payment', 0) or 0
                    
#                     debt_info = f"- {name}: ₹{total_amount:,.2f} total amount, {interest_rate}% APR, ₹{min_payment:,.2f} minimum payment"
#                     context_parts.append(debt_info)
                
#                 except Exception as e:
#                     print(f"Error formatting debt {i+1}: {e}")
#                     context_parts.append(f"- Debt information unavailable (Error: {str(e)})")
            
#             if 'debt_summary' in financial_data:
#                 summary = financial_data['debt_summary']
#                 context_parts.append(f"\nDEBT SUMMARY:")
#                 context_parts.append(f"- Total debt: ₹{summary['total_debt']:,.2f}")
#                 context_parts.append(f"- Total minimum payments: ₹{summary['total_minimum_payment']:,.2f}")
#                 context_parts.append(f"- Number of debts: {summary['debt_count']}")
        
#         if 'plans' in financial_data and financial_data['plans']:
#             if 'available_strategies' in financial_data['plans']:
#                 context_parts.append("\nAVAILABLE REPAYMENT STRATEGIES:")
#                 for strategy in financial_data['plans']['available_strategies']:
#                     strategy_info = f"- {strategy['name']}: {strategy['description']} (Best for: {strategy['best_for']})"
#                     context_parts.append(strategy_info)
                
#                 context_parts.append(f"\nPLANNING DETAILS:")
#                 context_parts.append(f"- Total debt to pay off: ₹{financial_data['plans']['total_debt']:,.2f}")
#                 context_parts.append(f"- Required minimum payments: ₹{financial_data['plans']['monthly_minimums']:,.2f}")
#                 context_parts.append(f"- Available budget for extra payments: ₹{financial_data['plans']['available_budget']:,.2f}")
#             elif 'error' in financial_data['plans']:
#                 context_parts.append(f"\nREPAYMENT PLANS: {financial_data['plans']['error']}")
#             elif 'message' in financial_data['plans']:
#                 context_parts.append(f"\nREPAYMENT PLANS: {financial_data['plans']['message']}")
        
#         if 'scenarios' in financial_data and financial_data['scenarios']:
#             if 'available_scenarios' in financial_data['scenarios']:
#                 context_parts.append("\nAVAILABLE WHAT-IF SCENARIOS:")
#                 for scenario in financial_data['scenarios']['available_scenarios']:
#                     context_parts.append(f"- {scenario}")
                
#                 context_parts.append(f"\nSCENARIO ANALYSIS READY FOR:")
#                 context_parts.append(f"- {financial_data['scenarios']['current_debt_count']} active debts")
#                 context_parts.append(f"- Total debt amount: ₹{financial_data['scenarios']['total_debt']:,.2f}")
#             elif 'error' in financial_data['scenarios']:
#                 context_parts.append(f"\nSCENARIO ANALYSIS: {financial_data['scenarios']['error']}")
#             elif 'message' in financial_data['scenarios']:
#                 context_parts.append(f"\nSCENARIO ANALYSIS: {financial_data['scenarios']['message']}")
        
#         if 'error' in financial_data:
#             context_parts.append(f"\nNOTE: {financial_data['error']}")
        
#         return "\n".join(context_parts) if context_parts else ""
    
#     @staticmethod
#     async def _get_loan_recommendations(
#         loan_type: str,
#         amount: Optional[float],
#         user_financial_data: Dict[str, Any]
#     ) -> Dict[str, Any]:
#         """Get loan recommendations by WEB SCRAPING real bank websites"""
        
#         try:
#             print(f"Starting web scraping for {loan_type} loan rates...")
            
#             # STEP 1: Scrape real bank websites for current rates
#             scraped_data = await LoanScraperService.scrape_bank_rates(loan_type)
            
#             print(f"Successfully scraped {len(scraped_data)} banks")
            
#             # STEP 2: Format scraped data for LLM
#             formatted_bank_data = LoanScraperService.format_scraped_data_for_llm(scraped_data)
            
#             print(f"Formatted bank data for LLM analysis")
            
#             # STEP 3: Use LLM to analyze with REAL scraped data
#             ai_response = await LLMService.generate_loan_recommendations(
#                 loan_type=loan_type,
#                 amount=amount,
#                 user_debt_data=user_financial_data.get('debt_summary', {}),
#                 scraped_bank_data=formatted_bank_data
#             )
            
#             # STEP 4: Parse and return
#             parsed_data = EducationService._parse_loan_response(ai_response)
            
#             return {
#                 'success': True,
#                 'loan_type': loan_type,
#                 'requested_amount': amount,
#                 'analysis': parsed_data.get('analysis', ai_response),
#                 'recommendations': parsed_data.get('banks', []),
#                 'comparison_table': parsed_data.get('table', None),
#                 'advice': parsed_data.get('advice', ''),
#                 'raw_response': ai_response,
#                 'scraped_banks': scraped_data,
#                 'scraping_success': True
#             }
        
#         except Exception as e:
#             print(f"Error in loan recommendations: {e}")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'fallback_message': f"Unable to fetch current loan rates. Please visit bank websites directly for {loan_type} loan information."
#             }
    
#     @staticmethod
#     def _parse_loan_response(response: str) -> Dict[str, Any]:
#         """Parse the LLM response to extract structured loan data"""
        
#         parsed = {
#             'banks': [],
#             'table': None,
#             'analysis': '',
#             'advice': ''
#         }
        
#         # Extract bank information
#         bank_pattern = r'BANK_START(.*?)BANK_END'
#         banks = re.findall(bank_pattern, response, re.DOTALL)
        
#         for bank_text in banks:
#             bank_info = {}
#             lines = bank_text.strip().split('\n')
#             for line in lines:
#                 if ':' in line:
#                     key, value = line.split(':', 1)
#                     bank_info[key.strip()] = value.strip()
#             if bank_info:
#                 parsed['banks'].append(bank_info)
        
#         # Extract table
#         table_pattern = r'TABLE_START(.*?)TABLE_END'
#         table_match = re.search(table_pattern, response, re.DOTALL)
#         if table_match:
#             parsed['table'] = table_match.group(1).strip()
        
#         # If no structured data found, use the whole response
#         if not parsed['banks']:
#             parsed['analysis'] = response
        
#         return parsed
    
#     @staticmethod
#     def _detect_text_language(text: str) -> Optional[str]:
#         """
#         Auto-detect language from text input
#         Simple detection based on Unicode character ranges
#         """
#         # Count characters from different scripts
#         devanagari = sum(1 for c in text if '\u0900' <= c <= '\u097F')  # Hindi/Marathi
#         bengali = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
#         gujarati = sum(1 for c in text if '\u0A80' <= c <= '\u0AFF')
#         gurmukhi = sum(1 for c in text if '\u0A00' <= c <= '\u0A7F')  # Punjabi
#         tamil = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
#         telugu = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
#         kannada = sum(1 for c in text if '\u0C80' <= c <= '\u0CFF')
#         malayalam = sum(1 for c in text if '\u0D00' <= c <= '\u0D7F')
        
#         # Total non-ASCII characters
#         total_indic = devanagari + bengali + gujarati + gurmukhi + tamil + telugu + kannada + malayalam
        
#         # If more than 30% of text is in Indic script, detect which one
#         if total_indic > len(text) * 0.3:
#             # Find the dominant script
#             scripts = {
#                 'hi-IN': devanagari,  # Hindi uses Devanagari
#                 'bn-IN': bengali,
#                 'gu-IN': gujarati,
#                 'pa-IN': gurmukhi,
#                 'ta-IN': tamil,
#                 'te-IN': telugu,
#                 'kn-IN': kannada,
#                 'ml-IN': malayalam
#             }
            
#             # Get the script with highest count
#             detected = max(scripts.items(), key=lambda x: x[1])
#             if detected[1] > 0:
#                 print(f"🌍 Auto-detected language: {detected[0]}")
#                 return detected[0]
        
#         # Default to English if no Indic script detected
#         print(f"🌍 Auto-detected language: en-IN (English)")
#         return 'en-IN'
    
#     @staticmethod
#     async def get_financial_education_response(
#         user_question: str,
#         clerk_user_id: str,
#         conversation_history: List[Dict] = None,
#         language_code: Optional[str] = None
#     ) -> Dict[str, Any]:
        
#         # Handle inappropriate content
#         if EducationService._check_inappropriate_content(user_question):
#             return {
#                 "success": True,
#                 "response": "I'm here to help with financial questions. Please keep the conversation respectful and professional.",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
        
#         # Handle basic greetings
#         greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
#         if user_question.lower().strip() in greetings:
#             return {
#                 "success": True,
#                 "response": "Hello! I'm your financial advisor assistant. I can help you with budgeting, debt management, investments, credit scores, and loan recommendations. What would you like to know?",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
        
#         try:
#             # PRIORITY 1: Check for loan request FIRST
#             loan_detection = EducationService._detect_loan_request(user_question)
            
#             if loan_detection['is_loan_request']:
#                 print(f"🔍 LOAN REQUEST DETECTED: {loan_detection}")
                
#                 # Fetch user financial data for loan assessment
#                 financial_data = await EducationService._fetch_user_financial_data(
#                     clerk_user_id, 
#                     {'needs_debt_data': True, 'needs_plan_data': False, 'needs_scenario_data': False}
#                 )
                
#                 # Get loan recommendations with WEB SCRAPING
#                 loan_recommendations = await EducationService._get_loan_recommendations(
#                     loan_type=loan_detection['loan_type'],
#                     amount=loan_detection['amount'],
#                     user_financial_data=financial_data
#                 )
                
#                 if loan_recommendations['success']:
#                     return {
#                         "success": True,
#                         "response": loan_recommendations['raw_response'],
#                         "loan_data": loan_recommendations,
#                         "is_loan_recommendation": True,
#                         "timestamp": datetime.utcnow().isoformat()
#                     }
            
#             # PRIORITY 2: Regular financial queries
#             data_needs = EducationService._detect_data_request(user_question)
            
#             print(f"📊 Data needs detected: {data_needs}")
            
#             financial_context = ""
            
#             if any(data_needs.values()):
#                 financial_data = await EducationService._fetch_user_financial_data(clerk_user_id, data_needs)
#                 financial_context = await EducationService._format_financial_context(financial_data)
#                 print(f"✅ Financial context prepared: {len(financial_context)} characters")
            
#             # Build the prompt
#             prompt = f"""
# You are a helpful financial advisor assistant with expertise in personal finance for India.

# User question: {user_question}
# """
            
#             # Add language instruction if provided
#             if language_code and language_code != "en":
#                 language_names = {
#                     'hi-IN': 'Hindi (हिंदी)',
#                     'mr-IN': 'Marathi (मराठी)',
#                     'ta-IN': 'Tamil (தமிழ்)',
#                     'te-IN': 'Telugu (తెలుగు)',
#                     'kn-IN': 'Kannada (ಕನ್ನಡ)',
#                     'gu-IN': 'Gujarati (ગુજરાતી)',
#                     'bn-IN': 'Bengali (বাংলা)',
#                     'ml-IN': 'Malayalam (മലയാളം)',
#                     'pa-IN': 'Punjabi (ਪੰਜਾਬੀ)',
#                     'en-IN': 'English',
#                     'od-IN': 'Odia (ଓଡ଼ିଆ)',
#                     'hi': 'Hindi (हिंदी)',
#                     'mr': 'Marathi (मराठी)',
#                     'ta': 'Tamil (தமிழ்)',
#                     'te': 'Telugu (తెలుగు)',
#                     'kn': 'Kannada (ಕನ್ನಡ)',
#                     'gu': 'Gujarati (ગુજરાતી)',
#                     'bn': 'Bengali (বাংলা)',
#                     'ml': 'Malayalam (മലയാളം)',
#                     'pa': 'Punjabi (ਪੰਜਾਬੀ)',
#                     'en': 'English',
#                     'od': 'Odia (ଓଡ଼ିଆ)'
#                 }
                
#                 language_name = language_names.get(language_code, 'Hindi')
                
#                 prompt += f"""
# CRITICAL LANGUAGE INSTRUCTION:
# **YOU MUST RESPOND ENTIRELY IN {language_name}.**
# - The user asked their question in {language_name}
# - Your ENTIRE response must be in {language_name}
# - Do NOT use English unless the user specifically asked in English
# - Use {language_name} script and vocabulary throughout your answer
# - This is MANDATORY - respond in {language_name} only
# """
            
#             if financial_context:
#                 prompt += f"""
# IMPORTANT - USER'S CURRENT FINANCIAL DATA:
# {financial_context}

# CRITICAL INSTRUCTIONS:
# - Use this REAL data to provide SPECIFIC, DETAILED, ACTIONABLE advice
# - Reference EXACT amounts, debts, and numbers from the data
# - If user asks for repayment strategies, create a DETAILED MONTH-BY-MONTH payment plan
# - If user asks for "monthwise plan", provide a table showing Month 1, Month 2, etc. with specific payment allocations
# - Include specific calculations showing how each strategy would work
# - Be comprehensive and detailed - don't give generic advice
# """
            
#             prompt += """
# Instructions:
# - If the question is about finance, money, budgeting, investing, debt, credit, loans, savings, etc. - provide DETAILED, SPECIFIC financial advice
# - If user asks about their current financial situation, use the provided financial data and give EXACT numbers
# - If user asks about repayment strategies, CREATE A DETAILED PLAN with:
#   * Month-by-month breakdown
#   * Exact payment amounts for each debt
#   * Total interest saved
#   * Payoff timeline
#   * Comparison of different strategies (Avalanche vs Snowball vs Optimal)
# - If user asks for "monthwise plan" or "month-wise plan", create a detailed table showing:
#   * Each month (Month 1, Month 2, etc.)
#   * Payments to each specific debt
#   * Remaining balances after each payment
#   * Interest saved
#   * Progress towards debt freedom
# - If user asks about what-if scenarios, explain the types of analysis available

# FORMATTING RULES (VERY IMPORTANT):
# - Use **bold** for headings and important terms
# - Use bullet points (•) for lists
# - Use numbered lists (1., 2., 3.) for step-by-step instructions
# - Add blank lines between sections for readability
# - Use ━━━ separators for major sections
# - Format numbers with commas: ₹1,50,000 not ₹150000
# - Use proper spacing around symbols
# - Make tables clean and aligned
# - Use emojis sparingly (only for key highlights like ✓, ✗, 💡)

# RESPONSE STRUCTURE:
# Start with a brief 1-2 line summary, then:

# **Key Points:**
# - Point 1
# - Point 2
# - Point 3

# **Detailed Analysis:**
# [Your detailed content here with proper formatting]

# **Recommendations:**
# 1. Action 1
# 2. Action 2
# 3. Action 3

# **Next Steps:**
# What user should do next

# - Write in a conversational but DETAILED and WELL-FORMATTED style
# - Use ₹ currency when discussing money
# - Be professional, specific, and data-driven
# - If you reference their financial data, be VERY specific about amounts and details
# - DO NOT give generic advice - use their ACTUAL numbers
# - ALWAYS format your response properly with headings, bullets, and spacing

# Answer the user's question with MAXIMUM detail, specificity, and PERFECT formatting.
# """
            
#             ai_response = await LLMService.generate_credit_advice(prompt, model="llama-3.3-70b-versatile")
            
#             return {
#                 "success": True,
#                 "response": ai_response,
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "used_financial_data": bool(financial_context),
#                 "is_loan_recommendation": False
#             }
        
#         except Exception as e:
#             print(f"❌ Education service error: {e}")
            
#             return {
#                 "success": True,
#                 "response": "I'm here to help with your financial questions! Ask me about budgeting, debt management, investments, loan recommendations, and more.",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
    
#     @staticmethod
#     async def get_suggested_topics():
#         return [
#             {
#                 "title": "Get Loan Recommendations",
#                 "description": "Find the best loan offers from Indian banks with REAL rates",
#                 "category": "personal",
#                 "example_question": "I need a personal loan of ₹5 lakhs"
#             },
#             {
#                 "title": "My Current Debts",
#                 "description": "Review your current debt situation",
#                 "category": "personal",
#                 "example_question": "What are my current debts?"
#             },
#             {
#                 "title": "Repayment Strategies",
#                 "description": "Explore debt payoff strategies with month-by-month plans",
#                 "category": "personal",
#                 "example_question": "What repayment strategies are available to me?"
#             },
#             {
#                 "title": "Month-wise Payment Plan",
#                 "description": "Get a detailed monthly breakdown of debt payments",
#                 "category": "personal",
#                 "example_question": "Give me a monthwise plan"
#             },
#             {
#                 "title": "What-If Scenarios",
#                 "description": "Analyze different financial scenarios",
#                 "category": "personal",
#                 "example_question": "What scenarios can I analyze for my debt?"
#             },
#             {
#                 "title": "Budgeting Basics",
#                 "description": "Learn to create and manage budgets",
#                 "category": "budgeting",
#                 "example_question": "How do I create a monthly budget?"
#             },
#             {
#                 "title": "Debt Management",
#                 "description": "Strategies to pay off debt faster", 
#                 "category": "debt",
#                 "example_question": "How should I pay off my credit card debt?"
#             },
#             {
#                 "title": "Investment Guide",
#                 "description": "Getting started with investments",
#                 "category": "investment",
#                 "example_question": "Should I invest in mutual funds or fixed deposits?"
#             },
#             {
#                 "title": "Credit Score Tips",
#                 "description": "Improving your credit score",
#                 "category": "credit",
#                 "example_question": "How can I improve my credit score?"
#             }
#         ]
    
#     @staticmethod
#     async def get_chat_history(clerk_user_id: str, limit: int = 20):
#         return []


from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.llm_service import LLMService
from app.services.debt_service import DebtService
from app.services.plan_service import PlanService
from app.services.scenario_service import ScenarioService
from app.services.loan_scraper_service import LoanScraperService
from app.models.user import User
import re


class EducationService:
    
    @staticmethod
    def _check_inappropriate_content(message: str) -> bool:
        """Check if message contains inappropriate content"""
        inappropriate_words = [
            'fuck', 'shit', 'damn', 'bitch', 'ass', 'hell', 'crap',
            'stupid', 'idiot', 'moron', 'hate'
        ]
        message_lower = message.lower()
        return any(word in message_lower for word in inappropriate_words)
    
    @staticmethod
    def _detect_loan_request(message: str) -> Dict[str, Any]:
        """Detect if user is requesting loan recommendations"""
        message_lower = message.lower()
        
        # Loan keywords
        loan_keywords = ['loan', 'borrow', 'finance', 'credit']
        loan_types = {
            'personal': ['personal loan', 'personal', 'quick loan'],
            'home': ['home loan', 'housing loan', 'mortgage', 'property loan'],
            'car': ['car loan', 'auto loan', 'vehicle loan'],
            'education': ['education loan', 'student loan', 'study loan'],
            'business': ['business loan', 'commercial loan', 'msme loan']
        }
        
        # Check if it's a loan request
        is_loan_request = any(keyword in message_lower for keyword in loan_keywords)
        
        # Determine loan type
        loan_type = None
        for ltype, keywords in loan_types.items():
            if any(keyword in message_lower for keyword in keywords):
                loan_type = ltype
                break
        
        # Extract amount (simple regex pattern)
        amount_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lakhs|cr|crore)?',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lakhs|cr|crore)',
            r'(\d+(?:,\d+)*)'
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, message_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                # Check for lakh/crore
                if 'lakh' in message_lower:
                    amount *= 100000
                elif 'cr' in message_lower or 'crore' in message_lower:
                    amount *= 10000000
                break
        
        return {
            'is_loan_request': is_loan_request,
            'loan_type': loan_type or 'personal',
            'amount': amount
        }
    
    @staticmethod
    def _detect_data_request(message: str) -> Dict[str, bool]:
        """Detect what type of user data is being requested - WITH FULL MULTILINGUAL SUPPORT"""
        message_lower = message.lower()
        
        # Keywords for different data types - COMPREHENSIVE MULTILINGUAL
        debt_keywords = [
            # English
            'debt', 'debts', 'owe', 'outstanding', 'borrowed', 
            'my debt', 'current debt', 'loan', 'loans', 'my loan', 'my loans',
            
            # Hindi (हिंदी)
            'कर्ज', 'कर्ज़', 'उधार', 'मेरा कर्ज', 'मेरे कर्ज', 'लोन',
            'क़र्ज़', 'क़र्ज', 'ऋण', 'मेरा ऋण',
            
            # Marathi (मराठी)
            'कर्ज', 'माझे कर्ज', 'माझा कर्ज', 'उसने', 'कर्जे',
            
            # Bengali (বাংলা)
            'ঋণ', 'ধার', 'আমার ঋণ', 'বর্তমান ঋণ', 'লোন',
            'ঋণের', 'আমার ধার', 'কর্জ',
            
            # Tamil (தமிழ்)
            'கடன்', 'என் கடன்', 'கடன்கள்', 'வாங்கிய கடன்',
            
            # Telugu (తెలుగు)
            'అప్పు', 'నా అప్పు', 'అప్పులు', 'రుణం', 'నా రుణం',
            
            # Kannada (ಕನ್ನಡ)
            'ಸಾಲ', 'ನನ್ನ ಸಾಲ', 'ಸಾಲಗಳು', 'ಋಣ',
            
            # Malayalam (മലയാളം)
            'കടം', 'എന്റെ കടം', 'കടങ്ങൾ', 'വായ്പ', 'എന്റെ വായ്പ',
            
            # Gujarati (ગુજરાતી)
            'દેવું', 'દેવાં', 'મારું દેવું', 'લોન', 'ઋણ',
            
            # Punjabi (ਪੰਜਾਬੀ)
            'ਕਰਜ਼ਾ', 'ਮੇਰਾ ਕਰਜ਼ਾ', 'ਕਰਜ਼ੇ', 'ਉਧਾਰ',
            
            # Odia (ଓଡ଼ିଆ)
            'ଋଣ', 'ମୋର ଋଣ', 'ଧାର', 'ଲୋନ୍'
        ]
        
        plan_keywords = [
            # English
            'repayment plan', 'payment plan', 'strategy', 'payoff plan', 
            'debt plan', 'my plan', 'current plan', 'repayment',
            'pay off', 'payoff', 'clear debt', 'avalanche', 'snowball', 'optimal',
            'monthwise', 'month wise', 'month-wise',
            
            # Hindi
            'चुकौती योजना', 'योजना', 'रणनीति', 'भुगतान योजना',
            'चुकौती', 'कर्ज चुकाना', 'वापसी योजना',
            
            # Marathi
            'परतफेड योजना', 'योजना', 'रणनीती', 'कर्ज फेडणे',
            
            # Bengali
            'পরিশোধ পরিকল্পনা', 'পরিকল্পনা', 'কৌশল', 'পেমেন্ট প্ল্যান',
            'পরিশোধ', 'ঋণ শোধ',
            
            # Tamil
            'திருப்பிச் செலுத்தும் திட்டம்', 'திட்டம்', 'உத்தி',
            'கடன் அடைக்க',
            
            # Telugu
            'పరిహార ప్రణాళిక', 'ప్రణాళిక', 'వ్యూహం', 'అప్పు తీర్చడం',
            
            # Kannada
            'ಮರುಪಾವತಿ ಯೋಜನೆ', 'ಯೋಜನೆ', 'ತಂತ್ರ', 'ಸಾಲ ತೀರಿಸು',
            
            # Malayalam
            'തിരിച്ചടവ് പദ്ധതി', 'പദ്ധതി', 'തന്ത്രം', 'കടം വീട്ടൽ',
            
            # Gujarati
            'ચુકવણી યોજના', 'યોજના', 'વ્યૂહરચના', 'દેવું ચૂકવવું',
            
            # Punjabi
            'ਵਾਪਸੀ ਯੋਜਨਾ', 'ਯੋਜਨਾ', 'ਰਣਨੀਤੀ', 'ਕਰਜ਼ਾ ਚੁਕਾਉਣਾ',
            
            # Odia
            'ପରିଶୋଧ ଯୋଜନା', 'ଯୋଜନା', 'ରଣନୀତି', 'ଋଣ ପରିଶୋଧ'
        ]
        
        scenario_keywords = [
            # English
            'what if', 'scenario', 'scenarios', 'simulation', 'compare', 
            'different plan', 'my scenario', 'extra payment', 'windfall',
            
            # Hindi
            'अगर', 'परिदृश्य', 'तुलना', 'सिमुलेशन', 'क्या होगा',
            
            # Marathi
            'जर', 'परिस्थिती', 'तुलना', 'काय होईल',
            
            # Bengali
            'যদি', 'পরিস্থিতি', 'তুলনা', 'সিমুলেশন', 'কি হবে',
            
            # Tamil
            'என்றால்', 'சூழ்நிலை', 'ஒப்பீடு', 'என்ன நடக்கும்',
            
            # Telugu
            'ఏమైతే', 'పరిస్థితి', 'పోలిక', 'ఏమవుతుంది',
            
            # Kannada
            'ಆದರೆ', 'ಸನ್ನಿವೇಶ', 'ಹೋಲಿಕೆ', 'ಏನಾಗುತ್ತದೆ',
            
            # Malayalam
            'എങ്കിൽ', 'സാഹചര്യം', 'താരതമ്യം', 'എന്താകും',
            
            # Gujarati
            'જો', 'પરિસ્થિતિ', 'તુલના', 'શું થશે',
            
            # Punjabi
            'ਜੇ', 'ਸਥਿਤੀ', 'ਤੁਲਨਾ', 'ਕੀ ਹੋਵੇਗਾ',
            
            # Odia
            'ଯଦି', 'ପରିସ୍ଥିତି', 'ତୁଳନା', 'କଣ ହେବ'
        ]
        
        # Voice-related keywords that indicate user wants debt info
        voice_debt_phrases = [
            # English
            'what are my', 'show my', 'tell me my', 'give me my',
            'what is my', 'how much do i owe', 'how much debt',
            'current', 'existing', 'have', 'got',
            
            # Hindi
            'मेरा क्या', 'मेरे', 'मुझे बताओ', 'मेरा', 'कितना', 'मेरे पास',
            
            # Marathi  
            'माझा काय', 'माझे', 'मला सांगा', 'माझा', 'किती', 'माझ्याकडे',
            
            # Bengali
            'আমার কি', 'আমার', 'আমাকে বলুন', 'কত', 'আছে',
            
            # Tamil
            'என் என்ன', 'என்', 'எனக்கு சொல்லுங்கள்', 'எவ்வளவு',
            
            # Telugu
            'నా ఏమిటి', 'నా', 'నాకు చెప్పండి', 'ఎంత',
            
            # Kannada
            'ನನ್ನ ಏನು', 'ನನ್ನ', 'ನನಗೆ ಹೇಳಿ', 'ಎಷ್ಟು',
            
            # Malayalam
            'എന്റെ എന്താണ്', 'എന്റെ', 'എന്നോട് പറയൂ', 'എത്ര',
            
            # Gujarati
            'મારું શું', 'મારું', 'મને કહો', 'કેટલું',
            
            # Punjabi
            'ਮੇਰਾ ਕੀ', 'ਮੇਰਾ', 'ਮੈਨੂੰ ਦੱਸੋ', 'ਕਿੰਨਾ',
            
            # Odia
            'ମୋର କଣ', 'ମୋର', 'ମୋତେ କୁହ', 'କେତେ'
        ]
        
        # Check if message is asking about their debt data
        needs_debt = any(keyword in message_lower for keyword in debt_keywords)
        
        # ENHANCED: Also detect when voice users ask conversational questions
        if not needs_debt:
            # Check for patterns like "what are my debts", "show my loans"
            for phrase in voice_debt_phrases:
                if phrase in message_lower:
                    # Check if any debt-related word follows
                    for debt_word in debt_keywords:
                        if debt_word in message_lower:
                            needs_debt = True
                            print(f"🔍 Detected debt request via phrase: '{phrase}' + '{debt_word}'")
                            break
                if needs_debt:
                    break
        
        if needs_debt:
            print(f"✅ DEBT DATA WILL BE FETCHED")
        
        return {
            'needs_debt_data': needs_debt,
            'needs_plan_data': any(keyword in message_lower for keyword in plan_keywords),
            'needs_scenario_data': any(keyword in message_lower for keyword in scenario_keywords)
        }
    
    @staticmethod
    async def _fetch_user_financial_data(clerk_user_id: str, data_needs: Dict[str, bool]) -> Dict[str, Any]:
        """Fetch relevant user financial data based on detected needs"""
        financial_data = {}
        
        try:
            if data_needs['needs_debt_data']:
                debts = await DebtService.get_user_debts(clerk_user_id)
                print(f"DEBUG: Fetched {len(debts)} debts")
                
                financial_data['debts'] = debts
                
                if debts:
                    total_debt = 0
                    total_minimum_payment = 0
                    
                    for debt in debts:
                        try:
                            total_debt += debt.total_amount or 0
                            min_pay = getattr(debt, 'min_payment', 0) or 0
                            total_minimum_payment += min_pay
                        except Exception as e:
                            print(f"Error processing debt: {e}")
                            continue
                    
                    financial_data['debt_summary'] = {
                        'total_debt': total_debt,
                        'total_minimum_payment': total_minimum_payment,
                        'debt_count': len(debts)
                    }
            
            if data_needs['needs_plan_data']:
                try:
                    debt_summary = await PlanService.get_user_debt_summary(clerk_user_id)
                    
                    if debt_summary["debt_count"] > 0:
                        plan_info = {
                            "available_strategies": [
                                {
                                    "name": "Debt Avalanche Strategy",
                                    "description": "Pay minimums + focus extra on highest APR debt (saves most money)",
                                    "best_for": "Minimizing total interest paid"
                                },
                                {
                                    "name": "Debt Snowball Strategy", 
                                    "description": "Pay minimums + focus extra on smallest balance (psychological wins)",
                                    "best_for": "Building momentum and motivation"
                                },
                                {
                                    "name": "Mathematical Optimal Strategy",
                                    "description": "Mathematically optimized allocation for fastest payoff",
                                    "best_for": "Maximum efficiency"
                                }
                            ],
                            "total_debt": debt_summary["total_debt"],
                            "monthly_minimums": debt_summary["monthly_minimums"],
                            "available_budget": debt_summary["available_budget"]
                        }
                        financial_data['plans'] = plan_info
                    else:
                        financial_data['plans'] = {"message": "No active debts found for repayment planning"}
                        
                except Exception as e:
                    print(f"Error fetching plans: {e}")
                    financial_data['plans'] = {"error": f"Could not fetch plan information: {str(e)}"}
            
            if data_needs['needs_scenario_data']:
                try:
                    debt_summary = await PlanService.get_user_debt_summary(clerk_user_id)
                    
                    if debt_summary["debt_count"] > 0:
                        scenario_info = {
                            "available_scenarios": [
                                "Extra Payment: See impact of paying extra each month",
                                "Windfall: Apply lump sum to debts", 
                                "Budget Reduction: What if available budget decreases",
                                "Interest Rate Change: Impact of rate changes",
                                "Debt Consolidation: Combine debts into single loan"
                            ],
                            "current_debt_count": debt_summary["debt_count"],
                            "total_debt": debt_summary["total_debt"]
                        }
                        financial_data['scenarios'] = scenario_info
                    else:
                        financial_data['scenarios'] = {"message": "No active debts found for scenario analysis"}
                        
                except Exception as e:
                    print(f"Error fetching scenarios: {e}")
                    financial_data['scenarios'] = {"error": f"Could not fetch scenario information: {str(e)}"}
                
        except Exception as e:
            print(f"Error fetching financial data: {e}")
            financial_data['error'] = f"Could not fetch some financial data: {str(e)}"
        
        return financial_data
    
    @staticmethod
    async def _format_financial_context(financial_data: Dict[str, Any]) -> str:
        """Format financial data into context for the LLM"""
        context_parts = []
        
        if 'debts' in financial_data and financial_data['debts']:
            context_parts.append("USER'S CURRENT DEBTS:")
            for i, debt in enumerate(financial_data['debts']):
                try:
                    name = debt.name
                    total_amount = debt.total_amount
                    interest_rate = debt.interest_rate
                    min_payment = getattr(debt, 'min_payment', 0) or 0
                    
                    debt_info = f"- {name}: ₹{total_amount:,.2f} total amount, {interest_rate}% APR, ₹{min_payment:,.2f} minimum payment"
                    context_parts.append(debt_info)
                    
                except Exception as e:
                    print(f"Error formatting debt {i+1}: {e}")
                    context_parts.append(f"- Debt information unavailable (Error: {str(e)})")
            
            if 'debt_summary' in financial_data:
                summary = financial_data['debt_summary']
                context_parts.append(f"\nDEBT SUMMARY:")
                context_parts.append(f"- Total debt: ₹{summary['total_debt']:,.2f}")
                context_parts.append(f"- Total minimum payments: ₹{summary['total_minimum_payment']:,.2f}")
                context_parts.append(f"- Number of debts: {summary['debt_count']}")
        
        if 'plans' in financial_data and financial_data['plans']:
            if 'available_strategies' in financial_data['plans']:
                context_parts.append("\nAVAILABLE REPAYMENT STRATEGIES:")
                for strategy in financial_data['plans']['available_strategies']:
                    strategy_info = f"- {strategy['name']}: {strategy['description']} (Best for: {strategy['best_for']})"
                    context_parts.append(strategy_info)
                
                context_parts.append(f"\nPLANNING DETAILS:")
                context_parts.append(f"- Total debt to pay off: ₹{financial_data['plans']['total_debt']:,.2f}")
                context_parts.append(f"- Required minimum payments: ₹{financial_data['plans']['monthly_minimums']:,.2f}")
                context_parts.append(f"- Available budget for extra payments: ₹{financial_data['plans']['available_budget']:,.2f}")
            elif 'error' in financial_data['plans']:
                context_parts.append(f"\nREPAYMENT PLANS: {financial_data['plans']['error']}")
            elif 'message' in financial_data['plans']:
                context_parts.append(f"\nREPAYMENT PLANS: {financial_data['plans']['message']}")
        
        if 'scenarios' in financial_data and financial_data['scenarios']:
            if 'available_scenarios' in financial_data['scenarios']:
                context_parts.append("\nAVAILABLE WHAT-IF SCENARIOS:")
                for scenario in financial_data['scenarios']['available_scenarios']:
                    context_parts.append(f"- {scenario}")
                
                context_parts.append(f"\nSCENARIO ANALYSIS READY FOR:")
                context_parts.append(f"- {financial_data['scenarios']['current_debt_count']} active debts")
                context_parts.append(f"- Total debt amount: ₹{financial_data['scenarios']['total_debt']:,.2f}")
            elif 'error' in financial_data['scenarios']:
                context_parts.append(f"\nSCENARIO ANALYSIS: {financial_data['scenarios']['error']}")
            elif 'message' in financial_data['scenarios']:
                context_parts.append(f"\nSCENARIO ANALYSIS: {financial_data['scenarios']['message']}")
        
        if 'error' in financial_data:
            context_parts.append(f"\nNOTE: {financial_data['error']}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    @staticmethod
    async def _get_loan_recommendations(
        loan_type: str,
        amount: Optional[float],
        user_financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get loan recommendations by WEB SCRAPING real bank websites"""
        
        try:
            print(f"Starting web scraping for {loan_type} loan rates...")
            
            # STEP 1: Scrape real bank websites for current rates
            scraped_data = await LoanScraperService.scrape_bank_rates(loan_type)
            
            print(f"Successfully scraped {len(scraped_data)} banks")
            
            # STEP 2: Format scraped data for LLM
            formatted_bank_data = LoanScraperService.format_scraped_data_for_llm(scraped_data)
            
            print(f"Formatted bank data for LLM analysis")
            
            # STEP 3: Use LLM to analyze with REAL scraped data
            ai_response = await LLMService.generate_loan_recommendations(
                loan_type=loan_type,
                amount=amount,
                user_debt_data=user_financial_data.get('debt_summary', {}),
                scraped_bank_data=formatted_bank_data
            )
            
            # STEP 4: Parse and return
            parsed_data = EducationService._parse_loan_response(ai_response)
            
            return {
                'success': True,
                'loan_type': loan_type,
                'requested_amount': amount,
                'analysis': parsed_data.get('analysis', ai_response),
                'recommendations': parsed_data.get('banks', []),
                'comparison_table': parsed_data.get('table', None),
                'advice': parsed_data.get('advice', ''),
                'raw_response': ai_response,
                'scraped_banks': scraped_data,
                'scraping_success': True
            }
            
        except Exception as e:
            print(f"Error in loan recommendations: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_message': f"Unable to fetch current loan rates. Please visit bank websites directly for {loan_type} loan information."
            }
    
    @staticmethod
    def _parse_loan_response(response: str) -> Dict[str, Any]:
        """Parse the LLM response to extract structured loan data"""
        
        parsed = {
            'banks': [],
            'table': None,
            'analysis': '',
            'advice': ''
        }
        
        # Extract bank information
        bank_pattern = r'BANK_START(.*?)BANK_END'
        banks = re.findall(bank_pattern, response, re.DOTALL)
        
        for bank_text in banks:
            bank_info = {}
            lines = bank_text.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    bank_info[key.strip()] = value.strip()
            if bank_info:
                parsed['banks'].append(bank_info)
        
        # Extract table
        table_pattern = r'TABLE_START(.*?)TABLE_END'
        table_match = re.search(table_pattern, response, re.DOTALL)
        if table_match:
            parsed['table'] = table_match.group(1).strip()
        
        # If no structured data found, use the whole response
        if not parsed['banks']:
            parsed['analysis'] = response
        
        return parsed
    
    @staticmethod
    async def get_financial_education_response(
        user_question: str,
        clerk_user_id: str,
        conversation_history: List[Dict] = None,
        language_code: Optional[str] = None  # ← ADDED THIS PARAMETER
    ) -> Dict[str, Any]:
        
        # Handle inappropriate content
        if EducationService._check_inappropriate_content(user_question):
            return {
                "success": True,
                "response": "I'm here to help with financial questions. Please keep the conversation respectful and professional.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Handle basic greetings
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 
                     'namaste', 'namaskar', 'vanakkam', 'nomoshkar']
        if user_question.lower().strip() in greetings:
            return {
                "success": True,
                "response": "Hello! I'm your financial advisor assistant. I can help you with budgeting, debt management, investments, credit scores, and loan recommendations with real-time rates from Indian banks!",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # PRIORITY 1: Check for loan request FIRST
            loan_detection = EducationService._detect_loan_request(user_question)
            
            if loan_detection['is_loan_request']:
                print(f"🔍 LOAN REQUEST DETECTED: {loan_detection}")
                
                # Fetch user financial data for loan assessment
                financial_data = await EducationService._fetch_user_financial_data(
                    clerk_user_id, 
                    {'needs_debt_data': True, 'needs_plan_data': False, 'needs_scenario_data': False}
                )
                
                # Get loan recommendations with WEB SCRAPING
                loan_recommendations = await EducationService._get_loan_recommendations(
                    loan_type=loan_detection['loan_type'],
                    amount=loan_detection['amount'],
                    user_financial_data=financial_data
                )
                
                if loan_recommendations['success']:
                    return {
                        "success": True,
                        "response": loan_recommendations['raw_response'],
                        "loan_data": loan_recommendations,
                        "is_loan_recommendation": True,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            # PRIORITY 2: Regular financial queries
            data_needs = EducationService._detect_data_request(user_question)
            
            print(f"📊 Data needs detected: {data_needs}")
            
            financial_context = ""
            
            if any(data_needs.values()):
                financial_data = await EducationService._fetch_user_financial_data(clerk_user_id, data_needs)
                financial_context = await EducationService._format_financial_context(financial_data)
                print(f"✅ Financial context prepared: {len(financial_context)} characters")
            
            # Build the prompt
            prompt = f"""
You are a helpful financial advisor assistant with expertise in personal finance for India.

User question: {user_question}
"""
            
            # Add language instruction ONLY if non-English
            if language_code and language_code not in ["en", "en-IN", "english", "English"]:
                language_names = {
                    'hi-IN': 'Hindi (हिंदी)',
                    'mr-IN': 'Marathi (मराठी)',
                    'ta-IN': 'Tamil (தமிழ்)',
                    'te-IN': 'Telugu (తెలుగు)',
                    'kn-IN': 'Kannada (ಕನ್ನಡ)',
                    'gu-IN': 'Gujarati (ગુજરાતી)',
                    'bn-IN': 'Bengali (বাংলা)',
                    'ml-IN': 'Malayalam (മലയാളം)',
                    'pa-IN': 'Punjabi (ਪੰਜਾਬੀ)',
                    'od-IN': 'Odia (ଓଡ଼ିଆ)',
                    'hi': 'Hindi (हिंदी)',
                    'mr': 'Marathi (मराठी)',
                    'ta': 'Tamil (தமிழ்)',
                    'te': 'Telugu (తెలుగు)',
                    'kn': 'Kannada (ಕನ್ನಡ)',
                    'gu': 'Gujarati (ગુજરાતી)',
                    'bn': 'Bengali (বাংলা)',
                    'ml': 'Malayalam (മലയാളം)',
                    'pa': 'Punjabi (ਪੰਜਾਬੀ)',
                    'od': 'Odia (ଓଡ଼ିଆ)'
                }
                
                language_name = language_names.get(language_code, 'Hindi')
                
                prompt += f"""
CRITICAL LANGUAGE INSTRUCTION:
**YOU MUST RESPOND ENTIRELY IN {language_name}.**
- The user asked their question in {language_name}
- Your ENTIRE response must be in {language_name}
- Do NOT use English unless the user specifically asked in English
- Use {language_name} script and vocabulary throughout your answer
- This is MANDATORY - respond in {language_name} only
"""
            
            if financial_context:
                prompt += f"""
IMPORTANT - USER'S CURRENT FINANCIAL DATA:
{financial_context}

CRITICAL INSTRUCTIONS:
- Use this REAL data to provide SPECIFIC, DETAILED, ACTIONABLE advice
- Reference EXACT amounts, debts, and numbers from the data
- If user asks for repayment strategies, create a DETAILED MONTH-BY-MONTH payment plan
- If user asks for "monthwise plan", provide a table showing Month 1, Month 2, etc. with specific payment allocations
- Include specific calculations showing how each strategy would work
- Be comprehensive and detailed - don't give generic advice
"""
            
            prompt += """
Instructions:
- If the question is about finance, money, budgeting, investing, debt, credit, loans, savings, etc. - provide DETAILED, SPECIFIC financial advice
- If user asks about their current financial situation, use the provided financial data and give EXACT numbers
- If user asks about repayment strategies, CREATE A DETAILED PLAN with:
  * Month-by-month breakdown
  * Exact payment amounts for each debt
  * Total interest saved
  * Payoff timeline
  * Comparison of different strategies (Avalanche vs Snowball vs Optimal)
- If user asks for "monthwise plan" or "month-wise plan", create a detailed table showing:
  * Each month (Month 1, Month 2, etc.)
  * Payments to each specific debt
  * Remaining balances after each payment
  * Interest saved
  * Progress towards debt freedom
- If user asks about what-if scenarios, explain the types of analysis available

FORMATTING RULES (VERY IMPORTANT):
- Use **bold** for headings and important terms
- Use bullet points (•) for lists
- Use numbered lists (1., 2., 3.) for step-by-step instructions
- Add blank lines between sections for readability
- Use ━━━ separators for major sections
- Format numbers with commas: ₹1,50,000 not ₹150000
- Use proper spacing around symbols
- Make tables clean and aligned
- Use emojis sparingly (only for key highlights like ✓, ✗, 💡)

RESPONSE STRUCTURE:
Start with a brief 1-2 line summary, then:

**Key Points:**
- Point 1
- Point 2
- Point 3

**Detailed Analysis:**
[Your detailed content here with proper formatting]

**Recommendations:**
1. Action 1
2. Action 2
3. Action 3

**Next Steps:**
What user should do next

- Write in a conversational but DETAILED and WELL-FORMATTED style
- Use ₹ currency when discussing money
- Be professional, specific, and data-driven
- If you reference their financial data, be VERY specific about amounts and details
- DO NOT give generic advice - use their ACTUAL numbers
- ALWAYS format your response properly with headings, bullets, and spacing

Answer the user's question with MAXIMUM detail, specificity, and PERFECT formatting.
"""
            
            ai_response = await LLMService.generate_credit_advice(prompt, model="llama-3.3-70b-versatile")
            
            return {
                "success": True,
                "response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "used_financial_data": bool(financial_context),
                "is_loan_recommendation": False
            }
            
        except Exception as e:
            print(f"❌ Education service error: {e}")
            
            return {
                "success": True,
                "response": "I'm here to help with your financial questions! Ask me about budgeting, debt management, investments, loan recommendations, and more.",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def get_suggested_topics():
        return [
            {
                "title": "Get Loan Recommendations",
                "description": "Find the best loan offers from Indian banks with REAL rates",
                "category": "personal",
                "example_question": "I need a personal loan of ₹5 lakhs"
            },
            {
                "title": "My Current Debts",
                "description": "Review your current debt situation",
                "category": "personal",
                "example_question": "What are my current debts?"
            },
            {
                "title": "Repayment Strategies",
                "description": "Explore debt payoff strategies with month-by-month plans",
                "category": "personal",
                "example_question": "What repayment strategies are available to me?"
            },
            {
                "title": "Month-wise Payment Plan",
                "description": "Get a detailed monthly breakdown of debt payments",
                "category": "personal",
                "example_question": "Give me a monthwise plan"
            },
            {
                "title": "What-If Scenarios",
                "description": "Analyze different financial scenarios",
                "category": "personal",
                "example_question": "What scenarios can I analyze for my debt?"
            },
            {
                "title": "Budgeting Basics",
                "description": "Learn to create and manage budgets",
                "category": "budgeting",
                "example_question": "How do I create a monthly budget?"
            },
            {
                "title": "Debt Management",
                "description": "Strategies to pay off debt faster", 
                "category": "debt",
                "example_question": "How should I pay off my credit card debt?"
            },
            {
                "title": "Investment Guide",
                "description": "Getting started with investments",
                "category": "investment",
                "example_question": "Should I invest in mutual funds or fixed deposits?"
            },
            {
                "title": "Credit Score Tips",
                "description": "Improving your credit score",
                "category": "credit",
                "example_question": "How can I improve my credit score?"
            }
        ]
    
    @staticmethod
    async def get_chat_history(clerk_user_id: str, limit: int = 20):
        return []