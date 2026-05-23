import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface VEmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
}

const VEmptyState = ({ icon, title, description, action, className }: VEmptyStateProps) => (
  <div className={cn("flex flex-col items-center justify-center py-16 px-4 text-center", className)}>
    <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
      {icon}
    </div>
    <h3 className="text-lg font-bold text-foreground mb-2">{title}</h3>
    <p className="text-sm text-muted-foreground max-w-sm mb-6">{description}</p>
    {action}
  </div>
);

export default VEmptyState;
