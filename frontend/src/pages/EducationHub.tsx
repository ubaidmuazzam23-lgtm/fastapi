import React, { useState, useEffect, useRef } from 'react';
import { UserButton, useAuth } from '@clerk/clerk-react';
import { 
  Coffee, Brain, MessageCircle, Send, Loader2, BookOpen, TrendingUp, CreditCard,
  Calculator, Shield, PiggyBank, Target, ArrowLeft, Sparkles, Clock, Users, ChevronRight,
  Mic, MicOff, Volume2, Languages
} from 'lucide-react';

interface EducationHubProps {
  onNavigate?: (page: string) => void;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  hasAudio?: boolean;
  audioBase64?: string;
  language?: string;
}

interface SuggestedTopic {
  title: string;
  description: string;
  category: string;
  example_question: string;
}

interface Language {
  code: string;
  name: string;
  native: string;
}

const EducationHub: React.FC<EducationHubProps> = ({ onNavigate }) => {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedTopics, setSuggestedTopics] = useState<SuggestedTopic[]>([]);
  const [showChat, setShowChat] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Voice states - WITH language selector
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [selectedLanguage, setSelectedLanguage] = useState('en');  // Default to English
  const [supportedLanguages, setSupportedLanguages] = useState<Language[]>([]);
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState<string | null>(null);

  useEffect(() => {
    loadSuggestedTopics();
    loadChatHistory();
    loadSupportedLanguages();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSupportedLanguages = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/education/supported-languages', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setSupportedLanguages(data.languages || []);
      }
    } catch (error) {
      console.error('Error loading languages:', error);
    }
  };

  const loadSuggestedTopics = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/education/suggested-topics', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setSuggestedTopics(data.topics || []);
      }
    } catch (error) {
      console.error('Error loading suggested topics:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/education/history?limit=10', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        if (data.history && data.history.length > 0) {
          const chatMessages: ChatMessage[] = [];
          data.history.reverse().forEach((chat: any) => {
            chatMessages.push({
              id: `${chat.id}-user`,
              role: 'user',
              content: chat.user_message,
              timestamp: new Date(chat.timestamp)
            });
            chatMessages.push({
              id: `${chat.id}-assistant`,
              role: 'assistant',
              content: chat.assistant_response,
              timestamp: new Date(chat.timestamp)
            });
          });
          setMessages(chatMessages);
        }
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        await sendVoiceMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setAudioChunks([]);
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceMessage = async (audioBlob: Blob) => {
    setIsLoading(true);
    
    try {
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      
      reader.onloadend = async () => {
        const base64Audio = reader.result?.toString().split(',')[1];
        
        if (!base64Audio) {
          throw new Error('Failed to convert audio');
        }

        console.log('🎤 Sending voice message...');
        console.log('Audio size:', base64Audio.length);
        console.log('Selected language:', selectedLanguage);

        const token = await getToken();
        const response = await fetch('http://localhost:8000/api/v1/education/voice-chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            audio_base64: base64Audio,
            language_code: selectedLanguage,  // Use selected language
            conversation_history: messages.slice(-6).map(msg => ({
              role: msg.role,
              content: msg.content
            }))
          })
        });

        const data = await response.json();
        
        if (!response.ok) {
          console.error('❌ Voice chat error:', data);
          throw new Error(data.detail || 'Failed to get voice response');
        }
        
        console.log('✅ Voice chat response:', data);
        console.log('🌐 Auto-detected language:', data.language);
        
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'user',
          content: data.user_text,
          timestamp: new Date(),
          language: data.language
        };
        setMessages(prev => [...prev, userMessage]);

        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response_text,
          timestamp: new Date(),
          hasAudio: data.audio_available,
          audioBase64: data.response_audio_base64,
          language: data.language
        };
        setMessages(prev => [...prev, assistantMessage]);

        if (data.audio_available && data.response_audio_base64) {
          playAudio(data.response_audio_base64, assistantMessage.id);
        }
      };

      reader.onerror = () => {
        throw new Error('Failed to read audio file');
      };
    } catch (error) {
      console.error('❌ Error sending voice message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please make sure you have configured the Sarvam API key.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const playAudio = (audioBase64: string, messageId: string) => {
    try {
      const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
      setIsPlayingAudio(messageId);
      
      audio.onended = () => {
        setIsPlayingAudio(null);
      };
      
      audio.onerror = () => {
        console.error('Error playing audio');
        setIsPlayingAudio(null);
      };
      
      audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/v1/education/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_history: messages.slice(-6).map(msg => ({
            role: msg.role,
            content: msg.content
          }))
          // No language_code - auto-detects from text!
        })
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTopicClick = async (topic: SuggestedTopic) => {
    setShowChat(true);
    setInputMessage(topic.example_question);
    setTimeout(() => sendMessage(), 100);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatContent = (text: string): string => {
    let formatted = text;
    
    const tableRegex = /\|(.+)\|[\r\n]+\|[\s:|-]+\|[\r\n]+((?:\|.+\|[\r\n]*)+)/g;
    formatted = formatted.replace(tableRegex, (match) => {
      const lines = match.trim().split(/[\r\n]+/);
      if (lines.length < 3) return match;
      
      const headerCells = lines[0].split('|').filter(cell => cell.trim()).map(cell => cell.trim());
      const dataRows = lines.slice(2).map(line =>
        line.split('|').filter(cell => cell.trim()).map(cell => cell.trim())
      );
      
      let html = '<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:0.875rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);">';
      
      html += '<thead><tr>';
      headerCells.forEach(cell => {
        html += `<th style="background-color:#fef3c7;padding:0.75rem;text-align:left;font-weight:600;border:1px solid #fbbf24;color:#78350f;">${cell}</th>`;
      });
      html += '</tr></thead>';
      
      html += '<tbody>';
      dataRows.forEach((row, idx) => {
        if (row.length === 0) return;
        const bgColor = idx % 2 === 0 ? '#fffbeb' : 'white';
        html += `<tr style="background-color:${bgColor};">`;
        row.forEach(cell => {
          html += `<td style="padding:0.75rem;border:1px solid #fde68a;color:#78350f;">${cell}</td>`;
        });
        html += '</tr>';
      });
      html += '</tbody></table>';
      
      return html;
    });

    formatted = formatted.replace(/^### (.+)$/gm, '<div style="font-size:1.1em;font-weight:600;color:#78350f;margin-top:1rem;margin-bottom:0.5rem;">$1</div>');
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong style="font-weight:600;color:#78350f;">$1</strong>');
    formatted = formatted.replace(/^[•-]\s+(.+)$/gm, '<div style="margin-left:1rem;margin-top:0.25rem;">• $1</div>');
    formatted = formatted.replace(/^(\d+)\.\s+(.+)$/gm, '<div style="margin-left:1rem;margin-top:0.25rem;">$1. $2</div>');
    formatted = formatted.replace(/^={10,}$/gm, '<hr style="border:none;border-top:2px solid #fbbf24;margin:1rem 0;" />');
    formatted = formatted.replace(/^━{10,}$/gm, '<hr style="border:none;border-top:2px solid #fbbf24;margin:1rem 0;" />');
    formatted = formatted.replace(/₹([\d,]+(?:\.\d+)?)/g, '<span style="font-weight:600;color:#b45309;">₹$1</span>');
    formatted = formatted.replace(/\n\n/g, '<div style="height:0.75rem;"></div>');
    formatted = formatted.replace(/\n/g, '<br />');
    
    return formatted;
  };

  const categoryIcons: { [key: string]: React.ReactNode } = {
    budgeting: <Calculator className="w-5 h-5" />,
    savings: <PiggyBank className="w-5 h-5" />,
    debt: <CreditCard className="w-5 h-5" />,
    investment: <TrendingUp className="w-5 h-5" />,
    credit: <Shield className="w-5 h-5" />,
    tax: <BookOpen className="w-5 h-5" />,
    planning: <Target className="w-5 h-5" />,
    insurance: <Shield className="w-5 h-5" />
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      <header className="bg-white border-b border-amber-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              {onNavigate && (
                <button
                  onClick={() => onNavigate('dashboard')}
                  className="flex items-center space-x-2 text-amber-700 hover:text-amber-800 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back to Dashboard</span>
                </button>
              )}
              <div className="flex items-center space-x-3">
                <Coffee className="w-8 h-8 text-amber-700" />
                <div>
                  <h1 className="text-xl font-bold text-amber-900">FinanceBrews</h1>
                  <p className="text-sm text-amber-700">Education Hub</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {/* Language selector */}
              <div className="relative">
                <button
                  onClick={() => setShowLanguageSelector(!showLanguageSelector)}
                  className="flex items-center space-x-2 px-3 py-2 bg-amber-100 text-amber-700 rounded-lg hover:bg-amber-200 transition-colors"
                >
                  <Languages className="w-4 h-4" />
                  <span className="text-sm">
                    {supportedLanguages.find(l => l.code === selectedLanguage)?.native || 'English'}
                  </span>
                </button>
                
                {showLanguageSelector && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-amber-200 py-2 z-50">
                    {supportedLanguages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setSelectedLanguage(lang.code);
                          setShowLanguageSelector(false);
                        }}
                        className={`w-full text-left px-4 py-2 hover:bg-amber-50 transition-colors ${
                          selectedLanguage === lang.code ? 'bg-amber-100 text-amber-900' : 'text-amber-700'
                        }`}
                      >
                        <div className="font-medium">{lang.native}</div>
                        <div className="text-xs text-amber-600">{lang.name}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!showChat ? (
          <>
            <div className="text-center mb-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-amber-100 to-orange-100 mb-4">
                <Brain className="w-8 h-8 text-amber-700" />
              </div>
              <h2 className="text-4xl font-bold text-amber-900 mb-4">Financial Education Hub</h2>
              <p className="text-xl text-amber-800 max-w-2xl mx-auto">
                Get personalized financial guidance from our AI-powered assistant with real-time loan rates.
                <span className="block mt-2 text-lg">
                  <Mic className="w-5 h-5 inline mr-2" />
                  Supports 11+ Indian languages - Select your language above!
                </span>
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm text-center">
                <Users className="w-8 h-8 text-amber-700 mx-auto mb-3" />
                <div className="text-2xl font-bold text-amber-900">10,000+</div>
                <div className="text-sm text-amber-700">Questions Answered</div>
              </div>
              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm text-center">
                <Clock className="w-8 h-8 text-amber-700 mx-auto mb-3" />
                <div className="text-2xl font-bold text-amber-900">24/7</div>
                <div className="text-sm text-amber-700">Available Support</div>
              </div>
              <div className="bg-white rounded-lg border border-amber-200 p-6 shadow-sm text-center">
                <Mic className="w-8 h-8 text-amber-700 mx-auto mb-3" />
                <div className="text-2xl font-bold text-amber-900">11+ Languages</div>
                <div className="text-sm text-amber-700">Voice & Text Support</div>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-2xl font-semibold text-amber-900 mb-6">Popular Topics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {suggestedTopics.map((topic, index) => (
                  <div
                    key={index}
                    onClick={() => handleTopicClick(topic)}
                    className="bg-gradient-to-br from-amber-50 to-orange-100 rounded-xl border border-amber-200 p-6 cursor-pointer transition-all hover:shadow-lg hover:scale-105"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="text-amber-700">
                        {categoryIcons[topic.category] || <BookOpen className="w-5 h-5" />}
                      </div>
                      <ChevronRight className="w-4 h-4 text-amber-600" />
                    </div>
                    <h4 className="text-lg font-semibold text-amber-900 mb-2">{topic.title}</h4>
                    <p className="text-sm text-amber-800 mb-4 leading-relaxed">{topic.description}</p>
                    <div className="text-xs text-amber-600 bg-amber-100 px-2 py-1 rounded-full inline-block">
                      {topic.category.charAt(0).toUpperCase() + topic.category.slice(1)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="text-center">
              <button
                onClick={() => setShowChat(true)}
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-amber-600 to-orange-600 text-white px-8 py-4 rounded-lg shadow-lg hover:shadow-xl transition-all"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Start Chat with AI Advisor</span>
              </button>
            </div>
          </>
        ) : (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg border border-amber-200 shadow-sm h-[600px] flex flex-col">
              <div className="border-b border-amber-200 p-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-amber-100 to-orange-100 flex items-center justify-center">
                    <Brain className="w-5 h-5 text-amber-700" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-amber-900">Financial AI Assistant</h3>
                    <p className="text-sm text-amber-700">
                      Ask in {supportedLanguages.find(l => l.code === selectedLanguage)?.name || 'English'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowChat(false)}
                  className="text-amber-600 hover:text-amber-800 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center py-8">
                    <Brain className="w-12 h-12 text-amber-300 mx-auto mb-4" />
                    <p className="text-amber-600 mb-2">Welcome to your Financial AI Assistant!</p>
                    <p className="text-sm text-amber-500">
                      Type or speak in {supportedLanguages.find(l => l.code === selectedLanguage)?.name || 'English'}
                    </p>
                  </div>
                )}

                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] px-4 py-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
                          : 'bg-amber-50 text-amber-900 border border-amber-200'
                      }`}
                    >
                      {message.role === 'assistant' ? (
                        <>
                          <div
                            className="text-sm leading-relaxed"
                            dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
                          />
                          {message.hasAudio && message.audioBase64 && (
                            <button
                              onClick={() => playAudio(message.audioBase64!, message.id)}
                              className="mt-2 flex items-center space-x-2 text-amber-700 hover:text-amber-900 transition-colors"
                              disabled={isPlayingAudio === message.id}
                            >
                              <Volume2 className={`w-4 h-4 ${isPlayingAudio === message.id ? 'animate-pulse' : ''}`} />
                              <span className="text-xs">
                                {isPlayingAudio === message.id ? 'Playing...' : 'Play Audio Response'}
                              </span>
                            </button>
                          )}
                        </>
                      ) : (
                        <div className="text-sm leading-relaxed whitespace-pre-wrap">
                          {message.content}
                          {message.language && (
                            <span className="ml-2 text-xs bg-amber-400 px-2 py-1 rounded">
                              {supportedLanguages.find(l => l.code === message.language || `${l.code}-IN` === message.language)?.native || 'Auto'}
                            </span>
                          )}
                        </div>
                      )}
                      <div className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-amber-100' : 'text-amber-600'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-amber-50 border border-amber-200 px-4 py-3 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
                        <span className="text-sm text-amber-600">
                          {isRecording ? 'Listening...' : 'Thinking...'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="border-t border-amber-200 p-4">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Type in ${supportedLanguages.find(l => l.code === selectedLanguage)?.name || 'English'}...`}
                    className="flex-1 px-4 py-3 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none"
                    disabled={isLoading || isRecording}
                  />
                  
                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isLoading}
                    className={`p-3 rounded-lg transition-all duration-200 ${
                      isRecording 
                        ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                        : 'bg-amber-500 hover:bg-amber-600'
                    } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
                    title={isRecording ? 'Stop Recording' : `Record in ${supportedLanguages.find(l => l.code === selectedLanguage)?.name || 'English'}`}
                  >
                    {isRecording ? (
                      <MicOff className="w-5 h-5" />
                    ) : (
                      <Mic className="w-5 h-5" />
                    )}
                  </button>

                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading || isRecording}
                    className="bg-gradient-to-r from-amber-600 to-orange-600 text-white px-6 py-3 rounded-lg transition-all duration-200 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </button>
                </div>
                
                {isRecording && (
                  <div className="mt-2 text-center">
                    <span className="text-sm text-red-600 flex items-center justify-center space-x-2">
                      <span className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></span>
                      <span>Recording in {supportedLanguages.find(l => l.code === selectedLanguage)?.name}... Click mic to stop.</span>
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default EducationHub;