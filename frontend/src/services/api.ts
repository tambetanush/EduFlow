import { apiGet, apiPost, apiPatch, apiDelete } from "@/api/client";
import {
    adaptWorkshopsPage,
    adaptModulesToMaterials,
    adaptAssessments,
    adaptCertificates,
    adaptNotifications,
    adaptAdminStats,
    adaptStudentStats,
    adaptDashboardStats,
    adaptStudentAnalytics,
    adaptWorkshopAnalytics,
    type StudentAnalyticsView,
    type WorkshopAnalyticsView,
} from "@/api/adapters";
import type {
    ApiPage,
    BackendWorkshop,
    BackendModule,
    BackendAssessment,
    BackendQuestion,
    BackendEnrollment,
    BackendCertificate,
    BackendNotification,
    BackendSubmissionResult,
    BackendStudentProgress,
    BackendUser,
    BackendInstitution,
    BackendApprovalRequest,
    BackendSalaryPayment,
    BackendSubmission,
    BackendAssessmentLeaderboard,
    BackendWorkshopLeaderboard,
    BackendLeaderboardStudentDrilldown,
    BackendAdminDashboardInsights,
    BackendInstitutionDashboardAggregate,
    BackendInstitutionStudentRoster,
    BackendInstitutionAttendanceReport,
    BackendParentMessageResponse,
    BackendParentContactDirectory,
    BackendCertificateRecommendationResponse,
    BackendCertificateDownloadResponse,
    BackendMaterialDownloadResponse,
    BackendExportFileResponse,
    BackendInstitutionStudentBulkActionResponse,
    BackendSubmissionReview,
    BackendWorkshopEducatorProfile,
    TokenResponse,
    AdminStatsResponse,
    StudentStatsResponse,
    DashboardStatsResponse,
    BackendStudentAnalytics,
    BackendWorkshopAnalytics,
    BackendAdminAIReportCreateRequest,
    BackendAdminAIReportCreateResponse,
    BackendAdminAIReportStatusResponse,
    BackendAdminAIReportResultResponse,
    BackendAdminAIReportHistoryItem,
    BackendStudentExplanationRequest,
    BackendStudentExplanationResponse,
    BackendStudentExplanationStatusResponse,
    BackendStudentExplanationResultResponse,
    BackendScheduledReportCreateRequest,
    BackendScheduledReportUpdateRequest,
    BackendScheduledReport,
    BackendScheduledReportRun,
    BackendSupportConfigResponse,
    BackendSupportJobDetailResponse,
    BackendSupportJobListItem,
    BackendSupportRerunResponse,
    BackendAuditLog,
    BackendRateLimitEvent,
    BackendCacheStatsResponse,
    BackendPublicStudentProfileResponse,
} from "@/api/types";
import type {
    Workshop,
    Material,
    Assessment,
    Certificate,
    Notification,
    DashboardStats,
    Submission,
} from "@/mock/mockData";

const WORKSHOP_LIMIT = 25;
const API_ORIGIN = String(
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
).replace(/\/+$/, "");

const fetchAllWorkshopItems = async (): Promise<BackendWorkshop[]> => {
    const items: BackendWorkshop[] = [];
    let offset = 0;

    while (true) {
        const page = await apiGet<ApiPage<BackendWorkshop>>("/workshops/", {
            params: { limit: WORKSHOP_LIMIT, offset },
        });

        items.push(...page.items);

        if (page.items.length === 0 || items.length >= page.total) {
            break;
        }

        offset += page.limit;
    }

    return items;
};

const buildWorkshopLookup = (workshops: Workshop[]) =>
    Object.fromEntries(workshops.map((w) => [w.id, w.name]));

const formatDateTime = (value?: string | null) => {
    if (!value) return "";
    const parsed = Date.parse(value);
    if (Number.isNaN(parsed)) return value;
    return new Date(parsed).toISOString().slice(0, 16).replace("T", " ");
};

export const resolveBackendMediaUrl = (relativePath?: string | null) => {
    if (!relativePath) return "";
    if (
        relativePath.startsWith("http://") ||
        relativePath.startsWith("https://")
    )
        return relativePath;
    const normalized = relativePath.startsWith("/")
        ? relativePath
        : `/${relativePath}`;
    return `${API_ORIGIN}${normalized}`;
};

export const fetchWorkshops = async (): Promise<Workshop[]> => {
    const workshopItems = await fetchAllWorkshopItems();

    // Map institution_id -> name when possible (avoids showing raw UUIDs in the UI).
    let institutionLookup: Record<string, string> = {};
    try {
        const institutions = await apiGet<BackendInstitution[]>(
            "/institutions/",
            { params: { limit: 200 } },
        );
        institutionLookup = Object.fromEntries(
            institutions.map((i) => [i.id, i.name]),
        );
    } catch {
        institutionLookup = {};
    }

    return adaptWorkshopsPage(
        {
            items: workshopItems,
            total: workshopItems.length,
            offset: 0,
            limit: workshopItems.length || WORKSHOP_LIMIT,
        },
        { institutionLookup },
    );
};

