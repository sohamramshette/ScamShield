import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { Search, Filter, Download, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

const ScanHistory = () => {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await api.get("/history/");
        setScans(data);
      } catch (err: any) {
        setError(err.message || "Failed to load history");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const getLevelColor = (score: number) => {
    if (score >= 70) return "text-red-400 bg-red-400/10";
    if (score >= 40) return "text-amber-400 bg-amber-400/10";
    return "text-emerald-400 bg-emerald-400/10";
  };

  const getLevelText = (score: number) => {
    if (score >= 70) return "Critical";
    if (score >= 40) return "Warning";
    return "Safe";
  };

  const handleDownload = async (scanId: number) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"}/history/report/${scanId}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (!response.ok) throw new Error("Failed to download PDF");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ScamShield_Report_${scanId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Error downloading report.");
    }
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
              Scan History
            </h1>
            <p className="text-slate-400">
              View and manage your past threat intelligence scans.
            </p>
          </div>

          <div className="flex gap-3">
            <button className="px-4 py-2 bg-slate-900 border border-slate-700 hover:bg-slate-800 text-white rounded-lg flex items-center gap-2 transition-colors">
              <Filter className="w-4 h-4" /> Filter
            </button>
            <button className="px-4 py-2 bg-slate-900 border border-slate-700 hover:bg-slate-800 text-white rounded-lg flex items-center gap-2 transition-colors">
              <Download className="w-4 h-4" /> Export
            </button>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl backdrop-blur-sm overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex gap-4 bg-slate-950/50">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 w-5 h-5 text-slate-500" />
              <input
                type="text"
                placeholder="Search scans by target or ID..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 pl-10 pr-4 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              />
            </div>
          </div>

          <div className="overflow-x-auto min-h-[300px] relative">
            {loading && (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm z-10">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              </div>
            )}
            
            {error && (
              <div className="p-4 m-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm text-center">
                {error}
              </div>
            )}

            {!loading && !error && scans.length === 0 && (
              <div className="p-8 text-center text-slate-400">
                No scan history found. Try scanning a website first!
              </div>
            )}

            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-950/30 text-slate-400 text-sm border-b border-slate-800">
                  <th className="p-4 font-medium">Scan ID</th>
                  <th className="p-4 font-medium">Target</th>
                  <th className="p-4 font-medium">Type</th>
                  <th className="p-4 font-medium">Risk Score</th>
                  <th className="p-4 font-medium">Date</th>
                  <th className="p-4 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {scans.map((scan) => (
                  <tr
                    key={scan.id}
                    className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="p-4 text-slate-400 font-mono">SCN-{scan.id}</td>
                    <td className="p-4 text-white font-medium">
                      {scan.url || scan.extracted_data || scan.upi_id || "Unknown"}
                    </td>
                    <td className="p-4 text-slate-400">{scan.url ? "Website" : scan.extracted_data ? "QR Code" : scan.upi_id ? "UPI" : "Scan"}</td>
                    <td className="p-4">
                      <span
                        className={`px-2 py-1 rounded border border-current ${getLevelColor(scan.risk_score || 0)}`}
                      >
                        {scan.risk_score || 0} - {getLevelText(scan.risk_score || 0)}
                      </span>
                    </td>
                    <td className="p-4 text-slate-400">{new Date(scan.created_at).toLocaleDateString()}</td>
                    <td className="p-4 text-right">
                      <button 
                        onClick={() => handleDownload(scan.id)}
                        className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                      >
                        View Report
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ScanHistory;
