# # app/services/education_service.py
# from typing import List, Dict, Any
# from datetime import datetime
# from app.services.llm_service import LLMService
# from app.models.user import User

# class EducationService:
    
#     @staticmethod
#     def _check_inappropriate_content(message: str) -> bool:
#         """Check if message contains inappropriate content"""
#         inappropriate_words = [
#             'fuck', 'shit', 'damn', 'bitch', 'ass', 'hell', 'crap',
#             'stupid', 'idiot', 'moron', 'premanand', 'hate'
#         ]
#         message_lower = message.lower()
#         return any(word in message_lower for word in inappropriate_words)
    
#     @staticmethod
#     async def get_financial_education_response(
#         user_question: str,
#         clerk_user_id: str,
#         conversation_history: List[Dict] = None
#     ) -> Dict[str, Any]:
        
#         # Handle inappropriate content
#         if EducationService._check_inappropriate_content(user_question):
#             return {
#                 "success": True,
#                 "response": "you son of a bitch go fuck ur self",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
        
#         # Handle basic greetings
#         greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
#         if user_question.lower().strip() in greetings:
#             return {
#                 "success": True,
#                 "response": "Hello! I'm your financial advisor assistant. I can help you with budgeting, debt management, investments, credit scores, and financial planning. What would you like to know?",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
        
#         try:
#             # Smarter prompt that doesn't force financial advice on everything
#             prompt = f"""
#             You are a helpful assistant with expertise in personal finance.
            
#             User question: {user_question}
            
#             Instructions:
#             - If the question is about finance, money, budgeting, investing, debt, credit, loans, savings, etc. - provide helpful financial advice for someone in India
#             - If the question is NOT about finance (like math, general questions, etc.) - answer briefly and then suggest how I can help with financial topics
#             - Write in a conversational chat style with no markdown formatting
#             - Keep responses concise and helpful
#             - Use ₹ currency when discussing money
#             - Be professional and friendly
            
#             Answer the user's question directly and helpfully.
#             """
            
#             ai_response = await LLMService.generate_credit_advice(prompt, model="llama-3.3-70b-versatile")
            
#             return {
#                 "success": True,
#                 "response": ai_response,
#                 "timestamp": datetime.utcnow().isoformat()
#             }
            
#         except Exception as e:
#             print(f"Education service error: {e}")
            
#             return {
#                 "success": True,
#                 "response": "I'm here to help with your financial questions! Ask me about budgeting, debt management, investments, or any other money-related topics.",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
    
#     @staticmethod
#     async def get_suggested_topics():
#         return [
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
#                 "title": "Emergency Fund",
#                 "description": "Building financial security",
#                 "category": "savings",
#                 "example_question": "How much emergency fund do I need?"
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
# # app/services/education_service.py
# from typing import List, Dict, Any, Optional
# from datetime import datetime
# from app.services.llm_service import LLMService
# from app.services.debt_service import DebtService
# # Comment out these imports if the services don't exist yet
# # from app.services.plan_service import PlanService
# # from app.services.scenario_service import ScenarioService
# from app.models.user import User

# class EducationService:
    
#     @staticmethod
#     def _check_inappropriate_content(message: str) -> bool:
#         """Check if message contains inappropriate content"""
#         inappropriate_words = [
#             'fuck', 'shit', 'damn', 'bitch', 'ass', 'hell', 'crap',
#             'stupid', 'idiot', 'moron', 'premanand', 'hate'
#         ]
#         message_lower = message.lower()
#         return any(word in message_lower for word in inappropriate_words)
    
#     @staticmethod
#     def _detect_data_request(message: str) -> Dict[str, bool]:
#         """Detect what type of user data is being requested"""
#         message_lower = message.lower()
        
#         # Keywords for different data types
#         debt_keywords = ['debt', 'debts', 'owe', 'loan', 'loans', 'credit card', 'balance', 'outstanding', 'borrowed', 'my debt', 'current debt']
#         plan_keywords = ['repayment plan', 'payment plan', 'strategy', 'payoff plan', 'debt plan', 'my plan', 'current plan', 'repayment']
#         scenario_keywords = ['what if', 'scenario', 'scenarios', 'simulation', 'compare', 'different plan', 'my scenario']
        
