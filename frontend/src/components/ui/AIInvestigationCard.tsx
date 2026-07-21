import { Sparkles, Brain, Target, ShieldAlert, FileSearch } from "lucide-react";

interface AIData {
  family: string;
  threat_type: string;
  behavior: string;
  confidence: number;
  impact: string;
  recommendation: string;
}

export const AIInvestigationCard = ({ data }: { data: AIData }) => {
  return (
    <div className="signature-panel p-8 group">
      {/* Header */}
      <div className="flex justify-between items-start mb-8 pb-6 border-b border-white/5 relative">
        <div className="flex gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 border border-white/10 flex items-center justify-center shadow-glow group-hover:shadow-[0_0_30px_-5px_rgba(139,92,246,0.5)] transition-shadow duration-500">
            <Brain className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h3 className="text-2xl font-heading font-bold text-white tracking-tight flex items-center gap-2">
              Granite AI Intelligence
              <Sparkles className="w-4 h-4 text-secondary animate-pulse" />
            </h3>
            <p className="text-sm font-mono text-muted-foreground mt-1 tracking-wider uppercase">Automated Threat Synthesis</p>
          </div>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-3xl font-heading font-black text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
            {data.confidence}%
          </span>
          <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mt-1">Confidence Score</span>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Column */}
        <div className="space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-danger" />
              <span className="text-xs font-mono font-bold text-muted-foreground uppercase tracking-widest">Classification</span>
            </div>
            <div className="bg-black/30 p-4 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
              <p className="text-lg font-bold text-white mb-1">{data.family}</p>
              <span className="chip-critical">{data.threat_type}</span>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-warning" />
              <span className="text-xs font-mono font-bold text-muted-foreground uppercase tracking-widest">Predicted Behavior</span>
            </div>
            <p className="text-sm text-foreground/80 leading-relaxed font-sans bg-black/30 p-4 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
              {data.behavior}
            </p>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <ShieldAlert className="w-4 h-4 text-secondary" />
              <span className="text-xs font-mono font-bold text-muted-foreground uppercase tracking-widest">Business Impact</span>
            </div>
            <p className="text-sm text-foreground/80 leading-relaxed font-sans bg-black/30 p-4 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
              {data.impact}
            </p>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <FileSearch className="w-4 h-4 text-success" />
              <span className="text-xs font-mono font-bold text-muted-foreground uppercase tracking-widest">Recommendations</span>
            </div>
            <div className="bg-success/5 border-l-2 border-success p-4 rounded-r-xl">
              <p className="text-sm font-medium text-success/90 leading-relaxed">
                {data.recommendation}
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

// Quick fix for missing Activity icon import
import { Activity } from "lucide-react";
