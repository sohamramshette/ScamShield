import { useState } from "react";
import {
  Globe,
  Search,
  ShieldAlert,
  AlertTriangle,
  FileText,
  Download,
} from "lucide-react";
import { motion } from "framer-motion";
import { Layout } from "@/components/layout/Layout";

import { api } from "@/lib/api";

const WebsiteScanner = () => {
  const [url, setUrl] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setIsScanning(true);
    setError("");
    setResult(null);

    try {
      const data = await api.post("/scanners/website", { target: url });
      setResult({
        score: data.risk_score || 0,
        level: data.status,
        confidence: data.confidence || 0,
        indicators: data.threat_indicators.map((ti: any) => ({
          severity: ti.severity,
          desc: ti.indicator + (ti.description ? `: ${ti.description}` : ""),
        })),
        explanation: data.ai_explanation || "No explanation provided.",
        recommendation: data.recommendations || "No recommendations.",
        id: data.id,
      });
    } catch (err: any) {
      setError(err.message || "Failed to scan website");
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
            Website Scanner
          </h1>
          <p className="text-slate-400">
            Analyze URLs for phishing, malware, and fraudulent activities.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl backdrop-blur-sm mb-8"
        >
          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm">
              {error}
            </div>
          )}
          <form onSubmit={handleScan} className="flex gap-4">
            <div className="relative flex-1">
              <Globe className="absolute left-4 top-4 w-5 h-5 text-slate-500" />
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full bg-slate-950/50 border border-slate-700 rounded-xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-lg"
                required
              />
            </div>
            <button
              type="submit"
              disabled={isScanning}
              className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-semibold transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)] flex items-center gap-2"
            >
              {isScanning ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
              {isScanning ? "Analyzing..." : "Scan URL"}
            </button>
          </form>
        </motion.div>

        {result && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {/* Score Card */}
            <div className="col-span-1 bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm flex flex-col items-center justify-center text-center">
              <div className="relative w-32 h-32 flex items-center justify-center mb-4">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="60"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    className="text-slate-800"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="60"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={377}
                    strokeDashoffset={377 - (377 * result.score) / 100}
                    className="text-red-500 transition-all duration-1000 ease-out"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold text-white">
                    {result.score}
                  </span>
                  <span className="text-xs text-slate-400 uppercase tracking-wider">
                    Score
                  </span>
                </div>
              </div>
              <h3 className="text-xl font-bold text-red-400 mb-1">
                {result.level}
              </h3>
              <p className="text-slate-400 text-sm">
                Confidence: {result.confidence}%
              </p>

              <button 
                onClick={async () => {
                  try {
                    const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"}/history/report/${result.id}`, {
                      headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
                    });
                    if (!response.ok) throw new Error("Failed");
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `ScamShield_Report_${result.id}.pdf`;
                    a.click();
                    window.URL.revokeObjectURL(url);
                  } catch (err) {
                    alert("Error downloading report");
                  }
                }}
                className="mt-6 w-full py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg flex items-center justify-center gap-2 transition-colors text-sm font-medium border border-slate-700"
              >
                <Download className="w-4 h-4" /> Download PDF Report
              </button>
            </div>

            {/* Explanations & Indicators */}
            <div className="col-span-1 md:col-span-2 space-y-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-4">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <h2 className="text-lg font-bold text-white">
                    AI Explanation
                  </h2>
                </div>
                <p className="text-slate-300 leading-relaxed mb-4">
                  {result.explanation}
                </p>
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-start gap-3">
                  <ShieldAlert className="w-5 h-5 shrink-0" />
                  <p className="font-medium">{result.recommendation}</p>
                </div>
              </div>

              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
                <h2 className="text-lg font-bold text-white mb-4">
                  Threat Indicators
                </h2>
                <div className="space-y-3">
                  {result.indicators.map((ind: any, i: number) => (
                    <div
                      key={i}
                      className="flex items-center gap-3 p-3 bg-slate-950/50 rounded-lg border border-slate-800"
                    >
                      <AlertTriangle
                        className={`w-5 h-5 ${ind.severity === "critical" ? "text-red-500" : "text-amber-500"}`}
                      />
                      <span className="text-slate-300">{ind.desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </Layout>
  );
};

export default WebsiteScanner;
