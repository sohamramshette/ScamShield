import { Layout } from "@/components/layout/Layout";
import { Search, Filter, Download } from "lucide-react";

const ScanHistory = () => {
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

          <div className="overflow-x-auto">
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
                {[
                  {
                    id: "SCN-8291",
                    target: "login-secure-paypal.com",
                    type: "Website",
                    score: 85,
                    level: "Critical",
                    date: "2026-07-17",
                    color: "text-red-400 bg-red-400/10",
                  },
                  {
                    id: "SCN-8290",
                    target: "Payment Gateway",
                    type: "QR Code",
                    score: 10,
                    level: "Safe",
                    date: "2026-07-17",
                    color: "text-emerald-400 bg-emerald-400/10",
                  },
                  {
                    id: "SCN-8289",
                    target: "google.com",
                    type: "Website",
                    score: 0,
                    level: "Safe",
                    date: "2026-07-16",
                    color: "text-emerald-400 bg-emerald-400/10",
                  },
                ].map((scan, i) => (
                  <tr
                    key={i}
                    className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="p-4 text-slate-400 font-mono">{scan.id}</td>
                    <td className="p-4 text-white font-medium">
                      {scan.target}
                    </td>
                    <td className="p-4 text-slate-400">{scan.type}</td>
                    <td className="p-4">
                      <span
                        className={`px-2 py-1 rounded border border-current ${scan.color}`}
                      >
                        {scan.score} - {scan.level}
                      </span>
                    </td>
                    <td className="p-4 text-slate-400">{scan.date}</td>
                    <td className="p-4 text-right">
                      <button className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
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
