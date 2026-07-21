import { useState } from "react";
import {
  Globe,
  Search,
  AlertTriangle,
  Download,
  TerminalSquare,
  Network
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Layout } from "@/components/layout/Layout";
import { api, API_URL } from "@/lib/api";
import { RiskMeter } from "@/components/ui/RiskMeter";
import { InvestigationTimeline } from "@/components/ui/InvestigationTimeline";
import type { TimelineStep } from "@/components/ui/InvestigationTimeline";
import { AIInvestigationCard } from "@/components/ui/AIInvestigationCard";

const WebsiteScanner = () => {
  const [url, setUrl] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [steps, setSteps] = useState<TimelineStep[]>([]);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setIsScanning(true);
    setError("");
    setResult(null);
    
    setSteps([
      { label: "Target Acquisition", status: "active" },
      { label: "DNS & Cert Analysis", status: "pending" },
      { label: "Threat Intel Sync", status: "pending" },
      { label: "Granite AI Inference", status: "pending" },
    ]);

    try {
      // Simulate stepped UI progression while waiting for the single API endpoint
      setTimeout(() => setSteps([
        { label: "Target Acquisition", status: "completed" },
        { label: "DNS & Cert Analysis", status: "active" },
        { label: "Threat Intel Sync", status: "pending" },
        { label: "Granite AI Inference", status: "pending" },
      ]), 800);

      setTimeout(() => setSteps([
        { label: "Target Acquisition", status: "completed" },
        { label: "DNS & Cert Analysis", status: "completed" },
        { label: "Threat Intel Sync", status: "active" },
        { label: "Granite AI Inference", status: "pending" },
      ]), 1600);
      
      const data = await api.post("/scanners/website", { target: url });
      
      setSteps([
        { label: "Target Acquisition", status: "completed" },
        { label: "DNS & Cert Analysis", status: "completed" },
        { label: "Threat Intel Sync", status: "completed" },
        { label: "Granite AI Inference", status: "active" },
      ]);
      
      setTimeout(() => {
        setSteps([
          { label: "Target Acquisition", status: "completed" },
          { label: "DNS & Cert Analysis", status: "completed" },
          { label: "Threat Intel Sync", status: "completed" },
          { label: "Granite AI Inference", status: "completed" },
        ]);
        
        setResult({
          score: data.risk_score || 0,
          level: data.status,
          confidence: data.confidence || 0,
          indicators: data.threat_indicators.map((ti: any) => ({
            severity: ti.severity,
            desc: ti.indicator + (ti.description ? `: ${ti.description}` : ""),
          })),
          aiData: {
            family: data.status === "Malicious" ? "Phishing/Malware Domain" : "Clean Domain",
            threat_type: data.status,
            behavior: data.ai_explanation || "No abnormal behavior detected.",
            confidence: data.confidence || 95,
            impact: data.risk_score >= 50 ? "High risk of credential theft or malware delivery." : "Safe to browse.",
            recommendation: data.recommendations || "Proceed with caution."
          },
          id: data.id,
        });
        setIsScanning(false);
      }, 800);

    } catch (err: any) {
      setError(err.message || "Failed to scan website");
      setIsScanning(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-[1400px] mx-auto flex flex-col gap-10">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 relative">
          <div className="absolute top-0 right-10 w-64 h-64 bg-primary/10 blur-[120px] rounded-full pointer-events-none" />
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <Network className="w-5 h-5 text-primary" />
              <span className="text-primary font-mono text-[10px] font-bold uppercase tracking-widest">Network Intelligence Module</span>
            </div>
            <h1 className="text-4xl font-heading font-black text-white tracking-tighter">
              Domain Reconnaissance
            </h1>
            <p className="text-muted-foreground font-sans mt-2 text-lg">Analyze URLs for phishing, malware, and infrastructure anomalies.</p>
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
                <Globe className="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter target URL (e.g. https://suspicious-domain.com)"
                  className="w-full bg-black/40 border border-border rounded-2xl py-6 pl-16 pr-6 text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all text-lg font-mono placeholder:font-sans"
                  required
                  disabled={isScanning}
                />
              </div>
              <button
                type="submit"
                disabled={isScanning}
                className="w-full py-5 bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 disabled:opacity-50 text-white rounded-2xl font-bold transition-all shadow-glow flex justify-center items-center gap-3 text-lg relative overflow-hidden"
              >
                {isScanning && <div className="absolute inset-0 bg-white/20 scan-line" />}
                <Search className="w-6 h-6 relative z-10" />
                <span className="relative z-10">{isScanning ? "Engaging Target..." : "Initiate Reconnaissance"}</span>
              </button>
            </form>
          </motion.div>
        )}

        {/* Scanning Timeline */}
        <AnimatePresence>
          {isScanning && steps.length > 0 && !result && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="max-w-4xl mx-auto w-full"
            >
              <InvestigationTimeline steps={steps} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Area */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-8"
            >
              {/* Left Column: Risk & Intel */}
              <div className="lg:col-span-4 flex flex-col gap-8">
                <div className="signature-panel flex flex-col items-center justify-center min-h-[300px]">
                  <RiskMeter score={result.score} />
                </div>
                
                <div className="signature-panel p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-sm font-mono font-bold text-white uppercase tracking-widest flex items-center gap-2">
                      <TerminalSquare className="w-4 h-4 text-secondary" /> Network IOCs
                    </h3>
                  </div>
                  <div className="space-y-3">
                    {result.indicators.length > 0 ? result.indicators.map((ind: any, i: number) => (
                      <div key={i} className="flex items-start gap-3 p-3 bg-black/30 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                        <AlertTriangle className={`w-4 h-4 mt-0.5 shrink-0 ${ind.severity === "critical" ? "text-danger" : ind.severity === "high" ? "text-warning" : "text-primary"}`} />
                        <span className="text-slate-300 font-mono text-xs break-words">{ind.desc}</span>
                      </div>
                    )) : (
                      <div className="p-4 bg-success/5 border border-success/20 rounded-xl flex items-center justify-center">
                        <span className="text-success text-xs font-mono font-bold uppercase tracking-widest">No Malicious IOCs Detected</span>
                      </div>
                    )}
                  </div>
                </div>

                <button 
                  onClick={() => window.open(`${API_URL}/history/report/${result.id}?format=pdf`, "_blank")}
                  className="w-full py-4 bg-card hover:bg-white/5 border border-border text-white rounded-xl flex items-center justify-center gap-3 transition-colors text-sm font-bold tracking-wide uppercase"
                >
                  <Download className="w-5 h-5 text-primary" /> Export Intelligence Brief
                </button>
              </div>

              {/* Right Column: AI Analysis */}
              <div className="lg:col-span-8 flex flex-col gap-8">
                <AIInvestigationCard data={result.aiData} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </Layout>
  );
};

export default WebsiteScanner;
