import { InputHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface VInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const VInput = forwardRef<HTMLInputElement, VInputProps>(
  ({ className, label, error, id, ...props }, ref) => (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={id} className="vidya-label">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={id}
        className={cn("vidya-input", error && "border-destructive focus:ring-destructive/30", className)}
        {...props}
      />
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  )
);

VInput.displayName = "VInput";
export default VInput;