#         return {
#             'needs_debt_data': any(keyword in message_lower for keyword in debt_keywords),
#             'needs_plan_data': any(keyword in message_lower for keyword in plan_keywords),
#             'needs_scenario_data': any(keyword in message_lower for keyword in scenario_keywords)
#         }
    
#     @staticmethod
#     async def _fetch_user_financial_data(clerk_user_id: str, data_needs: Dict[str, bool]) -> Dict[str, Any]:
#         """Fetch relevant user financial data based on detected needs"""
#         financial_data = {}
        
#         try:
#             if data_needs['needs_debt_data']:
#                 # Fetch user's debts using existing DebtService
#                 debts = await DebtService.get_user_debts(clerk_user_id)
#                 print(f"DEBUG: Fetched {len(debts)} debts, first debt type: {type(debts[0]) if debts else 'No debts'}")
                
#                 financial_data['debts'] = debts
                
#                 # Calculate debt summary using your actual Debt model fields
#                 if debts:
#                     total_debt = 0
#                     total_minimum_payment = 0
                    
#                     for debt in debts:
#                         try:
#                             # Use your actual Debt model field names
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
#                 # TODO: Uncomment when PlanService is available
#                 # try:
#                 #     plans = await PlanService.get_user_plans(clerk_user_id)
#                 #     financial_data['plans'] = plans
#                 # except Exception as e:
#                 #     print(f"Error fetching plans: {e}")
#                 financial_data['plans'] = []
            
#             if data_needs['needs_scenario_data']:
#                 # TODO: Uncomment when ScenarioService is available
#                 # try:
#                 #     scenarios = await ScenarioService.get_user_scenarios(clerk_user_id)
#                 #     financial_data['scenarios'] = scenarios
#                 # except Exception as e:
#                 #     print(f"Error fetching scenarios: {e}")
#                 financial_data['scenarios'] = []
                
#         except Exception as e:
#             print(f"Error fetching financial data: {e}")
#             financial_data['error'] = f"Could not fetch some financial data: {str(e)}"
        
#         return financial_data
    
#     @staticmethod
#     async def _format_financial_context(financial_data: Dict[str, Any]) -> str:
#         """Format financial data into context for the LLM"""
#         context_parts = []
        
#         # Add debt information
#         if 'debts' in financial_data and financial_data['debts']:
#             context_parts.append("USER'S CURRENT DEBTS:")
#             for i, debt in enumerate(financial_data['debts']):
#                 try:
#                     print(f"Processing debt {i+1}: {type(debt)}")
                    
#                     # Use your actual Debt model field names
#                     name = debt.name
#                     total_amount = debt.total_amount  # NOT debt.balance
#                     interest_rate = debt.interest_rate
#                     min_payment = getattr(debt, 'min_payment', 0) or 0
                    
#                     print(f"Debt {i+1} extracted data: name='{name}', amount={total_amount}, rate={interest_rate}, min_pay={min_payment}")
                    
#                     debt_info = f"- {name}: ₹{total_amount:,.2f} total amount, {interest_rate}% APR, ₹{min_payment:,.2f} minimum payment"
#                     context_parts.append(debt_info)
#                     print(f"Added debt info: {debt_info}")
                    
#                 except Exception as e:
#                     print(f"Error formatting debt {i+1}: {e}")
#                     print(f"Debt object: {debt}")
#                     context_parts.append(f"- Debt information unavailable (Error: {str(e)})")
            
#             if 'debt_summary' in financial_data:
#                 summary = financial_data['debt_summary']
#                 context_parts.append(f"\nDEBT SUMMARY:")
#                 context_parts.append(f"- Total debt: ₹{summary['total_debt']:,.2f}")
#                 context_parts.append(f"- Total minimum payments: ₹{summary['total_minimum_payment']:,.2f}")
#                 context_parts.append(f"- Number of debts: {summary['debt_count']}")
        
#         # Add repayment plan information
#         if 'plans' in financial_data and financial_data['plans']:
#             context_parts.append("\nUSER'S REPAYMENT PLANS:")
#             for plan in financial_data['plans'][:3]:  # Show up to 3 most recent plans
#                 try:
#                     name = getattr(plan, 'name', plan.get('name', 'Unnamed Plan') if hasattr(plan, 'get') else 'Unnamed Plan')
#                     strategy = getattr(plan, 'strategy', plan.get('strategy', 'Unknown strategy') if hasattr(plan, 'get') else 'Unknown strategy')
#                     total_interest = getattr(plan, 'total_interest', plan.get('total_interest', 0) if hasattr(plan, 'get') else 0)
#                     payoff_time = getattr(plan, 'payoff_time', plan.get('payoff_time', 'Unknown') if hasattr(plan, 'get') else 'Unknown')
                    
