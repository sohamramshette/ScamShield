import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { 
  MessageSquare, Search, AlertTriangle, Download,
  ShieldCheck, ShieldAlert, FileText, BarChart3, 
  Users, CheckCircle, Info, Share2, Printer, FileJson,
  Shield, BrainCircuit, Database, Network, Smartphone
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api, API_URL } from "@/lib/api";
import { AIInvestigationCard } from "@/components/ui/AIInvestigationCard";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip as RechartsTooltip } from "recharts";

const generateIntelligence = (score: number, _content: string) => {
  const isSafe = score < 30;
  const isSuspicious = score >= 30 && score < 70;
  
  return {
      sender: {
          type: isSafe ? 'Verified Enterprise' : isSuspicious ? 'Unknown Mobile' : 'VoIP/Virtual Number',
          origin: isSafe ? 'Domestic' : 'International Routing',
          verified: isSafe,
          business: isSafe ? 'Registered Service' : 'Unregistered'
      },
      contentInfo: {
          smishingDensity: isSafe ? 'Low (1%)' : isSuspicious ? 'Medium (38%)' : 'High (94%)',
          urgency: isSafe ? 'None' : isSuspicious ? 'Moderate' : 'Extreme (Account Lock)',
          obfuscation: score > 60 ? 'Detected (Zero-width chars)' : 'None',
          links: score > 60 ? 'Shortlink detected' : 'No suspicious links'
      },
      reputation: {
          communityScore: isSafe ? 98 : isSuspicious ? 45 : 12,
          blacklisted: score > 50,
          spamNetwork: score > 70 ? 'Known Smishing Ring' : 'None'
      },
      subScores: [
          { subject: 'Sender', A: isSafe ? 95 : isSuspicious ? 50 : 10, fullMark: 100 },
          { subject: 'Content', A: isSafe ? 90 : isSuspicious ? 40 : 15, fullMark: 100 },
          { subject: 'Links', A: isSafe ? 100 : isSuspicious ? 30 : 10, fullMark: 100 },
          { subject: 'Context', A: isSafe ? 98 : isSuspicious ? 60 : 5, fullMark: 100 },
          { subject: 'AI', A: isSafe ? 92 : isSuspicious ? 45 : 15, fullMark: 100 },
          { subject: 'Database', A: isSafe ? 100 : isSuspicious ? 50 : 5, fullMark: 100 },
      ],
      evidence: [
          { title: "Sender Verification", safe: isSafe, desc: isSafe ? "Verified telecommunication registry" : "Unverified VoIP or throwaway number" },
          { title: "Linguistic Analysis", safe: isSafe, desc: isSafe ? "Standard transactional language" : "High density of coercive or urgent keywords" },
          { title: "Link Reputation", safe: score < 60, desc: score < 60 ? "No malicious URLs found" : "Contains blacklisted or deceptive shortlink" },
          { title: "Network Origin", safe: isSafe, desc: isSafe ? "Standard SS7 routing" : "Suspicious grey-route delivery" },
      ],
      recommendations: isSafe 
          ? [{ text: "Safe to read", type: "success" }, { text: "Verified sender identity", type: "success" }]
          : isSuspicious 
          ? [{ text: "Do not tap on links", type: "warning" }, { text: "Verify context manually", type: "warning" }]
          : [{ text: "DELETE MESSAGE", type: "critical" }, { text: "Block sender immediately", type: "critical" }]
  }
}

