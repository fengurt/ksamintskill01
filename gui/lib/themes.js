import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { BASLIDE_ROOT } from "./paths.js";

const FALLBACK = {
  TIANSIGHT: { label: "侍天报告", canvas: "2880×1620", mechanical: true },
  magazine: { label: "电子杂志 A", canvas: "100vw×100vh", mechanical: false },
  swiss: { label: "瑞士 B", canvas: "100vw×100vh", mechanical: false },
  tableai: { label: "Table AI C", canvas: "100vw×100vh", mechanical: false },
  atelier: { label: "Atelier", canvas: "100vw×100vh", mechanical: false },
};

export function listThemes() {
  const pageTypes = join(BASLIDE_ROOT, "page-types.json");
  let skins = { ...FALLBACK };
  if (existsSync(pageTypes)) {
    try {
      const data = JSON.parse(readFileSync(pageTypes, "utf8"));
      const fromFile = data.skins || {};
      skins = {};
      for (const [id, meta] of Object.entries(fromFile)) {
        skins[id] = {
          id,
          label: meta.label || id,
          canvas: meta.canvas || "",
          template: meta.template || null,
          mechanical: id === "TIANSIGHT",
        };
      }
    } catch {
      skins = { ...FALLBACK };
    }
  }
  return {
    baslide: BASLIDE_ROOT,
    themes: Object.entries(skins).map(([id, meta]) => ({
      id,
      label: meta.label || id,
      canvas: meta.canvas || "",
      template: meta.template || null,
      mechanical: meta.mechanical === true || id === "TIANSIGHT",
    })),
  };
}
