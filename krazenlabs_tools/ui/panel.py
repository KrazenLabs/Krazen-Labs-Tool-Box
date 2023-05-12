import bpy

class KRAZENLABS_PT_panel(bpy.types.Panel):
    bl_label = "Krazen Labs"
    bl_idname = "KRAZENLABS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Krazen Labs'

    def draw(self, context):
        layout = self.layout
        layout.operator("kl_tools.join_meshes")
        layout.operator("export_scene.unity_fbx")