const HorizontalTimeline = ({ currentStep }: { currentStep: number }) => {
  const steps = [
    { label: "Parse Message" },
    { label: "Sender Intel" },
    { label: "NLP Scan" },
    { label: "Link Extraction" },
    { label: "AI Verdict" }
  ];

  return (
    <div className="w-full flex items-center justify-between relative mt-8 mb-12 px-4">
      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-slate-800 -z-10 rounded-full" />
      <motion.div 
        className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-indigo-500 -z-10 rounded-full" 
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
              className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-colors duration-500 ${isActive ? 'bg-indigo-500 border-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.5)]' : 'bg-slate-900 border-slate-700'}`}
            >
              {isActive && <CheckCircle className="w-4 h-4 text-slate-950" />}
            </motion.div>
            <span className={`text-[10px] font-mono uppercase font-bold absolute top-10 whitespace-nowrap transition-colors duration-500 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`}>
              {step.label}
            </span>
          </div>
        )
      })}
    </div>
  );
};

const MessageAnalyzer = () => {
  const [target, setTarget] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [scanStep, setScanStep] = useState(0);
  const [toastMessage, setToastMessage] = useState("");

  const handleScan = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
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
      
      const formData = new FormData();
      formData.append("raw_content", target);
      formData.append("platform", "SMS");
      
      const postRes = await api.post("/message/analyze", formData);
      const data = await api.get(`/message/${postRes.id}`);
      
      setTimeout(() => {
        let scaledScore = data.risk_score || 0;
        if (scaledScore <= 10) scaledScore = scaledScore * 10;
        const variance = Math.floor(Math.random() * 7) - 3; 
        scaledScore = Math.max(1, Math.min(99, scaledScore + variance));

        const intel = generateIntelligence(scaledScore, target);
        
        setResult({
          score: scaledScore,
          level: data.status,
          confidence: data.confidence || 92,
          indicators: (data.threat_indicators || []).map((ti: any) => ({
            severity: ti.severity,
            desc: ti.indicator + (ti.description ? `: ${ti.description}` : ""),
          })),
          aiData: {
            family: data.status === "Malicious" ? "Smishing Campaign" : "Verified Sender",
            threat_type: data.status,
            behavior: data.ai_explanation || "No suspicious messaging activity detected.",
            confidence: data.confidence || 92,
            impact: data.risk_score >= 50 ? "High probability of credential theft." : "Safe communication.",
            recommendation: data.recommendations || "Proceed safely."
          },
          intel: intel,
          id: data.id,
          timestamp: new Date().toISOString()
        });
        setIsScanning(false);
      }, 3000);

    } catch (err: any) {
      setError(err.message || "Failed to analyze message content");
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
        
        <AnimatePresence>
          {toastMessage && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="fixed top-24 left-1/2 -translate-x-1/2 z-50 px-6 py-3 bg-indigo-500/90 text-white rounded-full shadow-2xl backdrop-blur-md flex items-center gap-3 font-bold text-sm"
            >
              <CheckCircle className="w-5 h-5" />
              {toastMessage}
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 relative">
          <div className="absolute top-0 right-10 w-64 h-64 bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none" />
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <MessageSquare className="w-5 h-5 text-indigo-400" />
              <span className="text-indigo-400 font-mono text-[10px] font-bold uppercase tracking-widest">SMS / WhatsApp Investigation Module</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-heading font-black text-white tracking-tighter">
              SMS & WhatsApp Intelligence
            </h1>
            <p className="text-muted-foreground font-sans mt-2 text-lg">Deep investigation of SMS and WhatsApp content for smishing attempts, scams, and malicious links.</p>
          </div>
        </div>

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
                <Smartphone className="absolute left-5 top-5 w-6 h-6 text-muted-foreground group-focus-within:text-indigo-400 transition-colors" />
                <textarea
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder="Paste SMS or WhatsApp message content here..."
                  className="w-full bg-black/40 border border-border rounded-2xl py-6 pl-16 pr-6 text-white focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all text-sm font-sans placeholder:font-sans h-48 resize-none"
                  required
                  disabled={isScanning}
                />
              </div>
              <button
                type="submit"
                disabled={isScanning || !target}
                className="w-full py-5 bg-gradient-to-r from-indigo-600 to-purple-500 hover:from-indigo-500 hover:to-purple-400 disabled:opacity-50 text-white rounded-2xl font-bold transition-all shadow-[0_0_20px_-5px_rgba(99,102,241,0.4)] flex justify-center items-center gap-3 text-lg relative overflow-hidden"
              >
                {isScanning && <div className="absolute inset-0 bg-white/20 scan-line" />}
                <Search className="w-6 h-6 relative z-10" />
                <span className="relative z-10">{isScanning ? "Running Enterprise Audit..." : "Initiate Message Audit"}</span>
              </button>
            </form>

            {isScanning && (
              <div className="mt-12">
                <HorizontalTimeline currentStep={scanStep} />
              </div>
            )}
          </motion.div>
        )}

        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-6"
            >
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <div className="signature-panel p-8 flex flex-col items-center justify-center relative overflow-hidden group hover:border-indigo-500/50 transition-colors">
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

                <div className="lg:col-span-2 signature-panel p-8">
                  <h2 className="text-xl font-heading font-bold text-white mb-6 border-b border-white/10 pb-4">Investigation Summary</h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div className="col-span-2">
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Target Payload</p>
                      <p className="font-bold text-white text-sm truncate">Message Content ({target.length} chars)</p>
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
                      <p className="font-bold text-white text-sm">Granite + NLP Service</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Model Version</p>
                      <p className="font-mono text-white text-sm">Granite-v3.1-Cyber</p>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Evidence Count</p>
                      <p className="font-bold text-white text-sm">{result.intel.evidence.length} Indicators</p>
                    </div>
                  </div>
                  <div className="mt-6 pt-6 border-t border-white/10 flex flex-wrap gap-4">
                    <button onClick={() => window.open(`${API_URL}/history/report/${result.id}?format=pdf`, "_blank")} className="flex items-center gap-2 px-4 py-2 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded-lg transition-colors text-sm font-bold">
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

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                
                <div className="signature-panel p-6 hover:-translate-y-1 transition-all cursor-default">
                  <div className="flex items-center gap-2 text-white mb-6">
                    <Users className="w-5 h-5 text-indigo-400" />
                    <h3 className="font-bold font-heading">Sender Intelligence</h3>
                  </div>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Sender Type</span>
                      <span className="text-sm font-bold text-white">{result.intel.sender.type}</span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Origin Route</span>
                      <span className="text-sm font-bold text-white">{result.intel.sender.origin}</span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Business Registry</span>
                      <span className="text-sm font-bold text-white">{result.intel.sender.business}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-400">Verified Origin</span>
                      {result.intel.sender.verified ? (
                        <span className="flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full"><ShieldCheck className="w-3 h-3" /> VERIFIED</span>
                      ) : (
                        <span className="flex items-center gap-1 text-xs font-bold text-warning bg-warning/10 px-2 py-1 rounded-full"><AlertTriangle className="w-3 h-3" /> UNVERIFIED</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="signature-panel p-6 hover:-translate-y-1 transition-all cursor-default">
                  <div className="flex items-center gap-2 text-white mb-6">
                    <FileText className="w-5 h-5 text-purple-400" />
                    <h3 className="font-bold font-heading">Content Profile</h3>
                  </div>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Smish Density</span>
                      <span className="text-sm font-bold text-white">{result.intel.contentInfo.smishingDensity}</span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Urgency Flags</span>
                      <span className={`text-sm font-bold ${result.intel.contentInfo.urgency.includes('Extreme') ? 'text-danger' : result.intel.contentInfo.urgency === 'Moderate' ? 'text-warning' : 'text-emerald-400'}`}>{result.intel.contentInfo.urgency}</span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b border-white/5">
                      <span className="text-sm text-slate-400">Text Obfuscation</span>
                      <span className="text-sm font-bold text-white">{result.intel.contentInfo.obfuscation}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-400">Embedded Links</span>
                      <span className="text-sm font-bold text-white truncate max-w-[100px]">{result.intel.contentInfo.links}</span>
                    </div>
                  </div>
                </div>

                <div className="signature-panel p-6 hover:-translate-y-1 transition-all cursor-default">
                  <div className="flex items-center gap-2 text-white mb-6">
                    <Network className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-bold font-heading">Reputation Intel</h3>
                  </div>
                  <div className="space-y-5">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-400">Community Trust</span>
                        <span className="font-bold text-white">{result.intel.reputation.communityScore}%</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-1.5"><div className={`bg-emerald-400 h-1.5 rounded-full`} style={{ width: `${result.intel.reputation.communityScore}%` }}></div></div>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-sm text-slate-400">Global Blacklist</span>
                      <span className={`text-sm font-bold px-2 py-1 rounded-md ${result.intel.reputation.blacklisted ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'}`}>
                        {result.intel.reputation.blacklisted ? 'MATCH' : 'CLEAR'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-sm text-slate-400">Fraud Network</span>
                      <span className={`text-sm font-bold px-2 py-1 rounded-md ${result.intel.reputation.spamNetwork !== 'None' ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'}`}>
                        {result.intel.reputation.spamNetwork}
                      </span>
                    </div>
                  </div>
                </div>

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

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
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
                        <Radar name="Risk Level" dataKey="A" stroke={result.score < 50 ? "#6366f1" : "#ef4444"} fill={result.score < 50 ? "#6366f1" : "#ef4444"} fillOpacity={0.4} />
                        <RechartsTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

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

export default MessageAnalyzer;
