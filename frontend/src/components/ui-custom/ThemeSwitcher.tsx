import { useState, useRef, useEffect } from "react";
import { Palette } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useTheme, themeConfig, type ThemeName } from "@/contexts/ThemeContext";
import { cn } from "@/lib/utils";

const ThemeSwitcher = ({ className }: { className?: string }) => {
    const { t } = useTranslation();
    const { theme, setTheme } = useTheme();
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node))
                setOpen(false);
        };
        document.addEventListener("mousedown", handler);
        return () => document.removeEventListener("mousedown", handler);
    }, []);

    return (
        <div ref={ref} className={cn("relative", className)}>
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-all"
                title={t("common.changeTheme")}
                aria-label={t("common.changeTheme")}>
                <Palette className="h-4 w-4" />
                <span className="hidden sm:inline">
                    {themeConfig[theme].emoji}
                </span>
            </button>

            {open && (
                <div className="absolute right-0 top-full mt-2 z-50 w-52 rounded-2xl border border-border bg-card p-2 shadow-xl animate-in fade-in slide-in-from-top-2 duration-200">
                    <p className="px-3 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        {t("common.theme")}
                    </p>
                    {(Object.keys(themeConfig) as ThemeName[]).map((key) => {
                        const themeMeta = themeConfig[key];
                        const active = theme === key;
                        return (
                            <button
                                key={key}
                                onClick={() => {
                                    setTheme(key);
                                    setOpen(false);
                                }}
                                className={cn(
                                    "flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
                                    active
                                        ? "bg-primary/10 text-primary"
                                        : "text-foreground hover:bg-accent",
                                )}>
                                <span className="text-base">{themeMeta.emoji}</span>
                                <span className="flex-1 text-left">
                                    {t(themeMeta.labelKey)}
                                </span>
                                <span
                                    className="h-4 w-4 rounded-full border-2 transition-all"
                                    style={{
                                        backgroundColor: themeMeta.accent,
                                        borderColor: active
                                            ? themeMeta.accent
                                            : "transparent",
                                        boxShadow: active
                                            ? `0 0 8px ${themeMeta.accent}40`
                                            : "none",
                                    }}
                                />
                            </button>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default ThemeSwitcher;
