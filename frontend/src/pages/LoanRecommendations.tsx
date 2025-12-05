import { API_URL } from '../lib/api';
import React, { useState, useEffect, useRef } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';
import {
  DollarSign,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Sparkles,
  ArrowRight,
  Loader,
  BarChart3,
  Calculator,
  ExternalLink,
  Info,
  MessageCircle,
  Send,
  Bot,
  User as UserIcon,
  X,
  ArrowLeft,
  Lightbulb,
  TrendingUp
} from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface AffordabilityAnalysis {
  monthly_income: number;
  monthly_expenses: number;
  available_budget: number;
  total_existing_debt: number;
  existing_monthly_debt_payments: number;
  debt_to_income_ratio: number;
  debt_to_income_with_loan: number;
  max_affordable_monthly: number;
  max_affordable_loan_amount: number;
  is_affordable: boolean;
  affordability_score: number;
  risk_level: string;
  recommendations: string[];
}

interface LoanOption {
  lender_name: string;
  loan_type: string;
  interest_rate: number;
  apr: number;
  monthly_payment: number;
  total_interest: number;
  total_cost: number;
  term_months: number;
  origination_fee: number;
  processing_fee: number;
  prepayment_penalty: boolean;
  min_credit_score?: number;
  min_income?: number;
  max_dti_ratio?: number;
  suitability_score: number;
  approval_probability: number;
  features: string[];
  pros: string[];
  cons: string[];
  source_url?: string;
  ai_rank?: number;
}

interface LoanRecommendationResponse {
  id: string;
  loan_type: string;
  requested_amount: number;
  affordability_analysis: AffordabilityAnalysis;
  recommended_loans: LoanOption[];
  comparison_data: any[];
  best_overall?: string;
  lowest_rate?: string;
  lowest_payment?: string;
  lowest_total_cost?: string;
  status: string;
  created_at: string;
  analysis_notes?: string;
}

