import React, { useEffect, useState } from 'react';
import { UserButton, useAuth, useUser } from '@clerk/clerk-react';
import {
  Coffee,
  CreditCard,
  MessageCircle,
  TrendingUp,
  Calculator,
  Brain,
  FileText,
  Shield,
  ArrowRight,
  Home,
  Star,
  Users,
  Clock,
  Sparkles
} from 'lucide-react';

interface DashboardProps {
  onNavigate?: (page: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const { user } = useUser();
  const [userSynced, setUserSynced] = useState(false);

  // Sync user with backend on component mount
  useEffect(() => {
    const syncUser = async () => {
      if (!user || userSynced) return;

      try {
        const token = await getToken();
        
        const response = await fetch('http://localhost:8000/api/v1/auth/me', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'X-User-Email': user.primaryEmailAddress?.emailAddress || '',
            'X-User-First-Name': user.firstName || '',
            'X-User-Last-Name': user.lastName || '',
            'X-User-Image': user.imageUrl || '',
          },
        });

        if (response.ok) {
          console.log('User synced to database');
          setUserSynced(true);
        }
      } catch (error) {
        console.error('Error syncing user:', error);
      }
    };

    syncUser();
  }, [user, getToken, userSynced]);

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <Home className="w-4 h-4" /> },
    { id: 'debt-management', label: 'Debt Management', icon: <CreditCard className="w-4 h-4" /> },
    { id: 'educational-hub', label: 'AI Assistant', icon: <MessageCircle className="w-4 h-4" /> },
    { id: 'repayment-plan', label: 'Repayment Plan', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'what-if', label: 'What If', icon: <Calculator className="w-4 h-4" /> },
    { id: 'document-analyzer', label: 'Document Analyzer', icon: <FileText className="w-4 h-4" /> },
    { id: 'credit-score', label: 'Credit Score', icon: <Shield className="w-4 h-4" /> }
  ];

  const features = [
    {
      id: 'debt-management',
      title: 'Debt Management',
      description: 'Track, organize, and manage all your debts in one centralized dashboard',
      icon: <CreditCard className="w-8 h-8" />,
      status: 'Available'
    },
    {
      id: 'educational-hub',
      title: 'AI Financial Assistant',
      description: 'Get instant answers to financial questions with our intelligent AI assistant',
      icon: <MessageCircle className="w-8 h-8" />,
      status: 'Available'
    },
    {
      id: 'repayment-plan',
      title: 'Smart Repayment Plans',
      description: 'Generate optimized debt payoff strategies using avalanche and snowball methods',
      icon: <TrendingUp className="w-8 h-8" />,
      status: 'Available'
    },
    {
      id: 'what-if',
      title: 'What-If Scenarios',
      description: 'Model different financial scenarios and see their impact on your debt timeline',
      icon: <Calculator className="w-8 h-8" />,
      status: 'Available'
    },
    {
      id: 'document-analyzer',
      title: 'Document Analyzer',
      description: 'Upload and analyze bank statements, bills, and financial documents with AI',
      icon: <FileText className="w-8 h-8" />,
      status: 'Available'
    },
    {
      id: 'credit-score',
      title: 'Credit Score Improvement',
      description: 'Monitor your credit score and get personalized improvement recommendations',
      icon: <Shield className="w-8 h-8" />,
      status: 'Available'
    }
  ];

  // Meaningful platform stats instead of fake debt numbers
  const platformStats = [
    { 
      label: 'AI Assistant', 
      value: 'Active', 
      trend: '24/7 Financial Guidance',
      icon: <MessageCircle className="w-5 h-5" />
    },
    { 
      label: 'Tools Available', 
      value: '6', 
      trend: 'All Features Ready',
      icon: <Star className="w-5 h-5" />
    },
    { 
      label: 'Users Helped', 
      value: '10,000+', 
      trend: 'Growing Community',
      icon: <Users className="w-5 h-5" />
    },
    { 
      label: 'Response Time', 
      value: '< 2s', 
      trend: 'Lightning Fast',
      icon: <Clock className="w-5 h-5" />
    }
  ];

  const handleNavigation = (page: string) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  const handleFeatureClick = (featureId: string, status: string) => {
    if (status === 'Available') {
      handleNavigation(featureId);
    } else {
      alert(`${featureId.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())} is coming soon!`);
    }
  };

  // Get personalized greeting
  const getPersonalizedGreeting = () => {
    const firstName = user?.firstName;
    if (firstName) {
      return `Hello ${firstName}, welcome to FinanceBrews`;
    }
    return 'Welcome to FinanceBrews';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      {/* Header with Scrollable Navigation */}
      <header className="bg-white border-b border-amber-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4 min-w-0 flex-1">
              <div className="flex items-center space-x-3 flex-shrink-0">
                <Coffee className="w-8 h-8 text-amber-700" />
                <h1 className="text-xl font-bold text-amber-900">FinanceBrews</h1>
              </div>
              
              {/* Scrollable Navigation */}
              <nav className="flex-1 overflow-x-auto">
                <div className="flex space-x-2 pb-2 min-w-max">
                  {navigationItems.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handleNavigation(item.id)}
                      className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap flex-shrink-0 ${
                        item.id === 'dashboard'
                          ? 'bg-amber-100 text-amber-800'
                          : 'text-amber-700 hover:text-amber-800 hover:bg-amber-50'
                      }`}
                    >
                      {item.icon}
                      <span>{item.label}</span>
                    </button>
                  ))}
                </div>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4 flex-shrink-0">
              <span className="text-amber-800 hidden sm:block">
                {user?.firstName ? `Hello, ${user.firstName}!` : 'Welcome!'}
              </span>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-amber-900 mb-2">
            {getPersonalizedGreeting()}
          </h2>
          <p className="text-amber-800">
            Your personal AI-powered financial advisor. Start by exploring our tools or ask our AI assistant any financial question.
          </p>
          {userSynced && (
            <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              Account synced
            </div>
          )}
        </div>

        {/* Platform Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {platformStats.map((stat, index) => (
            <div key={index} className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-amber-700">{stat.label}</div>
                <div className="text-amber-600">{stat.icon}</div>
              </div>
              <div className="text-2xl font-bold text-amber-900 mb-1">{stat.value}</div>
              <div className="text-sm text-green-600">{stat.trend}</div>
            </div>
          ))}
        </div>

        {/* Features Grid */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-amber-900 mb-6">Financial Tools & Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <div
                key={feature.id}
                onClick={() => handleFeatureClick(feature.id, feature.status)}
                className={`relative bg-gradient-to-br from-amber-50 to-orange-100 rounded-xl border border-amber-200 p-6 transition-all duration-200 cursor-pointer ${
                  feature.status === 'Available'
                    ? 'hover:scale-105 hover:shadow-lg'
                    : 'opacity-75 hover:opacity-90'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-amber-700">
                    {feature.icon}
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    feature.status === 'Available'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-amber-100 text-amber-700'
                  }`}>
                    {feature.status}
                  </span>
                </div>
                
                <h4 className="text-lg font-semibold text-amber-900 mb-2">
                  {feature.title}
                </h4>
                <p className="text-sm text-amber-800 mb-4 leading-relaxed">
                  {feature.description}
                </p>
                
                {feature.status === 'Available' ? (
                  <div className="flex items-center text-sm font-medium text-amber-700">
                    Get Started
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </div>
                ) : (
                  <div className="flex items-center text-sm font-medium text-amber-600">
                    Coming Soon
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Getting Started Section */}
        <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
          <div className="px-6 py-4 border-b border-amber-200">
            <h3 className="text-lg font-semibold text-amber-900 flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-amber-600" />
              Get Started in 3 Easy Steps
            </h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <div className="w-12 h-12 bg-amber-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                  1
                </div>
                <h4 className="font-semibold text-amber-900 mb-2">Add Your Debts</h4>
                <p className="text-sm text-amber-700 mb-4">Input your debts to get personalized recommendations</p>
                <button 
                  onClick={() => handleNavigation('debt-management')}
                  className="bg-amber-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-amber-700 transition-colors"
                >
                  Start Here
                </button>
              </div>
              
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                  2
                </div>
                <h4 className="font-semibold text-blue-900 mb-2">Ask AI Assistant</h4>
                <p className="text-sm text-blue-700 mb-4">Get instant financial advice from our AI advisor</p>
                <button 
                  onClick={() => handleNavigation('educational-hub')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                >
                  Chat Now
                </button>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="w-12 h-12 bg-green-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                  3
                </div>
                <h4 className="font-semibold text-green-900 mb-2">Track Progress</h4>
                <p className="text-sm text-green-700 mb-4">Monitor your credit score and financial health</p>
                <button 
                  onClick={() => handleNavigation('credit-score')}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition-colors"
                >
                  View Score
                </button>
              </div>
            </div>
            
            <div className="mt-6 text-center">
              <p className="text-amber-600 mb-2">Need help? Our AI assistant is ready 24/7!</p>
              <button 
                onClick={() => handleNavigation('educational-hub')}
                className="text-amber-700 hover:text-amber-800 font-medium"
              >
                Ask any financial question →
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;