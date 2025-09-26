import React, { useState, useEffect } from 'react';
import { UserButton, useAuth, useUser } from '@clerk/clerk-react';
import { 
  Coffee, 
  ArrowLeft, 
  CreditCard, 
  Plus, 
  Edit, 
  Trash2, 
  TrendingUp, 
  DollarSign,
  PieChart,
  AlertCircle,
  X,
  Check,
  BarChart3,
  IndianRupee
} from 'lucide-react';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Line
} from 'recharts';

interface DebtManagementProps {
  onNavigate?: (page: string) => void;
}

interface Debt {
  id: string;
  name: string;
  total_amount: number;
  interest_rate: number;
}

interface DebtSummary {
  user_profile: {
    monthly_income: number;
    monthly_expenses: number;
    available_budget: number;
  };
  debt_summary: {
    total_debt_amount: number;
    total_monthly_interest: number;
    debt_count: number;
    debt_to_income_ratio: number;
    average_interest_rate: number;
  };
  debts: Debt[];
}

interface DebtFormData {
  name: string;
  total_amount: number;
  interest_rate: number;
}

interface FinancialProfileData {
  monthly_income: number;
  monthly_expenses: number;
}

const DebtManagement: React.FC<DebtManagementProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const { user } = useUser();
  const [summary, setSummary] = useState<DebtSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showFinancialProfileModal, setShowFinancialProfileModal] = useState(false);
  const [editingDebt, setEditingDebt] = useState<Debt | null>(null);
  const [formData, setFormData] = useState<DebtFormData>({
    name: '',
    total_amount: 0,
    interest_rate: 0
  });
  const [financialProfileData, setFinancialProfileData] = useState<FinancialProfileData>({
    monthly_income: 0,
    monthly_expenses: 0
  });

  // Check if user has set up financial profile
  useEffect(() => {
    console.log('Component mounted, checking financial profile...');
    checkFinancialProfile();
  }, []);

  const checkFinancialProfile = async () => {
    console.log('🔄 Starting checkFinancialProfile...');
    try {
      const token = await getToken();
      console.log('✅ Got token:', token ? 'Yes' : 'No');
      
      if (!token) {
        console.log('❌ No token available');
        setShowFinancialProfileModal(true);
        setLoading(false);
        return;
      }
      
      console.log('📡 Making request to financial-profile endpoint...');
      const response = await fetch('http://localhost:8000/api/v1/debt/financial-profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      console.log('📊 Response status:', response.status);
      console.log('📊 Response ok:', response.ok);
      
      if (response.ok) {
        const profile = await response.json();
        console.log('✅ Profile data received:', profile);
        console.log('📊 Profile details:', JSON.stringify(profile, null, 2));
        console.log('💰 Income:', profile.monthly_income, 'Expenses:', profile.monthly_expenses);
        
        setFinancialProfileData(profile);
        
        // If no income/expenses set, show financial profile modal
        if (profile.monthly_income === 0 && profile.monthly_expenses === 0) {
          console.log('💡 No financial profile set, showing modal');
          setShowFinancialProfileModal(true);
        } else {
          console.log('✅ Financial profile exists, fetching debt summary');
          await fetchDebtSummary();
        }
      } else {
        console.log('❌ Response not ok:', response.status);
        const errorText = await response.text();
        console.log('❌ Error response:', errorText);
        setShowFinancialProfileModal(true);
      }
    } catch (error) {
      console.error('❌ Error in checkFinancialProfile:', error);
      setShowFinancialProfileModal(true);
    } finally {
      console.log('🏁 Setting loading to false');
      setLoading(false);
    }
  };

  const handleUpdateFinancialProfile = async () => {
    console.log('💾 Updating financial profile...', financialProfileData);
    try {
      const token = await getToken();
      console.log('✅ Got token for profile update:', token ? 'Yes' : 'No');
      
      const response = await fetch('http://localhost:8000/api/v1/debt/financial-profile', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(financialProfileData),
      });
      
      console.log('📊 Profile update response status:', response.status);
      
      if (response.ok) {
        console.log('✅ Profile updated successfully');
        setShowFinancialProfileModal(false);
        await fetchDebtSummary();
      } else {
        const errorText = await response.text();
        console.log('❌ Profile update failed:', errorText);
      }
    } catch (error) {
      console.error('❌ Error updating financial profile:', error);
    }
  };

  const fetchDebtSummary = async () => {
    console.log('🔄 Starting fetchDebtSummary...');
    try {
      const token = await getToken();
      console.log('✅ Got token for summary:', token ? 'Yes' : 'No');
      
      if (!token) {
        console.log('❌ No token for summary request');
        setDefaultSummary();
        return;
      }
      
      console.log('📡 Making request to debt summary endpoint...');
      const response = await fetch('http://localhost:8000/api/v1/debt/summary', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      console.log('📊 Summary response status:', response.status);
      console.log('📊 Summary response ok:', response.ok);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Summary data received:', data);
        console.log('📊 Summary details:', JSON.stringify(data, null, 2));
        setSummary(data);
      } else {
        console.log('❌ Summary response not ok:', response.status);
        const errorText = await response.text();
        console.log('❌ Summary error response:', errorText);
        setDefaultSummary();
      }
    } catch (error) {
      console.error('❌ Error in fetchDebtSummary:', error);
      setDefaultSummary();
    }
  };

  const setDefaultSummary = () => {
    console.log('🔧 Setting default summary');
    setSummary({
      user_profile: {
        monthly_income: financialProfileData.monthly_income || 0,
        monthly_expenses: financialProfileData.monthly_expenses || 0,
        available_budget: (financialProfileData.monthly_income || 0) - (financialProfileData.monthly_expenses || 0)
      },
      debt_summary: {
        total_debt_amount: 0,
        total_monthly_interest: 0,
        debt_count: 0,
        debt_to_income_ratio: 0,
        average_interest_rate: 0
      },
      debts: []
    });
  };

  const handleAddDebt = async () => {
    console.log('➕ Adding debt:', formData);
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/debt/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      console.log('Add debt response status:', response.status);
      
      if (response.ok) {
        console.log('✅ Debt added successfully');
        setShowAddModal(false);
        resetForm();
        await fetchDebtSummary();
      } else {
        const errorText = await response.text();
        console.log('❌ Add debt failed:', errorText);
      }
    } catch (error) {
      console.error('❌ Error adding debt:', error);
    }
  };

  const handleEditDebt = async () => {
    if (!editingDebt) return;
    
    console.log('✏️ Editing debt:', editingDebt.id, formData);
    try {
      const token = await getToken();
      const response = await fetch(`http://localhost:8000/api/v1/debt/${editingDebt.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      console.log('Edit debt response status:', response.status);
      
      if (response.ok) {
        console.log('✅ Debt updated successfully');
        setEditingDebt(null);
        resetForm();
        await fetchDebtSummary();
      } else {
        const errorText = await response.text();
        console.log('❌ Edit debt failed:', errorText);
      }
    } catch (error) {
      console.error('❌ Error updating debt:', error);
    }
  };

  const handleDeleteDebt = async (debtId: string) => {
    if (!window.confirm('Are you sure you want to delete this debt?')) return;
    
    console.log('🗑️ Deleting debt:', debtId);
    try {
      const token = await getToken();
      const response = await fetch(`http://localhost:8000/api/v1/debt/${debtId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      console.log('Delete debt response status:', response.status);
      
      if (response.ok) {
        console.log('✅ Debt deleted successfully');
        await fetchDebtSummary();
      } else {
        const errorText = await response.text();
        console.log('❌ Delete debt failed:', errorText);
      }
    } catch (error) {
      console.error('❌ Error deleting debt:', error);
    }
  };

  const resetForm = () => {
    console.log('🔄 Resetting form');
    setFormData({
      name: '',
      total_amount: 0,
      interest_rate: 0
    });
  };

  const openEditModal = (debt: Debt) => {
    console.log('✏️ Opening edit modal for debt:', debt);
    setEditingDebt(debt);
    setFormData({
      name: debt.name,
      total_amount: debt.total_amount,
      interest_rate: debt.interest_rate
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Chart data functions
  const getFinancialOverviewData = () => {
    if (!summary) return [];
    
    const income = summary.user_profile.monthly_income;
    const expenses = summary.user_profile.monthly_expenses;
    const debtInterest = summary.debt_summary.total_monthly_interest;
    const availableBudget = Math.max(0, income - expenses - debtInterest);
    
    return [
      { name: 'Available Budget', value: availableBudget, fill: '#059669' },
      { name: 'Regular Expenses', value: expenses, fill: '#d97706' },
      { name: 'Debt Interest', value: debtInterest, fill: '#dc2626' }
    ];
  };

  const getDebtBreakdownData = () => {
    if (!summary || summary.debts.length === 0) return [];
    
    const colors = ['#dc2626', '#d97706', '#059669', '#7c3aed', '#0891b2', '#ea580c'];
    
    return summary.debts.map((debt, index) => ({
      name: debt.name.length > 12 ? debt.name.substring(0, 12) + '...' : debt.name,
      fullName: debt.name,
      amount: debt.total_amount,
      interest_rate: debt.interest_rate,
      monthly_interest: debt.total_amount * (debt.interest_rate / 100 / 12),
      fill: colors[index % colors.length]
    }));
  };

  const getDebtComparisonData = () => {
    if (!summary || summary.debts.length === 0) return [];
    
    return summary.debts.map(debt => ({
      name: debt.name.length > 10 ? debt.name.substring(0, 10) + '...' : debt.name,
      fullName: debt.name,
      balance: debt.total_amount,
      interest_rate: debt.interest_rate,
      monthly_interest: debt.total_amount * (debt.interest_rate / 100 / 12)
    }));
  };

  console.log('🎨 Rendering component - Loading:', loading, 'Summary:', !!summary, 'ShowModal:', showFinancialProfileModal);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50 flex items-center justify-center">
        <div className="text-amber-700">Loading debt information...</div>
      </div>
    );
  }

  if (!summary && !showFinancialProfileModal) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">Error loading debt data</div>
          <button 
            onClick={() => {
              console.log('🔄 Retry button clicked');
              setLoading(true);
              checkFinancialProfile();
            }}
            className="bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      {/* Header */}
      <header className="bg-white border-b border-amber-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => onNavigate && onNavigate('dashboard')}
                className="flex items-center space-x-2 text-amber-700 hover:text-amber-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Dashboard</span>
              </button>
              <div className="h-6 w-px bg-amber-200"></div>
              <Coffee className="w-6 h-6 text-amber-700" />
              <h1 className="text-xl font-bold text-amber-900">Debt Management</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-amber-800 hidden sm:block">
                {user?.firstName ? `Hello, ${user.firstName}!` : 'Welcome!'}
              </span>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      {/* Show content only if we have summary data */}
      {summary && (
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Financial Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-amber-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-amber-700">Monthly Income</h3>
                <IndianRupee className="w-5 h-5 text-green-600" />
              </div>
              <p className="text-2xl font-bold text-amber-900">
                {formatCurrency(summary.user_profile.monthly_income)}
              </p>
              <button
                onClick={() => setShowFinancialProfileModal(true)}
                className="text-sm text-amber-600 hover:text-amber-800 mt-2"
              >
                Edit Profile
              </button>
            </div>

            <div className="bg-white rounded-lg border border-amber-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-amber-700">Monthly Expenses</h3>
                <TrendingUp className="w-5 h-5 text-red-600" />
              </div>
              <p className="text-2xl font-bold text-amber-900">
                {formatCurrency(summary.user_profile.monthly_expenses)}
              </p>
            </div>

            <div className="bg-white rounded-lg border border-amber-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-amber-700">Available Budget</h3>
                <PieChart className="w-5 h-5 text-blue-600" />
              </div>
              <p className={`text-2xl font-bold ${summary.user_profile.available_budget >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(summary.user_profile.available_budget)}
              </p>
            </div>
          </div>

          {/* Financial Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Financial Overview Pie Chart */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                  <PieChart className="w-5 h-5 mr-2 text-amber-700" />
                  Monthly Budget Breakdown
                </h3>
              </div>
              <div className="p-6">
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={getFinancialOverviewData()}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
                      >
                        {getFinancialOverviewData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [formatCurrency(value as number), '']} />
                      <Legend />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Debt Distribution Chart */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                  <CreditCard className="w-5 h-5 mr-2 text-amber-700" />
                  Debt Distribution
                </h3>
              </div>
              <div className="p-6">
                {summary.debts.length > 0 ? (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPieChart>
                        <Pie
                          data={getDebtBreakdownData()}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={100}
                          paddingAngle={5}
                          dataKey="amount"
                          label={false}
                        >
                          {getDebtBreakdownData().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                        <Tooltip 
                          formatter={(value) => [formatCurrency(value as number), 'Amount']}
                          labelFormatter={(label, payload) => {
                            if (payload && payload.length > 0) {
                              return payload[0].payload.fullName;
                            }
                            return label;
                          }}
                        />
                        <Legend 
                          wrapperStyle={{ fontSize: '12px' }}
                          iconType="circle"
                        />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-80 flex items-center justify-center text-amber-600">
                    <div className="text-center">
                      <CreditCard className="w-16 h-16 mx-auto mb-4 text-amber-300" />
                      <p>No debts to display</p>
                      <p className="text-sm">Add your first debt to see the breakdown</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Debt Comparison Bar Chart */}
          {summary.debts.length > 0 && (
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-amber-700" />
                  Debt Analysis: Balance vs Interest Impact
                </h3>
              </div>
              <div className="p-6">
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart 
                      data={getDebtComparisonData()}
                      margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#fbbf24" opacity={0.3} />
                      <XAxis 
                        dataKey="name" 
                        stroke="#92400e" 
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        fontSize={12}
                      />
                      <YAxis 
                        yAxisId="left" 
                        stroke="#92400e" 
                        tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
                        fontSize={12}
                      />
                      <YAxis 
                        yAxisId="right" 
                        orientation="right" 
                        stroke="#dc2626"
                        fontSize={12}
                      />
                      <Tooltip 
                        formatter={(value, name) => {
                          if (name === 'Balance') return [formatCurrency(value as number), name];
                          if (name === 'Monthly Interest') return [formatCurrency(value as number), name];
                          if (name === 'Interest Rate') return [`${value}%`, name];
                          return [value, name];
                        }}
                        labelFormatter={(label, payload) => {
                          if (payload && payload.length > 0) {
                            return payload[0].payload.fullName;
                          }
                          return label;
                        }}
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #fbbf24',
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: '12px' }} />
                      <Bar 
                        yAxisId="left" 
                        dataKey="balance" 
                        fill="#059669" 
                        name="Balance" 
                        opacity={0.8}
                      />
                      <Bar 
                        yAxisId="left" 
                        dataKey="monthly_interest" 
                        fill="#dc2626" 
                        name="Monthly Interest"
                        opacity={0.8}
                      />
                      <Line 
                        yAxisId="right" 
                        type="monotone" 
                        dataKey="interest_rate" 
                        stroke="#d97706" 
                        strokeWidth={3}
                        name="Interest Rate"
                        dot={{ fill: '#d97706', strokeWidth: 2, r: 6 }}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* Debt Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-amber-200 p-6">
              <h3 className="text-lg font-semibold text-amber-900 mb-4">Debt Overview</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-amber-700">Total Debt Amount:</span>
                  <span className="font-bold text-red-600">{formatCurrency(summary.debt_summary.total_debt_amount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-amber-700">Monthly Interest:</span>
                  <span className="font-bold text-red-600">{formatCurrency(summary.debt_summary.total_monthly_interest)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-amber-700">Number of Debts:</span>
                  <span className="font-bold">{summary.debt_summary.debt_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-amber-700">Average Interest Rate:</span>
                  <span className="font-bold">{summary.debt_summary.average_interest_rate.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-amber-200 p-6">
              <h3 className="text-lg font-semibold text-amber-900 mb-4">Interest Impact</h3>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600 mb-2">
                  {formatCurrency(summary.debt_summary.total_monthly_interest)}
                </div>
                <div className="text-sm text-amber-700">Monthly Interest Cost</div>
                <div className="text-xs text-amber-600 mt-2">
                  Annually: {formatCurrency(summary.debt_summary.total_monthly_interest * 12)}
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-amber-200 p-6">
              <h3 className="text-lg font-semibold text-amber-900 mb-4">Debt-to-Income Ratio</h3>
              <div className="text-center">
                <div className="text-3xl font-bold text-amber-900 mb-2">
                  {summary.debt_summary.debt_to_income_ratio.toFixed(1)}%
                </div>
                <div className={`text-sm ${
                  summary.debt_summary.debt_to_income_ratio > 20 ? 'text-red-600' :
                  summary.debt_summary.debt_to_income_ratio > 10 ? 'text-amber-600' : 'text-green-600'
                }`}>
                  {summary.debt_summary.debt_to_income_ratio > 20 ? 'High Impact' :
                   summary.debt_summary.debt_to_income_ratio > 10 ? 'Moderate Impact' : 'Low Impact'}
                </div>
              </div>
            </div>
          </div>

          {/* Debt List */}
          <div className="bg-white rounded-lg border border-amber-200">
            <div className="px-6 py-4 border-b border-amber-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-amber-900">Your Debts</h3>
                <button
                  onClick={() => setShowAddModal(true)}
                  className="flex items-center space-x-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Debt</span>
                </button>
              </div>
            </div>

            <div className="p-6">
              {summary.debts.length === 0 ? (
                <div className="text-center py-8 text-amber-600">
                  <CreditCard className="w-12 h-12 mx-auto mb-3 text-amber-300" />
                  <p>No debts added yet.</p>
                  <p className="text-sm">Click "Add Debt" to start tracking your debts.</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {summary.debts.map((debt) => (
                    <div key={debt.id} className="border border-amber-100 rounded-lg p-4 hover:shadow-sm transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <CreditCard className="w-5 h-5 text-amber-600" />
                            <h4 className="font-semibold text-amber-900">{debt.name}</h4>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="text-amber-600">Total Amount:</span>
                              <div className="font-semibold">{formatCurrency(debt.total_amount)}</div>
                            </div>
                            <div>
                              <span className="text-amber-600">Interest Rate:</span>
                              <div className="font-semibold">{debt.interest_rate}%</div>
                            </div>
                            <div>
                              <span className="text-amber-600">Monthly Interest:</span>
                              <div className="font-semibold text-red-600">
                                {formatCurrency(debt.total_amount * (debt.interest_rate / 100 / 12))}
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => openEditModal(debt)}
                            className="p-2 text-amber-600 hover:bg-amber-50 rounded-lg transition-colors"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={() => handleDeleteDebt(debt.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Alert for negative budget */}
          {summary.user_profile.available_budget < 0 && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <div>
                  <h4 className="font-semibold text-red-900">Budget Alert</h4>
                  <p className="text-red-700 text-sm">
                    Your expenses exceed your income. Consider increasing income or reducing expenses.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Financial Profile Modal */}
      {showFinancialProfileModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition-opacity duration-300">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 transform transition-all duration-300 ease-out scale-100 translate-y-0 animate-slideInUp">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-amber-900">Set Up Your Financial Profile</h3>
            </div>

            <p className="text-sm text-amber-700 mb-4">
              Please enter your monthly income and expenses to get started with debt management.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-amber-700 mb-1">Monthly Income (₹)</label>
                <input
                  type="number"
                  value={financialProfileData.monthly_income}
                  onChange={(e) => setFinancialProfileData({
                    ...financialProfileData, 
                    monthly_income: parseFloat(e.target.value) || 0
                  })}
                  className="w-full border border-amber-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all duration-200"
                  placeholder="e.g., 50000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-amber-700 mb-1">Monthly Expenses (₹)</label>
                <input
                  type="number"
                  value={financialProfileData.monthly_expenses}
                  onChange={(e) => setFinancialProfileData({
                    ...financialProfileData, 
                    monthly_expenses: parseFloat(e.target.value) || 0
                  })}
                  className="w-full border border-amber-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all duration-200"
                  placeholder="e.g., 30000"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleUpdateFinancialProfile}
                className="flex-1 bg-amber-600 text-white py-2 px-4 rounded-lg hover:bg-amber-700 transition-all duration-200 transform hover:scale-105 flex items-center justify-center space-x-2"
              >
                <Check className="w-4 h-4" />
                <span>Save Profile</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit Debt Modal */}
      {(showAddModal || editingDebt) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition-opacity duration-300">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 transform transition-all duration-300 ease-out scale-100 translate-y-0 animate-slideInUp">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-amber-900">
                {editingDebt ? 'Edit Debt' : 'Add New Debt'}
              </h3>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setEditingDebt(null);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors duration-200 transform hover:scale-110"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-amber-700 mb-1">Debt Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full border border-amber-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all duration-200"
                  placeholder="e.g., Credit Card Debt, Personal Loan"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-amber-700 mb-1">Total Debt Amount (₹)</label>
                <input
                  type="number"
                  value={formData.total_amount}
                  onChange={(e) => setFormData({...formData, total_amount: parseFloat(e.target.value) || 0})}
                  className="w-full border border-amber-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all duration-200"
                  placeholder="e.g., 50000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-amber-700 mb-1">Interest Rate (% per year)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.interest_rate}
                  onChange={(e) => setFormData({...formData, interest_rate: parseFloat(e.target.value) || 0})}
                  className="w-full border border-amber-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all duration-200"
                  placeholder="e.g., 18.5"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setEditingDebt(null);
                  resetForm();
                }}
                className="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg hover:bg-gray-300 transition-all duration-200 transform hover:scale-105"
              >
                Cancel
              </button>
              <button
                onClick={editingDebt ? handleEditDebt : handleAddDebt}
                className="flex-1 bg-amber-600 text-white py-2 px-4 rounded-lg hover:bg-amber-700 transition-all duration-200 transform hover:scale-105 flex items-center justify-center space-x-2"
              >
                <Check className="w-4 h-4" />
                <span>{editingDebt ? 'Update' : 'Add'} Debt</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DebtManagement;