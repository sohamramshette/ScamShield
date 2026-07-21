import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Filter, ShieldAlert, CheckCircle2, Shield } from "lucide-react";

export const ThreatFeed = ({ activities, delay = 0 }: any) => {
  const [filter, setFilter] = useState("All");
  
  const filtered = activities?.filter((a: any) => {
    if (filter === "All") return true;
    if (filter === "Critical" && a.risk_score >= 70) return true;
    if (filter === "Safe" && a.risk_score < 40) return true;
    if (filter === "Website" && a.type === "website") return true;
    if (filter === "QR" && a.type === "qr") return true;
    if (filter === "UPI" && a.type === "upi") return true;
    return false;
  }) || [];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm h-full flex flex-col"
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
        <h2 className="text-xl font-bold text-white">Live Threat Feed</h2>
        <div className="flex flex-wrap gap-2">
          {["All", "Critical", "Safe", "Website", "QR", "UPI"].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                filter === f 
                  ? "bg-blue-500/20 border-blue-500/50 text-blue-400" 
                  : "bg-slate-950/50 border-slate-800 text-slate-400 hover:border-slate-700"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3 overflow-y-auto flex-1 pr-2 custom-scrollbar">
        <AnimatePresence>
          {filtered.map((activity: any, i: number) => {
            let riskColor = "text-emerald-400 bg-emerald-400/10 border-emerald-500/20";
            let Icon = CheckCircle2;
            let riskLabel = "Safe";
            
            if (activity.risk_score >= 40) {
              riskColor = "text-amber-400 bg-amber-400/10 border-amber-500/20";
              Icon = Shield;
              riskLabel = "Warning";
            }
            if (activity.risk_score >= 70) {
              riskColor = "text-red-400 bg-red-400/10 border-red-500/20";
              Icon = ShieldAlert;
              riskLabel = "Critical";
            }

            const date = new Date(activity.created_at);
            const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

            return (
              <motion.div
                key={activity.id + i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="group flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition-colors gap-4"
              >
                <div className="flex items-start gap-4 flex-1 min-w-0">
                  <div className={`p-2 rounded-lg border mt-1 shrink-0 ${riskColor}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-white mb-1 truncate" title={activity.target}>
                      {activity.target}
                    </p>
                    <div className="flex flex-wrap items-center gap-2 text-xs font-medium text-slate-500">
                      <span className="uppercase text-slate-400">{activity.type}</span>
                      <span>&bull;</span>
                      <span className="text-slate-400">{activity.threat_category}</span>
                      <span>&bull;</span>
                      <span>{timeString}</span>
                      <span>&bull;</span>
                      <span className="text-indigo-400">Conf: {activity.confidence}%</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 shrink-0">
                  <div className="hidden sm:flex flex-col items-end text-xs mr-2">
                    <span className="text-slate-500">{activity.provider_count} Providers</span>
                    <span className="text-slate-400 font-medium">{activity.providers_used}</span>
                  </div>
                  <div className={`px-3 py-1.5 rounded-lg text-xs font-bold border tracking-wider uppercase shadow-sm ${riskColor}`}>
                    {riskLabel} {activity.risk_score}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
        
        {filtered.length === 0 && (
          <div className="text-center text-slate-500 py-12 flex flex-col items-center">
            <Filter className="w-8 h-8 mb-3 opacity-20" />
            <p>No threats match this filter.</p>
          </div>
        )}
      </div>
    </motion.div>
  );
};
