import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { VToastProvider } from "@/components/ui-custom/VToast";
import { AuthProvider } from "@/hooks/useAuth";
import AppRoutes from "@/routes/AppRoutes";
import { useAutoLocalizeDocument } from "@/lib/useAutoLocalizeDocument";
import ErrorBoundary from "@/components/ErrorBoundary";
import "./index.css";

const queryClient = new QueryClient();

const AppShell = () => {
  useAutoLocalizeDocument();

  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <AuthProvider>
          <ThemeProvider>
            <VToastProvider>
              <BrowserRouter>
                <AppRoutes />
              </BrowserRouter>
            </VToastProvider>
          </ThemeProvider>
        </AuthProvider>
      </ErrorBoundary>
    </QueryClientProvider>
  );
};

const App = () => <AppShell />;

export default App;
