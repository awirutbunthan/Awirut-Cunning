import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./main";

describe("review screen", () => {
  it("provides a constrained upload control", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Ledger Beacon" })).toBeTruthy();
    expect(screen.getByLabelText("Upload document")).toHaveProperty("accept", ".pdf,.xlsx,.zip");
  });
});
