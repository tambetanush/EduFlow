import { ReactNode, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { useAuth } from "@/hooks/useAuth";
import VLoader from "@/components/ui-custom/VLoader";

interface DashboardLayoutProps {
    title: string;
    subtitle?: string;
    children: ReactNode;
}

const DashboardLayout = ({
    title,
    subtitle,
    children,
}: DashboardLayoutProps) => {
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const { user, isLoading, logout } = useAuth();

    useEffect(() => {
        if (!isLoading && !user) {
            navigate("/login");
        }
    }, [isLoading, user, navigate]);

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background">
                <VLoader text="Loading your workspace..." />
            </div>
        );
    }

    if (!user) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background">
                <VLoader text="Redirecting to login..." />
            </div>
        );
    }

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <div className="min-h-screen bg-background vidya-pattern">
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            <div
                className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-200 ease-in-out lg:translate-x-0 ${
                    sidebarOpen ? "translate-x-0" : "-translate-x-full"
                }`}>
                <Sidebar
                    onLogout={handleLogout}
                    onClose={() => setSidebarOpen(false)}
                />
            </div>

            <div className="lg:ml-64">
                <Topbar
                    title={title}
                    subtitle={subtitle}
                    userName={user?.name ?? undefined}
                    onMenuToggle={() => setSidebarOpen(true)}
                    onLogout={handleLogout}
                />
                <main className="p-4 sm:p-6 lg:p-8">{children}</main>
            </div>
        </div>
    );
};

export default DashboardLayout;
