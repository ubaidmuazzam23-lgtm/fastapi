import React, { useState, useEffect, useRef } from 'react';
import { UserButton, useAuth } from '@clerk/clerk-react';
import { 
  Coffee, 
  Brain, 
  MessageCircle, 
  Send, 
  Loader2, 
  BookOpen,
  TrendingUp,
  CreditCard,
  Calculator,
  Shield,
  PiggyBank,
  Target,
  ArrowLeft,
  Sparkles,
  Clock,
  Users,
  ChevronRight
} from 'lucide-react';

interface EducationHubProps {
  onNavigate?: (page: string) => void;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface SuggestedTopic {
  title: string;
  description: string;
  category: string;
  example_question: string;
}

const EducationHub: React.FC<EducationHubProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedTopics, setSuggestedTopics] = useState<SuggestedTopic[]>([]);
  const [showChat, setShowChat] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSuggestedTopics();
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSuggestedTopics = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/education/suggested-topics', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSuggestedTopics(data.topics || []);
      }
    } catch (error) {
      console.error('Error loading suggested topics:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/education/history?limit=10', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.history && data.history.length > 0) {
          const chatMessages: ChatMessage[] = [];
          data.history.reverse().forEach((chat: any) => {
            chatMessages.push({
              id: `${chat.id}-user`,
              role: 'user',
              content: chat.user_message,
              timestamp: new Date(chat.timestamp)
            });
            chatMessages.push({
              id: `${chat.id}-assistant`,
              role: 'assistant',
              content: chat.assistant_response,
              timestamp: new Date(chat.timestamp)
            });
          });
          setMessages(chatMessages);
        }
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/education/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_history: messages.slice(-6).map(msg => ({
            role: msg.role,
            content: msg.content
          }))
        })
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTopicClick = async (topic: SuggestedTopic) => {
    setShowChat(true);
    setInputMessage(topic.example_question);
    
    // Auto-send the question after a brief delay
    setTimeout(() => {
      const event = new Event('submit');
      document.querySelector('form')?.dispatchEvent(event);
    }, 500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const categoryIcons: { [key: string]: React.ReactNode } = {
    budgeting: <Calculator className="w-5 h-5" />,
    savings: <PiggyBank className="w-5 h-5" />,
    debt: <CreditCard className="w-5 h-5" />,
    investment: <TrendingUp className="w-5 h-5" />,
    credit: <Shield className="w-5 h-5" />,
    tax: <BookOpen className="w-5 h-5" />,
    planning: <Target className="w-5 h-5" />,
    insurance: <Shield className="w-5 h-5" />
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      {/* Header */}
      <header className="bg-white border-b border-amber-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              {onNavigate && (
                <button
                  onClick={() => onNavigate('dashboard')}
                  className="flex items-center space-x-2 text-amber-700 hover:text-amber-800 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back to Dashboard</span>
                </button>
              )}
              <div className="flex items-center space-x-3">
                <Coffee className="w-8 h-8 text-amber-700" />
                <div>
                  <h1 className="text-xl font-bold text-amber-900">FinanceBrews</h1>
                  <p className="text-sm text-amber-700">Education Hub</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!showChat ? (
          // Landing Page
          <>
            {/* Hero Section */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-amber-100 to-orange-100 mb-4">
                <Brain className="w-8 h-8 text-amber-700" />
              </div>
              <h2 className="text-4xl font-bold text-amber-900 mb-4">
                Financial Education Hub
              </h2>
              <p className="text-xl text-amber-800 max-w-2xl mx-auto">
                Get personalized financial guidance from our AI-powered education assistant. 
                Learn budgeting, investing, debt management, and more.
              </p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm text-center">
                <Users className="w-8 h-8 text-amber-700 mx-auto mb-3" />
                <div className="text-2xl font-bold text-amber-900">10,000+</div>
                <div className="text-sm text-amber-700">Questions Answered</div>
              </div>
              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm text-center">
                <Clock className="w-8 h-8 text-amber-700 mx-auto mb-3" />
                <div className="text-2xl font-bold text-amber-900">24/7</div>
                <div className="text-sm text-amber-700">Available Support</div>
              </div>
              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm text-center">
                <Sparkles className="w-8 h-8 text-amber-700 mx-auto mb-3" />
                <div className="text-2xl font-bold text-amber-900">AI-Powered</div>
                <div className="text-sm text-amber-700">Personalized Advice</div>
              </div>
            </div>

            {/* Suggested Topics */}
            <div className="mb-8">
              <h3 className="text-2xl font-semibold text-amber-900 mb-6">Popular Topics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {suggestedTopics.map((topic, index) => (
                  <div
                    key={index}
                    onClick={() => handleTopicClick(topic)}
                    className="bg-gradient-to-br from-amber-50 to-orange-100 rounded-xl border border-amber-200 p-6 cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-lg"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="text-amber-700">
                        {categoryIcons[topic.category] || <BookOpen className="w-5 h-5" />}
                      </div>
                      <ChevronRight className="w-4 h-4 text-amber-600" />
                    </div>
                    
                    <h4 className="text-lg font-semibold text-amber-900 mb-2">
                      {topic.title}
                    </h4>
                    <p className="text-sm text-amber-800 mb-4 leading-relaxed">
                      {topic.description}
                    </p>
                    
                    <div className="text-xs text-amber-600 bg-amber-100 px-2 py-1 rounded-full inline-block">
                      {topic.category.charAt(0).toUpperCase() + topic.category.slice(1)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Start Chat Button */}
            <div className="text-center">
              <button
                onClick={() => setShowChat(true)}
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-amber-600 to-orange-600 text-white px-8 py-4 rounded-lg font-semibold transition-all duration-200 hover:scale-105 hover:shadow-lg"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Start Chat with AI Advisor</span>
              </button>
            </div>
          </>
        ) : (
          // Chat Interface
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm h-[600px] flex flex-col">
              {/* Chat Header */}
              <div className="border-b border-amber-200 p-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-amber-100 to-orange-100 flex items-center justify-center">
                    <Brain className="w-5 h-5 text-amber-700" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-amber-900">Financial AI Assistant</h3>
                    <p className="text-sm text-amber-700">Ask me anything about personal finance</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowChat(false)}
                  className="text-amber-600 hover:text-amber-800 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center py-8">
                    <Brain className="w-12 h-12 text-amber-300 mx-auto mb-4" />
                    <p className="text-amber-600 mb-2">Welcome to your Financial AI Assistant!</p>
                    <p className="text-sm text-amber-500">Ask me about budgeting, investing, debt management, or any financial topic.</p>
                  </div>
                )}
                
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] px-4 py-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
                          : 'bg-amber-50 text-amber-900 border border-amber-200'
                      }`}
                    >
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </div>
                      <div className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-amber-100' : 'text-amber-600'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-amber-50 border border-amber-200 px-4 py-3 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
                        <span className="text-sm text-amber-600">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="border-t border-amber-200 p-4">
                <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me about budgeting, investing, debt management..."
                    className="flex-1 px-4 py-3 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    disabled={!inputMessage.trim() || isLoading}
                    className="bg-gradient-to-r from-amber-600 to-orange-600 text-white px-6 py-3 rounded-lg transition-all duration-200 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default EducationHub;