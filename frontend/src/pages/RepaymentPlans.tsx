import { API_URL } from '../lib/api';
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
  Save,
  BookMarked,
  X,
  Clock,
  BarChart2,
  Trash2
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
  ComposedChart
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

interface MonthlyPaymentResponse {
  month_index: number;
  status: 'pending' | 'paid' | 'skipped';
  due_date?: string;
  paid_date?: string;
  total_paid: number;
  total_interest: number;
  allocations: any[];
  notes?: string;
}

interface SavedPlanResponse {
  id: string;
  plan_name: string;
  strategy: string;
  monthly_budget: number;
  total_interest_paid: number;
  months_to_debt_free: number;
  original_total_debt: number;
  current_month: number;
  completed_months: number;
  progress_percentage: number;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  monthly_payments: MonthlyPaymentResponse[];
}

const RepaymentPlans: React.FC<RepaymentPlansProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const { user } = useUser();
  
  const [debtSummary, setDebtSummary] = useState<DebtSummary | null>(null);
  const [currentPlan, setCurrentPlan] = useState<RepaymentPlan | null>(null);
  const [savedPlans, setSavedPlans] = useState<SavedPlanResponse[]>([]);
  const [selectedSavedPlan, setSelectedSavedPlan] = useState<SavedPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('balance-over-time');
  const [showAllMonths, setShowAllMonths] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showSavedPlansView, setShowSavedPlansView] = useState(false);
  const [planName, setPlanName] = useState('');
  
  const [monthlyBudget, setMonthlyBudget] = useState(15000);
  const [strategy, setStrategy] = useState<'avalanche' | 'snowball' | 'optimal'>('avalanche');
  const [maxMonths, setMaxMonths] = useState(60);

  useEffect(() => {
    fetchDebtSummary();
    fetchSavedPlans();
  }, []);

  const fetchDebtSummary = async () => {
    try {
      const token = await getToken();
      const response = await fetch(API_URL + '/api/v1/plans/debt-summary', {
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

  const fetchSavedPlans = async () => {
    try {
      const token = await getToken();
      const response = await fetch(API_URL + '/api/v1/saved-plans/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSavedPlans(data);
      }
    } catch (error) {
      console.error('Error fetching saved plans:', error);
    }
  };

  const generatePlan = async () => {
    if (!debtSummary) return;
    
    setLoading(true);
    try {
      const token = await getToken();
      const response = await fetch(API_URL + '/api/v1/plans/generate', {
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
        alert(`Error: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error generating plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const savePlan = async () => {
    if (!currentPlan || !planName.trim()) {
      alert('Please enter a plan name');
      return;
    }

    try {
      const token = await getToken();
      const response = await fetch(API_URL + '/api/v1/saved-plans/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan_name: planName,
          plan_data: {
            ...currentPlan,
            monthly_budget: monthlyBudget
          }
        }),
      });

      if (response.ok) {
        alert('Plan saved successfully! You can now track your payments.');
        setShowSaveDialog(false);
        setPlanName('');
        await fetchSavedPlans();
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Failed to save plan'}`);
      }
    } catch (error) {
      console.error('Error saving plan:', error);
      alert('Failed to save plan');
    }
  };

  const markPaymentComplete = async (planId: string, monthIndex: number) => {
    try {
      const token = await getToken();
      const response = await fetch(`${API_URL}/api/v1/saved-plans/${planId}/mark-payment`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          month_index: monthIndex,
          payment_date: new Date().toISOString()
        }),
      });

      if (response.ok) {
        alert('Payment marked as complete! Your debt balances have been updated.');
        await fetchSavedPlans();
        await fetchDebtSummary();
        if (selectedSavedPlan) {
          const updatedPlan = await response.json();
          setSelectedSavedPlan(updatedPlan);
        }
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Failed to mark payment'}`);
      }
    } catch (error) {
      console.error('Error marking payment:', error);
      alert('Failed to mark payment');
    }
  };

  const markAllPaymentsComplete = async (planId: string) => {
    if (!selectedSavedPlan) return;
    
    const pendingPayments = selectedSavedPlan.monthly_payments.filter(p => p.status === 'pending');
    
    if (pendingPayments.length === 0) {
      alert('All payments are already marked as complete!');
      return;
    }
    
    const confirmMessage = `This will mark ALL ${pendingPayments.length} remaining payments as complete and update all your debt balances to $0. This action cannot be undone. Are you sure?`;
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      const token = await getToken();
      
      // Mark each pending payment as complete
      for (const payment of pendingPayments) {
        const response = await fetch(`${API_URL}/api/v1/saved-plans/${planId}/mark-payment`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            month_index: payment.month_index,
            payment_date: new Date().toISOString()
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          alert(`Error marking payment ${payment.month_index + 1}: ${errorData.detail || 'Failed'}`);
          break;
        }
      }
      
      alert('All payments marked as complete! Your debts have been cleared.');
      await fetchSavedPlans();
      await fetchDebtSummary();
      
      if (selectedSavedPlan) {
        const response = await fetch(`${API_URL}/api/v1/saved-plans/${planId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const updatedPlan = await response.json();
          setSelectedSavedPlan(updatedPlan);
        }
      }
    } catch (error) {
      console.error('Error marking all payments:', error);
      alert('Failed to mark all payments as complete');
    }
  };

  const deleteSavedPlan = async (planId: string, planName: string) => {
    const confirmMessage = `Are you sure you want to delete "${planName}"? This action cannot be undone.`;
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      const token = await getToken();
      const response = await fetch(`${API_URL}/api/v1/saved-plans/${planId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        alert('Plan deleted successfully!');
        if (selectedSavedPlan?.id === planId) {
          setSelectedSavedPlan(null);
        }
        await fetchSavedPlans();
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Failed to delete plan'}`);
      }
    } catch (error) {
      console.error('Error deleting plan:', error);
      alert('Failed to delete plan');
    }
  };

  const viewSavedPlan = (plan: SavedPlanResponse) => {
    setSelectedSavedPlan(plan);
  };

  const getBalanceOverTimeData = () => {
    if (!currentPlan?.balance_series || !Array.isArray(currentPlan.balance_series)) {
      return [];
    }
    
    return currentPlan.balance_series.map((balance, index) => ({
      month: index,
      balance: Number(balance) || 0,
      formattedBalance: `₹${((Number(balance) || 0) / 1000).toFixed(0)}K`
    }));
  };

  const getMonthlyPaymentData = () => {
    if (!currentPlan?.months || !Array.isArray(currentPlan.months)) {
      return [];
    }
    
    return currentPlan.months.slice(0, 12).map(month => ({
      month: month.month_index || 0,
      total_payment: Number(month.total_paid) || 0,
      interest: Number(month.total_interest) || 0,
      principal: (Number(month.total_paid) || 0) - (Number(month.total_interest) || 0)
    }));
  };

  const getInterestVsPrincipalData = () => {
    if (!currentPlan || !debtSummary) {
      return [];
    }
    
    const totalInterest = Number(currentPlan.total_interest_paid) || 0;
    const totalPrincipal = Number(debtSummary.total_debt) || 0;
    
    return [
      { name: 'Principal Payments', value: totalPrincipal, fill: '#059669' },
      { name: 'Interest Payments', value: totalInterest, fill: '#DC2626' }
    ];
  };

  const getPaymentAllocationData = () => {
    if (!currentPlan?.months || !Array.isArray(currentPlan.months) || currentPlan.months.length === 0) {
      return { data: [], debtNames: [] };
    }
    
    const monthsToShow = currentPlan.months.slice(0, Math.min(12, currentPlan.months.length));
    
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
    
    const data = monthsToShow.map(month => {
      const monthData: any = {
        month: month.month_index || 0,
        total: Number(month.total_paid) || 0
      };
      
      debtNames.forEach(debtName => {
        const allocation = month.allocations?.find(alloc => alloc && alloc.name === debtName);
        monthData[debtName] = Number(allocation?.payment) || 0;
      });
      
      return monthData;
    });
    
    return { data, debtNames };
  };

  const getDebtComparisonData = () => {
    if (!debtSummary?.debts || !Array.isArray(debtSummary.debts)) {
      return [];
    }
    
    const data = debtSummary.debts.map((debt, index) => ({
      name: debt.name || `Debt ${index + 1}`,
      balance: Number(debt.balance) || 0,
      apr: Number(debt.apr) || 0,
      monthlyInterest: Number(debt.monthly_interest) || 0,
      riskScore: ((Number(debt.apr) || 0) * (Number(debt.balance) || 0)) / 100000,
      id: debt.id
    }));
    
    return data;
  };

  const getDebtBumpData = () => {
    if (!debtSummary?.debts || !Array.isArray(debtSummary.debts)) {
      return { data: [], debtNames: [] };
    }
    
    if (!currentPlan?.months || currentPlan.months.length === 0) {
      return {
        data: [{
          month: 0,
          ...debtSummary.debts.reduce((acc, debt, index) => {
            acc[debt.name || `Debt ${index + 1}`] = Number(debt.balance) || 0;
            return acc;
          }, {} as any)
        }],
        debtNames: debtSummary.debts.map(d => d.name)
      };
    }
    
    const monthsToShow = Math.min(currentPlan.months.length, 24);
    const data = [];
    
    const debtNames = Array.from(new Set(
      currentPlan.months.flatMap(month => 
        month.allocations?.map(alloc => alloc.name) || []
      ).filter(Boolean)
    ));
    
    const debtBalances = debtSummary.debts.reduce((acc, debt) => {
      acc[debt.name || debt.id] = Number(debt.balance) || 0;
      return acc;
    }, {} as Record<string, number>);
    
    for (let i = 0; i <= monthsToShow; i++) {
      const monthData: any = { month: i };
      
      if (i === 0) {
        debtNames.forEach(debtName => {
          const debt = debtSummary.debts.find(d => d.name === debtName);
          monthData[debtName] = debt ? Number(debt.balance) || 0 : 0;
        });
      } else if (i <= currentPlan.months.length) {
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
        
        debtNames.forEach(debtName => {
          monthData[debtName] = debtBalances[debtName] || 0;
        });
      }
      
      data.push(monthData);
    }
    
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
            <button
              onClick={() => setShowSavedPlansView(!showSavedPlansView)}
              className="flex items-center space-x-2 bg-amber-100 text-amber-800 px-4 py-2 rounded-lg hover:bg-amber-200 transition-colors"
            >
              <BookMarked className="w-4 h-4" />
              <span>{showSavedPlansView ? 'Back to Plans' : 'My Saved Plans'} ({savedPlans.length})</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {showSavedPlansView ? (
          <div className="space-y-6">
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm p-6">
              <h2 className="text-xl font-semibold text-amber-900 mb-4">Your Saved Plans</h2>
              
              {savedPlans.length === 0 ? (
                <div className="text-center py-12 text-amber-600">
                  <BookMarked className="w-16 h-16 mx-auto mb-4 text-amber-300" />
                  <p className="text-lg font-medium">No saved plans yet</p>
                  <p className="text-sm">Generate and save a repayment plan to start tracking your progress</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {savedPlans.map((plan) => (
                    <div key={plan.id} className="border border-amber-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-amber-900">{plan.plan_name}</h3>
                          <p className="text-sm text-amber-600">{plan.strategy} Strategy</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => viewSavedPlan(plan)}
                            className="text-amber-700 hover:text-amber-900 text-sm font-medium"
                          >
                            {selectedSavedPlan?.id === plan.id ? 'Viewing ✓' : 'View Details →'}
                          </button>
                          <button
                            onClick={() => deleteSavedPlan(plan.id, plan.plan_name)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete plan"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-amber-600">Monthly Budget</p>
                          <p className="font-semibold text-amber-900">{formatCurrency(plan.monthly_budget)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-amber-600">Total Interest</p>
                          <p className="font-semibold text-red-600">{formatCurrency(plan.total_interest_paid)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-amber-600">Time to Debt-Free</p>
                          <p className="font-semibold text-amber-900">{plan.months_to_debt_free} months</p>
                        </div>
                        <div>
                          <p className="text-xs text-amber-600">Progress</p>
                          <p className="font-semibold text-green-600">{plan.progress_percentage.toFixed(1)}%</p>
                        </div>
                      </div>

                      <div className="w-full bg-amber-100 rounded-full h-3 mb-2">
                        <div
                          className="bg-green-600 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${plan.progress_percentage}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <span className="text-amber-700">
                          {plan.completed_months} of {plan.months_to_debt_free} months completed
                        </span>
                        {plan.is_completed && (
                          <span className="flex items-center space-x-1 text-green-600 font-medium">
                            <CheckCircle className="w-4 h-4" />
                            <span>Completed</span>
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {selectedSavedPlan && (
              <>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
                    <div className="px-6 py-4 border-b border-amber-200">
                      <h3 className="text-lg font-semibold text-amber-900">Payment Progress</h3>
                    </div>
                    <div className="p-6">
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={selectedSavedPlan.monthly_payments.map(p => ({
                            month: `M${p.month_index + 1}`,
                            paid: p.status === 'paid' ? p.total_paid : 0,
                            pending: p.status === 'pending' ? p.total_paid : 0
                          }))}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                            <XAxis dataKey="month" stroke="#92400e" />
                            <YAxis stroke="#92400e" tickFormatter={formatNumber} />
                            <Tooltip formatter={(value) => [formatCurrency(value as number), '']} />
                            <Legend />
                            <Bar dataKey="paid" fill="#059669" name="Completed" />
                            <Bar dataKey="pending" fill="#d1d5db" name="Pending" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
                    <div className="px-6 py-4 border-b border-amber-200">
                      <h3 className="text-lg font-semibold text-amber-900">Cumulative Payments</h3>
                    </div>
                    <div className="p-6">
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={selectedSavedPlan.monthly_payments.map((p, idx) => {
                            const cumulativePaid = selectedSavedPlan.monthly_payments
                              .slice(0, idx + 1)
                              .filter(mp => mp.status === 'paid')
                              .reduce((sum, mp) => sum + mp.total_paid, 0);
                            const cumulativeTotal = selectedSavedPlan.monthly_payments
                              .slice(0, idx + 1)
                              .reduce((sum, mp) => sum + mp.total_paid, 0);
                            return {
                              month: idx + 1,
                              paid: cumulativePaid,
                              planned: cumulativeTotal
                            };
                          })}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                            <XAxis dataKey="month" stroke="#92400e" />
                            <YAxis stroke="#92400e" tickFormatter={formatNumber} />
                            <Tooltip formatter={(value) => [formatCurrency(value as number), '']} />
                            <Legend />
                            <Area type="monotone" dataKey="planned" stroke="#d1d5db" fill="#e5e7eb" name="Planned Total" />
                            <Area type="monotone" dataKey="paid" stroke="#059669" fill="#10b981" fillOpacity={0.6} name="Actually Paid" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
                  <div className="px-6 py-4 border-b border-amber-200 flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-semibold text-amber-900">Complete Payment Schedule: {selectedSavedPlan.plan_name}</h3>
                      <p className="text-sm text-amber-600 mt-1">Check off payments as you complete them - your debt balances will update automatically</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => markAllPaymentsComplete(selectedSavedPlan.id)}
                        disabled={selectedSavedPlan.monthly_payments.every(p => p.status === 'paid')}
                        className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        <CheckCircle className="w-4 h-4" />
                        <span>Mark All as Paid</span>
                      </button>
                      <button
                        onClick={() => deleteSavedPlan(selectedSavedPlan.id, selectedSavedPlan.plan_name)}
                        className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span>Delete Plan</span>
                      </button>
                    </div>
                  </div>

                  <div className="overflow-auto max-h-[600px]">
                    <table className="w-full">
                      <thead className="bg-amber-50 sticky top-0">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                            ✓
                          </th>
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
                          <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-amber-100">
                        {selectedSavedPlan.monthly_payments.map((payment) => (
                          payment.allocations.map((alloc, allocIndex) => (
                            <tr 
                              key={`${payment.month_index}-${allocIndex}`} 
                              className={`hover:bg-amber-50 ${payment.status === 'paid' ? 'bg-green-50' : ''}`}
                            >
                              {allocIndex === 0 && (
                                <td rowSpan={payment.allocations.length} className="px-6 py-4 whitespace-nowrap border-r border-amber-100">
                                  <input
                                    type="checkbox"
                                    checked={payment.status === 'paid'}
                                    onChange={() => {
                                      if (payment.status === 'pending') {
                                        if (window.confirm('Mark this payment as complete? This will automatically update your debt balances.')) {
                                          markPaymentComplete(selectedSavedPlan.id, payment.month_index);
                                        }
                                      }
                                    }}
                                    disabled={payment.status === 'paid'}
                                    className="w-5 h-5 rounded border-amber-300 text-green-600 focus:ring-green-500 disabled:opacity-50 cursor-pointer"
                                  />
                                </td>
                              )}
                              {allocIndex === 0 && (
                                <td rowSpan={payment.allocations.length} className="px-6 py-4 whitespace-nowrap text-sm font-medium text-amber-900 border-r border-amber-100">
                                  {payment.month_index + 1}
                                </td>
                              )}
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-800">
                                {alloc.name}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-900 text-right">
                                {formatCurrency(alloc.payment)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 text-right">
                                {formatCurrency(alloc.interest_accrued)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 text-right">
                                {formatCurrency(alloc.principal_reduction)}
                              </td>
                              {allocIndex === 0 && (
                                <td rowSpan={payment.allocations.length} className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-amber-900 text-right border-l border-amber-100">
                                  {formatCurrency(payment.total_paid)}
                                </td>
                              )}
                              {allocIndex === 0 && (
                                <td rowSpan={payment.allocations.length} className="px-6 py-4 whitespace-nowrap text-sm text-amber-700 border-l border-amber-100">
                                  {payment.status === 'paid' && payment.paid_date ? (
                                    <div className="flex items-center space-x-2">
                                      <CheckCircle className="w-4 h-4 text-green-600" />
                                      <span className="text-green-600">Paid {new Date(payment.paid_date).toLocaleDateString()}</span>
                                    </div>
                                  ) : (
                                    <div className="flex items-center space-x-2 text-amber-500">
                                      <Clock className="w-4 h-4" />
                                      <span>Pending</span>
                                    </div>
                                  )}
                                </td>
                              )}
                            </tr>
                          ))
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="px-6 py-4 border-t border-amber-200 bg-amber-50">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-amber-600">Completed Payments</p>
                        <p className="text-lg font-bold text-green-600">
                          {selectedSavedPlan.completed_months} / {selectedSavedPlan.months_to_debt_free}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-amber-600">Total Paid So Far</p>
                        <p className="text-lg font-bold text-amber-900">
                          {formatCurrency(
                            selectedSavedPlan.monthly_payments
                              .filter(p => p.status === 'paid')
                              .reduce((sum, p) => sum + p.total_paid, 0)
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-amber-600">Remaining Payments</p>
                        <p className="text-lg font-bold text-amber-700">
                          {formatCurrency(
                            selectedSavedPlan.monthly_payments
                              .filter(p => p.status === 'pending')
                              .reduce((sum, p) => sum + p.total_paid, 0)
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-amber-600">Overall Progress</p>
                        <p className="text-lg font-bold text-green-600">
                          {selectedSavedPlan.progress_percentage.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        ) : (
          <>
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

            {currentPlan && (
              <>
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
                    <button
                      onClick={() => setShowSaveDialog(true)}
                      className="w-full h-full flex flex-col items-center justify-center space-y-2 hover:bg-amber-50 transition-colors rounded-lg"
                    >
                      <Save className="w-8 h-8 text-green-600" />
                      <div className="text-sm font-medium text-green-700">Save This Plan</div>
                      <div className="text-xs text-amber-600">Track payments & progress</div>
                    </button>
                  </div>
                </div>

                <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
                  <div className="px-6 py-4 border-b border-amber-200">
                    <h3 className="text-lg font-semibold text-amber-900">Visual Analysis</h3>
                  </div>

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
                                label={{ value: 'Months', position: 'insideBottom', offset: -10 }}
                              />
                              <YAxis 
                                stroke="#92400e" 
                                tickFormatter={formatNumber}
                                label={{ value: 'Balance', angle: -90, position: 'insideLeft' }}
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
          </>
        )}
      </main>

      {showSaveDialog && currentPlan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-amber-900">Save Repayment Plan</h3>
              <button
                onClick={() => {
                  setShowSaveDialog(false);
                  setPlanName('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-sm text-amber-700 mb-4">
              Save this plan to track your progress and automatically update your debts as you make payments.
            </p>

            <div className="bg-amber-50 rounded-lg p-4 mb-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-amber-600">Strategy</p>
                  <p className="font-semibold text-amber-900">{currentPlan.strategy_name}</p>
                </div>
                <div>
                  <p className="text-amber-600">Time to Debt-Free</p>
                  <p className="font-semibold text-amber-900">{currentPlan.months_to_debt_free} months</p>
                </div>
                <div>
                  <p className="text-amber-600">Monthly Budget</p>
                  <p className="font-semibold text-amber-900">{formatCurrency(monthlyBudget)}</p>
                </div>
                <div>
                  <p className="text-amber-600">Total Interest</p>
                  <p className="font-semibold text-red-600">{formatCurrency(currentPlan.total_interest_paid)}</p>
                </div>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-amber-700 mb-2">
                Plan Name
              </label>
              <input
                type="text"
                value={planName}
                onChange={(e) => setPlanName(e.target.value)}
                placeholder="e.g., My Debt Freedom Plan 2025"
                className="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowSaveDialog(false);
                  setPlanName('');
                }}
                className="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={savePlan}
                disabled={!planName.trim()}
                className="flex-1 bg-amber-600 text-white py-2 px-4 rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>Save Plan</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RepaymentPlans;