import { motion } from "framer-motion";
import { BrainCircuit, AlertTriangle, ShieldCheck } from "lucide-react";

export const AIInsightCard = ({ insights, delay = 0 }: any) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-gradient-to-br from-indigo-900/40 to-slate-900/80 border border-indigo-500/20 rounded-2xl p-6 backdrop-blur-sm flex flex-col h-full relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl" />
      
      <div className="flex items-center gap-3 mb-6 relative z-10">
        <div className="p-2 bg-indigo-500/20 rounded-xl text-indigo-400">
          <BrainCircuit className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-white">AI Security Insights</h2>
      </div>

      <div className="space-y-4 flex-1 relative z-10">
        <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5" />
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase mb-1">Primary Threat Vector</p>
              <p className="text-white font-medium">{insights?.most_common_attack_type || "Unknown"}</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
          <div className="flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-400 mt-0.5" />
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase mb-1">Recommended Action</p>
              <p className="text-white font-medium">{insights?.recommended_action || "System Secure"}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
          <div className="flex items-start gap-3">
            <BrainCircuit className="w-5 h-5 text-indigo-400 mt-0.5" />
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase mb-1">Most Suspicious Target</p>
              <p className="text-white font-medium truncate" title={insights?.most_suspicious_domain}>{insights?.most_suspicious_domain || "None"}</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
