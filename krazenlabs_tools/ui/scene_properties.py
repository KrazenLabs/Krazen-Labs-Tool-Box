import bpy

# Define scene properties
bpy.types.Scene.unity_export_path = bpy.props.StringProperty(
    name="Unity Export Path",
    description="Path to export FBX files to",
    default="",
    maxlen=1024,
    subtype='DIR_PATH'
)

bpy.types.Scene.unity_export_file_name = bpy.props.StringProperty(
    name="Unity Export File Name",
    description="Name of the exported file",
    default="my_export.fbx",
    maxlen=1024,
    subtype='FILE_NAME'
)

bpy.types.Scene.selected_objects = bpy.props.BoolProperty(
    name="Selected Objects Only",
    description="Export selected objects only. May be combined with Active Collection Only.",
    default=True,
)

bpy.types.Scene.active_collection = bpy.props.BoolProperty(
    name="Active Collection Only",
    description="Export objects in the active collection only (and its children). May be combined with Selected Objects Only.",
    default=True,
)

bpy.types.Scene.deform_bones = bpy.props.BoolProperty(
    name="Only Deform Bones",
    description="Only write deforming bones (and non-deforming ones when they have deforming children)",
    default=False,
)

bpy.types.Scene.leaf_bones = bpy.props.BoolProperty(
    name="Add Leaf Bones",
    description="Append a final bone to the end of each chain to specify last bone length (use this when you intend to edit the armature from exported data)",
    default=False,
)

bpy.types.Scene.primary_bone_axis = bpy.props.EnumProperty(
    name="Primary Bone Axis",
    items=(('X', "X Axis", ""),
           ('Y', "Y Axis", ""),
           ('Z', "Z Axis", ""),
           ('-X', "-X Axis", ""),
           ('-Y', "-Y Axis", ""),
           ('-Z', "-Z Axis", ""),
           ),
    default='Y',
)
bpy.types.Scene.secondary_bone_axis = bpy.props.EnumProperty(
    name="Secondary Bone Axis",
    items=(('X', "X Axis", ""),
           ('Y', "Y Axis", ""),
           ('Z', "Z Axis", ""),
           ('-X', "-X Axis", ""),
           ('-Y', "-Y Axis", ""),
           ('-Z', "-Z Axis", ""),
           ),
    default='X',
)


# Panel class
class KRAZENLABS_PT_export_properties_panel(bpy.types.Panel):
    bl_label = "FBX Export Settings"
    bl_idname = "KRAZENLABS_PT_export_properties_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "unity_export_path")
        layout.prop(scene, "unity_export_file_name")
        layout.prop(scene, "active_collection")
        layout.prop(scene, "selected_objects")
        layout.prop(scene, "deform_bones")
        layout.prop(scene, "leaf_bones")
        layout.prop(scene, "primary_bone_axis")
        layout.prop(scene, "secondary_bone_axis")