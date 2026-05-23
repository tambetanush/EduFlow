import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Upload,
  Eye,
  Trash2,
  Download,
  FileText,
  Link2,
  Search,
  PlayCircle,
  StickyNote,
  ExternalLink,
} from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VTable from "@/components/ui-custom/VTable";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VDrawer from "@/components/ui-custom/VDrawer";
import VConfirmDialog from "@/components/ui-custom/VConfirmDialog";
import { useVToast } from "@/components/ui-custom/VToast";
import { useAuth } from "@/hooks/useAuth";
import { useRole } from "@/hooks/useRole";
import {
  createWorkshopModule,
  createModuleMaterial,
  deleteModuleMaterial,
  fetchMaterialDownload,
  fetchMaterials,
  fetchWorkshopModules,
  fetchWorkshops,
  resolveBackendMediaUrl,
  uploadModuleMaterial,
} from "@/services/api";
import type { Material } from "@/mock/mockData";

type MaterialInputMode = "file" | "video" | "pdf" | "link" | "text";

const modeToType: Record<Exclude<MaterialInputMode, "file">, "video" | "pdf" | "link" | "text"> = {
  video: "video",
  pdf: "pdf",
  link: "link",
  text: "text",
};

const materialIcons: Record<string, React.ElementType> = {
  video: PlayCircle,
  pdf: FileText,
  link: Link2,
  text: StickyNote,
};

const toYouTubeEmbedUrl = (url: string): string | null => {
  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes("youtube.com")) {
      const id = parsed.searchParams.get("v");
      return id ? `https://www.youtube.com/embed/${id}` : null;
    }
    if (parsed.hostname.includes("youtu.be")) {
      const id = parsed.pathname.replace("/", "").trim();
      return id ? `https://www.youtube.com/embed/${id}` : null;
    }
    return null;
  } catch {
    return null;
  }
};

const isAbsoluteUrl = (value: string) =>
  value.startsWith("http://") || value.startsWith("https://");

const resolveMaterialContentUrl = (content?: string) => {
  if (!content) return "";
  if (isAbsoluteUrl(content)) return content;
  return resolveBackendMediaUrl(content);
};

const toVisualType = (material: Material) =>
  (material.materialType ?? material.fileType?.toLowerCase() ?? "link") as
    | "video"
    | "pdf"
    | "link"
    | "text";

