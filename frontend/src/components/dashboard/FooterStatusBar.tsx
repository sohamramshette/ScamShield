export const FooterStatusBar = ({ health, lastUpdated }: any) => {
  const engines = [
    { name: "API", status: health?.api_status },
    { name: "Database", status: health?.database_status },
    { name: "Threat Cache", status: health?.threat_cache },
    { name: "Registry", status: health?.provider_registry },
    { name: "Orchestrator", status: health?.threat_orchestrator },
    { name: "Evidence Engine", status: health?.evidence_engine },
    { name: "Risk Engine", status: health?.risk_engine },
    { name: "IBM Granite", status: health?.ibm_granite },
    { name: "Docker", status: health?.docker_status },
  ];

  const timeString = lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : "Unknown";

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-slate-950 border-t border-slate-800 z-50 flex items-center justify-between px-4 py-1.5 text-[10px] sm:text-xs">
      <div className="flex items-center gap-4 overflow-x-auto custom-scrollbar whitespace-nowrap hide-scrollbar">
        {engines.map((engine, i) => {
          let dotColor = "bg-slate-500";
          if (engine.status === "Healthy" || engine.status === "Online") dotColor = "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]";
          if (engine.status === "Warning") dotColor = "bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)]";
          if (engine.status === "Offline") dotColor = "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]";
          
          return (
            <div key={i} className="flex items-center gap-1.5 text-slate-400 shrink-0">
              <div className={`w-2 h-2 rounded-full ${dotColor}`} />
              <span className="font-medium uppercase tracking-wider">{engine.name}</span>
            </div>
          );
        })}
      </div>
      
      <div className="flex items-center gap-3 shrink-0 ml-4 text-slate-500 font-medium">
        <span>v2.0.0-rc1</span>
        <span>|</span>
        <span>SYNC: {timeString}</span>
      </div>
    </div>
  );
};
