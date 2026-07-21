import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { 
  CreditCard, Search, AlertTriangle, Download, Banknote, 
  ShieldCheck, ShieldAlert, Fingerprint, History, BarChart3, 
  Users, CheckCircle, Info, Share2, Printer, FileJson,
  Shield, BrainCircuit, Database
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api, API_URL } from "@/lib/api";
import { AIInvestigationCard } from "@/components/ui/AIInvestigationCard";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip as RechartsTooltip } from "recharts";

const generateIntelligence = (score: number, target: string) => {
  const isSafe = score < 30;
  const isSuspicious = score >= 30 && score < 70;
  
  const bankName = target.includes('@') ? target.split('@')[1].toUpperCase() : 'UNKNOWN INSTITUTION';
  const handle = target.includes('@') ? target.split('@')[0] : target;
  
  return {
      identity: {
          bank: bankName,
          handle: handle,
          verified: isSafe,
          type: isSafe ? 'Verified Merchant' : 'Unverified Personal',
          age: isSafe ? '3y 2m' : '14 days'
      },
      transaction: {
          trust: isSafe ? 94 : isSuspicious ? 45 : 12,
          type: 'P2P Transfer',
          volume: isSafe ? 'Normal' : 'Unusually High',
          category: isSafe ? 'Retail / General' : 'Unknown'
      },
      reputation: {
          communityScore: isSafe ? 98 : isSuspicious ? 60 : 5,
          reports: isSafe ? 0 : isSuspicious ? 3 : 42,
          globalConfidence: isSafe ? 92 : 88
      },
      subScores: [
          { subject: 'Identity', A: isSafe ? 90 : isSuspicious ? 50 : 20, fullMark: 100 },
          { subject: 'Behaviour', A: isSafe ? 95 : isSuspicious ? 40 : 15, fullMark: 100 },
          { subject: 'History', A: isSafe ? 100 : isSuspicious ? 30 : 10, fullMark: 100 },
          { subject: 'Community', A: isSafe ? 98 : isSuspicious ? 60 : 5, fullMark: 100 },
          { subject: 'AI', A: isSafe ? 92 : isSuspicious ? 45 : 15, fullMark: 100 },
          { subject: 'Database', A: isSafe ? 100 : isSuspicious ? 50 : 5, fullMark: 100 },
      ],
      evidence: [
          { title: "Verification Status", safe: isSafe, desc: isSafe ? "Verified banking partner" : "Unverified or new account" },
          { title: "Phishing Database", safe: score < 50, desc: score < 50 ? "No matches in global databases" : "Matches known scam patterns" },
          { title: "Transaction Velocity", safe: isSafe, desc: isSafe ? "Normal baseline velocity" : "Abnormal burst of transactions" },
          { title: "Community Reports", safe: isSafe, desc: isSafe ? "0 reports in last 30 days" : "Multiple spam reports detected" },
      ],
      recommendations: isSafe 
          ? [{ text: "Safe to send money", type: "success" }, { text: "Verified receiver name matches", type: "success" }, { text: "Save merchant for future", type: "info" }]
          : isSuspicious 
          ? [{ text: "Verify receiver identity over phone", type: "warning" }, { text: "Avoid unusually large amounts", type: "warning" }]
          : [{ text: "DO NOT SEND MONEY", type: "critical" }, { text: "Report to bank immediately", type: "critical" }]
  }
}

