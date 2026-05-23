import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import Sidebar from "@/components/layout/Sidebar";
import ProtectedRoute from "@/routes/ProtectedRoute";
import type { UserRole } from "@/mock/mockData";

let mockRole: UserRole = "student";
let mockUser: { id: string; name: string; email: string; role: UserRole; institution_id?: string } | null = null;

vi.mock("@/hooks/useRole", () => ({
  useRole: () => mockRole,
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({
    user: mockUser,
    isLoading: false,
    logout: vi.fn(),
  }),
}));

const setRole = (role: UserRole) => {
  mockRole = role;
  mockUser = {
    id: `${role}-1`,
    name: `${role} user`,
    email: `${role}@example.com`,
    role,
    institution_id: role === "institution_admin" ? "inst-1" : undefined,
  };
};

describe("Admin AI Report Access Control", () => {
  beforeEach(() => {
    setRole("student");
  });

  it("hides AI Reports nav item for student and educator", () => {
    setRole("student");
    const { rerender } = render(
      <MemoryRouter>
        <Sidebar onLogout={() => {}} />
      </MemoryRouter>,
    );
    expect(screen.queryByText("AI Reports")).not.toBeInTheDocument();

    setRole("educator");
    rerender(
      <MemoryRouter>
        <Sidebar onLogout={() => {}} />
      </MemoryRouter>,
    );
    expect(screen.queryByText("AI Reports")).not.toBeInTheDocument();
  });

  it("shows AI Reports nav item for platform and institutional admins", () => {
    setRole("admin");
    const { rerender } = render(
      <MemoryRouter>
        <Sidebar onLogout={() => {}} />
      </MemoryRouter>,
    );
    expect(screen.getByText("AI Reports")).toBeInTheDocument();

    setRole("institution_admin");
    rerender(
      <MemoryRouter>
        <Sidebar onLogout={() => {}} />
      </MemoryRouter>,
    );
    expect(screen.getByText("AI Reports")).toBeInTheDocument();
  });

  it("blocks /reports/ai route for student and educator, allows admins", () => {
    const renderWithRole = (role: UserRole) => {
      setRole(role);
      return render(
        <MemoryRouter initialEntries={["/reports/ai"]}>
          <Routes>
            <Route path="/login" element={<div>Login Screen</div>} />
            <Route
              path="/reports/ai"
              element={
                <ProtectedRoute allowedRoles={["admin", "institution_admin"]}>
                  <div>AI Reports Screen</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>,
      );
    };

    const studentView = renderWithRole("student");
    expect(studentView.getByText("Login Screen")).toBeInTheDocument();
    studentView.unmount();

    const educatorView = renderWithRole("educator");
    expect(educatorView.getByText("Login Screen")).toBeInTheDocument();
    educatorView.unmount();

    const adminView = renderWithRole("admin");
    expect(adminView.getByText("AI Reports Screen")).toBeInTheDocument();
    adminView.unmount();

    const instAdminView = renderWithRole("institution_admin");
    expect(instAdminView.getByText("AI Reports Screen")).toBeInTheDocument();
    instAdminView.unmount();
  });
});
