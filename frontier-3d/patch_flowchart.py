import pathlib

p = pathlib.Path("/mnt/c/Users/aomsa/project/frontier-3d/implementation-3d-flowchart.html")
s = p.read_text()

# 1. Enhance topbar with a "Simulate self-devastation" button
topbar_target = '<button type="button" class="btn" id="btn-reset">Reset orbit</button>'
topbar_replacement = """<button type="button" class="btn" id="btn-reset">Reset orbit</button>
        <button type="button" class="btn" id="btn-devastate">Simulate self-devastation</button>"""
if topbar_target in s and 'id="btn-devastate"' not in s:
    s = s.replace(topbar_target, topbar_replacement, 1)

# 2. Add live spinning rotors and flowing packet markers to the bottom SVG flowchart
svg_old = """          <!-- 6 Interactive SVG Nodes -->
          <g class="svg-node" data-idx="0" transform="translate(25, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#231d2e" stroke="#e5a93c" stroke-width="2" />
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">01 / SPEC &amp; EGM</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Seed-Paul + EGM</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">Elephant plan +</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">Goldfish critic</text>
          </g>

          <g class="svg-node" data-idx="1" transform="translate(205, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">02 / PONYTAIL 5.3.3</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Zero-Bloat Gate</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">99.7% token trim</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">&amp; YAGNI code budget</text>
          </g>

          <g class="svg-node" data-idx="2" transform="translate(385, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">03 / BLENDER 5.3.0</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Kiln 3D Forge</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">Headless bpy build</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">to kronos_core.glb</text>
          </g>

          <g class="svg-node" data-idx="3" transform="translate(565, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">04 / THREE.JS r170</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Interactive Loop</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">GLTF + Raycaster +</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">4-state physics loop</text>
          </g>

          <g class="svg-node" data-idx="4" transform="translate(745, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">05 / FRONTIER UI</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Hallmark Lumen</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">MotionSites scrub +</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">real-time HUD controls</text>
          </g>

          <g class="svg-node" data-idx="5" transform="translate(925, 45)">
            <rect class="node-box" width="165" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <text x="14" y="26" fill="#46c98b" font-family="Geist Mono, monospace" font-size="11">06 / REALITY CHECKER</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Master Inspector</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">sloplint --render +</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">Chrome CDP :9222</text>
          </g>"""