export const fetchWorkshop = async (workshopId: string): Promise<Workshop> => {
    const data = await apiGet<BackendWorkshop>("/workshops/" + workshopId);
    return adaptWorkshopsPage({
        items: [data],
        total: 1,
        offset: 0,
        limit: 1,
    })[0];
};

export const fetchWorkshopEducatorProfile = async (
    workshopId: string,
): Promise<BackendWorkshopEducatorProfile> => {
    return apiGet<BackendWorkshopEducatorProfile>(
        `/workshops/${workshopId}/educator-profile`,
    );
};

export const createWorkshop = async (payload: {
    title: string;
    description?: string | null;
    institution_id?: string | null;
    start_date?: string | null;
    end_date?: string | null;
}): Promise<Workshop> => {
    const data = await apiPost<BackendWorkshop>("/workshops/", payload);
    return adaptWorkshopsPage({
        items: [data],
        total: 1,
        offset: 0,
        limit: 1,
    })[0];
};

export const updateWorkshop = async (
    workshopId: string,
    payload: {
        title?: string | null;
        description?: string | null;
        institution_id?: string | null;
        start_date?: string | null;
        end_date?: string | null;
    },
): Promise<Workshop> => {
    const data = await apiPatch<BackendWorkshop>(
        "/workshops/" + workshopId,
        payload,
    );
    return adaptWorkshopsPage({
        items: [data],
        total: 1,
        offset: 0,
        limit: 1,
    })[0];
};

export const updateAssessmentQuestion = async (
    questionId: string,
    payload: {
        text?: string;
        type?: string;
        marks?: number;
        options?: Array<{ id: string; text: string; is_correct: boolean }>;
    },
): Promise<BackendQuestion> => {
    return apiPatch<BackendQuestion>(`/questions/${questionId}`, payload);
};

export const deleteWorkshop = async (workshopId: string): Promise<void> => {
    await apiDelete<void>("/workshops/" + workshopId);
};


const filterToStudentEnrollments = async (
    workshops: Workshop[],
    studentId?: string,
): Promise<Workshop[]> => {
    if (!studentId) return workshops;
    const enrollmentPage = await fetchEnrollments(studentId);
    const enrolledWorkshopIds = new Set(
        (enrollmentPage.items ?? [])
            .map((item) => item.workshop_id)
            .filter(Boolean) as string[],
    );
    return workshops.filter((workshop) => enrolledWorkshopIds.has(workshop.id));
};

export const fetchMaterials = async (
    options: { studentId?: string } = {},
): Promise<Material[]> => {
    const workshops = await fetchWorkshops();
    const scopedWorkshops = await filterToStudentEnrollments(
        workshops,
        options.studentId,
    );
    const workshopLookup = buildWorkshopLookup(scopedWorkshops);

    if (options.studentId) {
        const settled = await Promise.allSettled(
            scopedWorkshops.map((workshop) =>
                apiGet<ApiPage<BackendModule>>(
                    "/workshops/" + workshop.id + "/modules",
                    { params: { limit: 20 } },
                ),
            ),
        );
        const modules = settled.flatMap((result) =>
            result.status === "fulfilled" ? result.value.items : [],
        );
        return adaptModulesToMaterials(modules, workshopLookup);
    }

    const modulePages = await Promise.all(
        scopedWorkshops.map((workshop) =>
            apiGet<ApiPage<BackendModule>>(
                "/workshops/" + workshop.id + "/modules",
                { params: { limit: 20 } },
            ),
        ),
    );
    const modules = modulePages.flatMap((page) => page.items);
    return adaptModulesToMaterials(modules, workshopLookup);
};

export const fetchAssessments = async (
    options: { studentId?: string } = {},
): Promise<Assessment[]> => {
    const workshops = await fetchWorkshops();
    const scopedWorkshops = await filterToStudentEnrollments(
        workshops,
        options.studentId,
    );
    const workshopLookup = buildWorkshopLookup(scopedWorkshops);

    if (options.studentId) {
        const settled = await Promise.allSettled(
            scopedWorkshops.map((workshop) =>
                apiGet<ApiPage<BackendAssessment>>(
                    "/assessments/workshop/" + workshop.id,
                    { params: { limit: 20 } },
                ),
            ),
        );
        const assessments = settled.flatMap((result) =>
            result.status === "fulfilled" ? result.value.items : [],
        );
        return adaptAssessments(assessments, workshopLookup);
    }

    const assessmentPages = await Promise.all(
        scopedWorkshops.map((workshop) =>
            apiGet<ApiPage<BackendAssessment>>(
                "/assessments/workshop/" + workshop.id,
                { params: { limit: 20 } },
            ),
        ),
    );
    const assessments = assessmentPages.flatMap((page) => page.items);
    return adaptAssessments(assessments, workshopLookup);
};

export const createAssessment = async (payload: {
    workshopId: string;
    moduleId?: string | null;
    title: string;
    totalMarks: number;
    passingMarks: number;
}): Promise<BackendAssessment> => {
    return apiPost<BackendAssessment>("/assessments/", {
        workshop_id: payload.workshopId,
        module_id: payload.moduleId ?? null,
        title: payload.title,
        total_marks: payload.totalMarks,
        pass_mark: payload.passingMarks,
    });
};

