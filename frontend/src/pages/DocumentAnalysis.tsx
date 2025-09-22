import React, { useState, useCallback } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';
import { 
  Coffee,
  FileText,
  Upload,
  X,
  ChevronLeft,
  Download,
  AlertCircle,
  CheckCircle,
  Clock,
  Loader2,
  TrendingUp,
  DollarSign,
  CreditCard,
  PieChart
} from 'lucide-react';

interface DocumentAnalyzerProps {
  onNavigate?: (page: string) => void;
}

interface AnalysisResult {
  summary: string;
  focused_analysis?: string;
  action_items?: string;
  analysis_type: string;
  focus_areas: string[];
  files_analyzed: string[];
  processing_time?: number;
}

const DocumentAnalyzer: React.FC<DocumentAnalyzerProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const { user } = useUser();
  
  const [files, setFiles] = useState<File[]>([]);
  const [analysisType, setAnalysisType] = useState('General Summary');
  const [focusAreas, setFocusAreas] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analysisTypes = [
    'General Summary',
    'Expense Categorization',
    'Cash Flow Analysis',
    'Debt Account Detection',
    'Investment Portfolio Review'
  ];

  const availableFocusAreas = [
    'Monthly Spending Patterns',
    'High-Interest Charges',
    'Fee Analysis',
    'Credit Utilization',
    'Payment History',
    'Budget Recommendations'
  ];

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    
    if (selectedFiles.length === 0) return;
    
    console.log('Files selected:', selectedFiles); // Debug log
    
    // Validate file types
    const validTypes = ['application/pdf', 'text/plain', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];
    const validExtensions = ['.pdf', '.txt', '.csv', '.xlsx', '.xls'];
    
    const invalidFiles = selectedFiles.filter(file => {
      const hasValidType = validTypes.includes(file.type);
      const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
      return !hasValidType && !hasValidExtension;
    });
    
    if (invalidFiles.length > 0) {
      setError(`Unsupported file types: ${invalidFiles.map(f => f.name).join(', ')}`);
      return;
    }

    // Check file size (10MB per file)
    const oversizedFiles = selectedFiles.filter(file => file.size > 10 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      setError(`Files too large (max 10MB): ${oversizedFiles.map(f => f.name).join(', ')}`);
      return;
    }

    // Check total files (max 5)
    if (files.length + selectedFiles.length > 5) {
      setError('Maximum 5 files allowed');
      return;
    }

    setFiles(prev => [...prev, ...selectedFiles]);
    setError(null);
    
    // Reset the input value so the same file can be selected again if needed
    event.target.value = '';
  }, [files.length]);

  const handleUploadClick = () => {
    const input = document.getElementById('file-upload') as HTMLInputElement;
    if (input) {
      input.click();
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const toggleFocusArea = (area: string) => {
    setFocusAreas(prev => 
      prev.includes(area) 
        ? prev.filter(a => a !== area)
        : [...prev, area]
    );
  };

  const analyzeDocuments = async () => {
    if (files.length === 0) {
      setError('Please upload at least one file');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const token = await getToken();
      const formData = new FormData();
      
      files.forEach(file => {
        formData.append('files', file);
      });
      
      formData.append('analysis_type', analysisType);
      if (focusAreas.length > 0) {
        formData.append('focus_areas', focusAreas.join(','));
      }

      const response = await fetch('http://localhost:8000/api/v1/documents/analyze', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-User-Email': user?.primaryEmailAddress?.emailAddress || '',
          'X-User-First-Name': user?.firstName || '',
          'X-User-Last-Name': user?.lastName || '',
          'X-User-Image': user?.imageUrl || '',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result = await response.json();
      setAnalysisResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const downloadReport = () => {
    if (!analysisResult) return;

    const report = `# Document Analysis Report

**Analysis Type:** ${analysisResult.analysis_type}
**Files Analyzed:** ${analysisResult.files_analyzed.join(', ')}
**Focus Areas:** ${analysisResult.focus_areas.join(', ') || 'None'}
**Processing Time:** ${analysisResult.processing_time?.toFixed(2)}s

## Summary
${analysisResult.summary}

${analysisResult.focused_analysis ? `## Detailed Analysis
${analysisResult.focused_analysis}` : ''}

${analysisResult.action_items ? `## Action Items
${analysisResult.action_items}` : ''}

---
Generated by FinanceBrews Document Analyzer
`;

    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis-report-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const resetAnalysis = () => {
    setFiles([]);
    setAnalysisResult(null);
    setError(null);
    setFocusAreas([]);
    setAnalysisType('General Summary');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      {/* Header */}
      <header className="bg-white border-b border-amber-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <button
                onClick={() => onNavigate?.('dashboard')}
                className="flex items-center space-x-2 text-amber-700 hover:text-amber-800"
              >
                <ChevronLeft className="w-5 h-5" />
                <span>Back to Dashboard</span>
              </button>
              
              <div className="flex items-center space-x-3">
                <Coffee className="w-8 h-8 text-amber-700" />
                <h1 className="text-xl font-bold text-amber-900">Document Analyzer</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!analysisResult ? (
          <>
            {/* Upload Section */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                  <Upload className="w-5 h-5 mr-2" />
                  Upload Financial Documents
                </h3>
              </div>
              
              <div className="p-6">
                {/* Hidden file input */}
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  accept=".pdf,.txt,.csv,.xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                
                {/* Main upload area */}
                <div 
                  onClick={handleUploadClick}
                  className="border-2 border-dashed border-amber-300 rounded-lg p-8 text-center hover:border-amber-400 hover:bg-amber-50 transition-all duration-200 cursor-pointer"
                >
                  <FileText className="w-12 h-12 text-amber-400 mx-auto mb-4" />
                  <div className="mb-4">
                    <span className="text-lg font-medium text-amber-900 hover:text-amber-800 block">
                      Click anywhere here to upload files
                    </span>
                    <span className="text-base text-amber-700 mt-2 block">
                      or drag and drop your documents
                    </span>
                  </div>
                  <p className="text-sm text-amber-600">
                    Supported: PDF, TXT, CSV, Excel • Max 10MB per file • Up to 5 files
                  </p>
                </div>

                {/* Alternative Upload Button */}
                <div className="mt-4 text-center">
                  <button
                    onClick={handleUploadClick}
                    className="inline-flex items-center px-6 py-3 border border-amber-300 rounded-lg shadow-sm bg-white text-amber-700 hover:bg-amber-50 hover:border-amber-400 transition-colors"
                  >
                    <Upload className="w-5 h-5 mr-2" />
                    Choose Files
                  </button>
                </div>

                {/* File List */}
                {files.length > 0 && (
                  <div className="mt-6">
                    <h4 className="text-sm font-medium text-amber-900 mb-3">Uploaded Files:</h4>
                    <div className="space-y-2">
                      {files.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-amber-50 border border-amber-200 rounded-lg p-3">
                          <div className="flex items-center space-x-3">
                            <FileText className="w-4 h-4 text-amber-600" />
                            <span className="text-sm text-amber-900">{file.name}</span>
                            <span className="text-xs text-amber-600">
                              ({(file.size / 1024 / 1024).toFixed(1)} MB)
                            </span>
                          </div>
                          <button
                            onClick={() => removeFile(index)}
                            className="text-amber-600 hover:text-amber-800"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Analysis Configuration */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm mb-8">
              <div className="px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900">Analysis Configuration</h3>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Analysis Type */}
                <div>
                  <label className="block text-sm font-medium text-amber-900 mb-2">
                    Analysis Type
                  </label>
                  <select
                    value={analysisType}
                    onChange={(e) => setAnalysisType(e.target.value)}
                    className="w-full px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                  >
                    {analysisTypes.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                {/* Focus Areas */}
                <div>
                  <label className="block text-sm font-medium text-amber-900 mb-2">
                    Focus Areas (Optional)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {availableFocusAreas.map(area => (
                      <label key={area} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={focusAreas.includes(area)}
                          onChange={() => toggleFocusArea(area)}
                          className="rounded border-amber-300 text-amber-600 focus:ring-amber-500"
                        />
                        <span className="text-sm text-amber-800">{area}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <span className="text-red-800">{error}</span>
                </div>
              </div>
            )}

            {/* Analyze Button */}
            <div className="flex justify-center">
              <button
                onClick={analyzeDocuments}
                disabled={files.length === 0 || isAnalyzing}
                className="flex items-center space-x-2 px-8 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Analyzing Documents...</span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5" />
                    <span>Analyze Documents</span>
                  </>
                )}
              </button>
            </div>
          </>
        ) : (
          /* Analysis Results */
          <div className="space-y-8">
            {/* Results Header */}
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
              <div className="px-6 py-4 border-b border-amber-200">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                      Analysis Complete
                    </h3>
                    <p className="text-sm text-amber-600 mt-1">
                      Analyzed {analysisResult.files_analyzed.length} files • {analysisResult.analysis_type}
                      {analysisResult.processing_time && ` • ${analysisResult.processing_time.toFixed(1)}s`}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={downloadReport}
                      className="flex items-center space-x-1 px-3 py-2 text-amber-700 hover:text-amber-800 hover:bg-amber-50 rounded-lg transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </button>
                    <button
                      onClick={resetAnalysis}
                      className="px-3 py-2 text-amber-700 hover:text-amber-800 hover:bg-amber-50 rounded-lg transition-colors"
                    >
                      New Analysis
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="p-6">
                <h4 className="font-medium text-amber-900 mb-3">Summary</h4>
                <div className="prose prose-amber max-w-none">
                  <p className="text-amber-800 whitespace-pre-wrap">{analysisResult.summary}</p>
                </div>
              </div>
            </div>

            {/* Detailed Analysis */}
            {analysisResult.focused_analysis && (
              <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
                <div className="px-6 py-4 border-b border-amber-200">
                  <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                    <PieChart className="w-5 h-5 mr-2" />
                    Detailed Analysis
                  </h3>
                </div>
                <div className="p-6">
                  <div className="prose prose-amber max-w-none">
                    <p className="text-amber-800 whitespace-pre-wrap">{analysisResult.focused_analysis}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Action Items */}
            {analysisResult.action_items && (
              <div className="bg-white rounded-lg border border-amber-200 shadow-sm">
                <div className="px-6 py-4 border-b border-amber-200">
                  <h3 className="text-lg font-semibold text-amber-900 flex items-center">
                    <Clock className="w-5 h-5 mr-2" />
                    Recommended Actions
                  </h3>
                </div>
                <div className="p-6">
                  <div className="prose prose-amber max-w-none">
                    <p className="text-amber-800 whitespace-pre-wrap">{analysisResult.action_items}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default DocumentAnalyzer;