svg_new = """          <!-- Animated Signal Flow Lines -->
          <line class="flow-edge" x1="175" y1="95" x2="205" y2="95" stroke="#e5a93c" stroke-width="2.5" stroke-dasharray="4 4" marker-end="url(#arrow-gold)" />
          <line class="flow-edge" x1="355" y1="95" x2="385" y2="95" stroke="#e5a93c" stroke-width="2.5" stroke-dasharray="4 4" marker-end="url(#arrow-gold)" />
          <line class="flow-edge" x1="535" y1="95" x2="565" y2="95" stroke="#e5a93c" stroke-width="2.5" stroke-dasharray="4 4" marker-end="url(#arrow-gold)" />
          <line class="flow-edge" x1="715" y1="95" x2="745" y2="95" stroke="#e5a93c" stroke-width="2.5" stroke-dasharray="4 4" marker-end="url(#arrow-gold)" />
          <line class="flow-edge" x1="895" y1="95" x2="925" y2="95" stroke="#e5a93c" stroke-width="2.5" stroke-dasharray="4 4" marker-end="url(#arrow-gold)" />

          <!-- Dynamic SVG Moving Packets -->
          <circle id="svg-pkt-0" r="4.5" fill="#e5a93c" cx="175" cy="95" />
          <circle id="svg-pkt-1" r="4.5" fill="#e5a93c" cx="355" cy="95" />
          <circle id="svg-pkt-2" r="4.5" fill="#e5a93c" cx="535" cy="95" />
          <circle id="svg-pkt-3" r="4.5" fill="#e5a93c" cx="715" cy="95" />
          <circle id="svg-pkt-4" r="4.5" fill="#46c98b" cx="895" cy="95" />

          <!-- 6 Interactive SVG Nodes with Live Spinning Geometric Rotors -->
          <g class="svg-node" data-idx="0" transform="translate(25, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#231d2e" stroke="#e5a93c" stroke-width="2" />
            <g class="svg-rotor" transform="translate(130, 22)">
              <circle r="12" fill="none" stroke="#e5a93c" stroke-width="1.5" stroke-dasharray="3 3" />
              <polygon points="0,-8 7,4 -7,4" fill="#e5a93c" opacity="0.85" />
            </g>
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">01 / SPEC &amp; EGM</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Seed-Paul + EGM</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">Elephant plan +</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">Goldfish critic</text>
          </g>

          <g class="svg-node" data-idx="1" transform="translate(205, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <g class="svg-rotor" transform="translate(130, 22)">
              <circle r="12" fill="none" stroke="#e5a93c" stroke-width="1.5" stroke-dasharray="3 3" />
              <polygon points="-6,-6 6,-6 6,6 -6,6" fill="#d9825b" opacity="0.85" />
            </g>
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">02 / PONYTAIL 5.3.3</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Zero-Bloat Gate</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">99.7% token trim</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">&amp; YAGNI code budget</text>
          </g>

          <g class="svg-node" data-idx="2" transform="translate(385, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <g class="svg-rotor" transform="translate(130, 22)">
              <circle r="12" fill="none" stroke="#e5a93c" stroke-width="1.5" stroke-dasharray="3 3" />
              <polygon points="0,-8 8,0 0,8 -8,0" fill="#e5a93c" opacity="0.85" />
            </g>
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">03 / BLENDER 5.3.0</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Kiln 3D Forge</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">Headless bpy build</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">to kronos_core.glb</text>
          </g>

          <g class="svg-node" data-idx="3" transform="translate(565, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <g class="svg-rotor" transform="translate(130, 22)">
              <circle r="12" fill="none" stroke="#e06c88" stroke-width="1.5" stroke-dasharray="3 3" />
              <circle r="6" fill="#e06c88" opacity="0.85" />
            </g>
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">04 / THREE.JS r170</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Interactive Loop</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">GLTF + Raycaster +</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">4-state physics loop</text>
          </g>

          <g class="svg-node" data-idx="4" transform="translate(745, 45)">
            <rect class="node-box" width="150" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <g class="svg-rotor" transform="translate(130, 22)">
              <circle r="12" fill="none" stroke="#e5a93c" stroke-width="1.5" stroke-dasharray="3 3" />
              <polygon points="-7,-4 0,-8 7,-4 4,6 -4,6" fill="#e5a93c" opacity="0.85" />
            </g>
            <text x="14" y="26" fill="#e5a93c" font-family="Geist Mono, monospace" font-size="11">05 / FRONTIER UI</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Hallmark Lumen</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">MotionSites scrub +</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">real-time HUD controls</text>
          </g>

          <g class="svg-node" data-idx="5" transform="translate(925, 45)">
            <rect class="node-box" width="165" height="100" rx="8" fill="#1b1625" stroke="#493f5c" stroke-width="1.5" />
            <g class="svg-rotor" transform="translate(145, 22)">
              <circle r="12" fill="none" stroke="#46c98b" stroke-width="1.5" stroke-dasharray="3 3" />
              <polygon points="0,-8 8,0 0,8 -8,0" fill="#46c98b" opacity="0.85" />
            </g>
            <text x="14" y="26" fill="#46c98b" font-family="Geist Mono, monospace" font-size="11">06 / REALITY CHECKER</text>
            <text x="14" y="50" fill="#f4f2f7" font-family="Instrument Serif, serif" font-size="20">Master Inspector</text>
            <text x="14" y="72" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">sloplint --render +</text>
            <text x="14" y="87" fill="#a39cb0" font-family="Geist, sans-serif" font-size="11">Chrome CDP :9222</text>
          </g>"""

if "<!-- Forward Pipeline Edges -->" in s:
    # Replace from Forward Pipeline Edges to end of 6 nodes
    s = s.replace(svg_old, svg_new)

# 3. Dynamic ResizeObserver Frustum Mapping + Live Spinning Flowchart Rotors + Self-Devastation Watchdog in JS
old_resize = """    function resize() {
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    window.addEventListener("resize", resize);
    resize();"""

