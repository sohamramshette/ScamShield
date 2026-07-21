import { motion } from "framer-motion";
import { CheckCircle2, Loader2, Circle } from "lucide-react";

export interface TimelineStep {
  label: string;
  status: "pending" | "active" | "completed";
}

export const InvestigationTimeline = ({ steps }: { steps: TimelineStep[] }) => {
  return (
    <div className="relative py-4">
      {/* Background Track */}
      <div className="absolute top-1/2 left-0 w-full h-[2px] bg-border -translate-y-1/2 rounded-full" />
      
      {/* Animated Progress Track */}
      <motion.div 
        className="absolute top-1/2 left-0 h-[2px] bg-gradient-to-r from-primary to-secondary -translate-y-1/2 rounded-full shadow-glow"
        initial={{ width: 0 }}
        animate={{ 
          width: `${(steps.filter(s => s.status === 'completed').length / (steps.length - 1)) * 100}%` 
        }}
        transition={{ duration: 1, ease: "easeInOut" }}
      />
      
      {/* Nodes */}
      <div className="relative flex justify-between items-center w-full z-10">
        {steps.map((step, index) => (
          <div key={index} className="flex flex-col items-center gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center backdrop-blur-sm transition-all duration-500
              ${step.status === 'completed' ? 'bg-primary/20 border-primary text-primary shadow-glow' : 
                step.status === 'active' ? 'bg-secondary/20 border-secondary text-secondary shadow-[0_0_15px_-3px_rgba(139,92,246,0.4)]' : 
                'bg-card border-border text-muted-foreground'} border-2`}
            >
              {step.status === 'completed' && <CheckCircle2 className="w-4 h-4" />}
              {step.status === 'active' && <Loader2 className="w-4 h-4 animate-spin" />}
              {step.status === 'pending' && <Circle className="w-3 h-3 fill-current opacity-20" />}
            </div>
            
            <span className={`text-[10px] font-mono font-bold uppercase tracking-widest whitespace-nowrap transition-colors duration-500
              ${step.status === 'completed' ? 'text-primary' : 
                step.status === 'active' ? 'text-secondary' : 
                'text-muted-foreground'}`}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
