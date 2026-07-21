import { motion } from "framer-motion";
import { Gauge, Clock, ServerCog, Cpu, BrainCircuit, Activity } from "lucide-react";

export const PerformanceCard = ({ performance, delay = 0 }: any) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm h-full flex flex-col"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-500/20 rounded-xl text-blue-400">
          <Gauge className="w-5 h-5" />
        </div>
        <h2 className="text-xl font-bold text-white">Engine Performance</h2>
      </div>

      <div className="space-y-4 flex-1">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400 flex items-center gap-2"><Clock className="w-4 h-4"/> DB Query</span>
          <span className="text-white font-mono">{performance?.database_query_time}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400 flex items-center gap-2"><ServerCog className="w-4 h-4"/> Cache Lookup</span>
          <span className="text-white font-mono">{performance?.cache_lookup_time}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400 flex items-center gap-2"><Cpu className="w-4 h-4"/> Orchestrator</span>
          <span className="text-white font-mono">{performance?.orchestrator_time}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400 flex items-center gap-2"><Activity className="w-4 h-4"/> Risk Engine</span>
          <span className="text-white font-mono">{performance?.risk_engine_time}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400 flex items-center gap-2"><BrainCircuit className="w-4 h-4"/> AI Generation</span>
          <span className="text-white font-mono">{performance?.ai_generation_time}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm pt-4 border-t border-slate-800">
          <span className="text-slate-300 font-semibold">Total E2E Average</span>
          <span className="text-emerald-400 font-mono font-bold bg-emerald-500/10 px-2 py-1 rounded">{performance?.total_e2e_time}</span>
        </div>
      </div>
    </motion.div>
  );
};
