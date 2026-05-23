import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from "react";
import { useAuth } from "@/hooks/useAuth";
import { updateUser } from "@/services/api";

export type ThemeName = "day" | "night" | "sunset" | "forest";

interface ThemeContextType {
    theme: ThemeName;
    setTheme: (theme: ThemeName) => void;
}

const ThemeContext = createContext<ThemeContextType>({
    theme: "day",
    setTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export const themeConfig: Record<
    ThemeName,
    { labelKey: string; accent: string; bg: string; emoji: string }
> = {
    day: { labelKey: "common.themeOptions.day", accent: "#3B82F6", bg: "#F8FAFC", emoji: "☀️" },
    night: { labelKey: "common.themeOptions.night", accent: "#60A5FA", bg: "#020617", emoji: "🌙" },
    sunset: {
        labelKey: "common.themeOptions.sunset",
        accent: "#F97316",
        bg: "#FAF6F2",
        emoji: "🌅",
    },
    forest: {
        labelKey: "common.themeOptions.forest",
        accent: "#059669",
        bg: "#F0FDF4",
        emoji: "🌲",
    },
};

const toBackendTheme = (theme: ThemeName) =>
    theme === "night" ? "dark" : "light";

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
    const { user } = useAuth();
    const [theme, setThemeState] = useState<ThemeName>(() => {
        return (localStorage.getItem("eduflow_theme") as ThemeName) || "day";
    });

    const setTheme = (t: ThemeName) => {
        setThemeState(t);
        localStorage.setItem("eduflow_theme", t);

        if (user?.id) {
            // Fire-and-forget: keep backend profile theme compatible (light/dark).
            void updateUser(user.id, { theme: toBackendTheme(t) }).catch(
                () => {},
            );
        }
    };

    useEffect(() => {
        document.documentElement.setAttribute("data-theme", theme);
    }, [theme]);

    return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};
