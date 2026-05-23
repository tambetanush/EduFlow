import { HTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface VCardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

const VCard = forwardRef<HTMLDivElement, VCardProps>(
  ({ className, hover, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(hover ? "vidya-card-hover" : "vidya-card", "p-6", className)}
      {...props}
    >
      {children}
    </div>
  )
);

VCard.displayName = "VCard";
export default VCard;
