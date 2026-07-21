import { motion } from "framer-motion";
import { Server, Activity, Database, CheckCircle2 } from "lucide-react";

export const ProviderGrid = ({ providers, delay = 0 }: any) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm h-full flex flex-col"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">Provider Operations</h2>
        <span className="text-xs text-slate-400 font-medium px-3 py-1 bg-slate-950 rounded-full border border-slate-800">
          Live Status
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 overflow-y-auto custom-scrollbar flex-1 pb-2">
        {providers?.map((p: any, i: number) => {
          let statusColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
          if (p.status === "Degraded" || p.status === "Rate Limited") statusColor = "text-amber-400 bg-amber-500/10 border-amber-500/20";
          if (p.status === "Offline" || p.status === "Disabled") statusColor = "text-red-400 bg-red-500/10 border-red-500/20";

          return (
            <div key={i} className="bg-slate-950/60 rounded-xl p-4 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-white font-semibold mb-1 truncate" title={p.name}>{p.name}</h3>
                  <div className={`inline-flex px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider border ${statusColor}`}>
                    {p.status}
                  </div>
                </div>
                <div className="p-2 bg-slate-900 rounded-lg text-slate-400 border border-slate-800">
                  <Server className="w-4 h-4" />
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400 flex items-center gap-1.5"><Activity className="w-3.5 h-3.5"/> Latency</span>
                  <span className="text-white font-medium">{p.latency}ms</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400 flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5"/> Success</span>
                  <span className="text-white font-medium">{p.success_rate}%</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400 flex items-center gap-1.5"><Database className="w-3.5 h-3.5"/> Cache</span>
                  <span className="text-white font-medium">{p.cache_hits} hits</span>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-slate-800/50 flex items-center justify-between text-[10px] text-slate-500 font-medium">
                <span>KEY: <span className="text-emerald-500">VALID</span></span>
                <span>{p.requests_processed} REQ</span>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};
