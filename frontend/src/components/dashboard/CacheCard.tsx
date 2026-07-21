import { motion } from "framer-motion";
import { DatabaseZap, Clock, Timer, Layers } from "lucide-react";

export const CacheCard = ({ cache, delay = 0 }: any) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm h-full flex flex-col relative overflow-hidden"
    >
      <div className="absolute -right-4 -top-4 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl" />
      
      <div className="flex items-center gap-3 mb-6 relative z-10">
        <div className="p-2 bg-purple-500/20 rounded-xl text-purple-400">
          <DatabaseZap className="w-5 h-5" />
        </div>
        <h2 className="text-xl font-bold text-white">Cache Analytics</h2>
      </div>

      <div className="grid grid-cols-2 gap-4 flex-1 relative z-10">
        <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Hit Ratio</span>
          <p className="text-xl font-bold text-white mt-1">{cache?.hit_ratio}%</p>
        </div>
        
        <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Size</span>
          <p className="text-xl font-bold text-white mt-1">{cache?.size} entries</p>
        </div>
        
        <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold flex items-center gap-1"><Clock className="w-3 h-3"/> Avg Age</span>
          <p className="text-xl font-bold text-white mt-1">{cache?.average_age_hours}h</p>
        </div>

        <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold flex items-center gap-1"><Timer className="w-3 h-3"/> Lookup</span>
          <p className="text-xl font-bold text-white mt-1">{cache?.average_lookup_ms}ms</p>
        </div>
        
        <div className="col-span-2 flex items-center justify-between text-xs text-slate-500 mt-2 px-2 border-t border-slate-800 pt-3">
          <span className="flex items-center gap-1"><Layers className="w-3 h-3"/> {cache?.hits} Hits</span>
          <span>{cache?.misses} Misses</span>
        </div>
      </div>
    </motion.div>
  );
};