export const updateAssessment = async (
    assessmentId: string,
    payload: {
        title?: string;
        totalMarks?: number;
        passingMarks?: number;
        moduleId?: string | null;
    },
): Promise<BackendAssessment> => {
    return apiPatch<BackendAssessment>(`/assessments/${assessmentId}`, {
        ...(payload.title !== undefined ? { title: payload.title } : {}),
        ...(payload.totalMarks !== undefined
            ? { total_marks: payload.totalMarks }
            : {}),
        ...(payload.passingMarks !== undefined
            ? { pass_mark: payload.passingMarks }
            : {}),
        ...(payload.moduleId !== undefined
            ? { module_id: payload.moduleId }
            : {}),
    });
};

export const deleteAssessment = async (assessmentId: string): Promise<void> => {
    await apiDelete<void>(`/assessments/${assessmentId}`);
};

export const fetchAssessmentQuestions = async (
    assessmentId: string,
): Promise<BackendQuestion[]> => {
    const page = await apiGet<ApiPage<BackendQuestion>>(
        `/assessments/${assessmentId}/questions`,
        { params: { limit: 200 } },
    );
    return page.items;
};

export const createAssessmentQuestion = async (
    assessmentId: string,
    payload: {
        text: string;
        type: string;
        marks: number;
        options: Array<{ id: string; text: string; is_correct: boolean }>;
    },
): Promise<BackendQuestion> => {
    return apiPost<BackendQuestion>(`/assessments/${assessmentId}/questions`, {
        assessment_id: assessmentId,
        text: payload.text,
        type: payload.type.toLowerCase(),
        marks: payload.marks,
        options: payload.options,
    });
};

export interface AttemptQuestionOption {
    id: string;
    text: string;
}

export interface AttemptQuestion {
    id: string;
    assessment_id?: string | null;
    text?: string | null;
    type?: string | null;
    marks?: number | null;
    options: AttemptQuestionOption[];
}

export interface StartAttemptResponse {
    submission_id: string;
    assessment_id: string;
    title: string;
    total_marks: number;
    questions: AttemptQuestion[];
}

export interface GradeAttemptResponse {
    submission_id: string;
    score: number;
    correct_count: number;
    total: number;
    pass_fail: boolean;
    per_question: Array<{
        question_id: string;
        question_text: string;
        options: Array<{ id: string; text: string }>;
        student_answer_id?: string | null;
        correct_answer_id?: string | null;
        is_correct: boolean;
        explanation?: string | null;
    }>;
}

export const startAssessmentAttempt = async (
    assessmentId: string,
): Promise<StartAttemptResponse> => {
    return apiPost<StartAttemptResponse>(`/tests/${assessmentId}/start`);
};

export const saveAssessmentAnswers = async (
    submissionId: string,
    answers: Array<{ questionId: string; selectedOptionIds: string[] }>,
) => {
    return apiPost(`/submissions/${submissionId}/answers`, {
        answers: answers.map((answer) => ({
            question_id: answer.questionId,
            selected_option_ids: answer.selectedOptionIds,
        })),
    });
};

export const submitAssessmentAttempt = async (
    assessmentId: string,
    submissionId: string,
): Promise<GradeAttemptResponse> => {
    return apiPost<GradeAttemptResponse>(
        `/tests/${assessmentId}/submit`,
        null,
        {
            params: { submission_id: submissionId },
        },
    );
};

export const fetchSubmissionResult = async (submissionId: string): Promise<BackendSubmissionResult> => {
    return apiGet<BackendSubmissionResult>(`/submissions/${submissionId}/result`);
};

export const fetchStudentProgress = async (): Promise<BackendStudentProgress[]> => {
    return apiGet<BackendStudentProgress[]>('/progress/');
};

export const updateStudentProgress = async (payload: {
    workshopId: string;
    moduleIndex: number;
}): Promise<BackendStudentProgress> => {
    return apiPatch<BackendStudentProgress>('/progress/', {
        workshop_id: payload.workshopId,
        current_module_index: payload.moduleIndex,
    });
};

export const fetchWorkshopModules = async (
    workshopId: string,
): Promise<BackendModule[]> => {
    const page = await apiGet<ApiPage<BackendModule>>(
        "/workshops/" + workshopId + "/modules",
        { params: { limit: 200 } },
    );
    return page.items;
};

export const createWorkshopModule = async (payload: {
    workshopId: string;
    title: string;
    orderIndex?: number;
}): Promise<BackendModule> => {
    return apiPost<BackendModule>("/modules/", {
        workshop_id: payload.workshopId,
        title: payload.title,
        order_index: payload.orderIndex ?? 1,
        materials: [],
    });
};

export const fetchWorkshopAssessments = async (
    workshopId: string,
): Promise<BackendAssessment[]> => {
    const page = await apiGet<ApiPage<BackendAssessment>>(
        "/assessments/workshop/" + workshopId,
        { params: { limit: 200 } },
    );
    return page.items;
};

export const fetchEnrollments = async (
    studentId: string,
): Promise<ApiPage<BackendEnrollment>> => {
    return apiGet<ApiPage<BackendEnrollment>>(
        "/enrollments/student/" + studentId,
        { params: { limit: 200 } },
    );
};

