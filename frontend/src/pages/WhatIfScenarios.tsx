import React, { useState, useEffect } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';
import {
  Coffee,
  Calculator,
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  Target,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  BarChart3,
  Download
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface WhatIfScenariosProps {
  onNavigate?: (page: string) => void;
}

interface ScenarioComparison {
  baseline: {
    months: number;
    total_interest: number;
    total_payments: number;
    balance_series: number[];
  };
  scenario: {
    months: number;
    total_interest: number;
    total_payments: number;
    balance_series: number[];
  };
  interest_savings: number;
  months_saved: number;
  payment_difference: number;
  insights: string[];
}

const WhatIfScenarios: React.FC<WhatIfScenariosProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const { user } = useUser();
  
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState<ScenarioComparison | null>(null);
  
  // Form state
  const [baseBudget, setBaseBudget] = useState(15000);
  const [baseStrategy, setBaseStrategy] = useState<'avalanche' | 'snowball' | 'optimal'>('avalanche');
  const [analysisMonths, setAnalysisMonths] = useState(60);
  const [scenarioType, setScenarioType] = useState<'extra_payment' | 'budget_reduction' | 'interest_rate_change' | 'debt_consolidation' | 'windfall'>('extra_payment');
  
  // Scenario-specific parameters
  const [extraPayment, setExtraPayment] = useState(3000);
  const [budgetReduction, setBudgetReduction] = useState(2000);
  const [rateChangePercent, setRateChangePercent] = useState(0);
  const [affectedDebts, setAffectedDebts] = useState<string[]>(['All']);
  const [consolidationRate, setConsolidationRate] = useState(12);
  const [consolidationFee, setConsolidationFee] = useState(5000);
  const [windfallAmount, setWindfallAmount] = useState(50000);
  const [windfallMonth, setWindfallMonth] = useState(1);

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      
      const requestBody = {
        scenario_type: scenarioType,
        base_budget: baseBudget,
        base_strategy: baseStrategy,
        analysis_months: analysisMonths,
        extra_payment: scenarioType === 'extra_payment' ? extraPayment : 0,
        budget_reduction: scenarioType === 'budget_reduction' ? budgetReduction : 0,
        rate_change_percent: scenarioType === 'interest_rate_change' ? rateChangePercent : 0,
        affected_debts: scenarioType === 'interest_rate_change' ? affectedDebts : [],
        consolidation_rate: scenarioType === 'debt_consolidation' ? consolidationRate : 0,
        consolidation_fee: scenarioType === 'debt_consolidation' ? consolidationFee : 0,
        windfall_amount: scenarioType === 'windfall' ? windfallAmount : 0,
        windfall_month: scenarioType === 'windfall' ? windfallMonth : 1
      };

      const response = await fetch('http://localhost:8000/api/v1/scenarios/what-if', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const data = await response.json();
        setComparison(data);
      } else {
        const errorData = await response.json();
        console.error('Failed to run analysis:', errorData);
        alert(`Error: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error running analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  const getBalanceComparisonData = () => {
    if (!comparison) return [];
    
    const maxLength = Math.max(
      comparison.baseline.balance_series.length,
      comparison.scenario.balance_series.length
    );
    
    const data = [];
    for (let i = 0; i < maxLength; i++) {
      data.push({
        month: i,
        baseline: comparison.baseline.balance_series[i] || 0,
        scenario: comparison.scenario.balance_series[i] || 0
      });
    }
    return data;
  };

  const getScenarioTitle = () => {
    switch (scenarioType) {
      case 'extra_payment':
        return `Extra Monthly Payment of ${formatCurrency(extraPayment)}`;
      case 'budget_reduction':
        return `Budget Reduction of ${formatCurrency(budgetReduction)}`;
      case 'interest_rate_change':
        return `Interest Rate ${rateChangePercent > 0 ? 'Increase' : 'Decrease'} of ${Math.abs(rateChangePercent)}%`;
      case 'debt_consolidation':
        return `Debt Consolidation at ${consolidationRate}% APR`;
      case 'windfall':
        return `Windfall of ${formatCurrency(windfallAmount)} in Month ${windfallMonth}`;
      default:
        return 'Scenario Analysis';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      {/* Header */}
      <header className="bg-white border-b border-amber-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => onNavigate?.('dashboard')}
                className="flex items-center space-x-2 text-amber-700 hover:text-amber-800"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Dashboard</span>
              </button>
              <div className="h-6 w-px bg-amber-200"></div>
              <div className="flex items-center space-x-3">
                <Coffee className="w-6 h-6 text-amber-700" />
                <h1 className="text-xl font-bold text-amber-900">What-If Scenarios</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Scenario Setup */}
        <div className="bg-white rounded-lg border border-amber-200 shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-amber-900 mb-6">Scenario Setup</h2>
          
          {/* Base Scenario */}
          <div className="mb-6">
            <h3 className="text-lg font-medium text-amber-800 mb-4">Base Scenario</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-amber-800 mb-2">
                  Base Monthly Budget (₹)
                </label>
                <input
                  type="number"
                  value={baseBudget}
                  onChange={(e) => setBaseBudget(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                  min="0"
                  step="1000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-amber-800 mb-2">
                  Base Strategy
                </label>
                <select
                  value={baseStrategy}
                  onChange={(e) => setBaseStrategy(e.target.value as any)}
                  className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                >
                  <option value="avalanche">Debt Avalanche</option>
                  <option value="snowball">Debt Snowball</option>
                  <option value="optimal">Mathematical Optimal</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-amber-800 mb-2">
                  Analysis Period (months)
                </label>
                <input
                  type="number"
                  value={analysisMonths}
                  onChange={(e) => setAnalysisMonths(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                  min="12"
                  max="120"
                  step="6"
                />
              </div>
            </div>
          </div>

          {/* What-If Scenario */}
          <div className="mb-6">
            <h3 className="text-lg font-medium text-amber-800 mb-4">What-If Scenario</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-amber-800 mb-2">
                Scenario Type
              </label>
              <select
                value={scenarioType}
                onChange={(e) => setScenarioType(e.target.value as any)}
                className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
              >
                <option value="extra_payment">Extra Monthly Payment</option>
                <option value="budget_reduction">Budget Reduction</option>
                <option value="interest_rate_change">Interest Rate Change</option>
                <option value="debt_consolidation">Debt Consolidation</option>
                <option value="windfall">Windfall/Lump Sum</option>
              </select>
            </div>

            {/* Scenario-specific inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {scenarioType === 'extra_payment' && (
                <div>
                  <label className="block text-sm font-medium text-amber-800 mb-2">
                    Extra Monthly Payment (₹)
                  </label>
                  <input
                    type="number"
                    value={extraPayment}
                    onChange={(e) => setExtraPayment(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                    min="0"
                    step="500"
                  />
                </div>
              )}

              {scenarioType === 'budget_reduction' && (
                <div>
                  <label className="block text-sm font-medium text-amber-800 mb-2">
                    Budget Reduction (₹)
                  </label>
                  <input
                    type="number"
                    value={budgetReduction}
                    onChange={(e) => setBudgetReduction(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                    min="0"
                    step="500"
                  />
                </div>
              )}

              {scenarioType === 'interest_rate_change' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-amber-800 mb-2">
                      APR Change (%)
                    </label>
                    <input
                      type="number"
                      value={rateChangePercent}
                      onChange={(e) => setRateChangePercent(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                      step="0.5"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-amber-800 mb-2">
                      Affected Debts
                    </label>
                    <select
                      value={affectedDebts[0] || 'All'}
                      onChange={(e) => setAffectedDebts([e.target.value])}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                    >
                      <option value="All">All Debts</option>
                    </select>
                  </div>
                </>
              )}

              {scenarioType === 'debt_consolidation' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-amber-800 mb-2">
                      Consolidation APR (%)
                    </label>
                    <input
                      type="number"
                      value={consolidationRate}
                      onChange={(e) => setConsolidationRate(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                      min="0"
                      max="100"
                      step="0.5"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-amber-800 mb-2">
                      One-time Fee (₹)
                    </label>
                    <input
                      type="number"
                      value={consolidationFee}
                      onChange={(e) => setConsolidationFee(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                      min="0"
                      step="1000"
                    />
                  </div>
                </>
              )}

              {scenarioType === 'windfall' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-amber-800 mb-2">
                      Windfall Amount (₹)
                    </label>
                    <input
                      type="number"
                      value={windfallAmount}
                      onChange={(e) => setWindfallAmount(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                      min="0"
                      step="5000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-amber-800 mb-2">
                      Apply in Month
                    </label>
                    <input
                      type="number"
                      value={windfallMonth}
                      onChange={(e) => setWindfallMonth(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                      min="1"
                      step="1"
                    />
                  </div>
                </>
              )}
            </div>
          </div>

          <button
            onClick={runAnalysis}
            disabled={loading}
            className="flex items-center space-x-2 bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Calculator className="w-4 h-4" />}
            <span>{loading ? 'Running Analysis...' : 'Run What-If Analysis'}</span>
          </button>
        </div>

        {/* Results */}
        {comparison && (
          <>
            {/* Comparison Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <Calendar className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Time Difference</div>
                    <div className="text-2xl font-bold text-amber-900">
                      {comparison.scenario.months} months
                    </div>
                    <div className={`text-sm ${comparison.months_saved > 0 ? 'text-green-600' : comparison.months_saved < 0 ? 'text-red-600' : 'text-amber-600'}`}>
                      {comparison.months_saved > 0 ? `${comparison.months_saved} months earlier` : 
                       comparison.months_saved < 0 ? `${Math.abs(comparison.months_saved)} months later` : 
                       'No change'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <DollarSign className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Interest Cost</div>
                    <div className="text-2xl font-bold text-amber-900">
                      {formatCurrency(comparison.scenario.total_interest)}
                    </div>
                    <div className={`text-sm ${comparison.interest_savings > 0 ? 'text-green-600' : comparison.interest_savings < 0 ? 'text-red-600' : 'text-amber-600'}`}>
                      {comparison.interest_savings > 0 ? `${formatCurrency(comparison.interest_savings)} saved` : 
                       comparison.interest_savings < 0 ? `${formatCurrency(Math.abs(comparison.interest_savings))} more` : 
                       'No change'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <Target className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Total Payments</div>
                    <div className="text-2xl font-bold text-amber-900">
                      {formatCurrency(comparison.scenario.total_payments)}
                    </div>
                    <div className={`text-sm ${comparison.payment_difference < 0 ? 'text-green-600' : comparison.payment_difference > 0 ? 'text-red-600' : 'text-amber-600'}`}>
                      {comparison.payment_difference > 0 ? `+${formatCurrency(comparison.payment_difference)}` :
                       comparison.payment_difference < 0 ? `-${formatCurrency(Math.abs(comparison.payment_difference))}` :
                       'No change'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  {comparison.interest_savings > 0 ? 
                    <TrendingUp className="w-8 h-8 text-green-600" /> : 
                    comparison.interest_savings < 0 ? 
                    <TrendingDown className="w-8 h-8 text-red-600" /> :
                    <BarChart3 className="w-8 h-8 text-amber-700" />
                  }
                  <div>
                    <div className="text-sm font-medium text-amber-700">Overall Impact</div>
                    <div className={`text-xl font-bold ${comparison.interest_savings > 0 ? 'text-green-600' : comparison.interest_savings < 0 ? 'text-red-600' : 'text-amber-900'}`}>
                      {comparison.interest_savings > 0 ? 'Beneficial' : 
                       comparison.interest_savings < 0 ? 'Costly' : 
                       'Neutral'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Visual Comparison */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900">Visual Comparison</h3>
                <p className="text-sm text-amber-600 mt-1">{getScenarioTitle()}</p>
              </div>

              <div className="p-6">
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={getBalanceComparisonData()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                      <XAxis dataKey="month" stroke="#92400e" />
                      <YAxis stroke="#92400e" tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`} />
                      <Tooltip formatter={(value) => [formatCurrency(value as number), '']} />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="baseline"
                        stroke="#dc2626"
                        fill="#fecaca"
                        fillOpacity={0.6}
                        name="Base Scenario"
                        strokeWidth={2}
                      />
                      <Area
                        type="monotone"
                        dataKey="scenario"
                        stroke="#059669"
                        fill="#d1fae5"
                        fillOpacity={0.6}
                        name={getScenarioTitle()}
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Key Insights */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900">Key Insights</h3>
              </div>
              
              <div className="p-6">
                {comparison.insights.length > 0 ? (
                  <div className="space-y-3">
                    {comparison.insights.map((insight, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-1">
                          {insight.includes('earlier') || insight.includes('saves') || insight.includes('savings') ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : insight.includes('extends') || insight.includes('cost') || insight.includes('more') ? (
                            <AlertCircle className="w-5 h-5 text-red-600" />
                          ) : (
                            <BarChart3 className="w-5 h-5 text-amber-600" />
                          )}
                        </div>
                        <p className="text-amber-800">{insight}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-amber-600 text-center py-4">
                    No significant insights detected for this scenario.
                  </p>
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default WhatIfScenarios;