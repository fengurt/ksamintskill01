import assert from "node:assert/strict";
import { mapApuchBrand, syncApuchThemes } from "./apuch.js";

const mapped = mapApuchBrand({
  slug: "opcglobal",
  mainName: "OPC Global",
  logoUrl: "https://media.apuch.art/logo.png",
  theme: {
    primary: "#1D3557",
    accent: "#B79B63",
    secondary: "#A23E3E",
    paper: "#FFFFFF",
    ink: "#162130",
    muted: "#596776",
  },
}, "opcglobal", "data:image/png;base64,AA==");

assert.equal(mapped.name, "OPC Global");
assert.equal(mapped.tokens.accent, "#b79b63");
assert.equal(mapped.tokens.warning, "#a23e3e");
assert.equal(mapped.tokens.grid, "#c9cec7");
assert.equal(mapped.sourceUrl, "https://apuch.art/brand.html?brand=opcglobal");
assert.match(mapped.logoDataUrl, /^data:image\/png/);
const oldBase = process.env.APUCH_API_BASE;
process.env.APUCH_API_BASE = "http://example.com";
assert.throws(() => mapApuchBrand({}, "bad"), /APUCH_API_BASE/);
if (oldBase == null) delete process.env.APUCH_API_BASE;
else process.env.APUCH_API_BASE = oldBase;
await assert.rejects(syncApuchThemes({ slugs: ["../private"] }), /invalid Apuch brand slugs/);

console.log("apuch.test.js ok");