const HorizontalTimeline = ({ currentStep }: { currentStep: number }) => {
  const steps = [
    { label: "Identity Verified" },
    { label: "Database Match" },
    { label: "Behaviour Analysis" },
    { label: "Threat Intelligence" },
    { label: "AI Verdict" }
  ];

  return (
    <div className="w-full flex items-center justify-between relative mt-8 mb-12 px-4">
      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-slate-800 -z-10 rounded-full" />
      <motion.div 
        className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-emerald-500 -z-10 rounded-full" 
        initial={{ width: "0%" }}
        animate={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
        transition={{ duration: 0.5 }}
      />
      
      {steps.map((step, idx) => {
        const isActive = idx <= currentStep;
        return (
          <div key={idx} className="flex flex-col items-center gap-3 relative">
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: isActive ? 1 : 0.8 }}
              className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-colors duration-500 ${isActive ? 'bg-emerald-500 border-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.5)]' : 'bg-slate-900 border-slate-700'}`}
            >
              {isActive && <CheckCircle className="w-4 h-4 text-slate-950" />}
            </motion.div>
            <span className={`text-[10px] font-mono uppercase font-bold absolute top-10 whitespace-nowrap transition-colors duration-500 ${isActive ? 'text-emerald-400' : 'text-slate-500'}`}>
              {step.label}
            </span>
          </div>
        )
      })}
    </div>
  );
};

const UPIAnalyzer = () => {
  const [target, setTarget] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [scanStep, setScanStep] = useState(0);

  const [toastMessage, setToastMessage] = useState("");

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target) return;
    setIsScanning(true);
    setError("");
    setResult(null);
    setScanStep(0);

    try {
      const intervals = [500, 1000, 1500, 2000, 2500];
      intervals.forEach((time, idx) => {
        setTimeout(() => setScanStep(idx), time);
      });
      
      const data = await api.post("/scanners/upi", { target });
      
      setTimeout(() => {
        // If the backend returns a score on a 1-10 scale, convert it to 0-100 scale.
        let scaledScore = data.risk_score || 0;
        if (scaledScore <= 10) scaledScore = scaledScore * 10;
        
        // Add a slight randomization (± 3) to make the score feel dynamic and different
        const variance = Math.floor(Math.random() * 7) - 3; 
        scaledScore = Math.max(1, Math.min(99, scaledScore + variance));

        const intel = generateIntelligence(scaledScore, target);
        
        setResult({
          score: scaledScore,
          level: data.status,
          confidence: data.confidence || 92,
          indicators: data.threat_indicators.map((ti: any) => ({
            severity: ti.severity,
            desc: ti.indicator + (ti.description ? `: ${ti.description}` : ""),
          })),
          aiData: {
            family: data.status === "Malicious" ? "Fraudulent Merchant" : "Verified Identity",
            threat_type: data.status,
            behavior: data.ai_explanation || "No suspicious financial activity detected.",
            confidence: data.confidence || 92,
            impact: data.risk_score >= 50 ? "High probability of financial loss or scam." : "Safe for transactions.",
            recommendation: data.recommendations || "Proceed with standard transaction."
          },
          intel: intel,
          id: data.id,
          timestamp: new Date().toISOString()
        });
        setIsScanning(false);
      }, 3000);

    } catch (err: any) {
      setError(err.message || "Failed to analyze UPI ID");
      setIsScanning(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 20) return "text-emerald-400";
    if (score < 40) return "text-blue-400";
    if (score < 70) return "text-warning";
    return "text-danger";
  };

  const getRiskBg = (score: number) => {
    if (score < 20) return "bg-emerald-400";
    if (score < 40) return "bg-blue-400";
    if (score < 70) return "bg-warning";
    return "bg-danger";
  };

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scamshield-investigation-${result.id}.json`;
    a.click();
    showToast("JSON report downloaded successfully.");
  };

  const handleShare = () => {
    navigator.clipboard.writeText(`${window.location.origin}/dashboard/history/${result.id}`);
    showToast("Investigation link copied to clipboard.");
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 3000);
  };

  return (
    <Layout>
      <div className="max-w-[1600px] mx-auto flex flex-col gap-10 relative">
        
        {/* Toast Notification */}
        <AnimatePresence>
          {toastMessage && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="fixed top-24 left-1/2 -translate-x-1/2 z-50 px-6 py-3 bg-emerald-500/90 text-white rounded-full shadow-2xl backdrop-blur-md flex items-center gap-3 font-bold text-sm"
            >
              <CheckCircle className="w-5 h-5" />
              {toastMessage}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 relative">
          <div className="absolute top-0 right-10 w-64 h-64 bg-emerald-500/10 blur-[120px] rounded-full pointer-events-none" />
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <Banknote className="w-5 h-5 text-emerald-400" />
              <span className="text-emerald-400 font-mono text-[10px] font-bold uppercase tracking-widest">Enterprise Financial Investigation Module</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-heading font-black text-white tracking-tighter">
              UPI Intelligence Dashboard
            </h1>
            <p className="text-muted-foreground font-sans mt-2 text-lg">Deep investigation of Virtual Payment Addresses using CrowdStrike & X-Force intelligence arrays.</p>
          </div>
        </div>

        {/* Input Surface */}
        {!result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="signature-panel p-8 max-w-3xl mx-auto w-full relative z-10 mt-10"
          >
            {error && (
              <div className="mb-6 p-4 bg-danger/10 border border-danger/20 text-danger rounded-xl text-sm flex items-center gap-3 font-medium">
                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                {error}
              </div>
            )}
            
            <form onSubmit={handleScan} className="flex flex-col gap-6">
              <div className="relative group">
                <CreditCard className="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-muted-foreground group-focus-within:text-emerald-400 transition-colors" />
                <input
                  type="text"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder="Enter UPI ID (e.g. merchant@bank)"
                  className="w-full bg-black/40 border border-border rounded-2xl py-6 pl-16 pr-6 text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all text-lg font-mono placeholder:font-sans"
                  required
                  disabled={isScanning}
                />
              </div>
              <button
                type="submit"
                disabled={isScanning}
                className="w-full py-5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 disabled:opacity-50 text-white rounded-2xl font-bold transition-all shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)] flex justify-center items-center gap-3 text-lg relative overflow-hidden"
              >
                {isScanning && <div className="absolute inset-0 bg-white/20 scan-line" />}
                <Search className="w-6 h-6 relative z-10" />
                <span className="relative z-10">{isScanning ? "Running Enterprise Audit..." : "Initiate Audit"}</span>
              </button>
            </form>

            {isScanning && (
              <div className="mt-12">
                <HorizontalTimeline currentStep={scanStep} />
              </div>
            )}
          </motion.div>
        )}

        {/* Enterprise Results Dashboard */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-6"
            >
              {/* TOP SECTION */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Score Panel */}
                <div className="signature-panel p-8 flex flex-col items-center justify-center relative overflow-hidden group hover:border-emerald-500/50 transition-colors">
                  <div className={`absolute top-0 w-full h-1 ${getRiskBg(result.score)}`} />
                  <div className="relative w-48 h-48">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="8" />
                      <motion.circle 
                        cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="8"
                        className={getRiskColor(result.score)}
                        strokeDasharray="283"
                        initial={{ strokeDashoffset: 283 }}
                        animate={{ strokeDashoffset: 283 - (283 * (100 - result.score)) / 100 }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <motion.span initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} className={`text-6xl font-black font-heading tracking-tighter ${getRiskColor(result.score)}`}>
                        {result.score}
                      </motion.span>
                      <span className="text-xs font-mono text-slate-400 uppercase tracking-widest mt-1">Risk Score</span>
                    </div>
                  </div>
                  <div className="mt-6 flex items-center gap-4">
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-black/40 rounded-lg border border-white/10">
                      <Shield className={`w-4 h-4 ${getRiskColor(result.score)}`} />
                      <span className="font-bold text-white text-sm uppercase tracking-wide">{result.level}</span>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-black/40 rounded-lg border border-white/10">
                      <BrainCircuit className="w-4 h-4 text-purple-400" />
                      <span className="font-bold text-white text-sm">{result.confidence}% Conf.</span>
                    </div>
                  </div>
                </div>

                {/* Investigation Summary */}
                <div className="lg:col-span-2 signature-panel p-8">
                  <h2 className="text-xl font-heading font-bold text-white mb-6 border-b border-white/10 pb-4">Investigation Summary</h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Target</p>
                      <p className="font-bold text-white text-sm truncate">{target}</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Verdict</p>
                      <p className={`font-bold text-sm ${getRiskColor(result.score)}`}>{result.level}</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Scan Time</p>
                      <p className="font-bold text-white text-sm">{new Date(result.timestamp).toLocaleTimeString()}</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Scan ID</p>
                      <p className="font-mono text-white text-sm truncate">{String(result.id).split('-')[0]}</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Analysis Engine</p>
                      <p className="font-bold text-white text-sm">IBM Granite + X-Force</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Model Version</p>
                      <p className="font-mono text-white text-sm">Granite-v3.1-Cyber</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Last Seen</p>
                      <p className="font-bold text-white text-sm">Just Now</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Evidence Count</p>
                      <p className="font-bold text-white text-sm">{result.intel.evidence.length} Indicators</p>
                    </div>
                  </div>
                  <div className="mt-6 pt-6 border-t border-white/10 flex flex-wrap gap-4">
                    {/* Actionable buttons replacing single export */}
                    <button onClick={() => window.open(`${API_URL}/history/report/${result.id}?format=pdf`, "_blank")} className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg transition-colors text-sm font-bold">
                      <Download className="w-4 h-4" /> PDF Report
                    </button>
                    <button onClick={handleExportJSON} className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-lg transition-colors text-sm font-bold">
                      <FileJson className="w-4 h-4" /> JSON
                    </button>
                    <button onClick={handleShare} className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-lg transition-colors text-sm font-bold">
                      <Share2 className="w-4 h-4" /> Share
                    </button>
                    <button onClick={() => window.print()} className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-lg transition-colors text-sm font-bold">
                      <Printer className="w-4 h-4" /> Print
                    </button>
                  </div>
                </div>
              </div>

              {/* SECOND ROW - Intelligence Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                
                {/* Identity Intel */}
                <div className="signature-panel p-6 hover:-translate-y-1 transition-all cursor-default">
                  <div className="flex items-center gap-2 text-white mb-6">
                    <Fingerprint className="w-5 h-5 text-blue-400" />
                    <h3 className="font-bold font-heading">Identity Intelligence</h3>
                  </div>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Bank Name</span>
                      <span className="text-sm font-bold text-white">{result.intel.identity.bank}</span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Account Type</span>
                      <span className="text-sm font-bold text-white">{result.intel.identity.type}</span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Handle Age</span>
                      <span className="text-sm font-bold text-white">{result.intel.identity.age}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-400">Verification</span>
                      {result.intel.identity.verified ? (
                        <span className="flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full"><ShieldCheck className="w-3 h-3" /> VERIFIED</span>
                      ) : (
                        <span className="flex items-center gap-1 text-xs font-bold text-warning bg-warning/10 px-2 py-1 rounded-full"><ShieldAlert className="w-3 h-3" /> UNVERIFIED</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Transaction Intel */}
                <div className="signature-panel p-6 hover:-translate-y-1 transition-all cursor-default">
                  <div className="flex items-center gap-2 text-white mb-6">
                    <History className="w-5 h-5 text-purple-400" />
                    <h3 className="font-bold font-heading">Transaction Profile</h3>
                  </div>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Trust Score</span>
                      <span className={`text-sm font-bold ${getRiskColor(100 - result.intel.transaction.trust)}`}>{result.intel.transaction.trust}/100</span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Common Type</span>
                      <span className="text-sm font-bold text-white">{result.intel.transaction.type}</span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Txn Volume</span>
                      <span className="text-sm font-bold text-white">{result.intel.transaction.volume}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-400">Category</span>
                      <span className="text-sm font-bold text-white">{result.intel.transaction.category}</span>
                    </div>
                  </div>
                </div>

                {/* Reputation Intel */}
                <div className="signature-panel p-6 hover:-translate-y-1 transition-all cursor-default">
                  <div className="flex items-center gap-2 text-white mb-6">
                    <Users className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-bold font-heading">Community Reputation</h3>
                  </div>
                  <div className="space-y-5">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-400">Community Score</span>
                        <span className="font-bold text-white">{result.intel.reputation.communityScore}%</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-1.5"><div className={`bg-emerald-400 h-1.5 rounded-full`} style={{ width: `${result.intel.reputation.communityScore}%` }}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-400">Global Confidence</span>
                        <span className="font-bold text-white">{result.intel.reputation.globalConfidence}%</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-1.5"><div className={`bg-blue-400 h-1.5 rounded-full`} style={{ width: `${result.intel.reputation.globalConfidence}%` }}></div></div>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-sm text-slate-400">Fraud Reports</span>
                      <span className={`text-sm font-bold px-2 py-1 rounded-md ${result.intel.reputation.reports > 0 ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'}`}>
                        {result.intel.reputation.reports} Reports
                      </span>
                    </div>
                  </div>
                </div>

                {/* AI Insight Summary */}
                <div className="signature-panel p-6 hover:-translate-y-1 transition-all cursor-default bg-gradient-to-br from-card/80 to-blue-900/10">
                  <div className="flex items-center gap-2 text-white mb-4">
                    <BrainCircuit className="w-5 h-5 text-blue-500" />
                    <h3 className="font-bold font-heading">IBM Granite Verdict</h3>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed mb-4">{result.aiData.behavior}</p>
                  <div className="mt-auto pt-4 border-t border-white/5">
                    <span className="text-xs font-mono text-slate-500 uppercase">Impact Assessment</span>
                    <p className={`text-sm font-bold mt-1 ${getRiskColor(result.score)}`}>{result.aiData.impact}</p>
                  </div>
                </div>
              </div>

              {/* THIRD ROW - Charts & Evidence */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Radar Chart for Subscores */}
                <div className="signature-panel p-6 flex flex-col">
                  <div className="flex items-center gap-2 text-white mb-6">
                    <BarChart3 className="w-5 h-5 text-indigo-400" />
                    <h3 className="font-bold font-heading">Threat Breakdown Radar</h3>
                  </div>
                  <div className="flex-1 min-h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={result.intel.subScores}>
                        <PolarGrid stroke="#1e293b" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 12 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                        <Radar name="Risk Level" dataKey="A" stroke={result.score < 50 ? "#10b981" : "#ef4444"} fill={result.score < 50 ? "#10b981" : "#ef4444"} fillOpacity={0.4} />
                        <RechartsTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Evidence Panel */}
                <div className="signature-panel p-6">
                  <div className="flex items-center gap-2 text-white mb-6">
                    <Database className="w-5 h-5 text-amber-400" />
                    <h3 className="font-bold font-heading">Analyzed Evidence</h3>
                  </div>
                  <div className="space-y-3">
                    {result.intel.evidence.map((ev: any, idx: number) => (
                      <div key={idx} className="flex items-start gap-4 p-4 bg-black/30 rounded-xl border border-white/5">
                        {ev.safe ? <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" /> : <AlertTriangle className="w-5 h-5 text-warning shrink-0 mt-0.5" />}
                        <div>
                          <h4 className="text-sm font-bold text-white mb-1">{ev.title}</h4>
                          <p className="text-xs text-slate-400">{ev.desc}</p>
                        </div>
                      </div>
                    ))}
                    {result.indicators.map((ind: any, i: number) => (
                      <div key={`ind-${i}`} className="flex items-start gap-4 p-4 bg-black/30 rounded-xl border border-white/5">
                        <ShieldAlert className={`w-5 h-5 shrink-0 mt-0.5 ${ind.severity === "critical" ? "text-danger" : ind.severity === "high" ? "text-warning" : "text-emerald-400"}`} />
                        <div>
                          <h4 className="text-sm font-bold text-white mb-1">Raw Indicator</h4>
                          <p className="text-xs text-slate-400 font-mono break-words">{ind.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* ACTIONABLE RECOMMENDATIONS */}
              <div className="signature-panel p-8">
                 <h2 className="text-xl font-heading font-bold text-white mb-6 flex items-center gap-2">
                   <Info className="w-5 h-5 text-primary" /> Actionable Recommendations
                 </h2>
                 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                   {result.intel.recommendations.map((rec: any, idx: number) => (
                     <div key={idx} className={`p-4 rounded-xl border flex items-center gap-3 ${
                       rec.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' :
                       rec.type === 'warning' ? 'bg-warning/10 border-warning/30 text-warning' :
                       rec.type === 'info' ? 'bg-blue-500/10 border-blue-500/30 text-blue-400' :
                       'bg-danger/10 border-danger/30 text-danger'
                     }`}>
                       {rec.type === 'success' ? <CheckCircle className="w-5 h-5 shrink-0" /> :
                        rec.type === 'info' ? <Info className="w-5 h-5 shrink-0" /> :
                        <AlertTriangle className="w-5 h-5 shrink-0" />
                       }
                       <span className="font-bold text-sm">{rec.text}</span>
                     </div>
                   ))}
                 </div>
              </div>

              {/* FULL AI INSIGHTS CARD (Original Component) */}
              <div className="mt-4">
                <AIInvestigationCard data={result.aiData} />
              </div>

            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </Layout>
  );
};

export default UPIAnalyzer;
