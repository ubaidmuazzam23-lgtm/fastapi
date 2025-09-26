import React, { useState, useEffect } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';
import {
  Coffee,
  TrendingUp,
  Calculator,
  BarChart3,
  PieChart,
  ArrowLeft,
  Download,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  IndianRupee,
  Calendar,
  Target,
  CreditCard,
  Map,
  BarChart2
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ComposedChart,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  RadialBarChart,
  RadialBar
} from 'recharts';

interface RepaymentPlansProps {
  onNavigate?: (page: string) => void;
}

interface Debt {
  id: string;
  name: string;
  balance: number;
  apr: number;
  monthly_interest: number;
}

interface DebtSummary {
  total_debt: number;
  monthly_minimums: number;
  weighted_apr: number;
  debt_count: number;
  available_budget: number;
  debts: Debt[];
}

interface AllocationResponse {
  name: string;
  payment: number;
  interest_accrued: number;
  principal_reduction: number;
}

interface RepaymentMonthResponse {
  month_index: number;
  allocations: AllocationResponse[];
  total_interest: number;
  total_paid: number;
}

interface RepaymentPlan {
  strategy_name: string;
  months: RepaymentMonthResponse[];
  total_interest_paid: number;
  months_to_debt_free: number;
  schedule_df: any[];
  balance_series: number[];
}

