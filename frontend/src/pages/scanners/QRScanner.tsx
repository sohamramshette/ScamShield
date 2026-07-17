import { useState, useRef } from "react";
import { Layout } from "@/components/layout/Layout";
import { Upload, ShieldAlert, AlertTriangle, FileText, Download, QrCode } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import jsQR from "jsqr";

const QRScanner = () => {
  const [target, setTarget] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processPayload = async (payload: string) => {
    setTarget(payload);
    setIsScanning(true);
    setError("");
    setResult(null);

    // Auto detect UPI vs Website
    let endpoint = "/scanners/qr"; // Default to general QR
    let reqBody = { target: payload };
    
    if (payload.includes("upi://pay") || payload.includes("@")) {
      endpoint = "/scanners/upi";
    } else if (payload.startsWith("http://") || payload.startsWith("https://")) {
      endpoint = "/scanners/website";
    }

    try {
      const data = await api.post(endpoint, reqBody);
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
        id: data.id || data.scan_id,
      });
    } catch (err: any) {
      setError(err.message || "Failed to scan QR code payload");
    } finally {
      setIsScanning(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;
        ctx.drawImage(img, 0, 0);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        const code = jsQR(imageData.data, imageData.width, imageData.height);
        if (code) {
          processPayload(code.data);
        } else {
          setError("No QR code found in the image. Please try a clearer image.");
        }
      };
      img.src = event.target?.result as string;
    };
    reader.readAsDataURL(file);
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
            QR Code Scanner
          </h1>
          <p className="text-slate-400">
            Upload an image to decode and analyze its payload.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900/50 border border-slate-800 p-8 rounded-2xl backdrop-blur-sm mb-8 text-center"
        >
          {error && (
            <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <input 
            type="file" 
            accept="image/*" 
            className="hidden" 
            ref={fileInputRef}
            onChange={handleFileUpload}
          />
          
          <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-slate-700 rounded-xl bg-slate-950/50 hover:bg-slate-900/80 transition-colors">
            <div className="p-4 rounded-full bg-blue-500/10 text-blue-400 mb-4">
              <Upload className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Upload Image</h3>
            <p className="text-slate-400 text-sm mb-6">
              Select a QR code image to decode and scan for threats.
            </p>
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={isScanning}
              className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-semibold transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)] flex items-center gap-2"
            >
              {isScanning ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <QrCode className="w-5 h-5" />
              )}
              {isScanning ? "Processing..." : "Select QR Image"}
            </button>
          </div>
          
          {target && !isScanning && !error && (
            <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-left">
              <p className="text-emerald-400 text-sm font-semibold mb-1">Decoded Payload:</p>
              <p className="text-white font-mono break-all">{target}</p>
            </div>
          )}
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

export default QRScanner;
