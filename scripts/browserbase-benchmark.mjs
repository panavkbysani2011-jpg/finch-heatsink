#!/usr/bin/env node
/**
 * FINCH Browserbase Benchmark
 * 
 * Uses Browserbase headless browser infrastructure to:
 *  1. Launch the FINCH tool in a remote browser
 *  2. Run an automated evolution
 *  3. Capture screenshots of the results
 *  4. Compare conventional vs optimised designs
 *
 * Prerequisites:
 *   Set BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID in your environment
 *   (or add them in the Freebuff Keys tab).
 *
 * Usage:
 *   node scripts/browserbase-benchmark.mjs [url]
 *
 *   If no URL is provided, it starts a local server and uses that.
 */

import { Stagehand } from "@browserbasehq/stagehand";
import { createServer } from "node:http";
import { readFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = join(__dirname, "..");
const OUTPUT_DIR = join(PROJECT_ROOT, "benchmark_output");

// ============================================================
// Configuration
// ============================================================
const MATERIALS = [
  { id: "steel_thin", label: "Thin steel, strong fan" },
  { id: "al_forced",  label: "Thick aluminium, fan" },
  { id: "steel",      label: "Thick steel, fan" },
  { id: "al_still",   label: "Thick aluminium, no fan" },
];
const EVOLVE_TIME_MS = 25000;   // let evolution run for ~25 seconds
const SCREENSHOT_DELAY = 3000;  // wait for render after actions

// ============================================================
// Helper: start a local static server (fallback)
// ============================================================
function startLocalServer(port = 5199) {
  const mime = {
    ".html": "text/html",
    ".css":  "text/css",
    ".js":   "application/javascript",
    ".png":  "image/png",
    ".svg":  "image/svg+xml",
    ".json": "application/json",
  };
  const server = createServer((req, res) => {
    let filePath = join(PROJECT_ROOT, "dist", req.url === "/" ? "index.html" : req.url);
    if (!existsSync(filePath)) {
      filePath = join(PROJECT_ROOT, "dist", "index.html");
    }
    try {
      const data = readFileSync(filePath);
      const ext = filePath.substring(filePath.lastIndexOf("."));
      res.writeHead(200, { "Content-Type": mime[ext] || "application/octet-stream" });
      res.end(data);
    } catch {
      res.writeHead(404);
      res.end("Not found");
    }
  });
  server.listen(port);
  console.log(`  Local server started on http://localhost:${port}`);
  return { server, url: `http://localhost:${port}/tool.html` };
}

// ============================================================
// Main benchmark
// ============================================================
async function runBenchmark(targetUrl) {
  console.log("\n============================================");
  console.log("  FINCH × Browserbase Benchmark Suite");
  console.log("============================================\n");

  // Ensure output directory exists
  if (!existsSync(OUTPUT_DIR)) mkdirSync(OUTPUT_DIR, { recursive: true });

  // Resolve URL
  let server = null;
  let url = targetUrl;
  if (!url) {
    console.log("  No URL provided — starting local server...");
    const srv = startLocalServer();
    server = srv.server;
    url = srv.url;
  }
  console.log(`  Target: ${url}\n`);

  // Initialise Browserbase session
  console.log("  Connecting to Browserbase...");
  const stagehand = new Stagehand({
    env: "BROWSERBASE",
    apiKey: process.env.BROWSERBASE_API_KEY,
    projectId: process.env.BROWSERBASE_PROJECT_ID,
    verbose: 0,
  });

  await stagehand.init({ modelName: "gpt-4o" });
  const { page } = stagehand;
  console.log("  Browserbase session established ✓\n");

  const results = [];

  for (const mat of MATERIALS) {
    console.log(`  ─── ${mat.label} ───`);

    // Navigate to tool
    await page.goto(url);
    await page.waitForTimeout(2000);

    // Select material preset
    await page.selectOption('select#preset', mat.id);
    await page.waitForTimeout(500);

    // Click "Evolve" and wait
    console.log(`    Starting evolution...`);
    await page.click("#run");
    await page.waitForTimeout(EVOLVE_TIME_MS);

    // Read peak temperatures from the DOM
    const tempA = await page.evaluate(() => {
      const el = document.querySelector("#degA");
      return el ? el.textContent.trim() : "N/A";
    });
    const tempB = await page.evaluate(() => {
      const el = document.querySelector("#degB");
      return el ? el.textContent.trim() : "N/A";
    });

    // Read wasted percentage
    const wasteA = await page.evaluate(() => {
      const el = document.querySelector("#wA");
      return el ? el.textContent.trim() : "N/A";
    });
    const wasteB = await page.evaluate(() => {
      const el = document.querySelector("#wB");
      return el ? el.textContent.trim() : "N/A";
    });

    // Read verdict
    const verdict = await page.evaluate(() => {
      const el = document.querySelector("#verd");
      return el ? el.textContent.trim() : "N/A";
    });

    // Screenshot
    const slug = mat.id;
    const screenshotPath = join(OUTPUT_DIR, `benchmark_${slug}.png`);
    await page.screenshot({ path: screenshotPath });
    console.log(`    Screenshot saved: benchmark_${slug}.png`);
    console.log(`    Conventional: ${tempA}  (${wasteA} wasted)`);
    console.log(`    Optimised:    ${tempB}  (${wasteB} wasted)`);
    console.log(`    Verdict:      ${verdict.substring(0, 80)}...\n`);

    // Stop the evolution
    await page.click("#run");
    await page.waitForTimeout(500);

    results.push({
      material: mat.label,
      materialId: mat.id,
      conventional: { peak: tempA, waste: wasteA },
      optimised: { peak: tempB, waste: wasteB },
      verdict: verdict,
    });
  }

  // Close Browserbase
  await stagehand.close();
  if (server) server.close();

  // ============================================================
  // Summary report
  // ============================================================
  console.log("============================================");
  console.log("  Benchmark Summary");
  console.log("============================================\n");

  const reportLines = [];
  reportLines.push("# FINCH × Browserbase Benchmark Report\n");
  reportLines.push("| Material | Conventional | Optimised | Improvement |");
  reportLines.push("|---|---|---|---|");

  for (const r of results) {
    const conv = parseFloat(r.conventional.peak);
    const opt = parseFloat(r.optimised.peak);
    let imp = "—";
    if (!isNaN(conv) && !isNaN(opt) && conv > 0) {
      const pct = ((conv - opt) / conv * 100).toFixed(1);
      imp = `${pct}%`;
    }
    reportLines.push(`| ${r.material} | ${r.conventional.peak} | ${r.optimised.peak} | ${imp} |`);
  }

  reportLines.push("");
  reportLines.push(`_Benchmark run at ${new Date().toISOString()}_`);
  reportLines.push(`_Browserbase session: headless Chrome via Browserbase_`);

  const reportPath = join(OUTPUT_DIR, "BENCHMARK_REPORT.md");
  writeFileSync(reportPath, reportLines.join("\n"), "utf-8");
  console.log(reportLines.join("\n"));
  console.log(`\n  Full report saved to benchmark_output/BENCHMARK_REPORT.md`);
  console.log(`  Screenshots in benchmark_output/`);
  console.log("\n============================================\n");
}

runBenchmark(process.argv[2]).catch((err) => {
  console.error("Benchmark failed:", err);
  process.exit(1);
});
