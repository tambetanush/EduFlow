export type UserRole = "admin" | "institution_admin" | "educator" | "student" | "technical_support";

export interface AppUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  institution?: string;
}

export interface Workshop {
  id: string;
  name: string;
  description: string;
  institution: string;
  startDate: string;
  endDate: string;
  studentsEnrolled: number;
  status: "Active" | "Upcoming" | "Completed";
}

export interface Material {
  id: string;
  title: string;
  workshop: string;
  fileType: string;
  materialType?: "video" | "pdf" | "link" | "text";
  content?: string;
  uploadDate: string;
  moduleId?: string;
  moduleTitle?: string;
}

export interface Assessment {
  id: string;
  title: string;
  workshop: string;
  totalMarks: number;
  passingMarks: number;
  status?: "Published" | "Draft";
  duration?: number;
}

export interface Question {
  id: string;
  text: string;
  options: string[];
  correctIndex: number;
}

export interface Submission {
  id: string;
  studentName: string;
  assessment: string;
  score: number;
  status: "Graded" | "Pending" | "Late";
  submittedAt: string;
}

export interface Certificate {
  id: string;
  certificateId: string;
  studentName: string;
  workshop: string;
  completionDate: string;
  status: "Issued" | "Pending";
  studentId?: string;
  workshopId?: string;
  downloadUrl?: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: "info" | "success" | "warning";
  date: string;
  read: boolean;
}

export interface DashboardStats {
  assignedWorkshops: number;
  materialsUploaded: number;
  activeAssessments: number;
  pendingSubmissions: number;
}

export interface AdminStats {
  totalInstitutions: number;
  totalWorkshops: number;
  totalEducators: number;
  totalStudents: number;
  certificatesIssued: number;
  activeWorkshops: number;
}

export interface StudentStats {
  enrolledWorkshops: number;
  completedAssessments: number;
  averageScore: number;
  certificatesEarned: number;
}

export const mockUsers: Record<string, AppUser> = {
  admin: { id: "u1", name: "Rajesh Verma", email: "admin@eduflow.com", role: "admin" },
  institution: { id: "u2", name: "Dr. Meena Sharma", email: "institution@eduflow.com", role: "institution_admin", institution: "IIT Delhi" },
  educator: { id: "u3", name: "Dr. Anand Kumar", email: "educator@eduflow.com", role: "educator", institution: "IIT Delhi" },
  student: { id: "u4", name: "Aarav Sharma", email: "student@eduflow.com", role: "student", institution: "IIT Delhi" },
};

export const dashboardStats: DashboardStats = {
  assignedWorkshops: 8,
  materialsUploaded: 24,
  activeAssessments: 5,
  pendingSubmissions: 37,
};

export const adminStats: AdminStats = {
  totalInstitutions: 12,
  totalWorkshops: 48,
  totalEducators: 36,
  totalStudents: 1250,
  certificatesIssued: 840,
  activeWorkshops: 15,
};

export const studentStats: StudentStats = {
  enrolledWorkshops: 4,
  completedAssessments: 7,
  averageScore: 82,
  certificatesEarned: 2,
};

export const workshops: Workshop[] = [
  { id: "1", name: "React Fundamentals", description: "Introduction to React 18 with hooks and modern patterns", institution: "IIT Delhi", startDate: "2026-03-10", endDate: "2026-04-10", studentsEnrolled: 42, status: "Active" },
  { id: "2", name: "Python for Data Science", description: "Hands-on Python workshop covering pandas, numpy, and matplotlib", institution: "IIT Bombay", startDate: "2026-03-15", endDate: "2026-04-15", studentsEnrolled: 35, status: "Active" },
  { id: "3", name: "Cloud Computing Basics", description: "AWS fundamentals including EC2, S3, and Lambda", institution: "NIT Trichy", startDate: "2026-04-01", endDate: "2026-05-01", studentsEnrolled: 28, status: "Upcoming" },
  { id: "4", name: "UI/UX Design Principles", description: "Design thinking and prototyping with Figma", institution: "IIT Delhi", startDate: "2026-02-01", endDate: "2026-03-01", studentsEnrolled: 50, status: "Completed" },
  { id: "5", name: "Machine Learning Intro", description: "Supervised and unsupervised learning with scikit-learn", institution: "IIT Madras", startDate: "2026-04-10", endDate: "2026-05-10", studentsEnrolled: 30, status: "Upcoming" },
  { id: "6", name: "DevOps Essentials", description: "CI/CD pipelines, Docker, and Kubernetes basics", institution: "BITS Pilani", startDate: "2026-03-20", endDate: "2026-04-20", studentsEnrolled: 22, status: "Active" },
];

