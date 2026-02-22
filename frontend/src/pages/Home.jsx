import { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle, AlertTriangle, ShieldCheck, ChevronRight } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function Home() {
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    // Feedback State
    const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
    const [showCorrectionPromt, setShowCorrectionPrompt] = useState(false);

    const handleAnalyze = async (e) => {
        e.preventDefault();
        if (!message.trim()) return;

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const response = await axios.post(`${API_URL}/analyze`, {
                message: message,
            });
            setResult(response.data);
            setFeedbackSubmitted(false);
            setShowCorrectionPrompt(false);
        } catch (err) {
            setError(
                err.response?.data?.detail || 'Failed to analyze message. Please try again.'
            );
        } finally {
            setLoading(false);
        }
    };

    const submitFeedback = async (correction) => {
        try {
            await axios.post(`${API_URL}/feedback`, {
                message: message,
                predicted_risk: result.risk_level,
                user_correction: correction
            });
            setFeedbackSubmitted(true);
            setShowCorrectionPrompt(false);
        } catch (err) {
            console.error(err);
        }
    };

    const getRiskColor = (level) => {
        switch (level) {
            case 'High':
                return 'text-brand-darkred bg-brand-lightrose border-red-200';
            case 'Medium':
                return 'text-brand-amber bg-amber-50 border-amber-200';
            case 'Low':
                return 'text-brand-emerald bg-emerald-50 border-emerald-200';
            default:
                return 'text-slate-600 bg-slate-50 border-slate-200';
        }
    };

    const getRiskIcon = (level) => {
        switch (level) {
            case 'High':
                return <ShieldAlert className="w-8 h-8 text-brand-darkred" />;
            case 'Medium':
                return <AlertTriangle className="w-8 h-8 text-brand-amber" />;
            case 'Low':
                return <ShieldCheck className="w-8 h-8 text-brand-emerald" />;
            default:
                return null;
        }
    };

    const getHeadline = (level) => {
        if (level === 'High') return '⚠️ Likely Fraudulent Message';
        if (level === 'Medium') return '⚠️ Suspicious Message';
        return '✅ Likely Safe Message';
    };

    const getSubtext = (level) => {
        if (level === 'High') return 'Strong fraud patterns detected in this message.';
        if (level === 'Medium') return 'Some risk signals detected. Proceed with caution.';
        return 'No major fraud indicators detected.';
    };

    const [showBreakdown, setShowBreakdown] = useState(false);
    const [toastMessage, setToastMessage] = useState('');

    const renderHighlightedMessage = (text, phrases) => {
        if (!phrases || phrases.length === 0) return <p className="text-slate-700">{text}</p>;

        // Case insensitive highlighting
        let highlightedText = text;
        phrases.forEach((phrase) => {
            const regex = new RegExp(`(${phrase})`, 'gi');
            highlightedText = highlightedText.replace(
                regex,
                '<span class="bg-red-200 text-red-900 font-semibold px-1 rounded">$1</span>'
            );
        });

        return (
            <p
                className="text-slate-700 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: highlightedText }}
            />
        );
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">

            {/* Header Section */}
            <div className="text-center space-y-4 pt-8">
                <div className="inline-flex items-center justify-center p-3 bg-brand-emerald/10 rounded-full mb-4">
                    <ShieldAlert className="w-10 h-10 text-brand-emerald" />
                </div>
                <h1 className="text-4xl font-extrabold text-brand-navy tracking-tight">
                    Digital Fraud <span className="text-brand-emerald">Awareness</span>
                </h1>
                <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                    Paste a suspicious SMS, WhatsApp message, or email below. Our AI and rule-based engine will determine if it's safe.
                </p>
            </div>

            {/* Input Section */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 md:p-8">
                <form onSubmit={handleAnalyze} className="space-y-4">
                    <div>
                        <label htmlFor="message" className="block text-sm font-medium text-slate-700 mb-2">
                            Message Content
                        </label>
                        <textarea
                            id="message"
                            rows={5}
                            className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-brand-navy focus:border-brand-navy outline-none transition-all resize-none shadow-inner"
                            placeholder="e.g. Dear Customer, your account is suspended. Click here to verify your KYC..."
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading || !message.trim()}
                        className="w-full md:w-auto px-8 py-3 bg-brand-navy hover:bg-slate-800 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl shadow-sm transition-all flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <span className="flex items-center gap-2">
                                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                                Analyzing...
                            </span>
                        ) : (
                            <span className="flex items-center gap-2">
                                Analyze Message
                                <ChevronRight className="w-4 h-4" />
                            </span>
                        )}
                    </button>
                </form>

                {error && (
                    <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                        <p>{error}</p>
                    </div>
                )}
            </div>

            {/* Results Section */}
            {result && (
                <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">

                    {/* Main Risk Card */}
                    <div className={`p-6 md:p-8 rounded-2xl border flex flex-col items-start shadow-sm transition-all duration-700 mt-2 ${getRiskColor(result.risk_level)} border-l-8`}>

                        <div className="flex flex-col md:flex-row items-center w-full justify-between gap-6">
                            <div className="flex-1 text-center md:text-left space-y-2">
                                <h2 className="text-2xl font-bold mb-1 flex items-center justify-center md:justify-start gap-2">
                                    {getHeadline(result.risk_level)}
                                </h2>
                                <p className="font-medium opacity-90">{getSubtext(result.risk_level)}</p>

                                <div className="inline-flex items-center gap-2 px-4 py-2 mt-2 rounded-xl bg-gray-50 border-2 border-current text-sm font-bold shadow-sm transition-transform hover:scale-105">
                                    <span className="w-2 h-2 rounded-full animate-pulse bg-current" />
                                    Confidence: {Math.round(result.final_score * 100)}%
                                </div>
                            </div>
                        </div>

                        {/* Action Steps */}
                        <div className="w-full bg-white/50 rounded-xl p-5 mt-8 space-y-3 shadow-inner">
                            <h3 className="font-bold text-slate-800 flex items-center gap-2">
                                📌 What You Should Do
                            </h3>
                            <ul className="text-slate-700 space-y-2 text-sm font-medium">
                                <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-current" /> Do NOT click links</li>
                                <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-current" /> Do NOT share OTP or PINs</li>
                                <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-current" /> Contact institution via their official website or app numbers</li>
                            </ul>
                        </div>
                    </div>

                    {/* Expandable Breakdown Layer */}
                    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                        <button
                            onClick={() => setShowBreakdown(!showBreakdown)}
                            className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-slate-50 transition-colors focus:outline-none"
                        >
                            <span className="font-bold text-slate-800 flex items-center gap-2">
                                <ShieldAlert className="w-5 h-5 text-brand-emerald" />
                                Safety Breakdown
                            </span>
                            <ChevronRight className={`w-5 h-5 text-slate-400 transition-transform ${showBreakdown ? 'rotate-90' : ''}`} />
                        </button>

                        {showBreakdown && (
                            <div className="px-6 pb-6 pt-2 border-t border-slate-100 bg-slate-50/50 space-y-6">
                                {/* Reason Matrix */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                    <div className="bg-slate-100 p-4 rounded-xl border border-slate-200 shadow-sm">
                                        <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-2">AI Pattern Analysis</div>
                                        <div className="font-semibold text-slate-800">
                                            {result.ml_probability >= 0.85 ? "Strong Fraud Pattern Detected" :
                                                result.ml_probability >= 0.65 ? "Elevated Risk Signals Present" :
                                                    "No Strong AI Patterns"}
                                        </div>
                                        <div className="font-mono text-xs text-slate-500 mt-2 bg-slate-100 p-1.5 rounded inline-block">
                                            Raw Model Probability: {(result.ml_probability * 100).toFixed(1)}%
                                        </div>
                                    </div>
                                    <div className="bg-slate-100 p-4 rounded-xl border border-slate-200 shadow-sm">
                                        <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-2">Rule Indicators</div>
                                        <div className="font-semibold text-slate-800">
                                            {result.triggered_rules?.length > 0 ? (
                                                <ul className="list-disc leading-tight pl-4 space-y-1">
                                                    {result.triggered_rules.map(r => <li key={r}>{r}</li>)}
                                                </ul>
                                            ) : "None Detected"}
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-slate-100 p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-2">Hybrid Decision Logic</div>
                                    <div className="font-medium text-slate-700 italic">
                                        "{result.decision_reason || "Standard evaluation applied."}"
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Feedback Widget */}
                    {!feedbackSubmitted ? (
                        <div className="flex flex-col sm:flex-row items-center justify-between p-4 bg-white border border-slate-200 rounded-xl shadow-sm gap-4">
                            <span className="text-sm font-bold text-slate-700">Was this analysis helpful?</span>

                            {!showCorrectionPromt ? (
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => submitFeedback(result.risk_level)}
                                        className="px-5 py-2 text-sm font-bold bg-slate-100 text-slate-700 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 rounded-lg border border-slate-200 transition-colors"
                                    >
                                        👍 Yes
                                    </button>
                                    <button
                                        onClick={() => setShowCorrectionPrompt(true)}
                                        className="px-5 py-2 text-sm font-bold bg-slate-100 text-slate-700 hover:bg-red-50 hover:text-red-700 hover:border-red-200 rounded-lg border border-slate-200 transition-colors"
                                    >
                                        👎 No
                                    </button>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2">
                                    <span className="text-sm text-slate-500 mr-2 font-medium">Actual Level:</span>
                                    <button onClick={() => submitFeedback('Low')} className="px-3 py-1 text-xs font-bold uppercase rounded border bg-slate-50 hover:bg-emerald-50 text-slate-600 transition-colors shadow-sm">Low</button>
                                    <button onClick={() => submitFeedback('Medium')} className="px-3 py-1 text-xs font-bold uppercase rounded border bg-slate-50 hover:bg-amber-50 text-slate-600 transition-colors shadow-sm">Med</button>
                                    <button onClick={() => submitFeedback('High')} className="px-3 py-1 text-xs font-bold uppercase rounded border bg-slate-50 hover:bg-red-50 text-slate-600 transition-colors shadow-sm">High</button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="p-4 bg-brand-offwhite border border-slate-200 rounded-xl text-center text-brand-emerald text-sm font-bold flex items-center justify-center gap-2 shadow-sm">
                            <CheckCircle className="w-5 h-5" />
                            Thank you! We will use this to retrain our models.
                        </div>
                    )}

                    <div className="grid md:grid-cols-1 gap-6">
                        {/* Original Message with Highlights */}
                        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                            <div className="bg-slate-900 border-b border-slate-800 p-4">
                                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-widest flex items-center gap-2">
                                    📄 Analyzed Message
                                </h3>
                            </div>

                            <div className="p-6">
                                <div className="bg-slate-50 rounded-xl p-5 border border-slate-200 font-medium font-sans text-lg text-slate-800 shadow-inner">
                                    {renderHighlightedMessage(message, result.matched_phrases)}
                                </div>

                                {result.matched_phrases.length > 0 && (
                                    <div className="mt-6 pt-6 border-t border-slate-100">
                                        <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Highlighted Triggers</p>
                                        <div className="flex flex-wrap gap-2">
                                            {result.matched_phrases.map((phrase, idx) => (
                                                <span key={idx} className="px-3 py-1.5 bg-red-100 text-red-900 text-sm rounded-md border border-red-200 font-bold shadow-sm">
                                                    "{phrase}"
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Footer Stats / Engine Meta */}
                    <div className="flex flex-col md:flex-row items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-widest pt-4 pb-8">
                        <div>Hybrid AI + Rule-Based Fraud Detection Engine</div>
                        {result.processing_time_sec !== undefined && (
                            <div>Analyzed in {result.processing_time_sec} seconds</div>
                        )}
                    </div>

                </div>
            )}
        </div>
    );
}

export default Home;
