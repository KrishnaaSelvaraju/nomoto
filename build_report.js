/*
MSMD Assignment 2026/2027 - Project 9
build_report.js - Generates the Word report by READING the actual results
from outputs/*.json (written by ship_data.py, task1/2/3/4 scripts) rather
than hardcoding numbers. Run this LAST, after all task scripts have run.
*/

const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ImageRun, AlignmentType, ShadingType, PageBreak, VerticalAlign
} = require("docx");
const fs = require("fs");

const FONT = "Calibri";
const O = (name) => JSON.parse(fs.readFileSync(`outputs/${name}.json`));

const shipData = O("ship_data");
const task1 = O("task1_results");
const task2 = O("task2_results");
const task3 = O("task3_results");
const task4 = O("task4_results");

const V1 = shipData.VESSEL1, V2 = shipData.VESSEL2;
const fmt = (x, d = 1) => (x === null || x === undefined) ? "N/A" : Number(x).toFixed(d);

// ---------------------------------------------------------------------
function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } }); }
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } }); }
function h3(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 100 } }); }
function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, font: FONT, size: 22, italics: opts.italics || false, bold: opts.bold || false })],
    spacing: { after: 160 }, alignment: opts.align || AlignmentType.JUSTIFIED,
  });
}
function eq(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Cambria Math", size: 24, italics: true })],
    spacing: { before: 80, after: 160 }, alignment: AlignmentType.CENTER,
  });
}
function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: FONT, size: 20, italics: true })],
    spacing: { before: 60, after: 240 }, alignment: AlignmentType.CENTER,
  });
}
function bullet(text) {
  return new Paragraph({ children: [new TextRun({ text, font: FONT, size: 22 })], bullet: { level: 0 }, spacing: { after: 80 } });
}
function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "DDEBF7" } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      children: [new TextRun({ text: String(text), font: FONT, size: 20, bold: opts.header || false })],
      alignment: opts.align || AlignmentType.LEFT,
    })],
  });
}
function dataTable(headers, rows, widths) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ children: headers.map((hd, i) => cell(hd, { header: true, width: widths[i] })), tableHeader: true }),
      ...rows.map(r => new TableRow({ children: r.map((v, i) => cell(v, { width: widths[i] })) })),
    ],
  });
}
function image(path, width, height) {
  return new Paragraph({
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path), transformation: { width, height } })],
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
  });
}
const pageBreak = new Paragraph({ children: [new PageBreak()] });

