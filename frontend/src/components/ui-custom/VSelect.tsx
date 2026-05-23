import { SelectHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface VSelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
}

const VSelect = forwardRef<HTMLSelectElement, VSelectProps>(
  ({ className, label, options, id, ...props }, ref) => (
    <div className="space-y-1.5">
      {label && <label htmlFor={id} className="vidya-label">{label}</label>}
      <select
        ref={ref}
        id={id}
        className={cn("vidya-input appearance-none cursor-pointer", className)}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  )
);

VSelect.displayName = "VSelect";
export default VSelect;
