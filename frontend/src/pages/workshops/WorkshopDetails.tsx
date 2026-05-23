import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Mail, Building2 } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTabs from "@/components/ui-custom/VTabs";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import { adaptModulesToMaterials, adaptAssessments } from "@/api/adapters";
import { fetchWorkshop, fetchWorkshopAssessments, fetchWorkshopEducatorProfile, fetchWorkshopModules } from "@/services/api";
type WorkshopAssessmentRow = ReturnType<typeof adaptAssessments>[number];

const WorkshopDetails = () => {
  const { id } = useParams();
  const { data: workshop } = useQuery({
    queryKey: ["workshop", id],
    queryFn: () => fetchWorkshop(id ?? ""),
    enabled: Boolean(id),
  });

  const { data: modules } = useQuery({
    queryKey: ["workshopModules", id],
    queryFn: () => fetchWorkshopModules(id ?? ""),
    enabled: Boolean(id),
  });

  const { data: workshopAssessments } = useQuery({
    queryKey: ["workshopAssessments", id],
    queryFn: () => fetchWorkshopAssessments(id ?? ""),
    enabled: Boolean(id),
  });
  const educatorQuery = useQuery({
    queryKey: ["workshopEducatorProfile", id],
    queryFn: () => fetchWorkshopEducatorProfile(id ?? ""),
    enabled: Boolean(id),
  });

  if (!workshop) {
    return (
      <DashboardLayout title="Workshop Details">
        <p className="text-muted-foreground">Workshop not found.</p>
      </DashboardLayout>
    );
  }
  const workshopLookup = { [workshop.id]: workshop.name };
  const relatedMaterials = modules ? adaptModulesToMaterials(modules, workshopLookup) : [];
  const relatedAssessments = workshopAssessments ? adaptAssessments(workshopAssessments, workshopLookup) : [];

  const tabs = [
    {
      key: "overview",
      label: "Overview",
      content: (
        <div className="grid gap-6 sm:grid-cols-2">
          <VCard>
            <p className="text-sm text-muted-foreground mb-1">Description</p>
            <p className="text-foreground">{workshop.description}</p>
          </VCard>
          <VCard>
            <div className="space-y-3">
              <div><span className="text-sm text-muted-foreground">Institution: </span><span className="text-foreground font-medium">{workshop.institution}</span></div>
              <div><span className="text-sm text-muted-foreground">Duration: </span><span className="text-foreground font-medium">{workshop.startDate} — {workshop.endDate}</span></div>
              <div><span className="text-sm text-muted-foreground">Students: </span><span className="text-foreground font-medium">{workshop.studentsEnrolled}</span></div>
              <div><span className="text-sm text-muted-foreground">Status: </span><VBadge variant={workshop.status === "Active" ? "success" : "outline"}>{workshop.status}</VBadge></div>
            </div>
          </VCard>
        </div>
      ),
    },
    {
      key: "educator",
      label: "Educator",
      content: (
        <VCard className="p-6">
          {educatorQuery.isLoading && <p className="text-xs text-muted-foreground mb-4">Loading educator profile...</p>}
          {educatorQuery.isError && <p className="text-xs text-muted-foreground mb-4">Unable to load educator profile.</p>}
          {educatorQuery.data && (
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
            <div className="h-20 w-20 rounded-full vidya-gradient flex items-center justify-center text-primary-foreground text-2xl font-bold shrink-0">
              {educatorQuery.data.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
            </div>
            <div className="text-center sm:text-left">
              <h3 className="text-xl font-bold text-foreground">{educatorQuery.data.name}</h3>
              <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-muted-foreground justify-center sm:justify-start">
                <span className="flex items-center gap-1"><Mail className="h-3.5 w-3.5" /> {educatorQuery.data.email}</span>
                <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5" /> {educatorQuery.data.department}</span>
              </div>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{educatorQuery.data.bio}</p>
            </div>
          </div>
          )}
        </VCard>
      ),
    },
    {
      key: "materials",
      label: "Materials",
      content: (
        <VTable
          columns={[
            { key: "title", header: "Title" },
            { key: "fileType", header: "Type" },
            { key: "uploadDate", header: "Uploaded" },
          ]}
          data={relatedMaterials}
        />
      ),
    },
    {
      key: "assessments",
      label: "Assessments",
      content: (
        <VTable
          columns={[
            { key: "title", header: "Title" },
            { key: "totalMarks", header: "Total Marks" },
            { key: "status", header: "Status", render: (row: WorkshopAssessmentRow) => <VBadge variant={row.status === "Published" ? "success" : "outline"}>{row.status}</VBadge> },
          ]}
          data={relatedAssessments}
        />
      ),
    },
  ];

  return (
    <DashboardLayout title={workshop.name}>
      <VTabs tabs={tabs} />
    </DashboardLayout>
  );
};

export default WorkshopDetails;
