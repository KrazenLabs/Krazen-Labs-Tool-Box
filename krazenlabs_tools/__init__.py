bl_info = {
    "name": "Krazen Labs Tool Box",
    "author": "Krazen Labs (krazenlabs.com)",
    "version": (1, 0),
    "blender": (3, 5, 1),
    "location": "View3D > Sidebar > Krazen Labs Tab",
    "description": "A collection of tools to aid in the creation of 3d avatars.",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

import bpy

from .operators.join_meshes import KRAZENLABS_OT_join_meshes
from .ui.panel import KRAZENLABS_PT_panel


def register():
    bpy.utils.register_class(KRAZENLABS_OT_join_meshes)
    bpy.utils.register_class(KRAZENLABS_PT_panel)


def unregister():
    bpy.utils.unregister_class(KRAZENLABS_OT_join_meshes)
    bpy.utils.unregister_class(KRAZENLABS_PT_panel)



if __name__ == "__main__":
    register()
