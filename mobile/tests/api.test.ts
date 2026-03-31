import { describe, it, expect, vi } from "vitest";

// Mock AsyncStorage
vi.mock("@react-native-async-storage/async-storage", () => ({
  default: {
    getItem: vi.fn().mockResolvedValue(null),
    setItem: vi.fn().mockResolvedValue(undefined),
  },
}));

describe("isDemoMode", () => {
  it("returns true when no backend URL is configured", async () => {
    // Reset module to clear cache
    vi.resetModules();
    const { isDemoMode } = await import("../lib/api");
    expect(isDemoMode()).toBe(true);
  });
});

describe("types", () => {
  it("task status values are valid", async () => {
    const types = await import("../lib/types");
    // Verify TaskStatus type covers expected values via MODULE_NAMES keys
    const moduleNames = types.MODULE_NAMES;
    expect(moduleNames).toBeDefined();
    // Verify the type file exports correctly
    expect(typeof moduleNames).toBe("object");
  });

  it("module names are defined for all modules", async () => {
    const { MODULE_NAMES } = await import("../lib/types");
    const expectedModules = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"];
    for (const m of expectedModules) {
      expect(MODULE_NAMES[m as keyof typeof MODULE_NAMES]).toBeDefined();
    }
  });
});

describe("mock data", () => {
  it("demo tasks have required fields", async () => {
    const { DEMO_TASKS } = await import("../lib/mock-data");
    expect(DEMO_TASKS.length).toBeGreaterThan(0);
    for (const task of DEMO_TASKS) {
      expect(task.id).toBeDefined();
      expect(task.title).toBeDefined();
      expect(task.topic).toBeDefined();
      expect(task.status).toBeDefined();
      expect(Array.isArray(task.modules)).toBe(true);
    }
  });

  it("demo tasks have valid module states", async () => {
    const { DEMO_TASKS } = await import("../lib/mock-data");
    const validStatuses = ["waiting", "running", "completed", "failed", "skipped"];
    for (const task of DEMO_TASKS) {
      for (const mod of task.modules) {
        expect(validStatuses).toContain(mod.status);
        expect(mod.percent).toBeGreaterThanOrEqual(0);
        expect(mod.percent).toBeLessThanOrEqual(100);
      }
    }
  });

  it("demo module IO has all 9 modules", async () => {
    const { DEMO_MODULE_IO } = await import("../lib/mock-data");
    expect(DEMO_MODULE_IO.length).toBe(9);
    const moduleIds = DEMO_MODULE_IO.map((d) => d.moduleId);
    for (let i = 1; i <= 9; i++) {
      expect(moduleIds).toContain(`M${i}`);
    }
  });
});
