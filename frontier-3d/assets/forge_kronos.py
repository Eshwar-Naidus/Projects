import bpy
import math

# Iron Rule 6 & 7: Clean factory scene and disable .blend1 backups
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0

def make_pbr_mat(name, base_color, metallic, roughness, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

mat_brass = make_pbr_mat("M_Kronos_Brass", (0.898, 0.663, 0.235, 1.0), 0.92, 0.18)
mat_obsidian = make_pbr_mat("M_Kronos_Obsidian", (0.09, 0.075, 0.125, 1.0), 0.78, 0.26)
mat_core_pulse = make_pbr_mat("M_Kronos_Pulse", (0.878, 0.424, 0.533, 1.0), 0.35, 0.15, (0.878, 0.424, 0.533, 1.0), 2.4)
mat_emerald = make_pbr_mat("M_Kronos_Telemetry", (0.275, 0.788, 0.545, 1.0), 0.55, 0.2, (0.275, 0.788, 0.545, 1.0), 1.8)

# 1. Central Chronometer Core (Icosahedron)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.42, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "SM_Kronos_Core"
core.data.name = "SM_Kronos_Core"
core.data.materials.append(mat_core_pulse)

# 2. Inner Gyroscopic Gimbal Ring
bpy.ops.mesh.primitive_torus_add(major_radius=0.72, minor_radius=0.045, major_segments=64, minor_segments=20, location=(0, 0, 0))
ring_inner = bpy.context.active_object
ring_inner.name = "SM_Kronos_Gimbal_Inner"
ring_inner.data.name = "SM_Kronos_Gimbal_Inner"
ring_inner.rotation_euler = (math.radians(32), 0, 0)
ring_inner.data.materials.append(mat_brass)

# 3. Mid Telemetry Stator Ring
bpy.ops.mesh.primitive_torus_add(major_radius=1.02, minor_radius=0.055, major_segments=72, minor_segments=24, location=(0, 0, 0))
ring_mid = bpy.context.active_object
ring_mid.name = "SM_Kronos_Stator_Mid"
ring_mid.data.name = "SM_Kronos_Stator_Mid"
ring_mid.rotation_euler = (0, math.radians(-28), math.radians(15))
ring_mid.data.materials.append(mat_obsidian)

# 4. Outer Orbital Chronometer Ring
bpy.ops.mesh.primitive_torus_add(major_radius=1.34, minor_radius=0.04, major_segments=96, minor_segments=20, location=(0, 0, 0))
ring_outer = bpy.context.active_object
ring_outer.name = "SM_Kronos_Orbit_Outer"
ring_outer.data.name = "SM_Kronos_Orbit_Outer"
ring_outer.data.materials.append(mat_brass)

# 5. Twelve Horological Indices around the Outer Ring
for i in range(12):
    ang = (i / 12.0) * math.pi * 2.0
    rx = math.cos(ang) * 1.34
    ry = math.sin(ang) * 1.34
    bpy.ops.mesh.primitive_cube_add(size=0.085, location=(rx, ry, 0))
    idx_obj = bpy.context.active_object
    idx_obj.name = f"SM_Kronos_Index_{i:02d}"
    idx_obj.data.name = f"SM_Kronos_Index_{i:02d}"
    idx_obj.scale = (1.6, 0.55, 0.55)
    idx_obj.rotation_euler = (0, 0, ang)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    idx_obj.data.materials.append(mat_emerald if i % 3 == 0 else mat_brass)

# Recalculate normals & smooth shade rings
for obj in bpy.data.objects:
    if obj.type == "MESH":
        bpy.context.view_layer.objects.active = obj
        if "Core" not in obj.name and "Index" not in obj.name:
            bpy.ops.object.shade_smooth()

blend_win = r"C:\Users\aomsa\project\frontier-3d\assets\kronos_core.blend"
glb_win = r"C:\Users\aomsa\project\frontier-3d\assets\kronos_core.glb"
bpy.ops.wm.save_as_mainfile(filepath=blend_win)
bpy.ops.export_scene.gltf(filepath=glb_win, export_format='GLB', export_apply=False)
print("FORGED_SUCCESS:", len(bpy.data.objects), "objects ->", glb_win)
