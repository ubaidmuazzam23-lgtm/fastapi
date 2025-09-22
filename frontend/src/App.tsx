import React, { useState } from 'react';
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import DebtManagement from './pages/DebtManagement';
import RepaymentPlan from './pages/RepaymentPlans';
import WhatIfScenarios from './pages/WhatIfScenarios';
import DocumentAnalyzer from './pages/DocumentAnalysis';
import CreditScore from './pages/CreditScore';
import EducationHub from './pages/EducationHub'; // Add this import

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  if (!PUBLISHABLE_KEY) {
    return <div>Missing Clerk Publishable Key</div>;
  }

  const handleNavigation = (page: string) => {
    setCurrentPage(page);
  };

  const renderPage = () => {
    switch(currentPage) {
      case 'debt-management':
        return <DebtManagement onNavigate={handleNavigation} />;
      case 'repayment-plan':
        return <RepaymentPlan onNavigate={handleNavigation} />;
      case 'what-if':
        return <WhatIfScenarios onNavigate={handleNavigation} />;
      case 'document-analyzer':
        return <DocumentAnalyzer onNavigate={handleNavigation} />;
      case 'credit-score':
        return <CreditScore onNavigate={handleNavigation} />;
      case 'educational-hub': // Add this case
        return <EducationHub onNavigate={handleNavigation} />;
      case 'dashboard':
      default:
        return <Dashboard onNavigate={handleNavigation} />;
    }
  };

  return (
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <div>
        <SignedOut>
          <Landing />
        </SignedOut>
        <SignedIn>
          {renderPage()}
        </SignedIn>
      </div>
    </ClerkProvider>
  );
}

export default App;