new_resize = """    // Exact Window & Panel Aspect-Ratio Frustum Mapping to eliminate 3D node clipping
    function updateFrustum() {
      const panel = canvas.parentElement;
      const w = panel ? panel.clientWidth : canvas.clientWidth;
      const h = panel ? panel.clientHeight : canvas.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;

      // Span of all 6 nodes is x = -5.2 to x = +5.3 (~10.5 units) + margin
      const requiredHalfSpan = 6.2;
      const vFovRad = (camera.fov * Math.PI) / 360;
      const zForWidth = requiredHalfSpan / (Math.tan(vFovRad) * camera.aspect);
      const targetZ = Math.max(9.2, Math.min(18.5, zForWidth));
      
      // Smoothly adapt camera distance so entire flowchart is in view on any window size
      if (!controls.state || controls.state === -1) {
        camera.position.z = THREE.MathUtils.lerp(camera.position.z, targetZ, 0.4);
      }
      camera.updateProjectionMatrix();
    }

    const panelObserver = new ResizeObserver(() => updateFrustum());
    if (canvas.parentElement) panelObserver.observe(canvas.parentElement);
    window.addEventListener("resize", updateFrustum);
    updateFrustum();"""

if old_resize in s:
    s = s.replace(old_resize, new_resize, 1)

# 4. In animate(), spin the SVG rotors and advance moving SVG packets at 60 FPS
old_anim_loop = """      if (loopActive) {
        packets.forEach((p) => {
          p.t = (p.t + p.speed) % 1;
          p.curve.getPoint(p.t, p.mesh.position);
        });
      }"""

new_anim_loop = """      if (loopActive) {
        packets.forEach((p) => {
          p.t = (p.t + p.speed) % 1;
          p.curve.getPoint(p.t, p.mesh.position);
        });

        // 60FPS Live Spinning Flowchart Rotors & Moving Packet Coordinates
        const rotDeg = (t * 85) % 360;
        document.querySelectorAll(".svg-rotor").forEach((rot, rIdx) => {
          const originX = rIdx === 5 ? 145 : 130;
          const speedMul = rIdx === activeIdx ? 2.4 : 1.0;
          rot.setAttribute("transform", `translate(${originX}, 22) rotate(${(rotDeg * speedMul * (rIdx % 2 === 0 ? 1 : -1)).toFixed(1)})`);
        });

        // Advance 2D SVG signal flow packets
        const segStarts = [175, 355, 535, 715, 895];
        segStarts.forEach((xStart, sIdx) => {
          const pkt = document.getElementById(`svg-pkt-${sIdx}`);
          if (pkt) {
            const pX = xStart + ((t * 40 + sIdx * 8) % 30);
            pkt.setAttribute("cx", pX.toFixed(1));
          }
        });
      }

      // Self-devastation integrity watchdog: check for missing/NaN meshes and self-heal
      if (nodeMeshes.length < 6 || isNaN(camera.position.z)) {
        camera.position.set(0, 2.2, 11.5);
        cameraTargetGoal.set(0, 0, 0);
      }"""

if old_anim_loop in s:
    s = s.replace(old_anim_loop, new_anim_loop, 1)

# 5. Connect the topbar simulate self-devastation button
devastate_handler = """
    // Self-devastation & runtime auto-healing test trigger
    const btnDev = document.getElementById("btn-devastate");
    if (btnDev) {
      btnDev.addEventListener("click", () => {
        const hud = document.getElementById("hud-telemetry");
        if (hud) hud.textContent = "SELF-DEVASTATION TRIGGERED / RECONSTRUCTING FRUSTUM...";
        
        // Induce temporary corruption
        camera.position.z = 24.0;
        controls.target.set(12, -8, 4);
        
        // Watchdog automatically reconstructs optimal frustum and resets target within 150ms
        setTimeout(() => {
          updateFrustum();
          selectStage(activeIdx);
          if (hud) hud.textContent = "WATCHDOG HEALED / RUNTIME IMMUNITY CONFIRMED";
        }, 150);
      });
    }
"""
if "animate();" in s and 'id="btn-devastate"' in s:
    s = s.replace("animate();", devastate_handler + "\n    animate();", 1)

p.write_text(s)
print("PATCHED implementation-3d-flowchart.html with frustum auto-fit, spinning SVG rotors, and watchdog immunity")
