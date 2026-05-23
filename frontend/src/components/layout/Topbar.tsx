import { useEffect, useRef, useState } from "react";
import { Bell, ChevronDown, Menu, LogOut, User, Settings } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "@/components/ui-custom/LanguageSwitcher";
import ThemeSwitcher from "@/components/ui-custom/ThemeSwitcher";
import { useVToast } from "@/components/ui-custom/VToast";
import { useAuth } from "@/hooks/useAuth";
import { fetchMyNotifications } from "@/services/api";
import { useQuery } from "@tanstack/react-query";

interface TopbarProps {
    title: string;
    subtitle?: string;
    userName?: string;
    onMenuToggle?: () => void;
    onLogout?: () => void;
}

const Topbar = ({
    title,
    subtitle,
    userName = "User",
    onMenuToggle,
    onLogout,
}: TopbarProps) => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { showToast } = useVToast();
    const { user } = useAuth();

    const [notifOpen, setNotifOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);

    const notifRef = useRef<HTMLDivElement>(null);
    const profileRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (
                notifRef.current &&
                !notifRef.current.contains(e.target as Node)
            ) {
                setNotifOpen(false);
            }
            if (
                profileRef.current &&
                !profileRef.current.contains(e.target as Node)
            ) {
                setProfileOpen(false);
            }
        };
        document.addEventListener("mousedown", handler);
        return () => document.removeEventListener("mousedown", handler);
    }, []);

    const { data: notifications = [] } = useQuery({
        queryKey: ["topbarNotifications", user?.id],
        queryFn: fetchMyNotifications,
        enabled: Boolean(user?.id),
        refetchInterval: 60_000,
    });

    const unreadCount = notifications.filter((item) => !item.read).length;

    const handleLogout = () => {
        onLogout?.();
        showToast(
            "success",
            t("topbar.loggedOutTitle"),
            t("topbar.loggedOutMessage"),
        );
        navigate("/login");
    };

    const today = new Intl.DateTimeFormat(
        i18n.language === "hi" ? "hi-IN" : "en-US",
        {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
        },
    ).format(new Date());

    const initials = userName
        .split(" ")
        .filter(Boolean)
        .map((n) => n[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();

    return (
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-card/80 backdrop-blur-md px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
                <button
                    onClick={onMenuToggle}
                    className="lg:hidden rounded-xl p-2 text-muted-foreground hover:bg-accent transition-all">
                    <Menu className="h-5 w-5" />
                </button>

                <div className="flex flex-col">
                    <p className="text-sm font-semibold text-foreground leading-tight">
                        {title}
                    </p>
                    <span className="text-xs text-muted-foreground hidden xl:block">
                        {subtitle ? `${subtitle} • ${today}` : today}
                    </span>
                </div>
            </div>

            <div className="flex items-center gap-1 sm:gap-2">
                <LanguageSwitcher />
                <ThemeSwitcher />

                <div ref={notifRef} className="relative">
                    <button
                        onClick={() => setNotifOpen((v) => !v)}
                        className="relative rounded-xl p-2 text-muted-foreground hover:bg-accent transition-all">
                        <Bell className="h-5 w-5" />
                        {unreadCount > 0 && (
                            <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-destructive ring-2 ring-card" />
                        )}
                    </button>

                    {notifOpen && (
                        <div className="absolute right-0 top-full mt-2 w-80 rounded-2xl border border-border bg-card shadow-xl z-50">
                            <div className="px-4 py-3 border-b border-border">
                                <p className="text-sm font-semibold text-foreground">
                                    {t("common.notifications")}
                                </p>
                            </div>

                            <div className="max-h-64 overflow-y-auto">
                                {notifications.slice(0, 6).map((n) => (
                                    <button
                                        key={n.id}
                                        onClick={() => {
                                            setNotifOpen(false);
                                            navigate("/notifications");
                                            showToast("info", n.title, n.message);
                                        }}
                                        className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-accent/50">
                                        <div
                                            className={`mt-1.5 h-2 w-2 rounded-full ${
                                                !n.read
                                                    ? "bg-destructive"
                                                    : "bg-muted"
                                            }`}
                                        />
                                        <div>
                                            <p className="text-sm text-foreground">
                                                {n.title}
                                            </p>
                                            <p className="text-xs text-muted-foreground mt-0.5">
                                                {n.date}
                                            </p>
                                        </div>
                                    </button>
                                ))}
                            </div>

                            <button
                                onClick={() => {
                                    setNotifOpen(false);
                                    navigate("/notifications");
                                }}
                                className="w-full px-4 py-3 text-sm text-primary font-medium border-t border-border hover:bg-accent/50">
                                {t("common.viewAllNotifications")}
                            </button>
                        </div>
                    )}
                </div>

                <div ref={profileRef} className="relative">
                    <button
                        onClick={() => setProfileOpen((v) => !v)}
                        className="flex items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-accent">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full vidya-gradient text-primary-foreground text-xs font-bold">
                            {initials}
                        </div>
                        <ChevronDown className="h-3.5 w-3.5 text-muted-foreground hidden sm:block" />
                    </button>

                    {profileOpen && (
                        <div className="absolute right-0 top-full mt-2 w-56 rounded-2xl border border-border bg-card shadow-xl z-50">
                            <div className="px-4 py-3 border-b border-border">
                                <p className="text-sm font-semibold text-foreground">
                                    {userName}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                    {t("common.loggedIn")}
                                </p>
                            </div>

                            <div className="p-1">
                                <button
                                    onClick={() => {
                                        setProfileOpen(false);
                                        navigate("/profile");
                                    }}
                                    className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm hover:bg-accent">
                                    <User className="h-4 w-4 text-muted-foreground" />
                                    {t("common.myProfile")}
                                </button>

                                <button
                                    onClick={() => {
                                        setProfileOpen(false);
                                        showToast(
                                            "info",
                                            t("common.settings"),
                                            t("common.settingsComingSoon"),
                                        );
                                    }}
                                    className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm hover:bg-accent">
                                    <Settings className="h-4 w-4 text-muted-foreground" />
                                    {t("common.settings")}
                                </button>

                                <button
                                    onClick={() => {
                                        setProfileOpen(false);
                                        handleLogout();
                                    }}
                                    className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-destructive hover:bg-destructive/10">
                                    <LogOut className="h-4 w-4" />
                                    {t("common.signOut")}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Topbar;
