import { useState, ReactNode } from "react";
import { cn } from "@/lib/utils";

interface Tab {
  key: string;
  label: string;
  content: ReactNode;
}

interface VTabsProps {
  tabs: Tab[];
  defaultTab?: string;
  className?: string;
}

const VTabs = ({ tabs, defaultTab, className }: VTabsProps) => {
  const [active, setActive] = useState(defaultTab || tabs[0]?.key);

  return (
    <div className={className}>
      <div className="flex gap-1 border-b border-border mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActive(tab.key)}
            className={cn(
              "px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px",
              active === tab.key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.find((t) => t.key === active)?.content}
    </div>
  );
};

export default VTabs;