export interface StudentLearningMaterial {
    id: string;
    title: string;
    type: string;
    content: string;
}

export interface StudentLearningModule {
    id: string;
    title: string;
    orderIndex: number;
    materials: StudentLearningMaterial[];
}

export interface StudentLearningCourse {
    workshopId: string;
    workshopName: string;
    workshopDescription: string;
    institution: string;
    startDate: string;
    endDate: string;
    status: Workshop["status"];
    modules: StudentLearningModule[];
}

export const fetchStudentLearningCourses = async (
    studentId: string,
): Promise<StudentLearningCourse[]> => {
    const [enrollmentPage, workshops] = await Promise.all([
        fetchEnrollments(studentId),
        fetchWorkshops(),
    ]);

    const enrolledWorkshopIds = Array.from(
        new Set(
            (enrollmentPage.items ?? [])
                .map((item) => item.workshop_id)
                .filter(Boolean) as string[],
        ),
    );

    const enrolledWorkshops = workshops.filter((workshop) =>
        enrolledWorkshopIds.includes(workshop.id),
    );
    const modulePages = await Promise.all(
        enrolledWorkshops.map(async (workshop) => ({
            workshopId: workshop.id,
            modules: await fetchWorkshopModules(workshop.id),
        })),
    );

    const moduleMap = Object.fromEntries(
        modulePages.map((entry) => [entry.workshopId, entry.modules]),
    );

    return enrolledWorkshops.map((workshop) => {
        const modules = (moduleMap[workshop.id] ?? [])
            .slice()
            .sort((a, b) => (a.order_index ?? 0) - (b.order_index ?? 0))
            .map((module, idx) => ({
                id: module.id,
                title: module.title ?? `Module ${idx + 1}`,
                orderIndex: module.order_index ?? idx,
                materials: (module.materials ?? []).map((material) => ({
                    id: material.id,
                    title: material.title,
                    type: material.type,
                    content: material.content,
                })),
            }));

        return {
            workshopId: workshop.id,
            workshopName: workshop.name,
            workshopDescription: workshop.description,
            institution: workshop.institution,
            startDate: workshop.startDate,
            endDate: workshop.endDate,
            status: workshop.status,
            modules,
        };
    });
};
export const enrollInWorkshop = async (
    studentId: string,
    workshopId: string,
): Promise<BackendEnrollment> => {
    return apiPost<BackendEnrollment>("/enrollments/", {
        student_id: studentId,
        workshop_id: workshopId,
    });
};

const fetchUserLookup = async (ids: string[]) => {
    const map: Record<string, string> = {};
    await Promise.all(
        ids.map(async (id) => {
            try {
                const result = await apiGet<BackendUser>("/users/" + id);
                map[id] = result.name ?? result.email ?? "";
            } catch {
                map[id] = "";
            }
        }),
    );
    return map;
};

export const fetchCertificates = async (
    options: { studentId?: string; asStaff?: boolean } = {},
): Promise<Certificate[]> => {
    const { studentId, asStaff } = options;
    const workshops = await fetchWorkshops();
    const workshopLookup = buildWorkshopLookup(workshops);

    let page: ApiPage<BackendCertificate> = {
        items: [],
        total: 0,
        offset: 0,
        limit: 0,
    };
    if (asStaff) {
        page = await apiGet<ApiPage<BackendCertificate>>("/certificates/", {
            params: { limit: 100 },
        });
    } else if (studentId) {
        page = await apiGet<ApiPage<BackendCertificate>>(
            "/certificates/student/" + studentId,
            { params: { limit: 100 } },
        );
    }

    const missingStudentIds = Array.from(
        new Set(
            page.items
                .filter((c) => !c.student_name)
                .map((item) => item.student_id)
                .filter(Boolean),
        ),
    ) as string[];
    const studentLookup =
        missingStudentIds.length > 0
            ? await fetchUserLookup(missingStudentIds)
            : {};
    return adaptCertificates(page.items, workshopLookup, studentLookup);
};

export const verifyCertificate = async (
    verificationCode: string,
): Promise<BackendCertificate> => {
    return apiGet<BackendCertificate>(
        "/certificates/verify/" + encodeURIComponent(verificationCode),
    );
};

export const fetchNotifications = async (
    userId: string,
): Promise<Notification[]> => {
    const data = await apiGet<ApiPage<BackendNotification>>(
        "/notifications/" + userId,
        { params: { limit: 50 } },
    );
    return adaptNotifications(data.items);
};

export const fetchMyNotifications = async (): Promise<Notification[]> => {
    const items = await apiGet<BackendNotification[]>('/notifications');
    return adaptNotifications(items);
};

export const markNotificationRead = async (
    notificationId: string,
): Promise<BackendNotification> => {
    return apiPatch<BackendNotification>(
        `/notifications/${notificationId}/read`,
    );
};

export const markAllNotificationsRead = async (): Promise<BackendNotification[]> => {
    return apiPatch<BackendNotification[]>('/notifications/read-all');
};

export const deleteNotification = async (
    notificationId: string,
): Promise<void> => {
    await apiDelete<void>(`/notifications/${notificationId}`);
};