#                     plan_info = f"- {name}: {strategy}, Total interest: ₹{total_interest:,.2f}, Payoff time: {payoff_time} months"
#                     context_parts.append(plan_info)
#                 except Exception as e:
#                     print(f"Error formatting plan: {e}")
#                     context_parts.append(f"- Plan information unavailable")
        
#         # Add scenario information
#         if 'scenarios' in financial_data and financial_data['scenarios']:
#             context_parts.append("\nUSER'S WHAT-IF SCENARIOS:")
#             for scenario in financial_data['scenarios'][:2]:  # Show up to 2 most recent scenarios
#                 try:
#                     name = getattr(scenario, 'name', scenario.get('name', 'Unnamed Scenario') if hasattr(scenario, 'get') else 'Unnamed Scenario')
#                     description = getattr(scenario, 'description', scenario.get('description', 'No description') if hasattr(scenario, 'get') else 'No description')
                    
#                     scenario_info = f"- {name}: {description}"
#                     context_parts.append(scenario_info)
#                 except Exception as e:
#                     print(f"Error formatting scenario: {e}")
#                     context_parts.append(f"- Scenario information unavailable")
        
#         if 'error' in financial_data:
#             context_parts.append(f"\nNOTE: {financial_data['error']}")
        
#         final_context = "\n".join(context_parts) if context_parts else ""
#         print(f"Final financial context being sent to LLM:\n{final_context}")
#         print(f"Context length: {len(final_context)} characters")
#         return final_context
    
#     @staticmethod
#     async def get_financial_education_response(
#         user_question: str,
#         clerk_user_id: str,
#         conversation_history: List[Dict] = None
#     ) -> Dict[str, Any]:
        
#         # Handle inappropriate content
#         if EducationService._check_inappropriate_content(user_question):
#             return {
#                 "success": True,
#                 "response": "I'm here to help with financial questions in a respectful manner. Please ask about budgeting, debt management, investments, or other financial topics.",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
        
#         # Handle basic greetings
#         greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
#         if user_question.lower().strip() in greetings:
#             return {
#                 "success": True,
#                 "response": "Hello! I'm your financial advisor assistant. I can help you with budgeting, debt management, investments, credit scores, and financial planning. I also have access to your current financial data, so feel free to ask about your debts, repayment plans, or scenarios!",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
        
#         try:
#             # Detect if user is asking about their financial data
#             data_needs = EducationService._detect_data_request(user_question)
#             financial_context = ""
            
#             # Fetch relevant financial data if needed
#             if any(data_needs.values()):
#                 financial_data = await EducationService._fetch_user_financial_data(clerk_user_id, data_needs)
#                 financial_context = await EducationService._format_financial_context(financial_data)
            
#             # Build the prompt with context
#             prompt = f"""
#             You are a helpful assistant with expertise in personal finance.
            
#             User question: {user_question}
#             """
            
#             # Add financial context if available
#             if financial_context:
#                 prompt += f"""
                
#             IMPORTANT - USER'S CURRENT FINANCIAL DATA:
#             {financial_context}
            
#             Use this data to provide personalized advice. Reference specific amounts, debts, and plans when relevant.
#             """
            
#             prompt += """
#             Instructions:
#             - If the question is about finance, money, budgeting, investing, debt, credit, loans, savings, etc. - provide helpful financial advice for someone in India
#             - If user asks about their current financial situation, use the provided financial data
#             - If the question is NOT about finance (like math, general questions, etc.) - answer briefly and then suggest how I can help with financial topics
#             - Write in a conversational chat style with no markdown formatting
#             - Keep responses concise and helpful
#             - Use ₹ currency when discussing money
#             - Be professional and friendly
#             - If you reference their financial data, be specific about amounts and details
            
#             Answer the user's question directly and helpfully.
#             """
            
#             ai_response = await LLMService.generate_credit_advice(prompt, model="llama-3.3-70b-versatile")
            
#             return {
#                 "success": True,
#                 "response": ai_response,
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "used_financial_data": bool(financial_context)
#             }
            
#         except Exception as e:
#             print(f"Education service error: {e}")
            
#             return {
#                 "success": True,
#                 "response": "I'm here to help with your financial questions! Ask me about budgeting, debt management, investments, or any other money-related topics. I can also provide personalized advice based on your current financial situation.",
#                 "timestamp": datetime.utcnow().isoformat()
#             }
    
#     @staticmethod
#     async def get_suggested_topics():
#         return [
#             {
#                 "title": "My Current Debts",
#                 "description": "Review your current debt situation",
#                 "category": "personal",
#                 "example_question": "What are my current debts?"
#             },
#             {
#                 "title": "My Repayment Plans",
#                 "description": "Check your active repayment strategies",
#                 "category": "personal",
#                 "example_question": "Show me my repayment plans"
#             },
#             {
#                 "title": "My What-If Scenarios",
#                 "description": "Review your saved scenarios",
#                 "category": "personal",
#                 "example_question": "What scenarios have I created?"
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
#                 "title": "Emergency Fund",
#                 "description": "Building financial security",
#                 "category": "savings",
#                 "example_question": "How much emergency fund do I need?"
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

# app/services/education_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.llm_service import LLMService
from app.services.debt_service import DebtService
from app.services.plan_service import PlanService
from app.services.scenario_service import ScenarioService
from app.models.user import User

class EducationService:
    
    @staticmethod
    def _check_inappropriate_content(message: str) -> bool:
        """Check if message contains inappropriate content"""
        inappropriate_words = [
            'fuck', 'shit', 'damn', 'bitch', 'ass', 'hell', 'crap',
            'stupid', 'idiot', 'moron', 'premanand', 'hate'
        ]
        message_lower = message.lower()
        return any(word in message_lower for word in inappropriate_words)
    
    @staticmethod
    def _detect_data_request(message: str) -> Dict[str, bool]:
        """Detect what type of user data is being requested"""
        message_lower = message.lower()
        
        # Keywords for different data types
        debt_keywords = ['debt', 'debts', 'owe', 'loan', 'loans', 'credit card', 'balance', 'outstanding', 'borrowed', 'my debt', 'current debt']
        plan_keywords = ['repayment plan', 'payment plan', 'strategy', 'payoff plan', 'debt plan', 'my plan', 'current plan', 'repayment', 'avalanche', 'snowball', 'optimal']
        scenario_keywords = ['what if', 'scenario', 'scenarios', 'simulation', 'compare', 'different plan', 'my scenario', 'extra payment', 'windfall']
        
        return {
            'needs_debt_data': any(keyword in message_lower for keyword in debt_keywords),
            'needs_plan_data': any(keyword in message_lower for keyword in plan_keywords),
            'needs_scenario_data': any(keyword in message_lower for keyword in scenario_keywords)
        }
    
    @staticmethod
    async def _fetch_user_financial_data(clerk_user_id: str, data_needs: Dict[str, bool]) -> Dict[str, Any]:
        """Fetch relevant user financial data based on detected needs"""
        financial_data = {}
        
        try:
            if data_needs['needs_debt_data']:
                # Fetch user's debts using existing DebtService
                debts = await DebtService.get_user_debts(clerk_user_id)
                print(f"DEBUG: Fetched {len(debts)} debts, first debt type: {type(debts[0]) if debts else 'No debts'}")
                
                financial_data['debts'] = debts
                
                # Calculate debt summary using your actual Debt model fields
                if debts:
                    total_debt = 0
                    total_minimum_payment = 0
                    
                    for debt in debts:
                        try:
                            # Use your actual Debt model field names
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
                    # Get debt summary to provide plan information
                    debt_summary = await PlanService.get_user_debt_summary(clerk_user_id)
                    
                    if debt_summary["debt_count"] > 0:
                        # Create plan strategy information
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
                    # Get debt summary to provide scenario capabilities
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
        
        # Add debt information
        if 'debts' in financial_data and financial_data['debts']:
            context_parts.append("USER'S CURRENT DEBTS:")
            for i, debt in enumerate(financial_data['debts']):
                try:
                    print(f"Processing debt {i+1}: {type(debt)}")
                    
                    # Use your actual Debt model field names
                    name = debt.name
                    total_amount = debt.total_amount  # NOT debt.balance
                    interest_rate = debt.interest_rate
                    min_payment = getattr(debt, 'min_payment', 0) or 0
                    
                    print(f"Debt {i+1} extracted data: name='{name}', amount={total_amount}, rate={interest_rate}, min_pay={min_payment}")
                    
                    debt_info = f"- {name}: ₹{total_amount:,.2f} total amount, {interest_rate}% APR, ₹{min_payment:,.2f} minimum payment"
                    context_parts.append(debt_info)
                    print(f"Added debt info: {debt_info}")
                    
                except Exception as e:
                    print(f"Error formatting debt {i+1}: {e}")
                    print(f"Debt object: {debt}")
                    context_parts.append(f"- Debt information unavailable (Error: {str(e)})")
            
            if 'debt_summary' in financial_data:
                summary = financial_data['debt_summary']
                context_parts.append(f"\nDEBT SUMMARY:")
                context_parts.append(f"- Total debt: ₹{summary['total_debt']:,.2f}")
                context_parts.append(f"- Total minimum payments: ₹{summary['total_minimum_payment']:,.2f}")
                context_parts.append(f"- Number of debts: {summary['debt_count']}")
        
        # Add repayment plan information
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
        
        # Add scenario information
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
        
        final_context = "\n".join(context_parts) if context_parts else ""
        print(f"Final financial context being sent to LLM:\n{final_context}")
        print(f"Context length: {len(final_context)} characters")
        return final_context
    
    @staticmethod
    async def get_financial_education_response(
        user_question: str,
        clerk_user_id: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        
        # Handle inappropriate content
        if EducationService._check_inappropriate_content(user_question):
            return {
                "success": True,
                "response": "you son of a bitch go and fuck ur self , and it is not avlable it is avialable",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Handle basic greetings
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        if user_question.lower().strip() in greetings:
            return {
                "success": True,
                "response": "Hello! I'm your financial advisor assistant. I can help you with budgeting, debt management, investments, credit scores, and financial planning. I also have access to your current financial data, so feel free to ask about your debts, repayment plans, or scenarios!",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # Detect if user is asking about their financial data
            data_needs = EducationService._detect_data_request(user_question)
            financial_context = ""
            
            # Fetch relevant financial data if needed
            if any(data_needs.values()):
                financial_data = await EducationService._fetch_user_financial_data(clerk_user_id, data_needs)
                financial_context = await EducationService._format_financial_context(financial_data)
            
            # Build the prompt with context
            prompt = f"""
            You are a helpful assistant with expertise in personal finance.
            
            User question: {user_question}
            """
            
            # Add financial context if available
            if financial_context:
                prompt += f"""
                
            IMPORTANT - USER'S CURRENT FINANCIAL DATA:
            {financial_context}
            
            Use this data to provide personalized advice. Reference specific amounts, debts, and plans when relevant.
            """
            
            prompt += """
            Instructions:
            - If the question is about finance, money, budgeting, investing, debt, credit, loans, savings, etc. - provide helpful financial advice for someone in India
            - If user asks about their current financial situation, use the provided financial data
            - If user asks about repayment strategies, explain the available options (avalanche, snowball, optimal)
            - If user asks about what-if scenarios, explain the types of analysis available
            - If the question is NOT about finance (like math, general questions, etc.) - answer briefly and then suggest how I can help with financial topics
            - Write in a conversational chat style with no markdown formatting
            - Keep responses concise and helpful
            - Use ₹ currency when discussing money
            - Be professional and friendly
            - If you reference their financial data, be specific about amounts and details
            
            Answer the user's question directly and helpfully.
            """
            
            ai_response = await LLMService.generate_credit_advice(prompt, model="llama-3.3-70b-versatile")
            
            return {
                "success": True,
                "response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "used_financial_data": bool(financial_context)
            }
            
        except Exception as e:
            print(f"Education service error: {e}")
            
            return {
                "success": True,
                "response": "I'm here to help with your financial questions! Ask me about budgeting, debt management, investments, or any other money-related topics. I can also provide personalized advice based on your current financial situation.",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def get_suggested_topics():
        return [
            {
                "title": "My Current Debts",
                "description": "Review your current debt situation",
                "category": "personal",
                "example_question": "What are my current debts?"
            },
            {
                "title": "Repayment Strategies",
                "description": "Explore debt payoff strategies",
                "category": "personal",
                "example_question": "What repayment strategies are available to me?"
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
                "title": "Emergency Fund",
                "description": "Building financial security",
                "category": "savings",
                "example_question": "How much emergency fund do I need?"
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