export const materials: Material[] = [
  { id: "1", title: "React Hooks Guide", workshop: "React Fundamentals", fileType: "PDF", uploadDate: "2026-03-05" },
  { id: "2", title: "Component Patterns", workshop: "React Fundamentals", fileType: "PDF", uploadDate: "2026-03-06" },
  { id: "3", title: "Pandas Cheat Sheet", workshop: "Python for Data Science", fileType: "PDF", uploadDate: "2026-03-10" },
  { id: "4", title: "AWS Setup Guide", workshop: "Cloud Computing Basics", fileType: "PDF", uploadDate: "2026-03-12" },
  { id: "5", title: "Figma Basics Slides", workshop: "UI/UX Design Principles", fileType: "PPTX", uploadDate: "2026-02-05" },
  { id: "6", title: "Docker Handbook", workshop: "DevOps Essentials", fileType: "PDF", uploadDate: "2026-03-18" },
];

export const assessments: Assessment[] = [
  { id: "1", title: "React Components Quiz", workshop: "React Fundamentals", totalMarks: 100, passingMarks: 40, status: "Published" },
  { id: "2", title: "Hooks Practical Test", workshop: "React Fundamentals", totalMarks: 50, passingMarks: 20, status: "Published" },
  { id: "3", title: "Data Analysis Assignment", workshop: "Python for Data Science", totalMarks: 100, passingMarks: 45, status: "Draft" },
  { id: "4", title: "Cloud Architecture Quiz", workshop: "Cloud Computing Basics", totalMarks: 75, passingMarks: 30, status: "Draft" },
  { id: "5", title: "Design Portfolio Review", workshop: "UI/UX Design Principles", totalMarks: 100, passingMarks: 50, status: "Published" },
];

export const sampleQuestions: Question[] = [
  { id: "q1", text: "What is the correct way to create a React component?", options: ["function App() {}", "class App {}", "const App = new Component()", "App.create()"], correctIndex: 0 },
  { id: "q2", text: "Which hook is used for side effects?", options: ["useState", "useEffect", "useContext", "useMemo"], correctIndex: 1 },
  { id: "q3", text: "What does JSX stand for?", options: ["JavaScript XML", "JavaScript Extension", "Java Syntax Extension", "JSON XML"], correctIndex: 0 },
  { id: "q4", text: "Which method is used to update state in a functional component?", options: ["this.setState()", "setState()", "useState setter", "updateState()"], correctIndex: 2 },
  { id: "q5", text: "What is the virtual DOM?", options: ["A real DOM copy", "A lightweight JS representation of the DOM", "A browser API", "A CSS framework"], correctIndex: 1 },
];

export const submissions: Submission[] = [
  { id: "1", studentName: "Aarav Sharma", assessment: "React Components Quiz", score: 85, status: "Graded", submittedAt: "2026-03-06 14:30" },
  { id: "2", studentName: "Priya Patel", assessment: "React Components Quiz", score: 92, status: "Graded", submittedAt: "2026-03-06 15:10" },
  { id: "3", studentName: "Rohan Gupta", assessment: "Hooks Practical Test", score: 0, status: "Pending", submittedAt: "2026-03-07 09:00" },
  { id: "4", studentName: "Sneha Reddy", assessment: "React Components Quiz", score: 0, status: "Pending", submittedAt: "2026-03-07 10:20" },
  { id: "5", studentName: "Vikram Singh", assessment: "Design Portfolio Review", score: 78, status: "Graded", submittedAt: "2026-03-05 16:45" },
  { id: "6", studentName: "Ananya Iyer", assessment: "Hooks Practical Test", score: 0, status: "Late", submittedAt: "2026-03-08 08:00" },
];

export const certificates: Certificate[] = [
  { id: "1", certificateId: "VSETU-2026-001", studentName: "Aarav Sharma", workshop: "UI/UX Design Principles", completionDate: "2026-03-01", status: "Issued" },
  { id: "2", certificateId: "VSETU-2026-002", studentName: "Priya Patel", workshop: "UI/UX Design Principles", completionDate: "2026-03-01", status: "Issued" },
  { id: "3", certificateId: "VSETU-2026-003", studentName: "Vikram Singh", workshop: "UI/UX Design Principles", completionDate: "2026-03-01", status: "Issued" },
  { id: "4", certificateId: "VSETU-2026-004", studentName: "Rohan Gupta", workshop: "React Fundamentals", completionDate: "", status: "Pending" },
];

export const notifications: Notification[] = [
  { id: "1", title: "New Assessment Published", message: "React Components Quiz is now available for students.", type: "info", date: "2026-03-07", read: false },
  { id: "2", title: "Workshop Starting Soon", message: "Cloud Computing Basics starts on April 1st.", type: "warning", date: "2026-03-06", read: false },
  { id: "3", title: "Results Published", message: "Design Portfolio Review results are now available.", type: "success", date: "2026-03-05", read: true },
  { id: "4", title: "Certificate Issued", message: "Certificates for UI/UX Design Principles have been issued.", type: "success", date: "2026-03-04", read: true },
  { id: "5", title: "Submission Deadline", message: "Hooks Practical Test deadline is approaching.", type: "warning", date: "2026-03-07", read: false },
];
