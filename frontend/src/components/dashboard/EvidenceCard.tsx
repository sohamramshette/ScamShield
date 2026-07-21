import { motion } from "framer-motion";
import { SearchCode } from "lucide-react";

export const EvidenceCard = ({ evidence, delay = 0 }: any) => {
  if (!evidence) return null;
  const categories = Object.keys(evidence);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm h-full flex flex-col relative"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-white">
          <SearchCode className="w-5 h-5 text-amber-400" />
          <h2 className="text-xl font-bold">Threat Evidence</h2>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-2">
        {categories.map((cat, i) => {
          const count = evidence[cat];
          const severity = count > 5 ? "bg-red-500/20 text-red-400" : (count > 0 ? "bg-amber-500/20 text-amber-400" : "bg-slate-800 text-slate-400");
          return (
            <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-slate-950/50 hover:bg-slate-900 transition-colors">
              <span className="text-sm text-slate-300 font-medium">{cat}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${severity}`}>{count}</span>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};
