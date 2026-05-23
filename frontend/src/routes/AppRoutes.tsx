import { Routes, Route, Navigate } from "react-router-dom";
import Login from "@/pages/Login";
import SignUp from "@/pages/SignUp";
import LandingPage from "@/pages/LandingPage";
import AdminDashboard from "@/pages/dashboard/AdminDashboard";
import InstitutionDashboard from "@/pages/dashboard/InstitutionDashboard";
import EducatorDashboard from "@/pages/dashboard/EducatorDashboard";
import StudentDashboard from "@/pages/dashboard/StudentDashboard";
import SupportDashboard from "@/pages/dashboard/SupportDashboard";
import WorkshopsList from "@/pages/workshops/WorkshopsList";
import WorkshopDetails from "@/pages/workshops/WorkshopDetails";
import MaterialsPage from "@/pages/materials/Materials";
import AssessmentsPage from "@/pages/assessments/Assessments";
import AssessmentAttempt from "@/pages/assessments/AssessmentAttempt";
import Results from "@/pages/assessments/Results";
import SubmissionsPage from "@/pages/submissions/Submissions";
import Certificates from "@/pages/certificates/Certificates";
import VerifyCertificate from "@/pages/certificates/VerifyCertificate";
import PerformanceReports from "@/pages/reports/PerformanceReports";
import AdminAIReports from "@/pages/reports/AdminAIReports";
import ScheduledAIReports from "@/pages/reports/ScheduledAIReports";
import Notifications from "@/pages/notifications/Notifications";
import ProfilePage from "@/pages/profile/ProfilePage";
import EducatorManagement from "@/pages/manage/EducatorManagement";
import StudentManagement from "@/pages/manage/StudentManagement";
import InstituteManagement from "@/pages/manage/InstituteManagement";
import ApprovalPanel from "@/pages/manage/ApprovalPanel";
import SalaryManagement from "@/pages/manage/SalaryManagement";
import ProtectedRoute from "@/routes/ProtectedRoute";
import NotFound from "@/pages/NotFound";
import SupportConsole from "@/pages/support/SupportConsole";
import AIContentGenerator from "@/pages/AIContentGenerator"; // ADD THIS IMPORT
import PublicStudentProfile from "@/pages/profile/PublicStudentProfile";

const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/signup" element={<SignUp />} />
    <Route path="/verify-certificate" element={<VerifyCertificate />} />
    <Route path="/public/student/:studentId" element={<PublicStudentProfile />} />

    {/* Role-based dashboards */}
    <Route path="/dashboard/admin" element={<ProtectedRoute allowedRoles={["admin"]}><AdminDashboard /></ProtectedRoute>} />
    <Route path="/dashboard/institution" element={<ProtectedRoute allowedRoles={["institution_admin"]}><InstitutionDashboard /></ProtectedRoute>} />
    <Route path="/dashboard/educator" element={<ProtectedRoute allowedRoles={["educator"]}><EducatorDashboard /></ProtectedRoute>} />
    <Route path="/dashboard/student" element={<ProtectedRoute allowedRoles={["student"]}><StudentDashboard /></ProtectedRoute>} />
    <Route path="/dashboard/technical_support" element={<ProtectedRoute allowedRoles={["technical_support"]}><SupportDashboard /></ProtectedRoute>} />

    {/* Shared pages */}
    <Route path="/workshops" element={<ProtectedRoute><WorkshopsList /></ProtectedRoute>} />
    <Route path="/workshops/:id" element={<ProtectedRoute><WorkshopDetails /></ProtectedRoute>} />
    <Route path="/materials" element={<ProtectedRoute><MaterialsPage /></ProtectedRoute>} />
    <Route path="/assessments" element={<ProtectedRoute><AssessmentsPage /></ProtectedRoute>} />
    <Route path="/assessments/attempt/:assessmentId" element={<ProtectedRoute allowedRoles={["student"]}><AssessmentAttempt /></ProtectedRoute>} />
    <Route path="/assessments/results" element={<ProtectedRoute><Results /></ProtectedRoute>} />
    <Route path="/submissions" element={<ProtectedRoute allowedRoles={["admin", "institution_admin", "educator"]}><SubmissionsPage /></ProtectedRoute>} />
    <Route path="/certificates" element={<ProtectedRoute><Certificates /></ProtectedRoute>} />
    <Route path="/reports" element={<ProtectedRoute allowedRoles={["admin", "institution_admin", "educator"]}><PerformanceReports /></ProtectedRoute>} />
    <Route path="/reports/ai" element={<ProtectedRoute allowedRoles={["admin", "institution_admin"]}><AdminAIReports /></ProtectedRoute>} />
    <Route path="/reports/ai/scheduled" element={<ProtectedRoute allowedRoles={["admin", "institution_admin"]}><ScheduledAIReports /></ProtectedRoute>} />
    <Route path="/support" element={<ProtectedRoute allowedRoles={["technical_support"]}><SupportConsole /></ProtectedRoute>} />
    <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
    <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

    {/* Management pages */}
    <Route path="/manage/educators" element={<ProtectedRoute allowedRoles={["admin", "institution_admin"]}><EducatorManagement /></ProtectedRoute>} />
    <Route path="/manage/students" element={<ProtectedRoute allowedRoles={["admin", "institution_admin"]}><StudentManagement /></ProtectedRoute>} />
    <Route path="/manage/institutes" element={<ProtectedRoute allowedRoles={["admin"]}><InstituteManagement /></ProtectedRoute>} />
    <Route path="/manage/approvals" element={<ProtectedRoute allowedRoles={["admin"]}><ApprovalPanel /></ProtectedRoute>} />
    <Route path="/manage/salary" element={<ProtectedRoute allowedRoles={["admin", "institution_admin"]}><SalaryManagement /></ProtectedRoute>} />

    {/* AI Content Generator - Accessible to all authenticated users */}
    <Route path="/ai-content-generator" element={<ProtectedRoute><AIContentGenerator /></ProtectedRoute>} /> {/* ADD THIS ROUTE */}

    {/* Legacy educator routes redirect */}
    <Route path="/educator/dashboard" element={<Navigate to="/dashboard/educator" replace />} />
    <Route path="/educator/workshops" element={<Navigate to="/workshops" replace />} />
    <Route path="/educator/materials" element={<Navigate to="/materials" replace />} />
    <Route path="/educator/assessments" element={<Navigate to="/assessments" replace />} />
    <Route path="/educator/submissions" element={<Navigate to="/submissions" replace />} />

    <Route path="/" element={<LandingPage />} />
    <Route path="*" element={<NotFound />} />
  </Routes>
);

export default AppRoutes;