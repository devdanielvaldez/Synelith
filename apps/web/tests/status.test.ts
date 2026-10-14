import { describe, expect, it } from "vitest";

import { formatEvidenceCount } from "../lib/status";

describe("formatEvidenceCount", () => {
  it("makes review completeness explicit", () => {
    expect(formatEvidenceCount(18, 24)).toBe("18 of 24 reviewed · 75%");
    expect(formatEvidenceCount(0, 0)).toBe("No evidence reviewed");
  });
});
