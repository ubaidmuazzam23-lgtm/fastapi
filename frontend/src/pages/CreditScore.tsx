import React, { useState, useEffect } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';
import {
  Shield,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  CreditCard,
  BarChart3,
  Target,
  Calendar,
  ArrowRight,
  Loader2,
  RefreshCw,
  Star,
  Info,
  ChevronDown,
  ChevronUp,
  Plus,
  Edit,
  Trash2,
  DollarSign,
  Percent,
  Save,
  X
} from 'lucide-react';

interface CreditScoreProps {
  onNavigate?: (page: string) => void;
}

interface CreditCard {
  name: string;
  credit_limit: number;
  current_balance: number;
  utilization_percent?: number;
  minimum_payment?: number;
  interest_rate?: number;
  statement_date?: number;
  due_date?: number;
  available_credit?: number;
}

interface CreditProfile {
  id: string;
  current_score: number | null;
  target_score: number;
  last_checked: string;
  factors_assessment: {
    payment_history: string;
    average_account_age_years: number;
    new_accounts_last_2_years: number;
    account_types: string[];
    current_utilization_percent: number;
    total_credit_limits: number;
    total_revolving_balances: number;
    number_of_credit_cards?: number;
    available_credit?: number;
  };
  credit_cards?: CreditCard[];
  ai_analysis_summary?: string;
  score_prediction?: {
    current_score: number;
    predicted_score: number;
    improvement_points: number;
    timeline_months: number;
    factors: Record<string, number>;
  };
}

interface CreditAnalysis {
  profile: CreditProfile;
  debt_impact: {
    high_utilization_debts: any[];
    credit_building_opportunities: string[];
    consolidation_recommendations: string[];
    payment_optimization_tips: string[];
  };
  utilization_breakdown: {
    total_balances: number;
    total_limits: number;
    utilization_percent: number;
    amount_to_pay_down: number;
    per_card_utilization: any[];
    cards_above_30_percent?: any[];
    cards_above_90_percent?: any[];
    paydown_recommendations?: Record<string, number>;
  };
  personalized_tips: string[];
  ai_generated_plan: string;
  next_steps: string[];
}

