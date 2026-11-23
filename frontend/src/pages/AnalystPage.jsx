import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Sparkles,
  Send,
  RotateCcw,
  AlertCircle,
  Lightbulb,
} from 'lucide-react';
import { analysisApi } from '../api/analysis';
import { datasetsApi } from '../api/datasets';
import { databasesApi } from '../api/databases';
import { documentsApi } from '../api/documents';
import ResourcePicker from '../components/analysis/ResourcePicker';
import MessageBubble from '../components/analysis/MessageBubble';
import Button from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export default function AnalystPage() {
  const location = useLocation();
  const initialQuestion = location.state?.initialQuestion || '';

  const [question, setQuestion] = useState(initialQuestion);
  const [messages, setMessages] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  // Available resources
  const [datasets, setDatasets] = useState([]);
  const [databases, setDatabases] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [isLoadingResources, setIsLoadingResources] = useState(true);

  // Selected resource IDs
  const [selectedDatasetIds, setSelectedDatasetIds] = useState(
    location.state?.selectedDatasetIds || []
  );
  const [selectedDataSourceIds, setSelectedDataSourceIds] = useState(
    location.state?.selectedDataSourceIds || []
  );
  const [selectedDocumentIds, setSelectedDocumentIds] = useState(
    location.state?.selectedDocumentIds || []
  );

  const chatBottomRef = useRef(null);

  // Load available resources on mount
  useEffect(() => {
    async function loadResources() {
      setIsLoadingResources(true);
      try {
        const [dsRes, dbRes, docRes] = await Promise.allSettled([
          datasetsApi.list(),
          databasesApi.list(),
          documentsApi.list(),
        ]);

        if (dsRes.status === 'fulfilled') setDatasets(dsRes.value || []);
        if (dbRes.status === 'fulfilled') setDatabases(dbRes.value || []);
        if (docRes.status === 'fulfilled') setDocuments(docRes.value || []);
      } catch (err) {
        console.error('Failed to load resources:', err);
      } finally {
        setIsLoadingResources(false);
      }
    }
    loadResources();
  }, []);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isAnalyzing]);

  const handleToggleDataset = (id) => {
    setSelectedDatasetIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleToggleDatabase = (id) => {
    setSelectedDataSourceIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleToggleDocument = (id) => {
    setSelectedDocumentIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
  };

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    const promptText = question.trim();
    if (!promptText || isAnalyzing) return;

    setError(null);
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: promptText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion('');
    setIsAnalyzing(true);

    try {
      const response = await analysisApi.run({
        question: promptText,
        dataset_ids: selectedDatasetIds,
        data_source_ids: selectedDataSourceIds,
        document_ids: selectedDocumentIds,
      });

      const aiMessage = {
        id: response.id || Date.now() + 1,
        role: 'assistant',
        route: response.route,
        answer: response.answer,
        evaluation: response.evaluation,
        structured_result: response.structured_result,
        document_context: response.document_context,
        error: response.error,
        created_at: response.created_at || new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError(err.message || 'Unable to complete the analysis. Please verify your selected resources.');
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        route: 'general',
        answer: 'I encountered an error trying to process your question.',
        error: err.message,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const promptSuggestions = [
    'What are the key numerical statistics and column distributions across our datasets?',
    'Identify any anomalies, missing values, or outliers in the structured data.',
    'Retrieve the relevant clauses, policy details, and citations from our uploaded PDFs.',
    'Generate an SQL query to calculate top performers and group by category.',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)] max-w-5xl mx-auto">
      {/* Workspace Controls Header */}
      <div className="flex flex-col gap-3 pb-3 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-600" />
              AI Analyst Workspace
            </h2>
            <p className="text-xs text-slate-500">
              Query relational databases, uploaded tabular data, and vector documents with natural language.
            </p>
          </div>

          {messages.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              icon={RotateCcw}
              onClick={handleClearChat}
              disabled={isAnalyzing || isLoadingResources}
            >
              Reset Thread
            </Button>
          )}
        </div>

        {/* Multi-Resource Selector */}
        <ResourcePicker
          datasets={datasets}
          databases={databases}
          documents={documents}
          selectedDatasetIds={selectedDatasetIds}
          selectedDataSourceIds={selectedDataSourceIds}
          selectedDocumentIds={selectedDocumentIds}
          onToggleDataset={handleToggleDataset}
          onToggleDatabase={handleToggleDatabase}
          onToggleDocument={handleToggleDocument}
          disabled={isAnalyzing || isLoadingResources}
        />
      </div>

      {/* Conversation Thread Area */}
      <div className="flex-1 overflow-y-auto py-4 px-1 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12 px-4">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-full mb-3 border border-blue-100">
              <Sparkles className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-800">
              How can AI Data Analysis assist your work today?
            </h3>
            <p className="text-xs text-slate-500 max-w-md mt-1 mb-6 leading-relaxed">
              Select datasets, connected databases, or PDF manuals above, or ask a general data engineering question.
            </p>

            {/* Quick Prompt Starters */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-w-2xl w-full text-left">
              {promptSuggestions.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setQuestion(prompt)}
                  className="p-3 rounded-lg border border-slate-200 bg-white hover:bg-slate-50/80 hover:border-slate-300 transition-all text-xs text-slate-700 flex items-start gap-2 shadow-2xs group"
                >
                  <Lightbulb className="h-4 w-4 text-amber-500 shrink-0 mt-0.5 group-hover:text-amber-600" />
                  <span className="leading-snug">{prompt}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}

        {/* Thinking / Analyzing Indicator */}
        {isAnalyzing && (
          <div className="flex gap-3 justify-start items-start my-4">
            <div className="h-8 w-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 border border-blue-200">
              <Sparkles className="h-4 w-4 animate-spin" />
            </div>
            <div className="rounded-lg bg-white border border-slate-200 p-4 shadow-2xs flex items-center gap-3">
              <LoadingSpinner size="sm" />
              <div className="text-xs text-slate-600">
                <span className="font-semibold block text-slate-800">AI Data Analysis is thinking...</span>
                <span className="text-[11px] text-slate-500">
                  Synthesizing query routes, SQL generation, and document vectors
                </span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-md text-xs text-rose-700 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
            <div>
              <p className="font-semibold">Analysis Failed</p>
              <p className="text-[11px] mt-0.5">{error}</p>
            </div>
          </div>
        )}

        <div ref={chatBottomRef} />
      </div>

      {/* Input Box Area */}
      <div className="pt-3 border-t border-slate-200 bg-white">
        <form onSubmit={handleSend} className="relative">
          <textarea
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask a question about your data (Press Enter to submit, Shift+Enter for new line)..."
            className="w-full rounded-lg border border-slate-300 p-3 pr-24 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-2xs resize-none"
            disabled={isAnalyzing || isLoadingResources}
          />

          <div className="absolute right-2.5 bottom-3.5 flex items-center gap-1.5">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              icon={Send}
              disabled={!question.trim() || isAnalyzing}
              isLoading={isAnalyzing}
            >
              Analyze
            </Button>
          </div>
        </form>
        <p className="text-[10px] text-slate-400 mt-1 text-center">
          AI Data Analysis routes queries to verified read-only execution with zero arbitrary SQL write access.
        </p>
      </div>
    </div>
  );
}