const LoanRecommendations: React.FC = () => {
  const { getToken } = useAuth();
  const { user } = useUser();
  
  const [step, setStep] = useState<'form' | 'results'>('form');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [loanType, setLoanType] = useState('personal');
  const [amount, setAmount] = useState('');
  const [purpose, setPurpose] = useState('');
  const [termMonths, setTermMonths] = useState('36');
  
  const [recommendation, setRecommendation] = useState<LoanRecommendationResponse | null>(null);
  const [selectedLoan, setSelectedLoan] = useState<LoanOption | null>(null);
  
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI loan advisor. Ask me anything about loans, interest rates, eligibility, or which loan type suits you best.'
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loanTypes = [
    { value: 'personal', label: 'Personal Loan', desc: 'For personal expenses, debt consolidation' },
    { value: 'home', label: 'Home Loan', desc: 'For buying or constructing property' },
    { value: 'car', label: 'Car Loan', desc: 'For purchasing a vehicle' },
    { value: 'education', label: 'Education Loan', desc: 'For higher education expenses' },
    { value: 'gold', label: 'Gold Loan', desc: 'Loan against gold jewelry' },
    { value: 'business', label: 'Business Loan', desc: 'For business needs and expansion' }
  ];

  const termOptions = [
    { value: '12', label: '1 Year' },
    { value: '24', label: '2 Years' },
    { value: '36', label: '3 Years' },
    { value: '48', label: '4 Years' },
    { value: '60', label: '5 Years' },
    { value: '84', label: '7 Years' },
    { value: '120', label: '10 Years' },
    { value: '180', label: '15 Years' },
    { value: '240', label: '20 Years' },
    { value: '360', label: '30 Years' }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const response = await fetch(API_URL + '/api/v1/loans/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          loan_type: loanType,
          requested_amount: parseFloat(amount),
          purpose: purpose || undefined,
          preferred_term_months: parseInt(termMonths)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get loan recommendations');
      }

      const data = await response.json();
      setRecommendation(data);
      setSelectedLoan(data.recommended_loans[0] || null);
      setStep('results');
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleChatSend = async () => {
    if (!chatInput.trim() || chatLoading) return;

    const userMessage = chatInput.trim();
    setChatInput('');
    
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);

    try {
      const token = await getToken();
      const response = await fetch(API_URL + '/api/v1/loans/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_history: messages
        })
      });

      if (!response.ok) {
        throw new Error('Chat failed');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-700 bg-green-100 border-green-300';
      case 'moderate': return 'text-yellow-700 bg-yellow-100 border-yellow-300';
      case 'high': return 'text-red-700 bg-red-100 border-red-300';
      default: return 'text-gray-700 bg-gray-100 border-gray-300';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  if (step === 'form') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-amber-900 mb-2 flex items-center">
              <Sparkles className="w-8 h-8 mr-3 text-amber-600" />
              AI Loan Recommendations
            </h1>
            <p className="text-amber-700">
              Get personalized loan recommendations from top 10 Indian banks with AI-powered insights
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-white rounded-xl border border-amber-200 shadow-lg p-8">
                <h2 className="text-xl font-semibold text-amber-900 mb-6">Loan Requirements</h2>
                <form onSubmit={handleSubmit}>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-amber-900 mb-3">
                        Select Loan Type
                      </label>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {loanTypes.map(type => (
                          <div
                            key={type.value}
                            onClick={() => setLoanType(type.value)}
                            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                              loanType === type.value
                                ? 'border-amber-500 bg-amber-50'
                                : 'border-gray-200 hover:border-amber-300'
                            }`}
                          >
                            <div className="font-semibold text-amber-900">{type.label}</div>
                            <div className="text-sm text-gray-600 mt-1">{type.desc}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-amber-900 mb-2">
                        Loan Amount (₹)
                      </label>
                      <input
                        type="number"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        placeholder="50000"
                        required
                        min="10000"
                        className="w-full px-4 py-3 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-amber-900 mb-2">
                        Purpose (Optional)
                      </label>
                      <input
                        type="text"
                        value={purpose}
                        onChange={(e) => setPurpose(e.target.value)}
                        placeholder="Debt consolidation, business expansion, etc."
                        className="w-full px-4 py-3 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-amber-900 mb-2">
                        Preferred Loan Term
                      </label>
                      <select
                        value={termMonths}
                        onChange={(e) => setTermMonths(e.target.value)}
                        className="w-full px-4 py-3 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                      >
                        {termOptions.map(term => (
                          <option key={term.value} value={term.value}>{term.label}</option>
                        ))}
                      </select>
                    </div>

                    {error && (
                      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start">
                        <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                        <span>{error}</span>
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={loading || !amount}
                      className="w-full bg-amber-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-amber-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      {loading ? (
                        <>
                          <Loader className="w-5 h-5 mr-2 animate-spin" />
                          AI is Analyzing...
                        </>
                      ) : (
                        <>
                          Get AI Recommendations
                          <ArrowRight className="w-5 h-5 ml-2" />
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <div className="lg:col-span-1">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 shadow-lg p-6 sticky top-8">
                <div className="flex items-center mb-4">
                  <Bot className="w-6 h-6 text-blue-600 mr-2" />
                  <h3 className="text-lg font-semibold text-blue-900">AI Loan Advisor</h3>
                </div>
                <p className="text-sm text-blue-800 mb-4">
                  Not sure which loan to choose? Ask our AI assistant about:
                </p>
                <ul className="text-sm text-blue-700 space-y-2 mb-4">
                  <li>• Best loan type for your needs</li>
                  <li>• Interest rate comparisons</li>
                  <li>• Eligibility requirements</li>
                  <li>• Documentation needed</li>
                </ul>
                <button
                  onClick={() => setShowChat(true)}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
                >
                  <MessageCircle className="w-5 h-5 mr-2" />
                  Chat with AI
                </button>
              </div>
            </div>
          </div>
        </div>

        {showChat && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl h-[600px] flex flex-col">
              <div className="bg-blue-600 text-white p-4 rounded-t-xl flex items-center justify-between">
                <div className="flex items-center">
                  <Bot className="w-6 h-6 mr-2" />
                  <h3 className="font-semibold">AI Loan Advisor</h3>
                </div>
                <button onClick={() => setShowChat(false)} className="hover:bg-blue-700 p-1 rounded">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`flex items-start max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        msg.role === 'user' ? 'bg-amber-100 ml-2' : 'bg-blue-100 mr-2'
                      }`}>
                        {msg.role === 'user' ? (
                          <UserIcon className="w-5 h-5 text-amber-700" />
                        ) : (
                          <Bot className="w-5 h-5 text-blue-700" />
                        )}
                      </div>
                      <div className={`px-4 py-2 rounded-lg ${
                        msg.role === 'user' 
                          ? 'bg-amber-600 text-white' 
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        {msg.content}
                      </div>
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-center bg-gray-100 px-4 py-2 rounded-lg">
                      <Loader className="w-4 h-4 animate-spin mr-2" />
                      <span className="text-gray-600">AI is thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="p-4 border-t border-gray-200">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleChatSend()}
                    placeholder="Ask about loans..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={handleChatSend}
                    disabled={chatLoading || !chatInput.trim()}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (!recommendation) return null;

  const { affordability_analysis, recommended_loans, analysis_notes } = recommendation;

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => setStep('form')}
          className="mb-6 text-amber-700 hover:text-amber-800 flex items-center font-medium"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          New Search
        </button>

        {analysis_notes && (
          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl border-2 border-purple-300 shadow-xl p-6 mb-6">
            <h2 className="text-2xl font-bold text-purple-900 mb-4 flex items-center">
              <Sparkles className="w-7 h-7 mr-3 text-purple-600" />
              AI-Powered Financial Analysis
            </h2>
            
            <div className="bg-white rounded-lg p-6 shadow-md">
              <div className="flex items-start mb-4">
                <Lightbulb className="w-6 h-6 text-yellow-500 mr-3 flex-shrink-0 mt-1" />
                <div className="text-sm text-gray-500">
                  Our AI analyzed your financial profile and {recommended_loans.length} loan options from top Indian banks
                </div>
              </div>
              
              <div className="prose prose-lg max-w-none">
                <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                  {analysis_notes}
                </div>
              </div>
            </div>
            
            <div className="mt-4 flex items-center text-sm text-purple-700 bg-purple-100 px-4 py-2 rounded-lg">
              <Bot className="w-5 h-5 mr-2" />
              This analysis was generated by AI based on real-time data from bank websites
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl border border-amber-200 shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-amber-900 mb-4 flex items-center">
            <Calculator className="w-6 h-6 mr-2" />
            Your Financial Analysis
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-amber-50 to-orange-100 rounded-lg p-4 border border-amber-200">
              <div className="text-sm text-amber-700 mb-1">Monthly Income</div>
              <div className="text-2xl font-bold text-amber-900">
                {formatCurrency(affordability_analysis.monthly_income)}
              </div>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-4 border border-blue-200">
              <div className="text-sm text-blue-700 mb-1">Available Budget</div>
              <div className="text-2xl font-bold text-blue-900">
                {formatCurrency(affordability_analysis.available_budget)}
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-pink-100 rounded-lg p-4 border border-purple-200">
              <div className="text-sm text-purple-700 mb-1">DTI Ratio</div>
              <div className="text-2xl font-bold text-purple-900">
                {affordability_analysis.debt_to_income_with_loan.toFixed(1)}%
              </div>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-emerald-100 rounded-lg p-4 border border-green-200">
              <div className="text-sm text-green-700 mb-1">Affordability Score</div>
              <div className="text-2xl font-bold text-green-900">
                {affordability_analysis.affordability_score}/100
              </div>
            </div>
          </div>

          <div className={`inline-flex items-center px-4 py-2 rounded-lg font-medium border-2 ${getRiskColor(affordability_analysis.risk_level)}`}>
            {affordability_analysis.is_affordable ? (
              <CheckCircle className="w-5 h-5 mr-2" />
            ) : (
              <AlertCircle className="w-5 h-5 mr-2" />
            )}
            Risk Level: {affordability_analysis.risk_level.toUpperCase()}
          </div>

          {affordability_analysis.recommendations.length > 0 && (
            <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="font-medium text-blue-900 mb-2 flex items-center">
                <Info className="w-5 h-5 mr-2" />
                AI Recommendations
              </div>
              <ul className="space-y-1">
                {affordability_analysis.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-blue-800">• {rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {recommended_loans.length > 0 && (
          <div className="bg-white rounded-xl border border-amber-200 shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-amber-900 mb-6 flex items-center">
              <BarChart3 className="w-6 h-6 mr-2" />
              Interest Rate Comparison
            </h2>
            <div className="space-y-3">
              {recommended_loans.slice(0, 5).map((loan, idx) => {
                const maxRate = Math.max(...recommended_loans.map(l => l.interest_rate));
                const widthPercent = (loan.interest_rate / maxRate) * 100;
                
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <div className="flex items-center">
                        <span className="font-medium text-gray-700">{loan.lender_name}</span>
                        {loan.ai_rank === 1 && (
                          <span className="ml-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                            AI Best Match
                          </span>
                        )}
                      </div>
                      <span className="font-bold text-amber-900">{loan.interest_rate.toFixed(2)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full transition-all duration-500"
                        style={{ width: `${widthPercent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl border border-amber-200 shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-amber-900 mb-6 flex items-center">
            <TrendingUp className="w-6 h-6 mr-2" />
            Top {recommended_loans.length} Loan Options (AI Ranked)
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {recommended_loans.map((loan, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedLoan(loan)}
                className={`border-2 rounded-xl p-6 cursor-pointer transition-all hover:shadow-lg ${
                  selectedLoan?.lender_name === loan.lender_name
                    ? 'border-amber-500 bg-amber-50 shadow-md'
                    : 'border-gray-200 hover:border-amber-300'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-amber-900">{loan.lender_name}</h3>
                    <div className="flex items-center mt-1 space-x-2">
                      <div className="text-sm text-amber-700">
                        AI Score: {loan.suitability_score.toFixed(0)}/100
                      </div>
                      <div className="text-sm text-green-700">
                        Approval: {loan.approval_probability.toFixed(0)}%
                      </div>
                    </div>
                  </div>
                  {loan.ai_rank === 1 && (
                    <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                      Best Match
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-red-50 rounded-lg p-3">
                    <div className="text-xs text-gray-600">Interest Rate</div>
                    <div className="text-xl font-bold text-red-700">{loan.interest_rate.toFixed(2)}%</div>
                  </div>
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-xs text-gray-600">Monthly EMI</div>
                    <div className="text-xl font-bold text-blue-700">{formatCurrency(loan.monthly_payment)}</div>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-3">
                    <div className="text-xs text-gray-600">Total Interest</div>
                    <div className="text-base font-semibold text-orange-700">{formatCurrency(loan.total_interest)}</div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="text-xs text-gray-600">Total Cost</div>
                    <div className="text-base font-semibold text-purple-700">{formatCurrency(loan.total_cost)}</div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="text-sm text-gray-600">
                    Term: <span className="font-semibold text-gray-900">{loan.term_months} months</span>
                  </div>
                  {loan.source_url && (
                    <a
                      href={loan.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-amber-600 hover:text-amber-700 flex items-center text-sm font-medium"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Apply Now
                      <ExternalLink className="w-4 h-4 ml-1" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {selectedLoan && (
          <div className="bg-white rounded-xl border border-amber-200 shadow-lg p-6">
            <h2 className="text-2xl font-bold text-amber-900 mb-6">
              {selectedLoan.lender_name} - Detailed Analysis
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
              <div>
                <h3 className="font-semibold text-green-900 mb-3 flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Advantages
                </h3>
                <ul className="space-y-2">
                  {selectedLoan.pros.map((pro, idx) => (
                    <li key={idx} className="flex items-start text-green-700 bg-green-50 px-3 py-2 rounded-lg">
                      <CheckCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-red-900 mb-3 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Considerations
                </h3>
                <ul className="space-y-2">
                  {selectedLoan.cons.map((con, idx) => (
                    <li key={idx} className="flex items-start text-red-700 bg-red-50 px-3 py-2 rounded-lg">
                      <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                      <span>{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {selectedLoan.features.length > 0 && (
              <div className="pt-6 border-t border-gray-200">
                <h3 className="font-semibold text-amber-900 mb-3">Key Features</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedLoan.features.map((feature, idx) => (
                    <span key={idx} className="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-sm font-medium">
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600">Origination Fee</div>
                <div className="font-semibold text-gray-900">{selectedLoan.origination_fee}%</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Processing Fee</div>
                <div className="font-semibold text-gray-900">{selectedLoan.processing_fee}%</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Min Credit Score</div>
                <div className="font-semibold text-gray-900">{selectedLoan.min_credit_score || 'N/A'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Prepayment</div>
                <div className={`font-semibold ${selectedLoan.prepayment_penalty ? 'text-red-700' : 'text-green-700'}`}>
                  {selectedLoan.prepayment_penalty ? 'Penalty' : 'Allowed'}
                </div>
              </div>
            </div>
          </div>
        )}

        <button
          onClick={() => setShowChat(true)}
          className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all hover:scale-110 z-40"
        >
          <MessageCircle className="w-6 h-6" />
        </button>

        {showChat && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl h-[600px] flex flex-col">
              <div className="bg-blue-600 text-white p-4 rounded-t-xl flex items-center justify-between">
                <div className="flex items-center">
                  <Bot className="w-6 h-6 mr-2" />
                  <h3 className="font-semibold">AI Loan Advisor</h3>
                </div>
                <button onClick={() => setShowChat(false)} className="hover:bg-blue-700 p-1 rounded">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`flex items-start max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        msg.role === 'user' ? 'bg-amber-100 ml-2' : 'bg-blue-100 mr-2'
                      }`}>
                        {msg.role === 'user' ? (
                          <UserIcon className="w-5 h-5 text-amber-700" />
                        ) : (
                          <Bot className="w-5 h-5 text-blue-700" />
                        )}
                      </div>
                      <div className={`px-4 py-2 rounded-lg ${
                        msg.role === 'user' 
                          ? 'bg-amber-600 text-white' 
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        {msg.content}
                      </div>
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-center bg-gray-100 px-4 py-2 rounded-lg">
                      <Loader className="w-4 h-4 animate-spin mr-2" />
                      <span className="text-gray-600">AI is thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="p-4 border-t border-gray-200">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleChatSend()}
                    placeholder="Ask about loans, rates, eligibility..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={handleChatSend}
                    disabled={chatLoading || !chatInput.trim()}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoanRecommendations;