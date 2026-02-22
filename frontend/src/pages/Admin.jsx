import { useState, useEffect } from 'react';
import { Settings, Plus, Trash2, Power, BookOpen, Download } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function Admin() {
    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // New Rule Form State
    const [showAddForm, setShowAddForm] = useState(false);
    const [newRule, setNewRule] = useState({
        category: '',
        weight: 0.1,
        keywords: '',
        explanation: '',
        is_regex: false
    });

    useEffect(() => {
        fetchRules();
    }, []);

    const fetchRules = async () => {
        try {
            const res = await axios.get(`${API_URL}/admin/rules`);
            setRules(res.data);
            setError('');
        } catch (err) {
            setError('Failed to load rules.');
        } finally {
            setLoading(false);
        }
    };

    const toggleRule = async (id) => {
        try {
            await axios.put(`${API_URL}/admin/rules/${id}`);
            fetchRules(); // Refresh list
        } catch (err) {
            alert('Failed to toggle rule.');
        }
    };

    const deleteRule = async (id) => {
        if (!window.confirm('Are you sure you want to delete this rule?')) return;
        try {
            await axios.delete(`${API_URL}/admin/rules/${id}`);
            fetchRules();
        } catch (err) {
            alert('Failed to delete rule.');
        }
    };

    const handleAddRule = async (e) => {
        e.preventDefault();
        if (!newRule.category || !newRule.keywords || !newRule.explanation) {
            alert('Please fill out all fields');
            return;
        }

        try {
            const formattedRule = {
                ...newRule,
                weight: parseFloat(newRule.weight),
                keywords: newRule.keywords.split(',').map(k => k.trim())
            };

            await axios.post(`${API_URL}/admin/rules`, formattedRule);
            setShowAddForm(false);
            setNewRule({ category: '', weight: 0.1, keywords: '', explanation: '', is_regex: false });
            fetchRules();
        } catch (err) {
            alert('Failed to add rule.');
        }
    };

    const handleExport = () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(rules, null, 4));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "rules_export.json");
        document.body.appendChild(downloadAnchorNode); // required for firefox
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    const totalActiveWeight = rules
        .filter(r => r.enabled)
        .reduce((sum, r) => sum + r.weight, 0)
        .toFixed(2);

    if (loading) return <div className="p-8 text-center text-slate-500 animate-pulse">Loading config...</div>;

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in">

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pt-8">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
                        <Settings className="w-8 h-8 text-slate-700" />
                        Detection Engine Configuration
                    </h1>
                    <p className="text-slate-600 mt-1">Manage heuristic rules and keyword triggers.</p>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                    <button
                        onClick={handleExport}
                        className="px-4 py-2 bg-white text-slate-700 border border-slate-300 rounded-lg flex items-center justify-center gap-2 hover:bg-slate-50 transition-colors shadow-sm font-medium"
                    >
                        <Download className="w-4 h-4" />
                        Export JSON
                    </button>
                    <button
                        onClick={() => setShowAddForm(!showAddForm)}
                        className="px-4 py-2 bg-brand-navy text-white rounded-lg flex items-center justify-center gap-2 hover:bg-slate-800 transition-colors shadow-sm font-medium"
                    >
                        <Plus className="w-4 h-4" />
                        {showAddForm ? 'Cancel Form' : 'Add New Rule'}
                    </button>
                </div>
            </div>

            {/* Metrics Bar */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-center justify-between shadow-inner">
                <div className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
                    Total Active Rule Weight
                </div>
                <div className="text-xl font-black text-slate-800">
                    {totalActiveWeight}
                </div>
            </div>

            {error && <div className="p-4 bg-red-50 text-red-600 rounded-lg">{error}</div>}

            {/* Add New Rule Form */}
            {showAddForm && (
                <div className="bg-white border text-left border-slate-200 rounded-xl shadow-sm p-6 bg-slate-50/10">
                    <h2 className="text-xl font-bold text-slate-800 mb-4">Create New Rule</h2>
                    <form onSubmit={handleAddRule} className="grid md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Category Name</label>
                            <input
                                type="text"
                                required
                                placeholder="e.g. Tax Scam"
                                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-brand-navy focus:ring-1 focus:ring-brand-navy outline-none"
                                value={newRule.category}
                                onChange={e => setNewRule({ ...newRule, category: e.target.value })}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Trigger Weight (0.0 to 1.0)</label>
                            <input
                                type="number"
                                step="0.05"
                                min="0"
                                max="1"
                                required
                                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-brand-navy focus:ring-1 focus:ring-brand-navy outline-none"
                                value={newRule.weight}
                                onChange={e => setNewRule({ ...newRule, weight: e.target.value })}
                            />
                        </div>

                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-slate-700 mb-1">Keywords (comma separated)</label>
                            <input
                                type="text"
                                required
                                placeholder="e.g. irs, tax refund, arrest"
                                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-brand-navy focus:ring-1 focus:ring-brand-navy outline-none"
                                value={newRule.keywords}
                                onChange={e => setNewRule({ ...newRule, keywords: e.target.value })}
                            />
                        </div>

                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-slate-700 mb-1">Explanation to User</label>
                            <textarea
                                required
                                rows={2}
                                placeholder="Reason to show user when this rule is triggered..."
                                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-brand-navy focus:ring-1 focus:ring-brand-navy outline-none resize-none"
                                value={newRule.explanation}
                                onChange={e => setNewRule({ ...newRule, explanation: e.target.value })}
                            />
                        </div>

                        <div className="md:col-span-2 flex items-center gap-2">
                            <input
                                type="checkbox"
                                id="is_regex"
                                className="w-4 h-4 text-brand-navy rounded border-slate-300 focus:ring-brand-navy"
                                checked={newRule.is_regex}
                                onChange={e => setNewRule({ ...newRule, is_regex: e.target.checked })}
                            />
                            <label htmlFor="is_regex" className="text-sm font-medium text-slate-700">
                                Use Advanced Regex Pattern Matching (Keywords are evaluated as Regular Expressions)
                            </label>
                        </div>

                        <div className="md:col-span-2 flex justify-end mt-2">
                            <button
                                type="submit"
                                className="px-6 py-2 bg-brand-navy text-white font-medium rounded-lg hover:bg-slate-800 shadow-sm"
                            >
                                Save Rule
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Rules List */}
            <div className="grid gap-4">
                {rules.map((rule) => (
                    <div
                        key={rule.id}
                        className={`bg-white border rounded-xl p-5 shadow-sm transition-opacity ${!rule.enabled ? 'opacity-60 grayscale-[50%]' : 'border-slate-200'}`}
                    >
                        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">

                            <div className="flex-1 space-y-2">
                                <div className="flex items-center gap-3">
                                    <h3 className="text-lg font-bold text-slate-900">{rule.category}</h3>
                                    <span className="px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-bold border border-slate-200">
                                        Weight: {rule.weight}
                                    </span>
                                    {!rule.enabled && (
                                        <span className="px-2.5 py-0.5 rounded-full bg-red-100 text-red-700 text-xs font-bold border border-red-200">
                                            Disabled
                                        </span>
                                    )}
                                    {rule.is_regex && (
                                        <span className="px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-700 text-xs font-bold border border-purple-200">
                                            Regex Mode
                                        </span>
                                    )}
                                </div>

                                <p className="text-sm text-slate-600 flex items-start gap-2">
                                    <BookOpen className="w-4 h-4 shrink-0 mt-0.5" />
                                    {rule.explanation}
                                </p>

                                <div className="flex flex-wrap gap-1.5 pt-2">
                                    {rule.keywords.map((kw, idx) => (
                                        <span key={idx} className="bg-slate-100 text-slate-700 text-xs px-2 py-1 rounded border border-slate-200 font-medium">
                                            {kw}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="flex items-center gap-2 md:pl-4 md:border-l border-slate-100 shrink-0">
                                <button
                                    onClick={() => toggleRule(rule.id)}
                                    title={rule.enabled ? "Disable Rule" : "Enable Rule"}
                                    className={`p-2 rounded-lg transition-colors ${rule.enabled ? 'text-green-600 hover:bg-green-50' : 'text-slate-400 hover:bg-slate-100'}`}
                                >
                                    <Power className="w-5 h-5" />
                                </button>
                                <button
                                    onClick={() => deleteRule(rule.id)}
                                    title="Delete Rule"
                                    className="p-2 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
                                >
                                    <Trash2 className="w-5 h-5" />
                                </button>
                            </div>

                        </div>
                    </div>
                ))}
                {rules.length === 0 && (
                    <div className="text-center py-12 bg-slate-50 rounded-2xl border border-dashed border-slate-300 text-slate-500">
                        No rules configured. Add a new rule to begin.
                    </div>
                )}
            </div>

        </div>
    );
}

export default Admin;