const CreditScore: React.FC<CreditScoreProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const { user } = useUser();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [creditProfile, setCreditProfile] = useState<CreditProfile | null>(null);
  const [creditAnalysis, setCreditAnalysis] = useState<CreditAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    factors: true,
    prediction: true,
    tips: false,
    cards: true
  });

  // Form state for credit profile
  const [profileForm, setProfileForm] = useState({
    current_score: 650,
    target_score: 750,
    last_checked: 'this_month',
    payment_history: 'always_on_time',
    average_account_age_years: 3.0,
    new_accounts_last_2_years: 1,
    account_types: ['credit_card'],
    credit_cards: [] as CreditCard[]
  });

  // Credit card management state
  const [showAddCard, setShowAddCard] = useState(false);
  const [editingCard, setEditingCard] = useState<string | null>(null);
  const [newCard, setNewCard] = useState<CreditCard>({
    name: '',
    credit_limit: 0,
    current_balance: 0,
    interest_rate: 24,
    minimum_payment: 0
  });

  const apiCall = async (url: string, options: any = {}) => {
    const token = await getToken();
    const response = await fetch(`http://localhost:8000${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-User-Email': user?.primaryEmailAddress?.emailAddress || '',
        'X-User-First-Name': user?.firstName || '',
        'X-User-Last-Name': user?.lastName || '',
        'X-User-Image': user?.imageUrl || '',
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorMessage = `API call failed: ${response.statusText}`;
      
      try {
        const errorData = await response.json();
        console.error('API Error Details:', errorData);
        
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // Pydantic validation errors
            const validationErrors = errorData.detail.map((err: any) => 
              `${err.loc?.join('.')} - ${err.msg}`
            ).join('; ');
            errorMessage = `Validation Error: ${validationErrors}`;
          } else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else {
            errorMessage = JSON.stringify(errorData.detail);
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (parseError) {
        console.error('Could not parse error response:', parseError);
      }
      
      throw new Error(errorMessage);
    }
    
    return response.json();
  };

  const fetchCreditProfile = async () => {
    try {
      const profile = await apiCall('/api/v1/credit/profile');
      console.log('Received profile data:', profile); // Debug log
      
      setCreditProfile(profile);
      
      // Safely extract credit cards with fallback handling
      let creditCards = [];
      if (profile.credit_cards && Array.isArray(profile.credit_cards)) {
        creditCards = profile.credit_cards.map((card: any) => ({
          name: card.name,
          credit_limit: card.credit_limit || card.limit || 0,
          current_balance: card.current_balance || card.balance || 0,
          utilization_percent: card.utilization_percent || card.utilization || 
            (card.credit_limit || card.limit > 0 ? 
              ((card.current_balance || card.balance || 0) / (card.credit_limit || card.limit)) * 100 : 0),
          available_credit: card.available_credit || 
            Math.max(0, (card.credit_limit || card.limit || 0) - (card.current_balance || card.balance || 0)),
          minimum_payment: card.minimum_payment,
          interest_rate: card.interest_rate,
          statement_date: card.statement_date,
          due_date: card.due_date,
          is_active: card.is_active !== undefined ? card.is_active : true
        }));
      }
      
      // Update form with fetched data
      setProfileForm({
        current_score: profile.current_score || 650,
        target_score: profile.target_score || 750,
        last_checked: profile.last_checked || 'this_month',
        payment_history: profile.factors_assessment?.payment_history || 'always_on_time',
        average_account_age_years: profile.factors_assessment?.average_account_age_years || 3.0,
        new_accounts_last_2_years: profile.factors_assessment?.new_accounts_last_2_years || 1,
        account_types: profile.factors_assessment?.account_types || ['credit_card'],
        credit_cards: creditCards
      });
      
    } catch (err) {
      console.error('Error fetching credit profile:', err);
      setError('Failed to load credit profile');
    }
  };

  const addCreditCard = async () => {
    if (!newCard.name?.trim()) {
      setError('Please enter a card name');
      return;
    }
    if (!newCard.credit_limit || newCard.credit_limit <= 0) {
      setError('Please enter a valid credit limit greater than 0');
      return;
    }
    if (newCard.current_balance < 0) {
      setError('Current balance cannot be negative');
      return;
    }
    if (newCard.current_balance > newCard.credit_limit * 1.1) {
      setError('Current balance cannot exceed credit limit by more than 10%');
      return;
    }

    // Clean the data before sending
    const cardData = {
      name: newCard.name.trim(),
      credit_limit: Number(newCard.credit_limit),
      current_balance: Number(newCard.current_balance) || 0,
      interest_rate: newCard.interest_rate ? Number(newCard.interest_rate) : undefined,
      minimum_payment: newCard.minimum_payment ? Number(newCard.minimum_payment) : undefined,
      statement_date: newCard.statement_date ? Number(newCard.statement_date) : undefined,
      due_date: newCard.due_date ? Number(newCard.due_date) : undefined
    };

    // Remove undefined values
    Object.keys(cardData).forEach(key => {
      if (cardData[key] === undefined) {
        delete cardData[key];
      }
    });

    console.log('Sending card data:', cardData); // Debug log

    try {
      const response = await apiCall('/api/v1/credit/cards', {
        method: 'POST',
        body: JSON.stringify(cardData)
      });
      
      console.log('Card added successfully:', response); // Debug log

      setNewCard({
        name: '',
        credit_limit: 0,
        current_balance: 0,
        interest_rate: 24,
        minimum_payment: 0
      });
      setShowAddCard(false);
      await fetchCreditProfile();
      setError(null);
    } catch (err) {
      console.error('Error adding credit card:', err);
      
      // Try to get more detailed error info
      try {
        const errorResponse = await err.response?.json();
        console.error('Detailed error:', errorResponse);
        setError(`Failed to add credit card: ${errorResponse.detail || err.message}`);
      } catch {
        setError(`Failed to add credit card: ${err.message}`);
      }
    }
  };

  const updateCardBalance = async (cardName: string, newBalance: number) => {
    try {
      await apiCall(`/api/v1/credit/cards/${encodeURIComponent(cardName)}/balance`, {
        method: 'PUT',
        body: JSON.stringify({
          card_name: cardName,
          new_balance: newBalance
        })
      });
      
      await fetchCreditProfile();
      setEditingCard(null);
    } catch (err) {
      console.error('Error updating card balance:', err);
      setError('Failed to update card balance');
    }
  };

  const removeCard = async (cardName: string) => {
    if (!confirm(`Are you sure you want to remove "${cardName}"?`)) return;

    try {
      await apiCall(`/api/v1/credit/cards/${encodeURIComponent(cardName)}`, {
        method: 'DELETE'
      });
      
      await fetchCreditProfile();
    } catch (err) {
      console.error('Error removing card:', err);
      setError('Failed to remove credit card');
    }
  };

  const generatePersonalizedTips = async () => {
    setGenerating(true);
    try {
      const analysis = await apiCall('/api/v1/credit/generate-tips', {
        method: 'POST',
        body: JSON.stringify({
          include_debt_analysis: true,
          focus_areas: ['utilization', 'payment_history'],
          urgency: 'normal'
        })
      });
      setCreditAnalysis(analysis);
    } catch (err) {
      console.error('Error generating tips:', err);
      setError('Failed to generate personalized tips');
    } finally {
      setGenerating(false);
    }
  };

  const updateCreditProfile = async () => {
    setLoading(true);
    try {
      await apiCall('/api/v1/credit/profile', {
        method: 'POST',
        body: JSON.stringify(profileForm)
      });
      await fetchCreditProfile();
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update credit profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initializePage = async () => {
      setLoading(true);
      try {
        await fetchCreditProfile();
      } catch (err) {
        setError('Failed to initialize credit score page');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      initializePage();
    }
  }, [user]);

  const getScoreColor = (score: number) => {
    if (score >= 750) return 'text-green-600';
    if (score >= 650) return 'text-amber-600';
    return 'text-red-600';
  };

  const getUtilizationColor = (utilization: number) => {
    if (utilization >= 90) return 'text-red-600 bg-red-50';
    if (utilization >= 30) return 'text-amber-600 bg-amber-50';
    return 'text-green-600 bg-green-50';
  };

  const formatPaymentHistory = (history: string) => {
    const map: Record<string, string> = {
      'always_on_time': 'Always on time',
      'occasional_late': '1-2 late payments this year',
      'several_late': 'Several late payments',
      'missed_recent': 'Missed payments recently'
    };
    return map[history] || history;
  };

  const formatLastChecked = (checked: string) => {
    const map: Record<string, string> = {
      'this_month': 'This month',
      '1-3_months': '1-3 months ago',
      '6+_months': '6+ months ago',
      'never_checked': 'Never checked'
    };
    return map[checked] || checked;
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const formatCreditPlan = (planText: string) => {
    if (!planText) return <div className="text-amber-600">No plan content available</div>;

    console.log('Raw plan text:', planText); // Debug log

    // If the text doesn't contain markdown headers, display it as formatted text
    if (!planText.includes('###') && !planText.includes('**')) {
      return (
        <div className="space-y-4">
          {planText.split('\n\n').map((paragraph, index) => (
            <div key={index} className="text-amber-900 leading-relaxed">
              {paragraph.split('\n').map((line, lineIndex) => (
                <div key={lineIndex} className={`
                  ${line.trim().startsWith('*') || line.trim().match(/^\d+\./) ? 'ml-4 mb-2 flex items-start' : 'mb-2'}
                `}>
                  {line.trim().startsWith('*') || line.trim().match(/^\d+\./) ? (
                    <>
                      <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span>{line.replace(/^\*\s*/, '').replace(/^\d+\.\s*/, '')}</span>
                    </>
                  ) : (
                    <span className={line.trim().length > 0 ? '' : 'hidden'}>{line}</span>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      );
    }

    // Parse markdown-style text into structured sections
    const sections: Record<string, string> = {};
    let currentSection = '';
    let currentContent: string[] = [];

    const lines = planText.split('\n');
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim();
      
      // Main headers (### **Header** or **Header**)
      if ((trimmedLine.startsWith('###') && trimmedLine.includes('**')) || 
          (trimmedLine.startsWith('**') && trimmedLine.endsWith('**') && !trimmedLine.includes(':'))) {
        
        // Save previous section
        if (currentSection && currentContent.length > 0) {
          sections[currentSection] = currentContent.join('\n');
        }
        
        // Extract new section name
        currentSection = trimmedLine
          .replace(/#{1,6}\s*/, '')
          .replace(/\*\*/g, '')
          .trim();
        currentContent = [];
        
      } else if (trimmedLine && 
                 !trimmedLine.startsWith('===') && 
                 !trimmedLine.startsWith('---') &&
                 trimmedLine !== '**Comprehensive Credit Improvement Plan**') {
        currentContent.push(line);
      }
    });
    
    // Add the last section
    if (currentSection && currentContent.length > 0) {
      sections[currentSection] = currentContent.join('\n');
    }

    console.log('Parsed sections:', sections); // Debug log

    // If no sections were parsed, fall back to simple formatting
    if (Object.keys(sections).length === 0) {
      return (
        <div className="bg-amber-50 rounded-lg p-6 border border-amber-200">
          <div className="whitespace-pre-line text-amber-900 leading-relaxed">
            {planText}
          </div>
        </div>
      );
    }

    const formatSectionContent = (content: string) => {
      return content.split('\n').map((line, idx) => {
        const trimmedLine = line.trim();
        if (!trimmedLine) return null;

        // Numbered or bulleted items
        if (trimmedLine.match(/^\d+\.\s*/) || trimmedLine.startsWith('*')) {
          const text = trimmedLine.replace(/^\d+\.\s*/, '').replace(/^\*\s*/, '');
          
          // Check if this is a bold item with description
          if (text.includes('**') && text.includes(':')) {
            const parts = text.split(':');
            const title = parts[0].replace(/\*\*/g, '').trim();
            const description = parts.slice(1).join(':').trim();
            
            return (
              <div key={idx} className="mb-4 p-4 bg-white rounded-lg border border-amber-200 shadow-sm">
                <div className="font-semibold text-amber-900 mb-2 flex items-start">
                  <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  {title}
                </div>
                {description && (
                  <div className="text-amber-800 ml-5">{description}</div>
                )}
              </div>
            );
          } else {
            return (
              <div key={idx} className="flex items-start mb-3">
                <div className="w-1.5 h-1.5 bg-amber-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span className="text-amber-800">{text}</span>
              </div>
            );
          }
        }

        // Regular content lines
        if (trimmedLine.length > 0) {
          return (
            <div key={idx} className="mb-2 text-amber-800">
              {trimmedLine.replace(/\*\*/g, '')}
            </div>
          );
        }

        return null;
      }).filter(Boolean);
    };

    const getSectionIcon = (sectionName: string) => {
      const name = sectionName.toLowerCase();
      if (name.includes('current') || name.includes('situation')) return <BarChart3 className="w-5 h-5" />;
      if (name.includes('immediate')) return <Clock className="w-5 h-5" />;
      if (name.includes('short-term') || name.includes('short term')) return <Calendar className="w-5 h-5" />;
      if (name.includes('long-term') || name.includes('long term')) return <Target className="w-5 h-5" />;
      if (name.includes('number') || name.includes('amount') || name.includes('₹')) return <DollarSign className="w-5 h-5" />;
      if (name.includes('monitor') || name.includes('track')) return <BarChart3 className="w-5 h-5" />;
      if (name.includes('warning') || name.includes('avoid')) return <AlertCircle className="w-5 h-5" />;
      return <Info className="w-5 h-5" />;
    };

    const getSectionColor = (sectionName: string) => {
      const name = sectionName.toLowerCase();
      if (name.includes('current') || name.includes('situation')) return 'bg-blue-50 border-blue-200';
      if (name.includes('immediate')) return 'bg-red-50 border-red-200';
      if (name.includes('short-term') || name.includes('short term')) return 'bg-amber-50 border-amber-200';
      if (name.includes('long-term') || name.includes('long term')) return 'bg-green-50 border-green-200';
      if (name.includes('number') || name.includes('amount')) return 'bg-purple-50 border-purple-200';
      if (name.includes('monitor') || name.includes('track')) return 'bg-indigo-50 border-indigo-200';
      if (name.includes('warning') || name.includes('avoid')) return 'bg-red-50 border-red-300';
      return 'bg-gray-50 border-gray-200';
    };

    const getSectionTextColor = (sectionName: string) => {
      const name = sectionName.toLowerCase();
      if (name.includes('current') || name.includes('situation')) return 'text-blue-900';
      if (name.includes('immediate')) return 'text-red-900';
      if (name.includes('short-term') || name.includes('short term')) return 'text-amber-900';
      if (name.includes('long-term') || name.includes('long term')) return 'text-green-900';
      if (name.includes('number') || name.includes('amount')) return 'text-purple-900';
      if (name.includes('monitor') || name.includes('track')) return 'text-indigo-900';
      if (name.includes('warning') || name.includes('avoid')) return 'text-red-900';
      return 'text-gray-900';
    };

    return (
      <div className="space-y-6">
        {Object.entries(sections).map(([sectionName, content], index) => (
          <div key={index} className={`rounded-lg border p-6 ${getSectionColor(sectionName)}`}>
            <div className={`flex items-center mb-4 ${getSectionTextColor(sectionName)}`}>
              {getSectionIcon(sectionName)}
              <h4 className="text-lg font-bold ml-2">{sectionName}</h4>
            </div>
            <div className="space-y-2">
              {formatSectionContent(content)}
            </div>
          </div>
        ))}
      </div>
    );
  };

  if (loading && !creditProfile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-amber-600 mx-auto mb-4" />
          <p className="text-amber-800">Loading your credit profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-amber-900 mb-2 flex items-center">
                <Shield className="w-8 h-8 mr-3 text-amber-700" />
                Credit Score Improvement Hub
              </h1>
              <p className="text-amber-800">
                Get personalized recommendations to improve your credit score with accurate credit card data.
              </p>
            </div>
            <button
              onClick={() => onNavigate?.('dashboard')}
              className="text-amber-700 hover:text-amber-900 flex items-center"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-100 border border-red-300 text-red-800 px-4 py-3 rounded-lg flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Credit Card Management Section */}
        <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
          <div className="px-6 py-4 border-b border-amber-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                <CreditCard className="w-5 h-5 mr-2" />
                Credit Cards ({profileForm.credit_cards.length})
              </h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowAddCard(true)}
                  className="bg-amber-600 text-white px-3 py-1 rounded-lg hover:bg-amber-700 flex items-center text-sm"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Card
                </button>
                <button
                  onClick={() => toggleSection('cards')}
                  className="text-amber-600 hover:text-amber-800"
                >
                  {expandedSections.cards ? <ChevronUp /> : <ChevronDown />}
                </button>
              </div>
            </div>
          </div>

          {expandedSections.cards && (
            <div className="p-6">
              {/* Add New Card Form */}
              {showAddCard && (
                <div className="mb-6 p-4 border border-amber-200 rounded-lg bg-amber-50">
                  <h4 className="font-medium text-amber-900 mb-4">Add New Credit Card</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-amber-700 mb-2">
                        Card Name <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        placeholder="e.g., HDFC Regalia Credit Card"
                        value={newCard.name}
                        onChange={(e) => setNewCard(prev => ({ ...prev, name: e.target.value }))}
                        className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                        required
                      />
                      {!newCard.name?.trim() && (
                        <p className="text-xs text-red-600 mt-1">Card name is required</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-amber-700 mb-2">
                        Credit Limit (₹) <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        placeholder="300000"
                        min="0"
                        step="1000"
                        value={newCard.credit_limit || ''}
                        onChange={(e) => {
                          const value = parseFloat(e.target.value);
                          setNewCard(prev => ({ 
                            ...prev, 
                            credit_limit: isNaN(value) ? 0 : value 
                          }));
                        }}
                        className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                        required
                      />
                      {(!newCard.credit_limit || newCard.credit_limit <= 0) && (
                        <p className="text-xs text-red-600 mt-1">Credit limit must be greater than 0</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-amber-700 mb-2">
                        Current Balance (₹)
                      </label>
                      <input
                        type="number"
                        placeholder="125000"
                        min="0"
                        step="100"
                        value={newCard.current_balance || ''}
                        onChange={(e) => {
                          const value = parseFloat(e.target.value);
                          setNewCard(prev => ({ 
                            ...prev, 
                            current_balance: isNaN(value) ? 0 : Math.max(0, value)
                          }));
                        }}
                        className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                      />
                      {newCard.current_balance > newCard.credit_limit * 1.1 && (
                        <p className="text-xs text-red-600 mt-1">Balance cannot exceed limit by more than 10%</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-amber-700 mb-2">
                        Interest Rate (% APR)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="50"
                        placeholder="24"
                        value={newCard.interest_rate || ''}
                        onChange={(e) => {
                          const value = parseFloat(e.target.value);
                          setNewCard(prev => ({ 
                            ...prev, 
                            interest_rate: isNaN(value) ? undefined : Math.min(50, Math.max(0, value))
                          }));
                        }}
                        className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-amber-700 mb-2">
                        Minimum Payment (₹)
                      </label>
                      <input
                        type="number"
                        placeholder="3750"
                        min="0"
                        step="50"
                        value={newCard.minimum_payment || ''}
                        onChange={(e) => {
                          const value = parseFloat(e.target.value);
                          setNewCard(prev => ({ 
                            ...prev, 
                            minimum_payment: isNaN(value) ? undefined : Math.max(0, value)
                          }));
                        }}
                        className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-amber-700 mb-2">
                        Statement Date (Day of Month)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="31"
                        placeholder="15"
                        value={newCard.statement_date || ''}
                        onChange={(e) => {
                          const value = parseInt(e.target.value);
                          setNewCard(prev => ({ 
                            ...prev, 
                            statement_date: isNaN(value) ? undefined : Math.min(31, Math.max(1, value))
                          }));
                        }}
                        className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={addCreditCard}
                      disabled={!newCard.name?.trim() || !newCard.credit_limit || newCard.credit_limit <= 0}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      Add Card
                    </button>
                    <button
                      onClick={() => {
                        setShowAddCard(false);
                        setNewCard({
                          name: '',
                          credit_limit: 0,
                          current_balance: 0,
                          interest_rate: 24,
                          minimum_payment: 0
                        });
                      }}
                      className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Credit Cards List */}
              <div className="grid gap-4">
                {profileForm.credit_cards.length === 0 ? (
                  <div className="text-center py-8 text-amber-600">
                    <CreditCard className="w-12 h-12 mx-auto mb-3 text-amber-300" />
                    <p className="mb-2">No credit cards added yet</p>
                    <p className="text-sm">Add your credit cards to get accurate utilization calculations</p>
                  </div>
                ) : (
                  profileForm.credit_cards.map((card, index) => (
                    <div key={index} className="border border-amber-200 rounded-lg p-4 bg-white">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-medium text-amber-900">{card.name}</h4>
                          <div className="text-sm text-amber-600">
                            Limit: ₹{card.credit_limit.toLocaleString()}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => setEditingCard(editingCard === card.name ? null : card.name)}
                            className="text-amber-600 hover:text-amber-800 p-1"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => removeCard(card.name)}
                            className="text-red-600 hover:text-red-800 p-1"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <div className="text-amber-700">Balance</div>
                          {editingCard === card.name ? (
                            <input
                              type="number"
                              value={card.current_balance}
                              onChange={(e) => {
                                const newBalance = parseFloat(e.target.value) || 0;
                                setProfileForm(prev => ({
                                  ...prev,
                                  credit_cards: prev.credit_cards.map(c => 
                                    c.name === card.name ? { ...c, current_balance: newBalance } : c
                                  )
                                }));
                              }}
                              className="w-full px-2 py-1 border border-amber-300 rounded text-sm"
                            />
                          ) : (
                            <div className="font-medium">₹{card.current_balance.toLocaleString()}</div>
                          )}
                        </div>
                        <div>
                          <div className="text-amber-700">Utilization</div>
                          <div className={`font-medium px-2 py-1 rounded text-xs ${getUtilizationColor(card.utilization_percent || 0)}`}>
                            {((card.current_balance / card.credit_limit) * 100).toFixed(1)}%
                          </div>
                        </div>
                        <div>
                          <div className="text-amber-700">Available</div>
                          <div className="font-medium text-green-600">
                            ₹{(card.credit_limit - card.current_balance).toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-amber-700">APR</div>
                          <div className="font-medium">{card.interest_rate || 'N/A'}%</div>
                        </div>
                      </div>

                      {editingCard === card.name && (
                        <div className="flex gap-2 mt-3">
                          <button
                            onClick={() => updateCardBalance(card.name, card.current_balance)}
                            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingCard(null)}
                            className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
                          >
                            Cancel
                          </button>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Current Credit Status */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-amber-900">Current Credit Status</h3>
            </div>
            <div className="text-center mb-4">
              <div className={`text-4xl font-bold mb-2 ${getScoreColor(creditProfile?.current_score || 650)}`}>
                {creditProfile?.current_score || 650}
              </div>
              <div className="text-sm text-amber-600">Current Credit Score</div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-amber-700">Target Score:</span>
                <span className="font-semibold text-amber-900">{creditProfile?.target_score || 750}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-amber-700">Last Checked:</span>
                <span className="text-amber-900">{formatLastChecked(creditProfile?.last_checked || 'never_checked')}</span>
              </div>
            </div>
          </div>

          {/* Credit Utilization */}
          <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-amber-900 mb-4">Credit Utilization</h3>
            <div className="text-center mb-4">
              <div className={`text-3xl font-bold mb-2 ${
                (creditProfile?.factors_assessment?.current_utilization_percent || 0) > 30
                  ? 'text-red-600'
                  : 'text-green-600'
              }`}>
                {(creditProfile?.factors_assessment?.current_utilization_percent || 0).toFixed(1)}%
              </div>
              <div className="text-sm text-amber-600">Current Utilization</div>
            </div>
            <div className="space-y-2">
              <div className="w-full bg-amber-100 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    (creditProfile?.factors_assessment?.current_utilization_percent || 0) > 30
                      ? 'bg-red-500'
                      : 'bg-green-500'
                  }`}
                  style={{
                    width: `${Math.min(creditProfile?.factors_assessment?.current_utilization_percent || 0, 100)}%`
                  }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-amber-600">
                <span>0%</span>
                <span className="font-semibold">Target: &lt;30%</span>
                <span>100%</span>
              </div>
            </div>
            <div className="mt-4 text-sm text-amber-700">
              <div>Total Balances: ₹{(creditProfile?.factors_assessment?.total_revolving_balances || 0).toLocaleString()}</div>
              <div>Total Limits: ₹{(creditProfile?.factors_assessment?.total_credit_limits || 0).toLocaleString()}</div>
            </div>
          </div>

          {/* Score Prediction */}
          <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-amber-900 mb-4">Score Improvement Prediction</h3>
            {creditProfile?.score_prediction ? (
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <span className="text-2xl font-bold text-amber-900">
                    {creditProfile.score_prediction.predicted_score}
                  </span>
                  <TrendingUp className="w-5 h-5 text-green-600 ml-2" />
                </div>
                <div className="text-sm text-amber-600 mb-3">Predicted Score</div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-amber-700">Improvement:</span>
                    <span className="text-green-600 font-semibold">
                      +{creditProfile.score_prediction.improvement_points} points
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-amber-700">Timeline:</span>
                    <span className="text-amber-900">{creditProfile.score_prediction.timeline_months} months</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-amber-600">
                <Target className="w-8 h-8 mx-auto mb-2 text-amber-300" />
                <p>Add credit cards and generate tips to see prediction</p>
              </div>
            )}
          </div>
        </div>

        {/* Credit Profile Setup */}
        <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
          <div className="px-6 py-4 border-b border-amber-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-amber-900">Credit Factors Assessment</h3>
              <button
                onClick={() => toggleSection('factors')}
                className="text-amber-600 hover:text-amber-800"
              >
                {expandedSections.factors ? <ChevronUp /> : <ChevronDown />}
              </button>
            </div>
          </div>

          {expandedSections.factors && (
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left Column */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-amber-700 mb-2">
                      Current Credit Score
                    </label>
                    <input
                      type="number"
                      min="300"
                      max="850"
                      value={profileForm.current_score}
                      onChange={(e) => setProfileForm(prev => ({
                        ...prev,
                        current_score: parseInt(e.target.value)
                      }))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-amber-700 mb-2">
                      Target Credit Score
                    </label>
                    <input
                      type="number"
                      min="300"
                      max="850"
                      value={profileForm.target_score}
                      onChange={(e) => setProfileForm(prev => ({
                        ...prev,
                        target_score: parseInt(e.target.value)
                      }))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-amber-700 mb-2">
                      Payment History
                    </label>
                    <select
                      value={profileForm.payment_history}
                      onChange={(e) => setProfileForm(prev => ({
                        ...prev,
                        payment_history: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    >
                      <option value="always_on_time">Always on time</option>
                      <option value="occasional_late">1-2 late payments this year</option>
                      <option value="several_late">Several late payments</option>
                      <option value="missed_recent">Missed payments recently</option>
                    </select>
                  </div>
                </div>

                {/* Right Column */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-amber-700 mb-2">
                      Average Age of Accounts (years)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="50"
                      step="0.5"
                      value={profileForm.average_account_age_years}
                      onChange={(e) => setProfileForm(prev => ({
                        ...prev,
                        average_account_age_years: parseFloat(e.target.value)
                      }))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-amber-700 mb-2">
                      New Accounts in Last 2 Years
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={profileForm.new_accounts_last_2_years}
                      onChange={(e) => setProfileForm(prev => ({
                        ...prev,
                        new_accounts_last_2_years: parseInt(e.target.value)
                      }))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-amber-700 mb-2">
                      Last Credit Check
                    </label>
                    <select
                      value={profileForm.last_checked}
                      onChange={(e) => setProfileForm(prev => ({
                        ...prev,
                        last_checked: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    >
                      <option value="this_month">This month</option>
                      <option value="1-3_months">1-3 months ago</option>
                      <option value="6+_months">6+ months ago</option>
                      <option value="never_checked">Never checked</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <button
                  onClick={updateCreditProfile}
                  disabled={loading}
                  className="flex-1 bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Shield className="w-4 h-4 mr-2" />}
                  Update Profile
                </button>
                <button
                  onClick={generatePersonalizedTips}
                  disabled={generating}
                  className="flex-1 bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-2 rounded-lg hover:from-amber-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {generating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Star className="w-4 h-4 mr-2" />}
                  Get Personalized Credit Improvement Plan
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Utilization Breakdown */}
        {creditAnalysis?.utilization_breakdown && (
          <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
            <div className="px-6 py-4 border-b border-amber-200">
              <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Credit Utilization Breakdown
              </h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-amber-900">
                    ₹{creditAnalysis.utilization_breakdown.amount_to_pay_down.toLocaleString()}
                  </div>
                  <div className="text-sm text-amber-600">Amount to Pay Down</div>
                  <div className="text-xs text-amber-500 mt-1">To reach 30% target</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    ₹{(creditAnalysis.utilization_breakdown.total_limits - creditAnalysis.utilization_breakdown.total_balances).toLocaleString()}
                  </div>
                  <div className="text-sm text-amber-600">Available Credit</div>
                  <div className="text-xs text-amber-500 mt-1">Unused credit limit</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {creditAnalysis.utilization_breakdown.cards_above_30_percent?.length || 0}
                  </div>
                  <div className="text-sm text-amber-600">Cards Above 30%</div>
                  <div className="text-xs text-amber-500 mt-1">Need attention</div>
                </div>
              </div>

              {/* Paydown Recommendations */}
              {creditAnalysis.utilization_breakdown.paydown_recommendations && 
               Object.keys(creditAnalysis.utilization_breakdown.paydown_recommendations).length > 0 && (
                <div className="bg-amber-50 rounded-lg p-4">
                  <h4 className="font-medium text-amber-900 mb-3">Recommended Paydowns:</h4>
                  <div className="space-y-2">
                    {Object.entries(creditAnalysis.utilization_breakdown.paydown_recommendations).map(([cardName, amount]) => (
                      <div key={cardName} className="flex justify-between items-center">
                        <span className="text-amber-800">{cardName}</span>
                        <span className="font-medium text-amber-900">₹{amount.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI Generated Analysis */}
        {creditAnalysis && (
          <div className="space-y-6">
            {/* Success Message */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
              <span className="text-green-800 font-medium">Personalized Credit Improvement Plan Generated!</span>
            </div>

            {/* Credit Score Action Plan */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
              <div className="px-6 py-4 border-b border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50">
                <h3 className="text-xl font-bold text-amber-900 flex items-center">
                  <Target className="w-6 h-6 mr-3" />
                  Comprehensive Credit Improvement Plan
                </h3>
                <p className="text-amber-700 mt-1">Your personalized roadmap to excellent credit</p>
              </div>
              <div className="p-6">
                <div className="credit-plan-content">
                  {formatCreditPlan(creditAnalysis.ai_generated_plan)}
                </div>
              </div>
            </div>

            {/* Quick Wins */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                  <Star className="w-5 h-5 mr-2" />
                  Quick Wins (30-90 days)
                </h3>
              </div>
              <div className="p-6">
                <div className="grid gap-4">
                  {creditAnalysis.personalized_tips.map((tip, index) => (
                    <div key={index} className="flex items-start p-4 bg-amber-50 rounded-lg border border-amber-100">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-amber-900">{tip}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Debt Management for Credit */}
            {creditAnalysis.debt_impact.payment_optimization_tips.length > 0 && (
              <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
                <div className="px-6 py-4 border-b border-amber-200">
                  <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                    <CreditCard className="w-5 h-5 mr-2" />
                    Debt Management for Credit Improvement
                  </h3>
                </div>
                <div className="p-6 space-y-4">
                  {creditAnalysis.debt_impact.payment_optimization_tips.map((tip, index) => (
                    <div key={index} className="flex items-start p-4 border border-amber-200 rounded-lg">
                      <Info className="w-5 h-5 text-amber-600 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-amber-900">{tip}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* High Utilization Alerts */}
            {creditAnalysis.debt_impact.high_utilization_debts.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-red-900 mb-4 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  High Utilization Alert
                </h3>
                <div className="space-y-3">
                  {creditAnalysis.debt_impact.high_utilization_debts.map((debt, index) => (
                    <div key={index} className="bg-white p-3 rounded border">
                      <div className="font-medium text-red-900">{debt.name || 'Credit Card'}</div>
                      <div className="text-sm text-red-700">
                        Utilization: {debt.utilization?.toFixed(1) || debt.estimated_utilization?.toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Next Steps */}
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-200 p-6">
              <h3 className="text-lg font-semibold text-amber-900 mb-4 flex items-center">
                <ArrowRight className="w-5 h-5 mr-2" />
                Next Steps
              </h3>
              <div className="grid gap-3">
                {creditAnalysis.next_steps.map((step, index) => (
                  <div key={index} className="flex items-center text-amber-900">
                    <span className="bg-amber-200 text-amber-800 text-sm font-semibold px-2 py-1 rounded-full mr-3">
                      {index + 1}
                    </span>
                    {step}
                  </div>
                ))}
              </div>
            </div>

            {/* Progress Tracking */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Progress Tracking
                </h3>
              </div>
              <div className="p-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-amber-900 mb-3">Monthly Checklist:</h4>
                    <div className="space-y-2 text-sm text-amber-800">
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2 text-amber-600" />
                        All payments made on time
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2 text-amber-600" />
                        Credit card balances updated
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2 text-amber-600" />
                        No new credit applications
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2 text-amber-600" />
                        Utilization under 30%
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-amber-900 mb-3">Quarterly Review:</h4>
                    <div className="space-y-2 text-sm text-amber-800">
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2 text-amber-600" />
                        Check credit score
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2 text-amber-600" />
                        Review credit report
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2 text-amber-600" />
                        Assess progress toward goals
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2 text-amber-600" />
                        Update credit card information
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Call to Action when no analysis */}
        {!creditAnalysis && !generating && (
          <div className="bg-gradient-to-r from-amber-100 to-orange-100 rounded-lg border border-amber-300 p-8 text-center">
            <Shield className="w-16 h-16 text-amber-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-amber-900 mb-2">
              Ready to Improve Your Credit Score?
            </h3>
            <p className="text-amber-800 mb-6 max-w-2xl mx-auto">
              Add your credit cards above and generate your personalized improvement plan.
              Our AI will analyze your actual credit data and provide specific, actionable recommendations to boost your credit score.
            </p>
            {profileForm.credit_cards.length === 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 max-w-md mx-auto">
                <p className="text-sm text-amber-700">
                  <Info className="w-4 h-4 inline mr-1" />
                  Add at least one credit card for accurate utilization calculations
                </p>
              </div>
            )}
            <button
              onClick={generatePersonalizedTips}
              className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-3 rounded-lg hover:from-amber-600 hover:to-orange-600 flex items-center mx-auto"
            >
              <Star className="w-5 h-5 mr-2" />
              Generate Your Credit Improvement Plan
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreditScore;