import { motion } from "framer-motion";
import { Server, Database, Zap, Activity } from "lucide-react";

export const SystemHealthCard = ({ system, performance, delay = 0 }: any) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm flex flex-col h-full"
    >
      <h2 className="text-xl font-bold text-white mb-4">System Health</h2>
      <div className="grid grid-cols-2 gap-4 flex-1">
        
        <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800 flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2 text-slate-400">
            <Server className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-semibold uppercase">API Status</span>
          </div>
          <p className="text-xl font-bold text-white">{system?.api_status || "Unknown"}</p>
        </div>

        <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800 flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2 text-slate-400">
            <Database className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold uppercase">Cache Size</span>
          </div>
          <p className="text-xl font-bold text-white">{system?.cache_size || 0} entries</p>
        </div>

        <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800 flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2 text-slate-400">
            <Activity className="w-4 h-4 text-purple-400" />
            <span className="text-xs font-semibold uppercase">Avg Latency</span>
          </div>
          <p className="text-xl font-bold text-white">{performance?.average_provider_latency || "0ms"}</p>
        </div>

        <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800 flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2 text-slate-400">
            <Zap className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-semibold uppercase">Orchestrator</span>
          </div>
          <p className="text-xl font-bold text-white">{performance?.orchestrator_time || "0ms"}</p>
        </div>
      </div>
    </motion.div>
  );
};
