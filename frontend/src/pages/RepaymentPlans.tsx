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
  DollarSign,
  Calendar,
  Target,
  CreditCard
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
  ResponsiveContainer
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
    if (!currentPlan?.balance_series) return [];
    return currentPlan.balance_series.map((balance, index) => ({
      month: index,
      balance: balance,
      formattedBalance: `₹${(balance / 1000).toFixed(0)}K`
    }));
  };

  const getMonthlyPaymentData = () => {
    if (!currentPlan?.months) return [];
    return currentPlan.months.slice(0, 12).map(month => ({
      month: month.month_index,
      total_payment: month.total_paid,
      interest: month.total_interest,
      principal: month.total_paid - month.total_interest
    }));
  };

  const getInterestVsPrincipalData = () => {
    if (!currentPlan || !debtSummary) return [];
    const totalInterest = currentPlan.total_interest_paid;
    const totalPrincipal = debtSummary.total_debt;
    
    return [
      { name: 'Principal Payments', value: totalPrincipal, fill: '#059669' },
      { name: 'Interest Payments', value: totalInterest, fill: '#DC2626' }
    ];
  };

  const getPaymentAllocationData = () => {
    if (!currentPlan?.months || !debtSummary?.debts) return [];
    
    const firstMonth = currentPlan.months[0];
    if (!firstMonth) return [];
    
    const colors = ['#d97706', '#059669', '#dc2626', '#7c3aed', '#0891b2', '#ea580c'];
    
    return firstMonth.allocations
      .filter(alloc => alloc.payment > 0)
      .map((alloc, index) => ({
        debt: alloc.name,
        payment: alloc.payment,
        fill: colors[index % colors.length]
      }));
  };

  // New debt overview chart
  const getDebtOverviewData = () => {
    if (!debtSummary?.debts) return [];
    
    const colors = ['#d97706', '#059669', '#dc2626', '#7c3aed', '#0891b2', '#ea580c'];
    
    return debtSummary.debts.map((debt, index) => ({
      name: debt.name,
      balance: debt.balance,
      apr: debt.apr,
      fill: colors[index % colors.length]
    }));
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  const downloadSchedule = () => {
    if (!currentPlan?.months) return;
    
    const csvData = [
      ['Month', 'Debt Name', 'Payment', 'Interest', 'Principal', 'Monthly Total']
    ];
    
    currentPlan.months.forEach(month => {
      month.allocations.forEach((allocation, index) => {
        csvData.push([
          month.month_index.toString(),
          allocation.name,
          allocation.payment.toFixed(2),
          allocation.interest_accrued.toFixed(2),
          allocation.principal_reduction.toFixed(2),
          index === 0 ? month.total_paid.toFixed(2) : ''
        ]);
      });
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
    { id: 'payment-allocation', label: 'Payment Allocation', icon: <DollarSign className="w-4 h-4" /> },
    { id: 'debt-overview', label: 'Debt Overview', icon: <CreditCard className="w-4 h-4" /> }
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
                  Min required: ₹{debtSummary.monthly_minimums.toLocaleString()}
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
                {monthlyBudget >= debtSummary.monthly_minimums ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                )}
                <span className="text-sm font-medium text-amber-800">
                  {monthlyBudget >= debtSummary.monthly_minimums
                    ? `Budget OK: ₹${(monthlyBudget - debtSummary.monthly_minimums).toLocaleString()} available for extra payments`
                    : `Budget short by ₹${(debtSummary.monthly_minimums - monthlyBudget).toLocaleString()}`
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
                    <div className="text-2xl font-bold text-amber-900">{currentPlan.months_to_debt_free} months</div>
                    <div className="text-sm text-amber-600">{(currentPlan.months_to_debt_free / 12).toFixed(1)} years</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <DollarSign className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Total Interest</div>
                    <div className="text-2xl font-bold text-amber-900">
                      {formatCurrency(currentPlan.total_interest_paid)}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <Target className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Strategy</div>
                    <div className="text-xl font-bold text-amber-900">{currentPlan.strategy_name}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
                <div className="flex items-center space-x-3">
                  <Calculator className="w-8 h-8 text-amber-700" />
                  <div>
                    <div className="text-sm font-medium text-amber-700">Total Months</div>
                    <div className="text-xl font-bold text-amber-900">
                      {currentPlan.months.length}
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
                        <YAxis stroke="#92400e" tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`} />
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
                        <YAxis stroke="#92400e" tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`} />
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

                  {activeTab === 'payment-allocation' && (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getPaymentAllocationData()} layout="horizontal">
                        <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                        <XAxis type="number" stroke="#92400e" tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`} />
                        <YAxis dataKey="debt" type="category" stroke="#92400e" width={120} />
                        <Tooltip formatter={(value) => [formatCurrency(value as number), 'Payment']} />
                        <Bar dataKey="payment" />
                      </BarChart>
                    </ResponsiveContainer>
                  )}

                  {activeTab === 'debt-overview' && (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getDebtOverviewData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                        <XAxis dataKey="name" stroke="#92400e" />
                        <YAxis stroke="#92400e" tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`} />
                        <Tooltip 
                          formatter={(value, name) => [
                            formatCurrency(value as number), 
                            name === 'balance' ? 'Balance' : 'APR'
                          ]}
                          labelFormatter={(label) => `Debt: ${label}`}
                        />
                        <Bar dataKey="balance" name="Balance" />
                      </BarChart>
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
                    Total Months: {currentPlan.months.length}
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
                    {(showAllMonths ? currentPlan.months : currentPlan.months.slice(0, 12)).map((month) =>
                      month.allocations.map((allocation, allocIndex) => (
                        <tr key={`${month.month_index}-${allocIndex}`} className="hover:bg-amber-50">
                          {allocIndex === 0 && (
                            <td rowSpan={month.allocations.length} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-amber-900 border-r border-amber-100">
                              {month.month_index}
                            </td>
                          )}
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-800">
                            {allocation.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                            {formatCurrency(allocation.payment)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 text-right">
                            {formatCurrency(allocation.interest_accrued)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 text-right">
                            {formatCurrency(allocation.principal_reduction)}
                          </td>
                          {allocIndex === 0 && (
                            <td rowSpan={month.allocations.length} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-amber-900 text-right border-l border-amber-100">
                              {formatCurrency(month.total_paid)}
                            </td>
                          )}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {!showAllMonths && currentPlan.months.length > 12 && (
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
                  {debtSummary.debts.map((debt) => (
                    <tr key={debt.id} className="hover:bg-amber-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-amber-900">
                        {debt.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                        {formatCurrency(debt.balance)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                        {debt.apr.toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                        {formatCurrency(debt.monthly_interest)}
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