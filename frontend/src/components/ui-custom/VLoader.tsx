import { cn } from "@/lib/utils";

const VLoader = ({ className, text }: { className?: string; text?: string }) => (
  <div className={cn("flex flex-col items-center justify-center py-12 gap-3", className)}>
    <div className="relative h-10 w-10">
      <div className="absolute inset-0 rounded-full border-2 border-primary/20" />
      <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-primary animate-spin" />
    </div>
    {text && <p className="text-sm text-muted-foreground">{text}</p>}
  </div>
);

export default VLoader;
