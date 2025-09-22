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
  ChevronUp
} from 'lucide-react';

interface CreditScoreProps {
  onNavigate?: (page: string) => void;
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
  };
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
    tips: false
  });

  // Form state for credit profile
  const [profileForm, setProfileForm] = useState({
    current_score: 650,
    target_score: 750,
    last_checked: 'this_month',
    payment_history: 'always_on_time',
    average_account_age_years: 3.0,
    new_accounts_last_2_years: 1,
    account_types: ['credit_card']
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
      throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
  };

  const fetchCreditProfile = async () => {
    try {
      const profile = await apiCall('/api/v1/credit/profile');
      setCreditProfile(profile);
      
      // Update form with fetched data
      setProfileForm({
        current_score: profile.current_score || 650,
        target_score: profile.target_score || 750,
        last_checked: profile.last_checked || 'this_month',
        payment_history: profile.factors_assessment?.payment_history || 'always_on_time',
        average_account_age_years: profile.factors_assessment?.average_account_age_years || 3.0,
        new_accounts_last_2_years: profile.factors_assessment?.new_accounts_last_2_years || 1,
        account_types: profile.factors_assessment?.account_types || ['credit_card']
      });
    } catch (err) {
      console.error('Error fetching credit profile:', err);
      setError('Failed to load credit profile');
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

  const refreshUtilization = async () => {
    try {
      await apiCall('/api/v1/credit/refresh-utilization', {
        method: 'POST'
      });
      await fetchCreditProfile();
    } catch (err) {
      console.error('Error refreshing utilization:', err);
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

  const getScoreBgColor = (score: number) => {
    if (score >= 750) return 'bg-green-100';
    if (score >= 650) return 'bg-amber-100';
    return 'bg-red-100';
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
                Get personalized recommendations to improve your credit score based on your debt profile.
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
          <div className="mb-6 bg-red-100 border border-red-300 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Current Credit Status */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-amber-900">Current Credit Status</h3>
              <button
                onClick={refreshUtilization}
                className="p-2 text-amber-600 hover:text-amber-800 hover:bg-amber-50 rounded-lg"
                title="Refresh utilization from debt data"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
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
                <p>Generate tips to see prediction</p>
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
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  Credit Score Action Plan
                </h3>
              </div>
              <div className="p-6">
                <div className="prose prose-amber max-w-none">
                  <div className="whitespace-pre-line text-amber-900 leading-relaxed">
                    {creditAnalysis.ai_generated_plan}
                  </div>
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
                        Balances paid down
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
                        Celebrate improvements!
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
              Fill out your credit factors above and generate your personalized improvement plan. 
              Our AI will analyze your debt data and provide specific, actionable recommendations to boost your credit score.
            </p>
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