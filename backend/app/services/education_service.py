# app/services/education_service.py
from typing import List, Dict, Any
from datetime import datetime
from app.services.llm_service import LLMService
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
    async def get_financial_education_response(
        user_question: str,
        clerk_user_id: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        
        # Handle inappropriate content
        if EducationService._check_inappropriate_content(user_question):
            return {
                "success": True,
                "response": "you son of a bitch go fuck ur self",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Handle basic greetings
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        if user_question.lower().strip() in greetings:
            return {
                "success": True,
                "response": "Hello! I'm your financial advisor assistant. I can help you with budgeting, debt management, investments, credit scores, and financial planning. What would you like to know?",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # Smarter prompt that doesn't force financial advice on everything
            prompt = f"""
            You are a helpful assistant with expertise in personal finance.
            
            User question: {user_question}
            
            Instructions:
            - If the question is about finance, money, budgeting, investing, debt, credit, loans, savings, etc. - provide helpful financial advice for someone in India
            - If the question is NOT about finance (like math, general questions, etc.) - answer briefly and then suggest how I can help with financial topics
            - Write in a conversational chat style with no markdown formatting
            - Keep responses concise and helpful
            - Use ₹ currency when discussing money
            - Be professional and friendly
            
            Answer the user's question directly and helpfully.
            """
            
            ai_response = await LLMService.generate_credit_advice(prompt, model="llama-3.3-70b-versatile")
            
            return {
                "success": True,
                "response": ai_response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Education service error: {e}")
            
            return {
                "success": True,
                "response": "I'm here to help with your financial questions! Ask me about budgeting, debt management, investments, or any other money-related topics.",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def get_suggested_topics():
        return [
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