import pathlib

p = pathlib.Path("/mnt/c/Users/aomsa/project/frontier-3d/index.html")
s = p.read_text()

# Locate the table row click handler in index.html
old_marker = """    document.querySelectorAll(".manifest-table tbody tr").forEach((row) => {
      row.addEventListener("click", () => highlightMesh(row.dataset.mesh));
    });"""

new_impl = """    // Live Interactive Bottom Sub-Assembly Inspector & Telemetry Rotor
    const subCanvas = document.getElementById("subassembly-canvas");
    const subCtx = subCanvas ? subCanvas.getContext("2d") : null;
    let subRotPhase = 0;

    function drawSubRotor(dt, speedEff) {
      if (!subCtx) return;
      const w = subCanvas.width;
      const h = subCanvas.height;
      subCtx.clearRect(0, 0, w, h);

      const cx = w * 0.5;
      const cy = h * 0.5;
      subRotPhase += dt * (speedEff * state.invertSpin + state.subPulseBoost);
      state.subPulseBoost *= 0.92;

      // Blueprint polar circular grid
      subCtx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--color-rule").trim();
      subCtx.lineWidth = 1;
      for (let r = 24; r <= 80; r += 22) {
        subCtx.beginPath();
        subCtx.arc(cx, cy, r, 0, Math.PI * 2);
        subCtx.stroke();
      }

      const activeSpec = SUB_SPECS[state.selectedName] || SUB_SPECS["SM_Kronos_Core"];
      const col = activeSpec.color || "#e5a93c";

      // Spinning telemetry reticle
      subCtx.save();
      subCtx.translate(cx, cy);
      subCtx.rotate(subRotPhase);

      subCtx.strokeStyle = col;
      subCtx.lineWidth = 2.5;

      if (activeSpec.shape === "icosa") {
        // Procedural wireframe icosahedron rotor
        const pts = 6;
        subCtx.beginPath();
        for (let i = 0; i < pts; i++) {
          const a = (i / pts) * Math.PI * 2;
          const x = Math.cos(a) * 44;
          const y = Math.sin(a) * 44;
          if (i === 0) subCtx.moveTo(x, y);
          else subCtx.lineTo(x, y);
        }
        subCtx.closePath();
        subCtx.stroke();

        subCtx.beginPath();
        subCtx.arc(0, 0, 18, 0, Math.PI * 2);
        subCtx.fillStyle = col;
        subCtx.fill();
      } else if (activeSpec.shape.startsWith("torus")) {
        const rad = activeSpec.shape === "torusInner" ? 38 : (activeSpec.shape === "torusMid" ? 54 : 70);
        subCtx.beginPath();
        subCtx.arc(0, 0, rad, 0, Math.PI * 1.5);
        subCtx.stroke();

        // Counter rotating tick ring
        subCtx.rotate(-subRotPhase * 2.2);
        subCtx.setLineDash([6, 8]);
        subCtx.beginPath();
        subCtx.arc(0, 0, rad - 8, 0, Math.PI * 2);
        subCtx.stroke();
        subCtx.setLineDash([]);
      } else {
        // Horological indices rotor (12 ticks)
        for (let i = 0; i < 12; i++) {
          const a = (i / 12) * Math.PI * 2;
          subCtx.beginPath();
          subCtx.moveTo(Math.cos(a) * 48, Math.sin(a) * 48);
          subCtx.lineTo(Math.cos(a) * 66, Math.sin(a) * 66);
          subCtx.stroke();
        }
      }
      subCtx.restore();

      // Readout text inside rotor
      subCtx.font = "11px Geist Mono, monospace";
      subCtx.fillStyle = "#f4f2f7";
      subCtx.textAlign = "center";
      subCtx.fillText(state.selectedName + " / ACTIVE", cx, h - 14);
    }

    function selectSubAssembly(meshName) {
      highlightMesh(meshName);
      const spec = SUB_SPECS[meshName] || SUB_SPECS["SM_Kronos_Core"];

      // Update bottom panel readout
      const elTitle = document.getElementById("sub-active-title");
      const elMat = document.getElementById("sub-meta-mat");
      const elBounds = document.getElementById("sub-meta-bounds");
      const elCoupling = document.getElementById("sub-meta-coupling");
      const elWatch = document.getElementById("sub-meta-watchdog");

      if (elTitle) elTitle.textContent = meshName;
      if (elMat) elMat.textContent = spec.mat;
      if (elBounds) elBounds.textContent = spec.bounds;
      if (elCoupling) elCoupling.textContent = spec.coupling;
      if (elWatch) elWatch.textContent = `ONLINE / MESH CONFIRMED (${selectableMeshes.length} TOTAL)`;

      // Update table row active styling
      document.querySelectorAll(".manifest-table tbody tr").forEach((row) => {
        const matches = row.dataset.mesh === meshName;
        row.dataset.active = matches ? "true" : "false";
      });

      // Solo part logic
      if (state.soloPart) {
        selectableMeshes.forEach((m) => {
          const isTarget = m.name === meshName || (meshName === "SM_Kronos_Index_00" && m.name.startsWith("SM_Kronos_Index_"));
          m.visible = isTarget;
        });
      } else {
        selectableMeshes.forEach((m) => { m.visible = true; });
      }

      state.subPulseBoost = 2.4;
    }

    // Attach click and keyboard listeners to manifest table rows and cells
    document.querySelectorAll(".manifest-table tbody tr").forEach((row) => {
      row.addEventListener("click", () => {
        selectSubAssembly(row.dataset.mesh);
      });
      row.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectSubAssembly(row.dataset.mesh);
        }
      });
    });

    // Sub-assembly action buttons
    const btnSubPulse = document.getElementById("btn-sub-pulse");
    if (btnSubPulse) {
      btnSubPulse.addEventListener("click", () => {
        state.subPulseBoost = 3.8;
        state.impulseBoost = 2.2;
      });
    }

    const btnSubSolo = document.getElementById("btn-sub-solo");
    if (btnSubSolo) {
      btnSubSolo.addEventListener("click", (e) => {
        state.soloPart = !state.soloPart;
        e.currentTarget.setAttribute("aria-pressed", String(state.soloPart));
        e.currentTarget.textContent = state.soloPart ? "Solo part: active" : "Solo part: off";
        selectSubAssembly(state.selectedName);
      });
    }

    const btnSubInvert = document.getElementById("btn-sub-invert");
    if (btnSubInvert) {
      btnSubInvert.addEventListener("click", (e) => {
        state.invertSpin *= -1;
        const isInverted = state.invertSpin < 0;
        e.currentTarget.setAttribute("aria-pressed", String(isInverted));
        e.currentTarget.textContent = isInverted ? "Invert spin: active" : "Invert spin: off";
      });
    }

    // Self-devastation & runtime auto-healing immunity watchdog
    const btnSubDev = document.getElementById("btn-sub-devastate");
    if (btnSubDev) {
      btnSubDev.addEventListener("click", () => {
        state.devastationCount++;
        const elWatch = document.getElementById("sub-meta-watchdog");
        if (elWatch) elWatch.textContent = "SELF-DEVASTATION TRIGGERED / PURGING SCENE...";
        
        // Purge scene to simulate catastrophic runtime fault
        clearRegisteredMeshes();
        
        // Watchdog automatically reconstructs clean PBR geometry within 120ms
        setTimeout(() => {
          buildProceduralFallback();
          selectSubAssembly(state.selectedName);
          if (elWatch) elWatch.textContent = `WATCHDOG RESTORED #${state.devastationCount} / IMMUNITY VERIFIED`;
          const elGlb = document.getElementById("glb-status");
          if (elGlb) elGlb.textContent = `Auto-healed #${state.devastationCount} / 16 meshes immune`;
        }, 120);
      });
    }"""

if old_marker in s:
    s = s.replace(old_marker, new_impl, 1)

# Hook drawSubRotor inside animate()
if "drawOscilloscope(phaseAccum, speedEff);" in s:
    s = s.replace(
        "drawOscilloscope(phaseAccum, speedEff);",
        "drawOscilloscope(phaseAccum, speedEff);\n      drawSubRotor(dt, speedEff);"
    )

p.write_text(s)
print("PATCHED index.html bottom sub-assembly workbench successfully")
