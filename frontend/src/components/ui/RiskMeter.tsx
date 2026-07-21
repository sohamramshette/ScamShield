import { motion } from "framer-motion";

export const RiskMeter = ({ score }: { score: number }) => {
  let level = "Safe";
  let color = "border-success";
  let textColor = "text-success";
  let shadow = "shadow-glow";
  
  if (score >= 20) { level = "Low"; color = "border-primary"; textColor = "text-primary"; shadow = "shadow-glow"; }
  if (score >= 40) { level = "Medium"; color = "border-warning"; textColor = "text-warning"; shadow = "shadow-[0_0_20px_-5px_rgba(245,158,11,0.4)]"; }
  if (score >= 70) { level = "High"; color = "border-danger"; textColor = "text-danger"; shadow = "shadow-glow-danger"; }
  if (score >= 90) { level = "Critical"; color = "border-danger"; textColor = "text-danger"; shadow = "shadow-glow-danger"; }

  return (
    <div className="flex flex-col items-center justify-center relative p-6">
      <div className="relative w-48 h-24 overflow-hidden">
        {/* Arch background */}
        <div className="absolute top-0 left-0 w-full h-[200%] border-[12px] border-border rounded-full" />
        
        {/* Progress Arch */}
        <motion.div 
          className={`absolute top-0 left-0 w-full h-[200%] border-[12px] border-t-transparent border-r-transparent rounded-full ${color} ${shadow}`}
          style={{ transformOrigin: 'center' }}
          initial={{ rotate: -45 }}
          animate={{ rotate: -45 + (score / 100) * 180 }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
      </div>
      
      {/* Metrics */}
      <div className="absolute bottom-4 flex flex-col items-center">
        <span className={`text-4xl font-heading font-black ${textColor}`}>
          {score}
        </span>
        <span className={`text-[10px] font-mono font-bold uppercase tracking-widest mt-1 ${textColor}`}>
          {level} RISK
        </span>
      </div>
    </div>
  );
};