// ---------------------------------------------------------------------
const doc = new Document({
  sections: [{
    properties: {},
    children: [
      // TITLE PAGE
      new Paragraph({ text: "", spacing: { before: 1800 } }),
      new Paragraph({ children: [new TextRun({ text: "Modelling and Safety of Maritime Traffic", font: FONT, size: 40, bold: true })], alignment: AlignmentType.CENTER, spacing: { after: 200 } }),
      new Paragraph({ children: [new TextRun({ text: "Assignment Report — Tasks 1 to 4", font: FONT, size: 32, bold: true })], alignment: AlignmentType.CENTER, spacing: { after: 600 } }),
      new Paragraph({ children: [new TextRun({ text: "Project 9", font: FONT, size: 26 })], alignment: AlignmentType.CENTER, spacing: { after: 100 } }),
      new Paragraph({ children: [new TextRun({ text: `Vessel 1: ${V1.name}   |   Vessel 2: ${V2.name}`, font: FONT, size: 24 })], alignment: AlignmentType.CENTER, spacing: { after: 100 } }),
      new Paragraph({ children: [new TextRun({ text: "Assigned encounter: Head-on   |   Scenarios: COLREG-COLREG, Blind-Blind", font: FONT, size: 24 })], alignment: AlignmentType.CENTER, spacing: { after: 800 } }),
      new Paragraph({ children: [new TextRun({ text: "MSc in Naval Architecture and Ocean Engineering, 2026-2027", font: FONT, size: 22, italics: true })], alignment: AlignmentType.CENTER }),
      pageBreak,

      // SECTION 1
      h1("1. Introduction and Scope"),
      p("This report documents Tasks 1 to 4 of the Modelling and Safety of Maritime Traffic (MSMD) assignment, for Project 9. Per the project data table (Section 2.1 of the assignment description), the vessels assigned are Vessel 1 = KCS and Vessel 2 = KVLCC2, the assigned encounter type is head-on, and the two scenarios assessed are COLREG-COLREG and Blind-Blind."),
      p("All simulations use the first-order Nomoto manoeuvring model exclusively (MMG was not implemented; solo submissions are understood to permit a single manoeuvring model — confirm this in writing with course staff before final submission). All figures, tables and numeric results in this report are generated directly from the accompanying Python scripts' output files (outputs/*.json), not transcribed by hand, so re-running the pipeline with different inputs will automatically update this document when regenerated."),

      // SECTION 2: TASK 1
      pageBreak,
      h1("2. Task 1 — Turning Manoeuvre Simulation (KCS)"),
      h2("2.1 Methodology"),
      p("The turning manoeuvre of Vessel 1 (KCS) was simulated using the first-order Nomoto equation, in the formulation used by Lotovskyi & Teixeira (2023):"),
      eq("T · ṙ + r = K · δ"),
      p("The rudder ramps from 0° to its target at the fixed execution rate of 2.33°/s (assignment Section 2.2), then holds. The turning circle runs to 720° total heading change. Position uses course-over-ground (COG = ψ − β):"),
      eq("x ← x + V·Δt·sin(COG),      y ← y + V·Δt·cos(COG)"),
      p("K, drift angle and speed reduction follow Lotovskyi & Teixeira (2023) Eqs. 8-16:"),
      eq("K = V_STD(35°) / (δ_R · R),   R = 2·Lpp   (SNAME, 1989)"),

      h3("2.1.1 Correcting the Nomoto time constant T"),
      p(`Earlier drafts of this work used a shared placeholder T = 100 s for both vessels (the most-likely value of Lotovskyi & Teixeira (2023)'s own Tri(70,100,130) s, drawn for their 330 m case-study ship). The paper attributes this distribution to Silveira et al. (2016) ("Probabilistic modelling of evasive manoeuvring actions to avoid collisions", MARTECH 2016 conference proceedings) — a paywalled conference chapter not available in this project's reference set.`),
      p(`Instead, T is derived here from the standard ship-manoeuvring non-dimensionalisation T' = T·V/L, which is approximately constant across similar ship types. Using the ONE real data point available — the reference paper's own worked example (Lpp=${shipData.reference.Lpp} m, V0=${shipData.reference.V0_kn} kn, T=${shipData.reference.T} s) — gives T' = ${fmt(shipData.T_prime, 4)}. Applying this to each vessel's own length and speed gives a distinct, physically grounded T for each ship instead of one shared number:`),
      dataTable(
        ["Vessel", "Lpp (m)", "V0 (kn)", "T (s), corrected"],
        [
          [V1.name, fmt(V1.Lpp, 0), fmt(V1.V0_kn, 1), fmt(V1.T, 1)],
          [V2.name, fmt(V2.Lpp, 0), fmt(V2.V0_kn, 1), fmt(V2.T, 1)],
        ],
        [3000, 2000, 2000, 2500]
      ),
      p("This is a standard, defensible naval-architecture scaling approach given the primary source is unavailable; it should be replaced with the real Silveira et al. (2016) table if it becomes available.", { italics: true }),

      h3("2.1.2 Other values used"),
      dataTable(
        ["Parameter", "Value", "Source"],
        [
          ["Lpp, B, V0", `${fmt(V1.Lpp,0)} m, ${fmt(V1.B,1)} m, ${fmt(V1.V0_kn,1)} kn`, "Assignment Table 3 (KCS)"],
          ["Rudder max, rate", "35°, 2.33°/s", "Assignment Section 2.2"],
          ["Turn direction", "Port", "Assignment Section 2.2"],
          ["R (steady radius)", `2·Lpp = ${fmt(V1.R,0)} m`, "SNAME (1989)"],
          ["V_ST/V0", "0.65 (midpoint of U(0.6,0.7))", "Lotovskyi & Teixeira (2023) Eq. 9"],
          ["β_ST", `${fmt(V1.beta_ST_deg,2)}°`, "Lotovskyi & Teixeira (2023), eq. following Eq. 9"],
        ],
        [3200, 3200, 3100]
      ),

      h2("2.2 Results"),
      dataTable(
        ["Parameter", "Value"],
        [
          ["Time to 90° heading change", `${fmt(task1.t90_s)} s`],
          ["Time to 180° heading change", `${fmt(task1.t180_s)} s`],
          ["Advance", `${fmt(task1.advance_m)} m (${fmt(task1.advance_Lpp,2)} Lpp)`],
          ["Transfer", `${fmt(task1.transfer_m)} m (${fmt(task1.transfer_Lpp,2)} Lpp)`],
          ["Tactical diameter", `${fmt(task1.tactical_diameter_m)} m (${fmt(task1.tactical_diameter_Lpp,2)} Lpp)`],
          ["Diameter of steady turn", `${fmt(task1.diameter_of_turn_m)} m (${fmt(task1.diameter_of_turn_Lpp,2)} Lpp)`],
          ["Yaw rate, initial", `${fmt(task1.yaw_rate_initial_deg_s,4)} °/s`],
          ["Yaw rate, steady", `${fmt(task1.yaw_rate_steady_deg_s,3)} °/s`],
          ["Speed, steady turn", `${fmt(task1.speed_steady_turn_kn,2)} kn`],
          ["Drift angle, steady turn", `${fmt(task1.drift_angle_steady_deg,2)}°`],
        ],
        [4500, 4000]
      ),
      image("figures/task1_kcs_turning_circle.png", 460, 460),
      caption(`Figure 1. Simulated KCS turning circle (720°), first-order Nomoto, T=${fmt(V1.T,1)}s.`),
      p("A supporting MP4 animation (figures/task1_kcs_turning_circle.mp4) is provided alongside this report."),

      // SECTION 3: TASK 2
      pageBreak,
      h1("3. Task 2 — Encounter Scenario Simulation (Head-on)"),
      h2("3.1 COLREG rule and methodology"),
      p("Rule 14 (head-on): both vessels alter course to starboard (Cockcroft & Lameijer, 2012). COLREG-COLREG uses the most-likely Tri(1°,20°,35°) angle (20°) for both vessels; Blind-Blind draws both vessels' rudder independently from U(-35°,35°). Collision is checked every timestep via the Separating Axis Theorem on each vessel's Lpp×B hull rectangle. The minimum safe distance search starts at D0=(Lpp1+Lpp2)/2, increments by 0.25×min(Lpp1,Lpp2) whenever a collision is detected, and stops once the vessels clear each other's hulls and end up farther apart than their starting separation."),
      h2("3.2 Results"),
      dataTable(
        ["Scenario", "Minimum safe distance", "As multiple of larger Lpp"],
        [
          ["COLREG-COLREG", `${fmt(task2["COLREG-COLREG"].D_min_m)} m`, `${fmt(task2["COLREG-COLREG"].D_min_over_larger_Lpp,2)}×`],
          ["Blind-Blind", `${fmt(task2["Blind-Blind"].D_min_m)} m`, `${fmt(task2["Blind-Blind"].D_min_over_larger_Lpp,2)}×`],
        ],
        [3500, 3500, 2500]
      ),
      p(`Blind-Blind's sampled rudder angles were δ1=${fmt(task2["Blind-Blind"].delta1_deg,1)}° and δ2=${fmt(task2["Blind-Blind"].delta2_deg,1)}° (one representative draw from U(-35°,35°), reproducible via the fixed seed in task2_encounter.py).`, { italics: true }),
      image("figures/task2_headon_colreg_colreg.png", 380, 420),
      caption("Figure 2. Head-on, COLREG-COLREG: both vessels turn to starboard and pass port-to-port."),
      image("figures/task2_headon_blind_blind.png", 380, 420),
      caption("Figure 3. Head-on, Blind-Blind."),
      p("Full per-timestep data tables (Excel) and MP4 animations for both scenarios are provided as separate files alongside this report."),

      // SECTION 4: TASK 3
      pageBreak,
      h1("4. Task 3 — Minimum Critical Distance for Give-Way Start"),
      p("Hashimoto & Okushima (1990) model each ship as a circle whose diameter equals its breadth (not its full hull), giving a collision diameter D_ij=(B_i+B_j)/2, and derive the head-on critical distance of give-way start geometrically as:"),
      eq("m^h_ij = D_ij / sin(θ)"),
      dataTable(
        ["Method", "Distance"],
        [
          ["Hashimoto & Okushima, θ=20°", `${fmt(task3.theta_20_m)} m`],
          ["Hashimoto & Okushima, θ=30°", `${fmt(task3.theta_30_m)} m`],
          ["Task 2 simulation, COLREG-COLREG", `${fmt(task3.task2_colreg_colreg_m)} m`],
          ["Task 2 simulation, Blind-Blind (reference only)", `${fmt(task3.task2_blind_blind_m)} m`],
        ],
        [5500, 3000]
      ),
      image("figures/task3_comparison.png", 440, 320),
      caption("Figure 4. Geometric (Hashimoto & Okushima) vs. simulated (Task 2) minimum safe distance."),
      p(`The Task 2 simulated value is approximately ${fmt(task3.ratio_task2_over_hashimoto20,1)}x larger than Hashimoto & Okushima's geometric criterion at θ=20°. This gap comes from two compounding simplifications in the geometric model: it uses breadth-only circles (ignoring the 230-320 m ship lengths entirely), and it assumes an instantaneous course change rather than a real, gradual Nomoto turn with a rudder ramp and time-constant lag. Both push the geometric answer below the dynamically simulated one; the simulated value should be considered the more trustworthy figure for actual navigational safety, while Hashimoto & Okushima's is better suited to its original purpose of aggregate channel-wide risk scoring.`),

      // SECTION 5: TASK 4
      pageBreak,
      h1("5. Task 4 — Minimum Safe Distance Assessment (Monte Carlo)"),
      h2("5.1 Methodology"),
      p(`Task 4 repeats the Task 2 search N=${task4["COLREG-COLREG"].N} times per scenario, drawing new random rudder angles and approach speeds each time. COLREG-COLREG draws δ1, δ2 independently from Tri(1°,15°,35°) (rounded to whole degrees, both to starboard — note this mode, 15°, differs from Task 2's illustrative 20°, since the assignment's own Task 4 instructions specify 15°). Blind-Blind draws both from U(-35°,35°). Each vessel's approach speed is drawn from U(V0-2, V0+2) kn independently. T, V_ST/V0 and β_ST are held at each vessel's fixed value from Section 2.1.1 — only rudder angle and speed vary between runs, per the assignment.`),
      p("P(collision) at a candidate separation i is the fraction of the N sampled minimum-safe-distances exceeding i (Lotovskyi & Teixeira, 2023, Eq. 1):"),
      eq("P(collision | separation = i) = count(d_min > i) / N"),
      p("The search was vectorised across all N trials at once with numpy (same algorithm as Task 2, batched) for tractable runtime. A small fraction of Blind-Blind draws never resolve at any practical distance (both vessels' random rudder happens to curve them the same way, or is too small to matter) and are censored once the search reaches a generous cap (~6 nm) without resolving — a genuine property of uncoordinated navigation, not a modelling artefact."),

      h2("5.2 Results"),
      dataTable(
        ["Scenario", "N", "Censored", "Min (nm)", "Max (nm)", "Mean (nm)", "Median (nm)"],
        [
          ["COLREG-COLREG", fmt(task4["COLREG-COLREG"].N,0), `${task4["COLREG-COLREG"].censored_count} (${fmt(task4["COLREG-COLREG"].censored_pct,1)}%)`,
            fmt(task4["COLREG-COLREG"].min_nm,2), fmt(task4["COLREG-COLREG"].max_nm,2), fmt(task4["COLREG-COLREG"].mean_nm,2), fmt(task4["COLREG-COLREG"].median_nm,2)],
          ["Blind-Blind", fmt(task4["Blind-Blind"].N,0), `${task4["Blind-Blind"].censored_count} (${fmt(task4["Blind-Blind"].censored_pct,1)}%)`,
            fmt(task4["Blind-Blind"].min_nm,2), fmt(task4["Blind-Blind"].max_nm,2), fmt(task4["Blind-Blind"].mean_nm,2), fmt(task4["Blind-Blind"].median_nm,2)],
        ],
        [2200, 1000, 1500, 1100, 1100, 1150, 1150]
      ),
      image("figures/task4_colreg_colreg.png", 430, 320),
      caption("Figure 5. Head-on, COLREG-COLREG: histogram of minimum safe distance and P(collision)."),
      image("figures/task4_blind_blind.png", 430, 320),
      caption("Figure 6. Head-on, Blind-Blind: histogram of minimum safe distance and P(collision). The rightmost bar is the censored trials, not a genuine concentration of results at that exact distance."),

      h2("5.3 Discussion"),
      p(`Both distributions are right-skewed with a long tail. Blind-Blind's median (${fmt(task4["Blind-Blind"].median_nm,2)} nm) is higher than COLREG-COLREG's (${fmt(task4["COLREG-COLREG"].median_nm,2)} nm), and unlike COLREG-COLREG it has a meaningful censored population (${fmt(task4["Blind-Blind"].censored_pct,1)}%) that cannot be resolved within a practical distance at all. This quantitatively demonstrates that coordinated, rule-following give-way manoeuvres are structurally more effective at creating separation than uncoordinated ones, where random rudder choices can just as easily send both vessels toward the same side or produce no meaningful turn at all.`),
      p("Raw per-trial samples (rudder angles, speeds, resulting minimum safe distance, censored flag) for both scenarios are provided as separate CSV files alongside this report for further analysis."),

      // SECTION 6: SUMMARY
      pageBreak,
      h1("6. Summary of Key Assumptions and Open Items"),
      bullet("T is now vessel-specific (see Section 2.1.1) via a length/speed scaling law, since the actual Silveira et al. (2016) length/type table is unavailable. Replace with the real table if it becomes accessible."),
      bullet("The MMG-vs-Nomoto-only decision for solo submissions should be confirmed in writing with course staff."),
      bullet("Task 2's search starts the give-way rudder at t=0 for each trial separation (correct for finding the minimum safe distance itself); a separate 'cruise then trigger at minimum safe distance' demonstration has not been built."),
      bullet("Task 4's Blind-Blind censoring cap and its effect on the reported tail statistics (Section 5.2) should be revisited if a tighter bound becomes necessary."),

      // REFERENCES
      pageBreak,
      h1("References"),
      p("Cockcroft, A. N., & Lameijer, J. N. F. (2012). A guide to the collision avoidance rules: International regulations for preventing collisions at sea. Elsevier."),
      p("Hashimoto, A., & Okushima, T. (1990). Evaluating marine traffic safety at channels. Accident Analysis & Prevention, 22(5), 421-442."),
      p("Lotovskyi, E., & Teixeira, A. P. (2023). Effect of timely manoeuvre execution on the collision probability in head-on and crossing encounter scenarios. In H. Le Sourne & C. Guedes Soares (Eds.), Advances in the Collision and Grounding of Ships and Offshore Structures (pp. 113-120). CRC Press."),
      p("Silveira, P., Teixeira, A. P., & Guedes Soares, C. (2016). Probabilistic modelling of evasive manoeuvring actions to avoid collisions. In Maritime Technology and Engineering III (MARTECH 2016). Taylor & Francis."),
      p("SNAME. (1989). Principles of Naval Architecture. Motions in Waves and Controllability: Vol. III (E. V. Lewis, Ed., 2nd ed.). SNAME."),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("MSMD_Project9_Report_Tasks1-4.docx", buf);
  console.log("Saved MSMD_Project9_Report_Tasks1-4.docx");
});
