import React, { useState, useEffect } from 'react';
import { Loader2, Zap, Code, GitBranch, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

/**
 * SuperAgent v8.0 Dashboard
 * Beautiful web interface with purple gradient theme
 * Real-time code generation and monitoring
 */

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('build');
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildProgress, setBuildProgress] = useState(0);
  const [generatedCode, setGeneratedCode] = useState('');
  const [userInput, setUserInput] = useState('');
  const [buildHistory, setBuildHistory] = useState<Array<{id: string; name: string; status: string; timestamp: string}>>([]);
  const [selectedLanguage, setSelectedLanguage] = useState('typescript');
  const [appType, setAppType] = useState('web-app');

  const appTypes = [
    { id: 'web-app', name: 'Web Application', icon: '🌐' },
    { id: 'api', name: 'REST API', icon: '⚙️' },
    { id: 'mobile', name: 'Mobile App', icon: '📱' },
    { id: 'microservices', name: 'Microservices', icon: '🔗' },
    { id: 'ecommerce', name: 'E-Commerce', icon: '🛍️' },
    { id: 'saas', name: 'SaaS Platform', icon: '☁️' },
  ];

  const languages = [
    { id: 'typescript', name: 'TypeScript', icon: '📘' },
    { id: 'python', name: 'Python', icon: '🐍' },
    { id: 'go', name: 'Go', icon: '🔵' },
    { id: 'rust', name: 'Rust', icon: '🦀' },
    { id: 'java', name: 'Java', icon: '☕' },
  ];

  const handleBuild = async () => {
    if (!userInput.trim()) return;

    setIsBuilding(true);
    setBuildProgress(0);

    // Simulate build progress
    const progressInterval = setInterval(() => {
      setBuildProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + Math.random() * 30;
      });
    }, 500);

    try {
      // Call API to build application
      const response = await fetch('/api/v1/enterprise/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instruction: userInput,
          language: selectedLanguage,
          app_type: appType,
          features: ['testing', 'documentation', 'deployment'],
        }),
      });

      const data = await response.json();
      setGeneratedCode(data.code || 'Code generated successfully');
      
      // Add to history
      const newBuild = {
        id: Date.now().toString(),
        name: userInput.substring(0, 50),
        status: 'completed',
        timestamp: new Date().toLocaleString(),
      };
      setBuildHistory([newBuild, ...buildHistory]);

      clearInterval(progressInterval);
      setBuildProgress(100);
    } catch (error) {
      console.error('Build error:', error);
      clearInterval(progressInterval);
    } finally {
      setIsBuilding(false);
      setTimeout(() => setBuildProgress(0), 1000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900">
      {/* Header */}
      <div className="border-b border-purple-700/50 bg-black/20 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                SuperAgent v8.0
              </h1>
            </div>
            <div className="flex items-center gap-2 text-sm text-purple-300">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>All Systems Operational</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-black/30 border border-purple-500/30 backdrop-blur-md">
            <TabsTrigger value="build" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-purple-500">
              Build
            </TabsTrigger>
            <TabsTrigger value="preview" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-purple-500">
              Preview
            </TabsTrigger>
            <TabsTrigger value="history" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-purple-500">
              History
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-purple-500">
              Settings
            </TabsTrigger>
          </TabsList>

          {/* Build Tab */}
          <TabsContent value="build" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Input Panel */}
              <div className="lg:col-span-2 space-y-6">
                <Card className="bg-black/40 border-purple-500/30 backdrop-blur-md p-6">
                  <h2 className="text-xl font-bold text-white mb-4">What do you want to build?</h2>
                  <textarea
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="Describe your application... e.g., 'Build an e-commerce platform with product catalog, shopping cart, and payment processing'"
                    className="w-full h-32 bg-black/50 border border-purple-500/30 rounded-lg p-4 text-white placeholder-purple-400/50 focus:outline-none focus:border-cyan-500/50 resize-none"
                  />
                  <Button
                    onClick={handleBuild}
                    disabled={isBuilding || !userInput.trim()}
                    className="mt-4 w-full bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-semibold py-3 rounded-lg transition-all"
                  >
                    {isBuilding ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Building... {Math.round(buildProgress)}%
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 mr-2" />
                        Build Application
                      </>
                    )}
                  </Button>

                  {/* Progress Bar */}
                  {isBuilding && (
                    <div className="mt-4 space-y-2">
                      <div className="w-full bg-black/50 rounded-full h-2 border border-purple-500/30">
                        <div
                          className="bg-gradient-to-r from-cyan-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${buildProgress}%` }}
                        />
                      </div>
                      <p className="text-sm text-purple-300">Generating code, tests, and deployment configs...</p>
                    </div>
                  )}
                </Card>

                {/* App Type Selection */}
                <Card className="bg-black/40 border-purple-500/30 backdrop-blur-md p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Application Type</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {appTypes.map(type => (
                      <button
                        key={type.id}
                        onClick={() => setAppType(type.id)}
                        className={`p-3 rounded-lg border-2 transition-all ${
                          appType === type.id
                            ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border-cyan-500'
                            : 'bg-black/30 border-purple-500/30 hover:border-purple-400/50'
                        }`}
                      >
                        <div className="text-2xl mb-1">{type.icon}</div>
                        <div className="text-sm font-medium text-white">{type.name}</div>
                      </button>
                    ))}
                  </div>
                </Card>
              </div>

              {/* Right Panel - Language Selection */}
              <div className="space-y-6">
                <Card className="bg-black/40 border-purple-500/30 backdrop-blur-md p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Language</h3>
                  <div className="space-y-2">
                    {languages.map(lang => (
                      <button
                        key={lang.id}
                        onClick={() => setSelectedLanguage(lang.id)}
                        className={`w-full p-3 rounded-lg border-2 transition-all text-left ${
                          selectedLanguage === lang.id
                            ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border-cyan-500'
                            : 'bg-black/30 border-purple-500/30 hover:border-purple-400/50'
                        }`}
                      >
                        <div className="text-2xl mb-1">{lang.icon}</div>
                        <div className="text-sm font-medium text-white">{lang.name}</div>
                      </button>
                    ))}
                  </div>
                </Card>

                {/* Features */}
                <Card className="bg-black/40 border-purple-500/30 backdrop-blur-md p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Features</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      <span>Automated Testing</span>
                    </div>
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      <span>Documentation</span>
                    </div>
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      <span>CI/CD Pipeline</span>
                    </div>
                    <div className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      <span>Security Scan</span>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Preview Tab */}
          <TabsContent value="preview">
            <Card className="bg-black/40 border-purple-500/30 backdrop-blur-md p-6">
              <div className="flex items-center gap-2 mb-4">
                <Code className="w-5 h-5 text-cyan-400" />
                <h3 className="text-lg font-bold text-white">Generated Code</h3>
              </div>
              <pre className="bg-black/50 border border-purple-500/30 rounded-lg p-4 text-green-400 text-sm overflow-x-auto max-h-96">
                {generatedCode || 'Code will appear here after building...'}
              </pre>
            </Card>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history">
            <Card className="bg-black/40 border-purple-500/30 backdrop-blur-md p-6">
              <h3 className="text-lg font-bold text-white mb-4">Build History</h3>
              {buildHistory.length === 0 ? (
                <p className="text-purple-300">No builds yet. Create one to get started!</p>
              ) : (
                <div className="space-y-2">
                  {buildHistory.map(build => (
                    <div key={build.id} className="flex items-center justify-between p-3 bg-black/30 border border-purple-500/20 rounded-lg hover:border-purple-500/50 transition-all">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <div>
                          <p className="text-white font-medium">{build.name}</p>
                          <p className="text-sm text-purple-300">{build.timestamp}</p>
                        </div>
                      </div>
                      <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-medium">
                        {build.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <Card className="bg-black/40 border-purple-500/30 backdrop-blur-md p-6">
              <h3 className="text-lg font-bold text-white mb-4">Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-purple-300 mb-2">AI Provider</label>
                  <select className="w-full bg-black/50 border border-purple-500/30 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500/50">
                    <option>Groq (Llama 3.1)</option>
                    <option>OpenAI (GPT-4)</option>
                    <option>Anthropic (Claude)</option>
                    <option>Google (Gemini)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-purple-300 mb-2">Deployment Target</label>
                  <select className="w-full bg-black/50 border border-purple-500/30 rounded-lg p-2 text-white focus:outline-none focus:border-cyan-500/50">
                    <option>Railway</option>
                    <option>Vercel</option>
                    <option>AWS</option>
                    <option>Google Cloud</option>
                    <option>Azure</option>
                  </select>
                </div>
                <Button className="w-full bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-semibold py-2 rounded-lg transition-all">
                  Save Settings
                </Button>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