const MaterialsPage = () => {
  const role = useRole();
  const canUpload = role !== "student";
  const { user } = useAuth();
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const { data: all = [] } = useQuery({
    queryKey: ["materials", role, user?.id],
    queryFn: () =>
      role === "student"
        ? fetchMaterials({ studentId: user?.id })
        : fetchMaterials(),
    enabled: role !== "student" || Boolean(user?.id),
  });
  const { data: workshops = [] } = useQuery({
    queryKey: ["workshops", "upload"],
    queryFn: fetchWorkshops,
    enabled: canUpload,
  });
  const [search, setSearch] = useState("");
  const [uploadModal, setUploadModal] = useState(false);
  const [viewDrawer, setViewDrawer] = useState(false);
  const [selected, setSelected] = useState<Material | null>(null);
  const [resolvedPreviewUrl, setResolvedPreviewUrl] = useState<string>("");
  const [textPreview, setTextPreview] = useState<string>("");
  const [textPreviewLoading, setTextPreviewLoading] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [materialMode, setMaterialMode] = useState<MaterialInputMode>("file");
  const [formTitle, setFormTitle] = useState("");
  const [formWorkshopId, setFormWorkshopId] = useState("");
  const [formModuleId, setFormModuleId] = useState("");
  const [newModuleTitle, setNewModuleTitle] = useState("");
  const [formContent, setFormContent] = useState("");
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);

  const { data: workshopModules = [] } = useQuery({
    queryKey: ["workshopModules", formWorkshopId],
    queryFn: () => fetchWorkshopModules(formWorkshopId),
    enabled: canUpload && Boolean(formWorkshopId),
  });

  useEffect(() => {
    if (!formWorkshopId) {
      setFormModuleId("");
      return;
    }
    if (!workshopModules.some((item) => item.id === formModuleId)) {
      setFormModuleId(workshopModules[0]?.id ?? "");
    }
  }, [formWorkshopId, formModuleId, workshopModules]);

  useEffect(() => {
    let cancelled = false;
    const loadText = async () => {
      if (!selected) {
        setTextPreview("");
        return;
      }
      const selectedType = toVisualType(selected);
      if (selectedType !== "text") {
        setTextPreview("");
        return;
      }

      const content = selected.content ?? "";
      if (!content || (!content.includes("/") && !isAbsoluteUrl(content))) {
        setTextPreview(content);
        return;
      }

      const possibleUrl = resolveMaterialContentUrl(content);
      if (!possibleUrl) {
        setTextPreview(content);
        return;
      }

      setTextPreviewLoading(true);
      try {
        const response = await fetch(possibleUrl);
        const value = await response.text();
        if (!cancelled) setTextPreview(value);
      } catch {
        if (!cancelled) setTextPreview(content);
      } finally {
        if (!cancelled) setTextPreviewLoading(false);
      }
    };

    void loadText();
    return () => {
      cancelled = true;
    };
  }, [selected]);

  const workshopOptions = useMemo(
    () => [{ value: "", label: "Select a workshop" }].concat(workshops.map((w) => ({ value: w.id, label: w.name }))),
    [workshops],
  );

  const moduleOptions = useMemo(
    () => [{ value: "", label: "Select a module" }].concat(
      workshopModules.map((m) => ({ value: m.id, label: m.title ?? "Module" })),
    ),
    [workshopModules],
  );

  const createModuleMutation = useMutation({
    mutationFn: (payload: { workshopId: string; title: string }) =>
      createWorkshopModule(payload),
    onSuccess: async (module) => {
      await queryClient.invalidateQueries({ queryKey: ["workshopModules", formWorkshopId] });
      setFormModuleId(module.id);
      setNewModuleTitle("");
      showToast("success", "Module Created", "New module selected automatically.");
    },
    onError: (err: unknown) => {
      showToast("error", "Module Create Failed", err instanceof Error ? err.message : "Unable to create module.");
    },
  });

  const filtered = all.filter((m) => {
    const q = search.toLowerCase();
    return (
      m.title.toLowerCase().includes(q) ||
      m.workshop.toLowerCase().includes(q) ||
      (m.moduleTitle ?? "").toLowerCase().includes(q)
    );
  });

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!formTitle.trim()) throw new Error("Please enter a title.");
      if (!formWorkshopId) throw new Error("Please select a workshop.");
      if (!formModuleId) throw new Error("Please select a module.");

      if (materialMode === "file") {
        if (!fileToUpload) throw new Error("Please choose a file.");
        const originalName = fileToUpload.name || "material";
        const extIndex = originalName.lastIndexOf(".");
        const originalExt = extIndex >= 0 ? originalName.slice(extIndex) : "";
        const hasUserExt = /\.[A-Za-z0-9]+$/.test(formTitle.trim());
        const uploadName = hasUserExt
          ? formTitle.trim()
          : `${formTitle.trim()}${originalExt}`;
        const renamed = new File([fileToUpload], uploadName, {
          type: fileToUpload.type,
        });
        return uploadModuleMaterial(formModuleId, renamed);
      }

      if (!formContent.trim()) throw new Error("Please enter content or URL.");
      return createModuleMaterial(formModuleId, {
        title: formTitle.trim(),
        type: modeToType[materialMode],
        content: formContent.trim(),
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["materials"] });
      await queryClient.invalidateQueries({ queryKey: ["workshopModules", formWorkshopId] });
      setUploadModal(false);
      setFileToUpload(null);
      setFormContent("");
      showToast("success", "Material saved", "Material has been added successfully.");
    },
    onError: (err: unknown) => {
      showToast("error", "Save failed", err instanceof Error ? err.message : "Unable to save material.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (material: Material) => {
      if (!material.moduleId) throw new Error("Missing module mapping for this material.");
      return deleteModuleMaterial(material.moduleId, material.id);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["materials"] });
      setDeleteDialog(false);
      showToast("success", "Material Deleted");
    },
    onError: (err: unknown) => {
      showToast("error", "Delete Failed", err instanceof Error ? err.message : "Unable to delete material.");
    },
  });

  const downloadMutation = useMutation({
    mutationFn: async (material: Material) => {
      if (!material.moduleId) throw new Error("Missing module mapping for this material.");
      return fetchMaterialDownload(material.moduleId, material.id);
    },
    onSuccess: (result, material) => {
      const url = resolveMaterialContentUrl(result.download_url || material.content);
      if (!url) {
        showToast("warning", "Unavailable", "No downloadable content for this material.");
        return;
      }
      window.open(url, "_blank", "noopener,noreferrer");
      showToast("success", "Downloaded", "Download started.");
    },
    onError: (err: unknown) => {
      showToast("error", "Download Failed", err instanceof Error ? err.message : "Unable to download material.");
    },
  });

  const handleView = async (material: Material) => {
    setSelected(material);
    setResolvedPreviewUrl("");

    const selectedType = toVisualType(material);
    if (selectedType === "link" || selectedType === "video") {
      setResolvedPreviewUrl(resolveMaterialContentUrl(material.content));
      setViewDrawer(true);
      return;
    }

    if (selectedType === "text") {
      setViewDrawer(true);
      return;
    }

    if (!material.moduleId) {
      setResolvedPreviewUrl(resolveMaterialContentUrl(material.content));
      setViewDrawer(true);
      return;
    }

    try {
      const result = await fetchMaterialDownload(material.moduleId, material.id);
      setResolvedPreviewUrl(resolveMaterialContentUrl(result.download_url || material.content));
    } catch {
      setResolvedPreviewUrl(resolveMaterialContentUrl(material.content));
    }
    setViewDrawer(true);
  };

  const columns = [
    {
      key: "title",
      header: "Title",
      render: (r: Material) => {
        const visualType = toVisualType(r);
        const Icon = materialIcons[visualType] || FileText;
        return (
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4 text-primary" />
            <span>{r.title}</span>
          </div>
        );
      },
    },
    { key: "workshop", header: "Workshop" },
    { key: "moduleTitle", header: "Module", render: (r: Material) => r.moduleTitle || "-" },
    {
      key: "materialType",
      header: "Type",
      render: (r: Material) => <VBadge variant="outline">{toVisualType(r).toUpperCase()}</VBadge>,
    },
    { key: "uploadDate", header: "Uploaded" },
    {
      key: "actions",
      header: "Actions",
      render: (r: Material) => (
        <div className="flex gap-1">
          <button
            onClick={() => void handleView(r)}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors">
            <Eye className="h-4 w-4" />
          </button>
          <button
            onClick={() => downloadMutation.mutate(r)}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-info transition-colors">
            <Download className="h-4 w-4" />
          </button>
          {canUpload && (
            <button
              onClick={() => {
                setSelected(r);
                setDeleteDialog(true);
              }}
              className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors">
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>
      ),
    },
  ];

  const selectedVisualType = selected ? toVisualType(selected) : null;
  const selectedUrl = selected ? resolvedPreviewUrl || resolveMaterialContentUrl(selected.content) : "";
  const selectedYouTubeEmbedUrl =
    selectedVisualType === "video" && selectedUrl ? toYouTubeEmbedUrl(selectedUrl) : null;

  return (
    <DashboardLayout title="Study Materials">
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search materials..." value={search} onChange={(e) => setSearch(e.target.value)} className="vidya-input pl-10" />
        </div>
        {canUpload && (
          <VButton
            onClick={() => {
              setFormTitle("");
              setFormWorkshopId("");
              setFormModuleId("");
              setNewModuleTitle("");
              setMaterialMode("file");
              setFormContent("");
              setFileToUpload(null);
              setUploadModal(true);
            }}>
            <Upload className="h-4 w-4" /> Add Material
          </VButton>
        )}
      </div>
      <VTable columns={columns} data={filtered} />

      <VModal isOpen={uploadModal} onClose={() => setUploadModal(false)} title="Add Material">
        <div className="space-y-4">
          <VInput
            label="Title"
            placeholder="Material title"
            value={formTitle}
            onChange={(e) => setFormTitle(e.target.value)}
          />
          <VSelect
            label="Workshop"
            value={formWorkshopId}
            onChange={(e) => setFormWorkshopId(e.target.value)}
            options={workshopOptions}
          />
          <VSelect
            label="Module"
            value={formModuleId}
            onChange={(e) => setFormModuleId(e.target.value)}
            options={moduleOptions}
          />
          {formWorkshopId && workshopModules.length === 0 && (
            <div className="rounded-lg border border-warning/40 bg-warning/5 p-3 space-y-2">
              <p className="text-sm text-foreground">No modules yet — create one first.</p>
              <div className="flex gap-2">
                <VInput
                  placeholder="New module title"
                  value={newModuleTitle}
                  onChange={(e) => setNewModuleTitle(e.target.value)}
                />
                <VButton
                  variant="secondary"
                  onClick={() => {
                    if (!newModuleTitle.trim()) {
                      showToast("warning", "Module Title Required", "Enter a module title.");
                      return;
                    }
                    createModuleMutation.mutate({
                      workshopId: formWorkshopId,
                      title: newModuleTitle.trim(),
                    });
                  }}
                  isLoading={createModuleMutation.isPending}
                >
                  Create Module
                </VButton>
              </div>
            </div>
          )}
          <VSelect
            label="Material Source"
            value={materialMode}
            onChange={(e) => setMaterialMode(e.target.value as MaterialInputMode)}
            options={[
              { value: "file", label: "Upload File" },
              { value: "video", label: "Video URL (YouTube/video)" },
              { value: "pdf", label: "PDF URL" },
              { value: "link", label: "External Link" },
              { value: "text", label: "Text / Notes" },
            ]}
          />

          {materialMode === "file" ? (
            <VInput
              label="File"
              type="file"
              onChange={(e) => setFileToUpload((e.target as HTMLInputElement).files?.[0] ?? null)}
            />
          ) : materialMode === "text" ? (
            <div>
              <label className="vidya-label">Notes</label>
              <textarea
                className="vidya-input min-h-[140px]"
                placeholder="Write the material notes here..."
                value={formContent}
                onChange={(e) => setFormContent(e.target.value)}
              />
            </div>
          ) : (
            <VInput
              label="URL"
              placeholder={
                materialMode === "video"
                  ? "https://www.youtube.com/watch?v=..."
                  : materialMode === "pdf"
                    ? "https://example.com/document.pdf"
                    : "https://example.com"
              }
              value={formContent}
              onChange={(e) => setFormContent(e.target.value)}
            />
          )}

          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setUploadModal(false)}>
              Cancel
            </VButton>
            <VButton
              onClick={() => uploadMutation.mutate()}
              disabled={
                !formTitle ||
                !formWorkshopId ||
                !formModuleId ||
                (materialMode === "file" ? !fileToUpload : !formContent.trim()) ||
                uploadMutation.isPending
              }>
              Save
            </VButton>
          </div>
        </div>
      </VModal>

      <VDrawer isOpen={viewDrawer} onClose={() => setViewDrawer(false)} title={selected?.title || ""}>
        {selected && (
          <div className="space-y-6">
            <div className="rounded-xl bg-muted/50 border border-border p-4">
              {selectedVisualType === "video" && selectedYouTubeEmbedUrl && (
                <div className="aspect-video overflow-hidden rounded-lg border border-border">
                  <iframe
                    src={selectedYouTubeEmbedUrl}
                    className="h-full w-full"
                    title={selected.title}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  />
                </div>
              )}

              {selectedVisualType === "video" && !selectedYouTubeEmbedUrl && selectedUrl && (
                <video className="w-full rounded-lg" controls src={selectedUrl}>
                  Your browser does not support video playback.
                </video>
              )}

              {selectedVisualType === "pdf" && selectedUrl && (
                <iframe title={selected.title} src={selectedUrl} className="h-[70vh] w-full rounded-lg border border-border" />
              )}

              {selectedVisualType === "link" && (
                <div className="flex min-h-[160px] flex-col items-center justify-center gap-3 text-center">
                  <Link2 className="h-10 w-10 text-primary" />
                  <p className="text-sm text-muted-foreground break-all">{selectedUrl || selected.content}</p>
                  <VButton
                    onClick={() => {
                      const link = selectedUrl || selected.content;
                      if (link) window.open(link, "_blank", "noopener,noreferrer");
                    }}>
                    <ExternalLink className="h-4 w-4" /> Open Link
                  </VButton>
                </div>
              )}

              {selectedVisualType === "text" && (
                <div className="min-h-[180px] whitespace-pre-wrap rounded-lg border border-border bg-background p-4 text-sm text-foreground">
                  {textPreviewLoading ? "Loading text content..." : textPreview || "No text content available."}
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div><p className="text-xs text-muted-foreground mb-1">Workshop</p><p className="text-sm font-medium text-foreground">{selected.workshop}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Type</p><VBadge variant="outline">{toVisualType(selected).toUpperCase()}</VBadge></div>
              <div><p className="text-xs text-muted-foreground mb-1">Uploaded</p><p className="text-sm text-foreground">{selected.uploadDate}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Module</p><p className="text-sm text-foreground">{selected.moduleTitle || "-"}</p></div>
            </div>

            <div className="grid grid-cols-1 gap-2">
              <VButton className="w-full" onClick={() => downloadMutation.mutate(selected)} isLoading={downloadMutation.isPending}>
                <Download className="h-4 w-4" /> Open / Download
              </VButton>
            </div>
          </div>
        )}
      </VDrawer>

      <VConfirmDialog isOpen={deleteDialog} onClose={() => setDeleteDialog(false)} onConfirm={() => {
        if (!selected) return;
        deleteMutation.mutate(selected);
      }} title="Delete Material" message={`Delete "${selected?.title}"?`} />
    </DashboardLayout>
  );
};

export default MaterialsPage;