export const sendBulkNotifications = async (payload: {
    userIds: string[];
    message: string;
    notificationType?: string;
}): Promise<BackendNotification[]> => {
    return apiPost<BackendNotification[]>("/notifications/send", {
        user_ids: payload.userIds,
        message: payload.message,
        notification_type: payload.notificationType ?? "general",
    });
};

export const fetchSubmissions = async (): Promise<Submission[]> => {
    const workshops = await fetchWorkshops();
    const assessmentPages = await Promise.all(
        workshops.map((workshop) =>
            apiGet<ApiPage<BackendAssessment>>(
                "/assessments/workshop/" + workshop.id,
                { params: { limit: 50 } },
            ),
        ),
    );
    const assessments = assessmentPages.flatMap((page) => page.items);
    const assessmentLookup = Object.fromEntries(
        assessments.map((a) => [a.id, a.title ?? "Assessment"]),
    );

    const submissionPages = await Promise.all(
        assessments.map(async (assessment) => {
            try {
                return await apiGet<ApiPage<BackendSubmission>>(
                    "/submissions/assessment/" + assessment.id,
                    { params: { limit: 200 } },
                );
            } catch {
                return {
                    items: [],
                    total: 0,
                    offset: 0,
                    limit: 0,
                } as ApiPage<BackendSubmission>;
            }
        }),
    );

    const submissions = submissionPages.flatMap((page) => page.items);
    const studentIds = Array.from(
        new Set(submissions.map((s) => s.student_id).filter(Boolean)),
    ) as string[];
    const studentLookup = await fetchUserLookup(studentIds);

    return submissions.map((s) => ({
        id: s.id,
        studentName: studentLookup[s.student_id ?? ""] ?? "",
        assessment: assessmentLookup[s.assessment_id ?? ""] ?? "Assessment",
        score: s.score ?? 0,
        status:
            s.pass_fail === null || s.pass_fail === undefined
                ? "Pending"
                : "Graded",
        submittedAt: formatDateTime(s.submitted_at),
    }));
};

export const uploadModuleMaterial = async (
    moduleId: string,
    file: File,
): Promise<BackendModule> => {
    const formData = new FormData();
    formData.append("file", file);
    return apiPost<BackendModule>(
        `/modules/${moduleId}/materials/upload`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } },
    );
};

export const createModuleMaterial = async (
    moduleId: string,
    payload: {
        title: string;
        type: "video" | "pdf" | "link" | "text";
        content: string;
    },
): Promise<BackendModule> => {
    return apiPost<BackendModule>(`/materials/${moduleId}`, {
        title: payload.title,
        type: payload.type,
        content: payload.content,
    });
};

export const deleteModuleMaterial = async (
    moduleId: string,
    materialId: string,
): Promise<BackendModule> => {
    return apiDelete<BackendModule>(`/materials/${moduleId}/${materialId}`);
};

export const fetchAdminStats = async () => {
    const data = await apiGet<AdminStatsResponse>("/dashboard/admin");
    return adaptAdminStats(data);
};

export const fetchStudentStats = async (studentId: string) => {
    const data = await apiGet<StudentStatsResponse>(
        "/dashboard/student/" + studentId,
    );
    return adaptStudentStats(data);
};

export const fetchDashboardStats = async (): Promise<DashboardStats> => {
    const data = await apiGet<DashboardStatsResponse>("/dashboard/educator");
    return adaptDashboardStats(data);
};

export const fetchCurrentUser = async () => {
    return apiGet<BackendUser>("/users/me");
};

export const registerUser = async (payload: {
    name: string;
    email: string;
    password: string;
    role: string;
}) => {
    return apiPost<BackendUser>("/auth/register", payload);
};

export const updateUser = async (
    userId: string,
    payload: {
        name?: string;
        phone?: string;
        profile_photo?: string;
        bio?: string;
        department?: string;
        parent_name?: string;
        parent_email?: string;
        institution_admin_name?: string;
        institution_admin_address?: string;
        institution_admin_code?: string;
        theme?: string;
        institution_id?: string;
    },
) => {
    return apiPatch<BackendUser>("/users/" + userId, payload);
};