const RepaymentPlans: React.FC<RepaymentPlansProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const { user } = useUser();
  
  const [debtSummary, setDebtSummary] = useState<DebtSummary | null>(null);
  const [currentPlan, setCurrentPlan] = useState<RepaymentPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('balance-over-time');
  const [showAllMonths, setShowAllMonths] = useState(false);
  
  // Form state
  const [monthlyBudget, setMonthlyBudget] = useState(15000);
  const [strategy, setStrategy] = useState<'avalanche' | 'snowball' | 'optimal'>('avalanche');
  const [maxMonths, setMaxMonths] = useState(60);

  // Fetch debt summary on mount
  useEffect(() => {
    fetchDebtSummary();
  }, []);

  const fetchDebtSummary = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/plans/debt-summary', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Debt Summary Data:', data);
        setDebtSummary(data);
        setMonthlyBudget(Math.max(15000, data.available_budget + data.monthly_minimums));
      }
    } catch (error) {
      console.error('Error fetching debt summary:', error);
    }
  };

  const generatePlan = async () => {
    if (!debtSummary) return;
    
    setLoading(true);
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/plans/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy,
          monthly_budget: monthlyBudget,
          max_months: maxMonths
        }),
      });

      if (response.ok) {
        const plan = await response.json();
        console.log('Generated Plan:', plan);
        setCurrentPlan(plan);
      } else {
        const errorData = await response.json();
        console.error('Failed to generate plan:', errorData);
        alert(`Error: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error generating plan:', error);
    } finally {
      setLoading(false);
    }
  };

  // Chart data functions
  const getBalanceOverTimeData = () => {
    if (!currentPlan?.balance_series || !Array.isArray(currentPlan.balance_series)) {
      console.log('No balance series data available');
      return [];
    }
    
    const data = currentPlan.balance_series.map((balance, index) => ({
      month: index,
      balance: Number(balance) || 0,
      formattedBalance: `₹${((Number(balance) || 0) / 1000).toFixed(0)}K`
    }));
    
    console.log('Balance over time data:', data);
    return data;
  };

  const getMonthlyPaymentData = () => {
    if (!currentPlan?.months || !Array.isArray(currentPlan.months)) {
      console.log('No monthly payment data available');
      return [];
    }
    
    const data = currentPlan.months.slice(0, 12).map(month => ({
      month: month.month_index || 0,
      total_payment: Number(month.total_paid) || 0,
      interest: Number(month.total_interest) || 0,
      principal: (Number(month.total_paid) || 0) - (Number(month.total_interest) || 0)
    }));
    
    console.log('Monthly payment data:', data);
    return data;
  };

  const getInterestVsPrincipalData = () => {
    if (!currentPlan || !debtSummary) {
      console.log('No interest vs principal data available');
      return [];
    }
    
    const totalInterest = Number(currentPlan.total_interest_paid) || 0;
    const totalPrincipal = Number(debtSummary.total_debt) || 0;
    
    const data = [
      { name: 'Principal Payments', value: totalPrincipal, fill: '#059669' },
      { name: 'Interest Payments', value: totalInterest, fill: '#DC2626' }
    ];
    
    console.log('Interest vs principal data:', data);
    return data;
  };

  const getPaymentAllocationData = () => {
    if (!currentPlan?.months || !Array.isArray(currentPlan.months) || currentPlan.months.length === 0) {
      console.log('No payment allocation data - no months');
      return { data: [], debtNames: [] };
    }
    
    // Get first 12 months for area chart
    const monthsToShow = currentPlan.months.slice(0, Math.min(12, currentPlan.months.length));
    
    // Get all unique debt names
    const allDebts = new Set<string>();
    monthsToShow.forEach(month => {
      if (month.allocations && Array.isArray(month.allocations)) {
        month.allocations.forEach(alloc => {
          if (alloc && alloc.name && (Number(alloc.payment) || 0) > 0) {
            allDebts.add(alloc.name);
          }
        });
      }
    });
    
    const debtNames = Array.from(allDebts);
    
    // Create data structure for area chart
    const data = monthsToShow.map(month => {
      const monthData: any = {
        month: month.month_index || 0,
        total: Number(month.total_paid) || 0
      };
      
      // Add each debt's payment for this month
      debtNames.forEach(debtName => {
        const allocation = month.allocations?.find(alloc => alloc && alloc.name === debtName);
        monthData[debtName] = Number(allocation?.payment) || 0;
      });
      
      return monthData;
    });
    
    console.log('Payment allocation area chart data:', data);
    console.log('All debts:', debtNames);
    return { data, debtNames };
  };

  // Enhanced chart data functions
  const getDebtComparisonData = () => {
    if (!debtSummary?.debts || !Array.isArray(debtSummary.debts)) {
      console.log('No debt comparison data available');
      return [];
    }
    
    const data = debtSummary.debts.map((debt, index) => ({
      name: debt.name || `Debt ${index + 1}`,
      balance: Number(debt.balance) || 0,
      apr: Number(debt.apr) || 0,
      monthlyInterest: Number(debt.monthly_interest) || 0,
      // Calculate debt-to-income ratio (assuming monthly interest represents burden)
      riskScore: ((Number(debt.apr) || 0) * (Number(debt.balance) || 0)) / 100000, // Simple risk calculation
      id: debt.id
    }));
    
    console.log('Debt comparison data:', data);
    return data;
  };

  const getDebtBumpData = () => {
    if (!debtSummary?.debts || !Array.isArray(debtSummary.debts)) {
      console.log('No debt bump data available');
      return [];
    }
    
    // Create time series data showing debt evolution over payment plan
    if (!currentPlan?.months || currentPlan.months.length === 0) {
      // If no plan, show current state
      return [{
        month: 0,
        ...debtSummary.debts.reduce((acc, debt, index) => {
          acc[debt.name || `Debt ${index + 1}`] = Number(debt.balance) || 0;
          return acc;
        }, {} as any)
      }];
    }
    
    // Create bump chart data showing how debt balances change over time
    const monthsToShow = Math.min(currentPlan.months.length, 24); // Show up to 24 months
    const data = [];
    
    // Get all debt names
    const debtNames = Array.from(new Set(
      currentPlan.months.flatMap(month => 
        month.allocations?.map(alloc => alloc.name) || []
      ).filter(Boolean)
    ));
    
    // Track remaining balances for each debt over time
    const debtBalances = debtSummary.debts.reduce((acc, debt) => {
      acc[debt.name || debt.id] = Number(debt.balance) || 0;
      return acc;
    }, {} as Record<string, number>);
    
    // Calculate balance progression
    for (let i = 0; i <= monthsToShow; i++) {
      const monthData: any = { month: i };
      
      if (i === 0) {
        // Initial balances
        debtNames.forEach(debtName => {
          const debt = debtSummary.debts.find(d => d.name === debtName);
          monthData[debtName] = debt ? Number(debt.balance) || 0 : 0;
        });
      } else if (i <= currentPlan.months.length) {
        // Apply payments from previous month
        const previousMonth = currentPlan.months[i - 1];
        if (previousMonth && previousMonth.allocations) {
          previousMonth.allocations.forEach(allocation => {
            if (allocation.name && debtBalances[allocation.name] !== undefined) {
              debtBalances[allocation.name] = Math.max(
                0, 
                debtBalances[allocation.name] - (Number(allocation.principal_reduction) || 0)
              );
            }
          });
        }
        
        // Set balances for this month
        debtNames.forEach(debtName => {
          monthData[debtName] = debtBalances[debtName] || 0;
        });
      }
      
      data.push(monthData);
    }
    
    console.log('Debt bump chart data:', data);
    console.log('Debt names:', debtNames);
    return { data, debtNames };
  };

  const formatCurrency = (value: number) => {
    const numValue = Number(value) || 0;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(numValue);
  };

  const formatNumber = (value: number) => {
    const numValue = Number(value) || 0;
    return `₹${(numValue / 1000).toFixed(0)}K`;
  };

  const downloadSchedule = () => {
    if (!currentPlan?.months) return;
    
    const csvData = [
      ['Month', 'Debt Name', 'Payment', 'Interest', 'Principal', 'Monthly Total']
    ];
    
    currentPlan.months.forEach(month => {
      if (month.allocations && Array.isArray(month.allocations)) {
        month.allocations.forEach((allocation, index) => {
          csvData.push([
            (month.month_index || 0).toString(),
            allocation.name || '',
            (Number(allocation.payment) || 0).toFixed(2),
            (Number(allocation.interest_accrued) || 0).toFixed(2),
            (Number(allocation.principal_reduction) || 0).toFixed(2),
            index === 0 ? (Number(month.total_paid) || 0).toFixed(2) : ''
          ]);
        });
      }
    });
    
    const csvContent = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `repayment-schedule-${strategy}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const visualTabs = [
    { id: 'balance-over-time', label: 'Balance Over Time', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'monthly-payments', label: 'Monthly Payments', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'interest-vs-principal', label: 'Interest vs Principal', icon: <PieChart className="w-4 h-4" /> },
    { id: 'payment-allocation', label: 'Payment Allocation', icon: <IndianRupee className="w-4 h-4" /> },
    { id: 'debt-bump', label: 'Debt Evolution', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'debt-comparison', label: 'Debt Comparison', icon: <BarChart2 className="w-4 h-4" /> }
  ];

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
                <h1 className="text-xl font-bold text-amber-900">Repayment Plans</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Plan Configuration */}
        <div className="bg-white rounded-lg border border-amber-200 shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-amber-900 mb-4">Configure Your Repayment Plan</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-2">
                Monthly Budget (₹)
              </label>
              <input
                type="number"
                value={monthlyBudget}
                onChange={(e) => setMonthlyBudget(Number(e.target.value))}
                className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                min="0"
                step="1000"
              />
              {debtSummary && (
                <p className="text-xs text-amber-600 mt-1">
                  Min required: ₹{(Number(debtSummary.monthly_minimums) || 0).toLocaleString()}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-amber-800 mb-2">
                Strategy
              </label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value as any)}
                className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
              >
                <option value="avalanche">Debt Avalanche (Highest APR First)</option>
                <option value="snowball">Debt Snowball (Smallest Balance First)</option>
                <option value="optimal">Mathematical Optimal</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-amber-800 mb-2">
                Max Planning Horizon (months)
              </label>
              <input
                type="number"
                value={maxMonths}
                onChange={(e) => setMaxMonths(Number(e.target.value))}
                className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                min="12"
                max="120"
                step="6"
              />
            </div>
          </div>

          <button
            onClick={generatePlan}
            disabled={loading || !debtSummary}
            className="flex items-center space-x-2 bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Calculator className="w-4 h-4" />}
            <span>{loading ? 'Generating...' : 'Generate Repayment Plan'}</span>
          </button>

          {/* Budget Validation */}
          {debtSummary && (
            <div className="mt-4 p-4 rounded-lg bg-amber-50 border border-amber-200">
              <div className="flex items-center space-x-2">
                {monthlyBudget >= (Number(debtSummary.monthly_minimums) || 0) ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                )}
                <span className="text-sm font-medium text-amber-800">
                  {monthlyBudget >= (Number(debtSummary.monthly_minimums) || 0)
                    ? `Budget OK: ₹${(monthlyBudget - (Number(debtSummary.monthly_minimums) || 0)).toLocaleString()} available for extra payments`
                    : `Budget short by ₹${((Number(debtSummary.monthly_minimums) || 0) - monthlyBudget).toLocaleString()}`
                  }
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Current Plan Results */}
        {currentPlan && (
          <>
            {/* Plan Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <Calendar className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Time to Debt-Free</div>
                    <div className="text-2xl font-bold text-amber-900">
                      {Number(currentPlan.months_to_debt_free) || 0} months
                    </div>
                    <div className="text-sm text-amber-600">
                      {((Number(currentPlan.months_to_debt_free) || 0) / 12).toFixed(1)} years
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <IndianRupee className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Total Interest</div>
                    <div className="text-2xl font-bold text-amber-900">
                      {formatCurrency(Number(currentPlan.total_interest_paid) || 0)}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <Target className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Strategy</div>
                    <div className="text-xl font-bold text-amber-900">{currentPlan.strategy_name || 'Unknown'}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <Calculator className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Total Months</div>
                    <div className="text-xl font-bold text-amber-900">
                      {currentPlan.months?.length || 0}
                    </div>
                    <div className="text-sm text-amber-600">in schedule</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Visual Analysis Section */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900">📈 Visual Analysis</h3>
              </div>

              {/* Tab Navigation */}
              <div className="px-6 py-4 border-b border-amber-200">
                <div className="flex space-x-1 overflow-x-auto">
                  {visualTabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                        activeTab === tab.id
                          ? 'bg-amber-100 text-amber-800'
                          : 'text-amber-700 hover:text-amber-800 hover:bg-amber-50'
                      }`}
                    >
                      {tab.icon}
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Chart Content */}
              <div className="p-6">
                <div className="h-96">
                  {activeTab === 'balance-over-time' && (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={getBalanceOverTimeData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                        <XAxis dataKey="month" stroke="#92400e" />
                        <YAxis stroke="#92400e" tickFormatter={formatNumber} />
                        <Tooltip formatter={(value) => [formatCurrency(value as number), 'Balance']} />
                        <Area
                          type="monotone"
                          dataKey="balance"
                          stroke="#d97706"
                          fill="#fed7aa"
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}

                  {activeTab === 'monthly-payments' && (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getMonthlyPaymentData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                        <XAxis dataKey="month" stroke="#92400e" />
                        <YAxis stroke="#92400e" tickFormatter={formatNumber} />
                        <Tooltip formatter={(value) => [formatCurrency(value as number), '']} />
                        <Legend />
                        <Bar dataKey="interest" stackId="a" fill="#dc2626" name="Interest" />
                        <Bar dataKey="principal" stackId="a" fill="#059669" name="Principal" />
                      </BarChart>
                    </ResponsiveContainer>
                  )}

                  {activeTab === 'interest-vs-principal' && (
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPieChart>
                        <Pie
                          data={getInterestVsPrincipalData()}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={120}
                          paddingAngle={5}
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
                        >
                          {getInterestVsPrincipalData().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [formatCurrency(value as number), '']} />
                        <Legend />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  )}

                  {activeTab === 'payment-allocation' && (() => {
                    const allocationData = getPaymentAllocationData();
                    const colors = ['#d97706', '#059669', '#dc2626', '#7c3aed', '#0891b2', '#ea580c'];
                    
                    return (
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={allocationData.data}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                          <XAxis dataKey="month" stroke="#92400e" />
                          <YAxis stroke="#92400e" tickFormatter={formatNumber} />
                          <Tooltip 
                            formatter={(value, name) => [formatCurrency(value as number), name]}
                            labelFormatter={(month) => `Month ${month}`}
                          />
                          <Legend />
                          {allocationData.debtNames.map((debtName, index) => (
                            <Area
                              key={debtName}
                              type="monotone"
                              dataKey={debtName}
                              stackId="1"
                              stroke={colors[index % colors.length]}
                              fill={colors[index % colors.length]}
                              fillOpacity={0.6}
                            />
                          ))}
                        </AreaChart>
                      </ResponsiveContainer>
                    );
                  })()}

                  {activeTab === 'debt-bump' && (() => {
                    const bumpData = getDebtBumpData();
                    const colors = ['#d97706', '#059669', '#dc2626', '#7c3aed', '#0891b2', '#ea580c', '#f59e0b', '#10b981'];
                    
                    return (
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={bumpData.data} stackOffset="wiggle">
                          <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                          <XAxis 
                            dataKey="month" 
                            stroke="#92400e"
                            label={{ value: 'Months →', position: 'insideBottom', offset: -10 }}
                          />
                          <YAxis 
                            stroke="#92400e" 
                            tickFormatter={formatNumber}
                            label={{ value: '← Balance', angle: -90, position: 'insideLeft' }}
                          />
                          <Tooltip 
                            formatter={(value, name) => [formatCurrency(value as number), name]}
                            labelFormatter={(month) => `Month ${month}`}
                            contentStyle={{
                              backgroundColor: 'white',
                              border: '1px solid #fbbf24',
                              borderRadius: '8px',
                              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                            }}
                          />
                          <Legend 
                            wrapperStyle={{
                              paddingTop: '20px'
                            }}
                          />
                          {bumpData.debtNames && bumpData.debtNames.map((debtName, index) => (
                            <Area
                              key={debtName}
                              type="monotone"
                              dataKey={debtName}
                              stackId="1"
                              stroke={colors[index % colors.length]}
                              fill={colors[index % colors.length]}
                              fillOpacity={0.7}
                              strokeWidth={2}
                            />
                          ))}
                        </AreaChart>
                      </ResponsiveContainer>
                    );
                  })()}

                  {activeTab === 'debt-comparison' && (
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={getDebtComparisonData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                        <XAxis dataKey="name" stroke="#92400e" />
                        <YAxis yAxisId="left" stroke="#92400e" tickFormatter={formatNumber} />
                        <YAxis yAxisId="right" orientation="right" stroke="#dc2626" />
                        <Tooltip 
                          formatter={(value, name) => {
                            if (name === 'Balance') return [formatCurrency(value as number), name];
                            if (name === 'Monthly Interest') return [formatCurrency(value as number), name];
                            if (name === 'APR') return [`${value}%`, name];
                            return [value, name];
                          }}
                        />
                        <Legend />
                        <Bar 
                          yAxisId="left" 
                          dataKey="balance" 
                          fill="#059669" 
                          name="Balance" 
                          opacity={0.8}
                        />
                        <Bar 
                          yAxisId="left" 
                          dataKey="monthlyInterest" 
                          fill="#dc2626" 
                          name="Monthly Interest"
                          opacity={0.8}
                        />
                        <Line 
                          yAxisId="right" 
                          type="monotone" 
                          dataKey="apr" 
                          stroke="#d97706" 
                          strokeWidth={3}
                          name="APR"
                          dot={{ fill: '#d97706', strokeWidth: 2, r: 6 }}
                        />
                      </ComposedChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>
            </div>

            {/* Payment Schedule Table */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
              <div className="px-6 py-4 border-b border-amber-200 flex justify-between items-center">
                <div className="flex items-center space-x-4">
                  <h3 className="text-lg font-semibold text-amber-900">Payment Schedule</h3>
                  <div className="text-sm text-amber-600">
                    Total Months: {currentPlan.months?.length || 0}
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2 text-sm text-amber-700">
                    <input
                      type="checkbox"
                      checked={showAllMonths}
                      onChange={(e) => setShowAllMonths(e.target.checked)}
                      className="rounded border-amber-300 text-amber-600 focus:ring-amber-500"
                    />
                    <span>Show all months</span>
                  </label>
                  <button 
                    onClick={downloadSchedule}
                    className="flex items-center space-x-2 text-amber-700 hover:text-amber-800"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download CSV</span>
                  </button>
                </div>
              </div>

              <div className="overflow-auto max-h-96">
                <table className="w-full">
                  <thead className="bg-amber-50 sticky top-0">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                        Month
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                        Debt Name
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-amber-800 uppercase tracking-wider">
                        Payment
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-amber-800 uppercase tracking-wider">
                        Interest
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-amber-800 uppercase tracking-wider">
                        Principal
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-amber-800 uppercase tracking-wider">
                        Monthly Total
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-amber-100">
                    {currentPlan.months && Array.isArray(currentPlan.months) && 
                     (showAllMonths ? currentPlan.months : currentPlan.months.slice(0, 12)).map((month) =>
                      month.allocations && Array.isArray(month.allocations) && month.allocations.map((allocation, allocIndex) => (
                        <tr key={`${month.month_index}-${allocIndex}`} className="hover:bg-amber-50">
                          {allocIndex === 0 && (
                            <td rowSpan={month.allocations.length} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-amber-900 border-r border-amber-100">
                              {month.month_index || 0}
                            </td>
                          )}
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-800">
                            {allocation.name || ''}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                            {formatCurrency(Number(allocation.payment) || 0)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 text-right">
                            {formatCurrency(Number(allocation.interest_accrued) || 0)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 text-right">
                            {formatCurrency(Number(allocation.principal_reduction) || 0)}
                          </td>
                          {allocIndex === 0 && (
                            <td rowSpan={month.allocations.length} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-amber-900 text-right border-l border-amber-100">
                              {formatCurrency(Number(month.total_paid) || 0)}
                            </td>
                          )}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {!showAllMonths && currentPlan.months && currentPlan.months.length > 12 && (
                <div className="px-6 py-4 border-t border-amber-200 text-center text-sm text-amber-600">
                  Showing first 12 months of {currentPlan.months.length} total months. 
                  Check "Show all months" to see the complete schedule.
                </div>
              )}
            </div>
          </>
        )}

        {/* Debt Summary */}
        {debtSummary && (
          <div className="mt-8 bg-white rounded-lg border border-amber-200 shadow-sm">
            <div className="px-6 py-4 border-b border-amber-200">
              <h3 className="text-lg font-semibold text-amber-900">Your Current Debts</h3>
            </div>
            <div className="overflow-auto max-h-64">
              <table className="w-full">
                <thead className="bg-amber-50 sticky top-0">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                      Debt Name
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-amber-800 uppercase tracking-wider">
                      Balance
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-amber-800 uppercase tracking-wider">
                      APR
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-amber-800 uppercase tracking-wider">
                      Monthly Interest
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-amber-100">
                  {debtSummary.debts && Array.isArray(debtSummary.debts) && debtSummary.debts.map((debt) => (
                    <tr key={debt.id} className="hover:bg-amber-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-amber-900">
                        {debt.name || 'Unnamed Debt'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                        {formatCurrency(Number(debt.balance) || 0)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                        {(Number(debt.apr) || 0).toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                        {formatCurrency(Number(debt.monthly_interest) || 0)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default RepaymentPlans;