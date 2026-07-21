import { motion } from "framer-motion";

export const MetricCard = ({ title, value, icon: Icon, color, delay }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3, delay }}
    whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
    className="relative group bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md flex items-center justify-between overflow-hidden cursor-default"
  >
    <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500 ${color.split(' ')[0]}`} />
    
    <div className="relative z-10">
      <h3 className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">{title}</h3>
      <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
    </div>
    <div className={`relative z-10 p-3 rounded-xl ${color} shadow-lg shadow-black/20`}>
      <Icon className="w-6 h-6" />
    </div>
  </motion.div>
);
