import React, { useState } from 'react';
import { SignInButton, SignUpButton, useAuth } from '@clerk/clerk-react';
import { 
  CreditCard, 
  TrendingUp, 
  Calculator, 
  FileText, 
  MessageCircle, 
  Shield, 
  Users, 
  Award,
  ChevronRight,
  Star,
  Coffee,
  Menu,
  X,
  PieChart,
  Brain,
  Target
} from 'lucide-react';

const LandingPage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { isSignedIn } = useAuth();

  const features = [
    {
      icon: <CreditCard className="w-8 h-8" />,
      title: "Smart Debt Management",
      description: "Track all your debts in one place with AI-powered insights and personalized recommendations."
    },
    {
      icon: <MessageCircle className="w-8 h-8" />,
      title: "AI Chat Advisor",
      description: "Get instant answers to financial questions with our intelligent AI chat system powered by advanced models."
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: "Repayment Plans",
      description: "Get optimized debt avalanche and snowball strategies to pay off debt faster and save money."
    },
    {
      icon: <Calculator className="w-8 h-8" />,
      title: "What-If Scenarios",
      description: "Explore different financial scenarios and see how changes impact your debt-free timeline."
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: "Educational Hub",
      description: "Learn financial concepts through our interactive chatbot and comprehensive educational resources."
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "Document Analyzer",
      description: "Upload bank statements and financial documents for AI-powered analysis and insights."
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Credit Score Improvement",
      description: "Monitor your credit score and get personalized improvement plans to boost your rating."
    },
    {
      icon: <Target className="w-8 h-8" />,
      title: "Goal Tracking",
      description: "Set financial goals and track your progress with smart milestones and achievement rewards."
    }
  ];

  const testimonials = [
    {
      name: "Priya Sharma",
      role: "Software Engineer",
      content: "Paid off ₹5,00,000 in debt 2 years early using the AI recommendations!",
      rating: 5
    },
    {
      name: "Rajesh Kumar",
      role: "Marketing Manager", 
      content: "The document analysis feature helped me find hidden fees I was paying.",
      rating: 5
    },
    {
      name: "Anita Patel",
      role: "Teacher",
      content: "Credit score improved by 120 points in 6 months with their guidance.",
      rating: 5
    }
  ];

  const stats = [
    { number: "₹50+ Cr", label: "Debt Optimized" },
    { number: "10,000+", label: "Users Helped" },
    { number: "2.5 Years", label: "Average Time Saved" },
    { number: "150+ Points", label: "Credit Score Improvement" }
  ];

  // If user is signed in, redirect message (optional)
  if (isSignedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50 flex items-center justify-center">
        <div className="text-center">
          <Coffee className="w-16 h-16 text-amber-700 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-amber-900 mb-2">Welcome back!</h1>
          <p className="text-amber-700 mb-4">Redirecting you to your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      {/* Header - Fixed Navigation Overlapping */}
      <header className="bg-white/95 backdrop-blur-sm shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-3">
            <div className="flex items-center space-x-2">
              <Coffee className="w-7 h-7 text-amber-700" />
              <span className="text-xl font-bold text-amber-900">FinanceBrews</span>
            </div>
            
            {/* Desktop Navigation - Better responsive design */}
            <nav className="hidden xl:flex space-x-3 text-sm">
              <a href="#debt-management" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-2 py-1">Debt Management</a>
              <a href="#chat-advisor" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-2 py-1">Chat Advisor</a>
              <a href="#repayment-plan" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-2 py-1">Repayment Plan</a>
              <a href="#what-if" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-2 py-1">What If</a>
              <a href="#educational-hub" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-2 py-1">Educational Hub</a>
              <a href="#document-analyzer" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-2 py-1">Document Analyzer</a>
              <a href="#credit-score" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-2 py-1">Credit Score</a>
            </nav>

            {/* Medium screens navigation - condensed */}
            <nav className="hidden lg:flex xl:hidden space-x-2 text-xs">
              <a href="#debt-management" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-1">Debt Mgmt</a>
              <a href="#chat-advisor" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-1">Chat</a>
              <a href="#repayment-plan" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-1">Repayment</a>
              <a href="#what-if" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-1">What If</a>
              <a href="#educational-hub" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-1">Education</a>
              <a href="#document-analyzer" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-1">Documents</a>
              <a href="#credit-score" className="text-amber-800 hover:text-amber-600 transition-colors whitespace-nowrap px-1">Credit</a>
            </nav>

            {/* CTA Buttons with Clerk */}
            <div className="hidden md:flex items-center space-x-3">
              <SignInButton mode="modal">
                <button className="text-amber-800 hover:text-amber-600 transition-colors text-sm">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-amber-700 hover:bg-amber-800 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                  Get Started
                </button>
              </SignUpButton>
            </div>

            {/* Mobile menu button */}
            <button 
              className="lg:hidden text-amber-800"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {/* Mobile Navigation */}
          {isMenuOpen && (
            <div className="lg:hidden py-4 border-t border-amber-100">
              <div className="flex flex-col space-y-3">
                <a href="#debt-management" className="text-amber-800 hover:text-amber-600 py-2">Debt Management</a>
                <a href="#chat-advisor" className="text-amber-800 hover:text-amber-600 py-2">Chat Advisor</a>
                <a href="#repayment-plan" className="text-amber-800 hover:text-amber-600 py-2">Repayment Plan</a>
                <a href="#what-if" className="text-amber-800 hover:text-amber-600 py-2">What If</a>
                <a href="#educational-hub" className="text-amber-800 hover:text-amber-600 py-2">Educational Hub</a>
                <a href="#document-analyzer" className="text-amber-800 hover:text-amber-600 py-2">Document Analyzer</a>
                <a href="#credit-score" className="text-amber-800 hover:text-amber-600 py-2">Credit Score Improvement</a>
                <div className="flex flex-col space-y-2 pt-4 border-t border-amber-100">
                  <SignInButton mode="modal">
                    <button className="text-amber-800 text-left py-2">Sign In</button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <button className="bg-amber-700 text-white px-6 py-2 rounded-lg text-left">
                      Get Started Free
                    </button>
                  </SignUpButton>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Rest of the sections remain the same... */}
      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl lg:text-6xl font-bold text-amber-900 leading-tight">
                Brew Your Way to
                <span className="text-amber-700 block">Financial Freedom</span>
              </h1>
              <p className="text-xl text-amber-800 mt-6 leading-relaxed">
                AI-powered debt management that helps you pay off debt faster, boost your credit score, 
                and achieve financial wellness. Like a perfect cup of coffee - strong, smart, and satisfying.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 mt-8">
                <SignUpButton mode="modal">
                  <button className="bg-amber-700 hover:bg-amber-800 text-white px-8 py-4 rounded-lg text-lg font-medium transition-colors flex items-center justify-center">
                    Start Your Financial Journey
                    <ChevronRight className="w-5 h-5 ml-2" />
                  </button>
                </SignUpButton>
                <button className="border-2 border-amber-700 text-amber-700 hover:bg-amber-700 hover:text-white px-8 py-4 rounded-lg text-lg font-medium transition-all">
                  Watch Demo
                </button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
                {stats.map((stat, index) => (
                  <div key={index} className="text-center">
                    <div className="text-2xl font-bold text-amber-900">{stat.number}</div>
                    <div className="text-sm text-amber-700">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8 transform rotate-2">
                <div className="bg-gradient-to-br from-amber-100 to-orange-100 rounded-xl p-6">
                  <h3 className="text-xl font-bold text-amber-900 mb-4">Your Debt Overview</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-amber-800">Credit Cards</span>
                      <span className="font-semibold text-amber-900">₹2,50,000</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-amber-800">Personal Loan</span>
                      <span className="font-semibold text-amber-900">₹5,00,000</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-amber-800">Car Loan</span>
                      <span className="font-semibold text-amber-900">₹3,75,000</span>
                    </div>
                    <div className="border-t border-amber-200 pt-3 mt-3">
                      <div className="flex justify-between items-center font-bold">
                        <span className="text-amber-900">Total Debt</span>
                        <span className="text-amber-900">₹11,25,000</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 bg-amber-700 text-white p-3 rounded-lg text-center">
                    <span className="text-sm">AI Recommendation: Pay off Credit Cards first!</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-amber-900 mb-4">
              Powerful Features for Financial Success
            </h2>
            <p className="text-xl text-amber-700 max-w-3xl mx-auto">
              Everything you need to take control of your finances, powered by AI and designed for results.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="bg-gradient-to-br from-amber-50 to-orange-50 p-6 rounded-xl border border-amber-100 hover:shadow-lg transition-shadow">
                <div className="text-amber-700 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-amber-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-amber-800 leading-relaxed text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-gradient-to-br from-amber-50 to-orange-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-amber-900 mb-4">
              Simple Steps to Financial Freedom
            </h2>
            <p className="text-xl text-amber-700">
              Get started in minutes and see results in days
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-amber-700 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                1
              </div>
              <h3 className="text-xl font-bold text-amber-900 mb-4">Connect Your Accounts</h3>
              <p className="text-amber-800">
                Securely link your bank accounts and credit cards. Upload documents for comprehensive analysis.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-amber-700 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                2
              </div>
              <h3 className="text-xl font-bold text-amber-900 mb-4">Get AI Recommendations</h3>
              <p className="text-amber-800">
                Our AI analyzes your financial situation and creates personalized debt payoff strategies.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-amber-700 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                3
              </div>
              <h3 className="text-xl font-bold text-amber-900 mb-4">Track Progress</h3>
              <p className="text-amber-800">
                Monitor your progress, celebrate milestones, and adjust your plan as your situation changes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-amber-900 mb-4">
              Real Stories, Real Results
            </h2>
            <p className="text-xl text-amber-700">
              Join thousands who have transformed their financial lives
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-gradient-to-br from-amber-50 to-orange-50 p-8 rounded-xl border border-amber-100">
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-amber-800 mb-6 italic">
                  "{testimonial.content}"
                </p>
                <div>
                  <div className="font-bold text-amber-900">{testimonial.name}</div>
                  <div className="text-amber-700 text-sm">{testimonial.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-amber-700 to-orange-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
            Ready to Start Your Financial Journey?
          </h2>
          <p className="text-xl text-amber-100 mb-8">
            Join thousands of users who have already taken control of their finances. 
            Start your free trial today and see results in the first week.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <SignUpButton mode="modal">
              <button className="bg-white text-amber-700 hover:bg-amber-50 px-8 py-4 rounded-lg text-lg font-medium transition-colors">
                Start Free Trial
              </button>
            </SignUpButton>
            <button className="border-2 border-white text-white hover:bg-white hover:text-amber-700 px-8 py-4 rounded-lg text-lg font-medium transition-all">
              Schedule Demo
            </button>
          </div>

          <p className="text-amber-200 text-sm mt-6">
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-amber-900 text-amber-100 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Coffee className="w-8 h-8 text-amber-400" />
                <span className="text-2xl font-bold text-white">FinanceBrews</span>
              </div>
              <p className="text-amber-200 leading-relaxed">
                Brewing financial success through AI-powered debt management and smart financial planning.
              </p>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-amber-200 hover:text-white">Debt Management</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">Credit Tracking</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">Document Analysis</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">AI Chat</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-amber-200 hover:text-white">About</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">Blog</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">Careers</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">Contact</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Support</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-amber-200 hover:text-white">Help Center</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="text-amber-200 hover:text-white">Security</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-amber-800 pt-8 mt-8 text-center">
            <p className="text-amber-200">
              © 2024 FinanceBrews. All rights reserved. Made with coffee and financial wisdom in India.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;