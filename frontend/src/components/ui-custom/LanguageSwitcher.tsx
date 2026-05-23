import { Languages } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { type AppLanguage, normalizeLanguage, setAppLanguage } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const languageOptions: AppLanguage[] = ["en", "hi"];

const LanguageSwitcher = ({ className }: { className?: string }) => {
  const { t, i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const language = normalizeLanguage(i18n.language);

  useEffect(() => {
    const handler = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className={cn("relative", className)} data-i18n-skip="true">
      <button
        onClick={() => setOpen((value) => !value)}
        className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-all"
        title={t("common.changeLanguage")}
        aria-label={t("common.changeLanguage")}
      >
        <Languages className="h-4 w-4" />
        <span className="hidden sm:inline">{language.toUpperCase()}</span>
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 z-50 w-52 rounded-2xl border border-border bg-card p-2 shadow-xl animate-in fade-in slide-in-from-top-2 duration-200">
          <p className="px-3 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            {t("common.language")}
          </p>
          {languageOptions.map((option) => {
            const active = language === option;
            return (
              <button
                key={option}
                onClick={() => {
                  void setAppLanguage(option);
                  setOpen(false);
                }}
                className={cn(
                  "flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
                  active ? "bg-primary/10 text-primary" : "text-foreground hover:bg-accent",
                )}
              >
                <span>{t(`common.languageOptions.${option}`)}</span>
                <span className="text-xs font-semibold">{option.toUpperCase()}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default LanguageSwitcher;