export const uploadUserProfilePhoto = async (
    userId: string,
    file: File,
): Promise<BackendUser> => {
    const formData = new FormData();
    formData.append("file", file);
    return apiPost<BackendUser>(`/users/${userId}/profile-photo`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
};

export const loginUser = async (payload: {
    email: string;
    password: string;
    role: string;
}) => {
    return apiPost<TokenResponse>("/auth/login", payload);
};

export const fetchStudents = async (): Promise<
    { id: string; name: string }[]
> => {
    const page = await apiGet<ApiPage<BackendUser>>("/users/", {
        params: { limit: 200 },
    });
    return page.items
        .filter((u) => u.role === "student")
        .map((u) => ({ id: u.id, name: u.name ?? u.email }));
};

export const generateCertificate = async (payload: {
    studentId: string;
    workshopId: string;
}): Promise<BackendCertificate> => {
    return apiPost<BackendCertificate>("/certificates/generate", {
        student_id: payload.studentId,
        workshop_id: payload.workshopId,
    });
};

export const recommendCertificate = async (payload: {
    studentId: string;
    workshopId: string;
    note?: string;
}): Promise<BackendCertificateRecommendationResponse> => {
    return apiPost<BackendCertificateRecommendationResponse>(
        "/certificates/recommend",
        {
            student_id: payload.studentId,
            workshop_id: payload.workshopId,
            note: payload.note,
        },
    );
};

export const fetchCertificateDownload = async (
    certificateId: string,
): Promise<BackendCertificateDownloadResponse> => {
    return apiGet<BackendCertificateDownloadResponse>(
        `/certificates/${certificateId}/download`,
    );
};

export const fetchInstitutions = async (): Promise<BackendInstitution[]> => {
    return apiGet<BackendInstitution[]>("/institutions/", {
        params: { limit: 200 },
    });
};

export const createInstitution = async (payload: {
    name: string;
    code?: string;
    address?: string;
    contact_email?: string;
    contact_phone?: string;
}): Promise<BackendInstitution> => {
    return apiPost<BackendInstitution>("/institutions/", payload);
};

export const updateInstitutionStatus = async (
    institutionId: string,
    isActive: boolean,
): Promise<BackendInstitution> => {
    return apiPatch<BackendInstitution>(`/institutions/${institutionId}/status`, {
        is_active: isActive,
    });
};

export const fetchUsers = async (
    options: { limit?: number; offset?: number } = {},
): Promise<ApiPage<BackendUser>> => {
    const { limit = 200, offset = 0 } = options;
    const safeLimit = Math.min(limit, 200); // backend Page caps limit at 200
    return apiGet<ApiPage<BackendUser>>("/users/", {
        params: { limit: safeLimit, offset },
    });
};

export const fetchAllUsers = async (
    options: { max?: number } = {},
): Promise<BackendUser[]> => {
    const max = options.max ?? 500;
    const limit = 200;
    let offset = 0;
    let items: BackendUser[] = [];

    while (items.length < max) {
        const page = await fetchUsers({ limit, offset });
        items = items.concat(page.items);
        if (page.items.length === 0) break;
        if (items.length >= page.total) break;
        offset += limit;
    }

    return items.slice(0, max);
};

export const fetchApprovalRequests = async (
    options: { status?: string; limit?: number; offset?: number } = {},
) => {
    const { status, limit = 200, offset = 0 } = options;
    const safeLimit = Math.min(limit, 200); // backend Page caps limit at 200
    return apiGet<ApiPage<BackendApprovalRequest>>("/approvals/requests", {
        params: { limit: safeLimit, offset, ...(status ? { status } : {}) },
    });
};

export const createApprovalRequest = async (payload: {
    request_type: string;
    payload: Record<string, unknown>;
}) => {
    return apiPost<BackendApprovalRequest>("/approvals/requests", {
        request_type: payload.request_type,
        payload: payload.payload,
    });
};

export const approveApprovalRequest = async (requestId: string) => {
    return apiPost<BackendApprovalRequest>(
        `/approvals/requests/${requestId}/approve`,
    );
};

export const rejectApprovalRequest = async (requestId: string) => {
    return apiPost<BackendApprovalRequest>(
        `/approvals/requests/${requestId}/reject`,
    );
};

export const fetchSalaryPayments = async (
    options: { month?: string; limit?: number; offset?: number } = {},
) => {
    const { month, limit = 200, offset = 0 } = options;
    const safeLimit = Math.min(limit, 200); // backend Page caps limit at 200
    return apiGet<ApiPage<BackendSalaryPayment>>("/salaries/", {
        params: { limit: safeLimit, offset, ...(month ? { month } : {}) },
    });
};

export const paySalary = async (payload: {
    educatorId: string;
    month: string;
    amount: number;
}) => {
    return apiPost<BackendSalaryPayment>("/salaries/pay", {
        educator_id: payload.educatorId,
        month: payload.month,
        amount: payload.amount,
    });
};

export const updateEducatorSalary = async (
    educatorId: string,
    payload: {
        salary_amount: number;
        salary_type: string;
    },
) => {
    return apiPatch<BackendUser>(`/users/${educatorId}/salary`, payload);
};

export const fetchWorkshopAnalytics = async (
    workshopId: string,
): Promise<WorkshopAnalyticsView> => {
    const data = await apiGet<BackendWorkshopAnalytics>(
        "/analytics/workshop/" + workshopId,
    );
    return adaptWorkshopAnalytics(data);
};

export const fetchStudentAnalytics = async (
    studentId: string,
): Promise<StudentAnalyticsView> => {
    const data = await apiGet<BackendStudentAnalytics>(
        "/analytics/student/" + studentId,
    );
    return adaptStudentAnalytics(data);
};

export const fetchAssessmentLeaderboard = async (
    assessmentId: string,
): Promise<BackendAssessmentLeaderboard> => {
    return apiGet<BackendAssessmentLeaderboard>(
        `/analytics/leaderboard/assessment/${assessmentId}`,
    );
};

export const fetchWorkshopLeaderboard = async (
    workshopId: string,
): Promise<BackendWorkshopLeaderboard> => {
    return apiGet<BackendWorkshopLeaderboard>(
        `/analytics/leaderboard/workshop/${workshopId}`,
    );
};

export const fetchAssessmentLeaderboardDrilldown = async (
    assessmentId: string,
    studentId: string,
): Promise<BackendLeaderboardStudentDrilldown> => {
    return apiGet<BackendLeaderboardStudentDrilldown>(
        `/analytics/leaderboard/assessment/${assessmentId}/student/${studentId}`,
    );
};

export const fetchWorkshopLeaderboardDrilldown = async (
    workshopId: string,
    studentId: string,
): Promise<BackendLeaderboardStudentDrilldown> => {
    return apiGet<BackendLeaderboardStudentDrilldown>(
        `/analytics/leaderboard/workshop/${workshopId}/student/${studentId}`,
    );
};

export const fetchInstitutionDashboardAggregate =
    async (): Promise<BackendInstitutionDashboardAggregate> => {
        return apiGet<BackendInstitutionDashboardAggregate>(
            "/analytics/institution/dashboard",
        );
    };

export const fetchAdminDashboardInsights =
    async (): Promise<BackendAdminDashboardInsights> => {
        return apiGet<BackendAdminDashboardInsights>(
            "/analytics/admin/insights",
        );
    };

export const fetchInstitutionStudentRoster =
    async (): Promise<BackendInstitutionStudentRoster> => {
        return apiGet<BackendInstitutionStudentRoster>(
            "/analytics/institution/students",
        );
    };

export const fetchInstitutionAttendanceReport =
    async (): Promise<BackendInstitutionAttendanceReport> => {
        return apiGet<BackendInstitutionAttendanceReport>(
            "/analytics/institution/attendance-report",
        );
    };


export const applyInstitutionStudentBulkAction = async (payload: {
    studentIds: string[];
    action: "set_inactive";
}): Promise<BackendInstitutionStudentBulkActionResponse> => {
    return apiPost<BackendInstitutionStudentBulkActionResponse>(
        "/analytics/institution/students/bulk-action",
        {
            student_ids: payload.studentIds,
            action: payload.action,
        },
    );
};

export const exportInstitutionStudents = async (
    studentIds: string[],
): Promise<BackendExportFileResponse> => {
    return apiGet<BackendExportFileResponse>(
        "/analytics/institution/students/export",
        {
            params: { student_ids: studentIds },
        },
    );
};

export const exportInstitutionAttendanceReport =
    async (): Promise<BackendExportFileResponse> => {
        return apiGet<BackendExportFileResponse>(
            "/analytics/institution/attendance-report/export",
        );
    };

export const exportInstitutionDashboardReport =
    async (): Promise<BackendExportFileResponse> => {
        return apiGet<BackendExportFileResponse>(
            "/analytics/institution/dashboard/export",
        );
    };

export const exportPerformanceReport =
    async (): Promise<BackendExportFileResponse> => {
        return apiGet<BackendExportFileResponse>(
            "/analytics/reports/performance/export",
        );
    };
export const fetchParentContactDirectory = async (studentIds: string[]): Promise<BackendParentContactDirectory> => {
    if (studentIds.length === 0) {
        return { items: [], total: 0 };
    }
    return apiGet<BackendParentContactDirectory>(
        "/communication/parent-contacts",
        {
            params: { student_ids: studentIds },
        },
    );
};
export const sendParentEmailMessage = async (payload: {
    studentIds: string[];
    subject: string;
    body: string;
}): Promise<BackendParentMessageResponse> => {
    return apiPost<BackendParentMessageResponse>(
        "/communication/parent-email",
        {
            student_ids: payload.studentIds,
            subject: payload.subject,
            body: payload.body,
        },
    );
};

export const fetchSubmissionReview = async (
    submissionId: string,
): Promise<BackendSubmissionReview> => {
    return apiGet<BackendSubmissionReview>(
        `/submissions/${submissionId}/review`,
    );
};

export const gradeSubmission = async (
    submissionId: string,
): Promise<BackendSubmission> => {
    return apiPost<BackendSubmission>(`/submissions/${submissionId}/grade`);
};

export const fetchMaterialDownload = async (
    moduleId: string,
    materialId: string,
): Promise<BackendMaterialDownloadResponse> => {
    return apiGet<BackendMaterialDownloadResponse>(
        `/materials/${moduleId}/${materialId}/download`,
    );
};




export const createAdminAIReport = async (
    payload: BackendAdminAIReportCreateRequest,
): Promise<BackendAdminAIReportCreateResponse> => {
    return apiPost<BackendAdminAIReportCreateResponse>("/ai/reports/", payload);
};

export const fetchAdminAIReportStatus = async (
    reportId: string,
): Promise<BackendAdminAIReportStatusResponse> => {
    return apiGet<BackendAdminAIReportStatusResponse>(`/ai/reports/${reportId}/status`);
};

export const fetchAdminAIReportResult = async (
    reportId: string,
): Promise<BackendAdminAIReportResultResponse> => {
    return apiGet<BackendAdminAIReportResultResponse>(`/ai/reports/${reportId}/result`);
};

export const fetchAdminAIReportsHistory = async (
    options: { institutionId?: string; limit?: number; offset?: number } = {},
): Promise<ApiPage<BackendAdminAIReportHistoryItem>> => {
    const { institutionId, limit = 50, offset = 0 } = options;
    const safeLimit = Math.min(limit, 200);
    return apiGet<ApiPage<BackendAdminAIReportHistoryItem>>("/ai/reports/", {
        params: {
            limit: safeLimit,
            offset,
            ...(institutionId ? { institution_id: institutionId } : {}),
        },
    });
};

export const createStudentAnswerExplanation = async (
    payload: BackendStudentExplanationRequest,
): Promise<BackendStudentExplanationResponse> => {
    return apiPost<BackendStudentExplanationResponse>("/ai/student-explanations/", payload);
};

export const fetchStudentExplanationStatus = async (
    explanationId: string,
): Promise<BackendStudentExplanationStatusResponse> => {
    return apiGet<BackendStudentExplanationStatusResponse>(`/ai/student-explanations/${explanationId}/status`);
};

export const fetchStudentExplanationResult = async (
    explanationId: string,
): Promise<BackendStudentExplanationResultResponse> => {
    return apiGet<BackendStudentExplanationResultResponse>(`/ai/student-explanations/${explanationId}/result`);
};

export const createScheduledAIReport = async (
    payload: BackendScheduledReportCreateRequest,
): Promise<BackendScheduledReport> => {
    return apiPost<BackendScheduledReport>("/ai/scheduled-reports/", payload);
};

export const fetchScheduledAIReports = async (
    options: { limit?: number; offset?: number } = {},
): Promise<ApiPage<BackendScheduledReport>> => {
    const { limit = 50, offset = 0 } = options;
    const safeLimit = Math.min(limit, 200);
    return apiGet<ApiPage<BackendScheduledReport>>("/ai/scheduled-reports/", {
        params: { limit: safeLimit, offset },
    });
};

export const updateScheduledAIReport = async (
    scheduleId: string,
    payload: BackendScheduledReportUpdateRequest,
): Promise<BackendScheduledReport> => {
    return apiPatch<BackendScheduledReport>(`/ai/scheduled-reports/${scheduleId}`, payload);
};

export const fetchScheduledAIReportRuns = async (
    scheduleId: string,
    options: { limit?: number; offset?: number } = {},
): Promise<ApiPage<BackendScheduledReportRun>> => {
    const { limit = 50, offset = 0 } = options;
    const safeLimit = Math.min(limit, 200);
    return apiGet<ApiPage<BackendScheduledReportRun>>(`/ai/scheduled-reports/${scheduleId}/runs`, {
        params: { limit: safeLimit, offset },
    });
};

export const fetchSupportConfig = async (): Promise<BackendSupportConfigResponse> => {
    return apiGet<BackendSupportConfigResponse>("/support/config");
};

export const fetchSupportJobs = async (
    options: {
        status?: string;
        feature_type?: string;
        institution_id?: string;
        requester_user_id?: string;
        limit?: number;
        offset?: number;
    } = {},
): Promise<ApiPage<BackendSupportJobListItem>> => {
    const { limit = 50, offset = 0, ...rest } = options;
    const safeLimit = Math.min(limit, 200);
    return apiGet<ApiPage<BackendSupportJobListItem>>("/support/jobs", {
        params: { limit: safeLimit, offset, ...rest },
    });
};

export const fetchSupportJobDetail = async (
    generationId: string,
): Promise<BackendSupportJobDetailResponse> => {
    return apiGet<BackendSupportJobDetailResponse>(`/support/jobs/${generationId}`);
};

export const rerunSupportJob = async (
    generationId: string,
): Promise<BackendSupportRerunResponse> => {
    return apiPost<BackendSupportRerunResponse>(`/support/jobs/${generationId}/rerun`, {});
};

export const fetchSupportAuditLogs = async (
    options: { limit?: number; offset?: number; since_hours?: number; action?: string } = {},
): Promise<ApiPage<BackendAuditLog>> => {
    const { limit = 50, offset = 0, ...rest } = options;
    const safeLimit = Math.min(limit, 200);
    return apiGet<ApiPage<BackendAuditLog>>("/support/audit-logs", {
        params: { limit: safeLimit, offset, ...rest },
    });
};

export const fetchSupportRateLimitEvents = async (
    options: { limit?: number; offset?: number; since_hours?: number; key_prefix?: string; allowed?: boolean } = {},
): Promise<ApiPage<BackendRateLimitEvent>> => {
    const { limit = 50, offset = 0, ...rest } = options;
    const safeLimit = Math.min(limit, 200);
    return apiGet<ApiPage<BackendRateLimitEvent>>("/support/rate-limit-events", {
        params: { limit: safeLimit, offset, ...rest },
    });
};

export const fetchSupportCacheStats = async (): Promise<BackendCacheStatsResponse> => {
    return apiGet<BackendCacheStatsResponse>("/support/cache-stats");
};

export const getPublicStudentProfile = async (
    studentId: string,
): Promise<BackendPublicStudentProfileResponse> => {
    return apiGet<BackendPublicStudentProfileResponse>(
        `/users/${studentId}/public-profile`,
    );
};


