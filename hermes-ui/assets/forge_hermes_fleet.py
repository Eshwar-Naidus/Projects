"""
Headless Blender 5.3.0 procedural asset forge for hermes-ui.
Constructs Hermes Mother-Ship Carrier + Orbital Drone Cluster.
Rules: blender-kiln v3.0, 1 unit = 1m, PascalCase naming, PBR materials.
"""
import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)

def make_mat(name, col, metallic=0.85, roughness=0.2, emissive_col=None, emissive_str=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = col
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emissive_col and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emissive_col
            bsdf.inputs["Emission Strength"].default_value = emissive_str
    return mat

mat_hull = make_mat("M_Hermes_Hull", (0.08, 0.08, 0.12, 1.0), metallic=0.9, roughness=0.18)
mat_gold = make_mat("M_Hermes_Antenna", (0.9, 0.66, 0.23, 1.0), metallic=0.95, roughness=0.12, emissive_col=(0.9, 0.66, 0.23, 1.0), emissive_str=1.2)
mat_ion = make_mat("M_Hermes_IonGlow", (0.1, 0.8, 0.45, 1.0), metallic=0.2, roughness=0.3, emissive_col=(0.1, 0.8, 0.45, 1.0), emissive_str=3.5)

# 1. SM_Hermes_Carrier (Command Mother-Ship)
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.2, depth=3.8, location=(0, 0, 0))
carrier = bpy.context.active_object
carrier.name = "SM_Hermes_Carrier"
carrier.rotation_euler = (math.pi / 2, 0, 0)
carrier.data.materials.append(mat_hull)

# 2. SM_Hermes_SensoryArray (Golden Forward Bevel)
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.1, depth=1.6, location=(0, 2.5, 0))
cone = bpy.context.active_object
cone.name = "SM_Hermes_SensoryArray"
cone.rotation_euler = (-math.pi / 2, 0, 0)
cone.data.materials.append(mat_gold)

# 3. SM_Hermes_EngineBay (Ion Drive Core)
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.85, depth=0.8, location=(0, -2.2, 0))
engine = bpy.context.active_object
engine.name = "SM_Hermes_EngineBay"
engine.rotation_euler = (math.pi / 2, 0, 0)
engine.data.materials.append(mat_ion)

# 4. SM_Hermes_DockingGimbal (Orbital Ring Stator)
bpy.ops.mesh.primitive_torus_add(major_radius=2.2, minor_radius=0.08, major_segments=48, minor_segments=16, location=(0, 0, 0))
stator = bpy.context.active_object
stator.name = "SM_Hermes_DockingGimbal"
stator.data.materials.append(mat_gold)

# 5. SM_Hermes_Drone_01 & 02 (Escort Sub-Workers)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.45, location=(-3.2, 0.8, 1.2))
d1 = bpy.context.active_object
d1.name = "SM_Hermes_Drone_01"
d1.data.materials.append(mat_ion)

bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.45, location=(3.2, -0.8, -1.2))
d2 = bpy.context.active_object
d2.name = "SM_Hermes_Drone_02"
d2.data.materials.append(mat_ion)

# Export to glTF binary
out_glb = "C:\\Users\\aomsa\\project\\hermes-ui\\assets\\hermes_fleet.glb"
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format="GLB",
    use_selection=False,
    export_apply=False
)
print("HERMES_FLEET_FORGE_COMPLETE:", out_glb)
