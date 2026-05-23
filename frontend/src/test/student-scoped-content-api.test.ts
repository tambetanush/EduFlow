import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiGet } from "@/api/client";
import { fetchAssessments, fetchMaterials } from "@/services/api";

vi.mock("@/api/client", () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPatch: vi.fn(),
  apiDelete: vi.fn(),
}));

const mockApiGet = vi.mocked(apiGet);

const workshopsPage = {
  items: [
    {
      id: "w1",
      title: "Workshop 1",
      description: "Desc 1",
      institution_id: "inst-1",
      start_date: "2026-01-01T00:00:00Z",
      end_date: "2026-12-31T00:00:00Z",
    },
    {
      id: "w2",
      title: "Workshop 2",
      description: "Desc 2",
      institution_id: "inst-1",
      start_date: "2026-01-01T00:00:00Z",
      end_date: "2026-12-31T00:00:00Z",
    },
  ],
  total: 2,
  offset: 0,
  limit: 25,
};

const institutions = [{ id: "inst-1", name: "Institution 1" }];

describe("student-scoped content fetchers", () => {
  beforeEach(() => {
    mockApiGet.mockReset();
  });

  it("fetchAssessments only requests enrolled workshop assessments for students", async () => {
    mockApiGet.mockImplementation(async (url: string) => {
      if (url === "/workshops/") return workshopsPage;
      if (url === "/institutions/") return institutions;
      if (url === "/enrollments/student/student-1") {
        return {
          items: [{ id: "en-1", student_id: "student-1", workshop_id: "w2" }],
          total: 1,
          offset: 0,
          limit: 200,
        };
      }
      if (url === "/assessments/workshop/w2") {
        return {
          items: [
            {
              id: "a-1",
              workshop_id: "w2",
              module_id: null,
              title: "Assessment 1",
              total_marks: 100,
              pass_mark: 40,
            },
          ],
          total: 1,
          offset: 0,
          limit: 20,
        };
      }
      throw new Error(`Unexpected call: ${url}`);
    });

    const items = await fetchAssessments({ studentId: "student-1" });
    const calledUrls = mockApiGet.mock.calls.map((call) => call[0] as string);

    expect(items).toHaveLength(1);
    expect(calledUrls).toContain("/assessments/workshop/w2");
    expect(calledUrls).not.toContain("/assessments/workshop/w1");
  });

  it("fetchMaterials only requests enrolled workshop modules for students", async () => {
    mockApiGet.mockImplementation(async (url: string) => {
      if (url === "/workshops/") return workshopsPage;
      if (url === "/institutions/") return institutions;
      if (url === "/enrollments/student/student-1") {
        return {
          items: [{ id: "en-1", student_id: "student-1", workshop_id: "w2" }],
          total: 1,
          offset: 0,
          limit: 200,
        };
      }
      if (url === "/workshops/w2/modules") {
        return {
          items: [
            {
              id: "m-1",
              workshop_id: "w2",
              title: "Module 1",
              order_index: 1,
              materials: [
                {
                  id: "mat-1",
                  title: "Slides",
                  type: "pdf",
                  content: "/media/slides.pdf",
                  created_at: "2026-04-08T09:00:00Z",
                },
              ],
            },
          ],
          total: 1,
          offset: 0,
          limit: 20,
        };
      }
      throw new Error(`Unexpected call: ${url}`);
    });

    const items = await fetchMaterials({ studentId: "student-1" });
    const calledUrls = mockApiGet.mock.calls.map((call) => call[0] as string);

    expect(items).toHaveLength(1);
    expect(calledUrls).toContain("/workshops/w2/modules");
    expect(calledUrls).not.toContain("/workshops/w1/modules");
  });
});

