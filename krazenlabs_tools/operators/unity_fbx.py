import bpy
import mathutils
import math
import os

# Multi-user datablocks are preserved here. Unique copies are made for applying the rotation.
# Eventually multi-user datablocks become single-user and gets processed.
# Therefore restoring the multi-user data assigns a shared but already processed datablock.
shared_data = dict()

# All objects and collections in this view layer must be visible while being processed.
# apply_rotation and matrix changes don't have effect otherwise.
# Visibility will be restored right before saving the FBX.
hidden_collections = []
hidden_objects = []
disabled_collections = []
disabled_objects = []


def unhide_collections(col):
    global hidden_collections
    global disabled_collections

    # No need to unhide excluded collections. Their objects aren't included in current view layer.
    if col.exclude:
        return

    # Find hidden child collections and unhide them
    hidden = [item for item in col.children if not item.exclude and item.hide_viewport]
    for item in hidden:
        item.hide_viewport = False

    # Add them to the list so they could be restored later
    hidden_collections.extend(hidden)

    # Same with the disabled collections
    disabled = [item for item in col.children if not item.exclude and item.collection.hide_viewport]
    for item in disabled:
        item.collection.hide_viewport = False

    disabled_collections.extend(disabled)

    # Recursively unhide child collections
    for item in col.children:
        unhide_collections(item)


def unhide_objects():
    global hidden_objects
    global disabled_objects

    view_layer_objects = [ob for ob in bpy.data.objects if
                          ob.name in bpy.context.view_layer.objects]

    for ob in view_layer_objects:
        if ob.hide_get():
            hidden_objects.append(ob)
            ob.hide_set(False)
        if ob.hide_viewport:
            disabled_objects.append(ob)
            ob.hide_viewport = False


def make_single_user_data():
    global shared_data

    for ob in bpy.data.objects:
        if ob.data and ob.data.users > 1:
            if ob.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}:
                # Figure out the objects that use this datablock
                users = [user for user in bpy.data.objects if user.data == ob.data]

                # Shared data will be restored if users have no active modifiers
                modifiers = 0
                for user in users:
                    modifiers += len([mod for mod in user.modifiers if mod.show_viewport])
                if modifiers == 0:
                    shared_data[ob.name] = ob.data

            # Make single-user copy
            ob.data = ob.data.copy()


def apply_object_modifiers():
    # Select objects in current view layer not using an armature modifier
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.data.objects:
        if ob.name in bpy.context.view_layer.objects:
            bypass_modifiers = False
            for mod in ob.modifiers:
                if mod.type == 'ARMATURE':
                    bypass_modifiers = True
            if not bypass_modifiers:
                ob.select_set(True)

    # Conversion to mesh may not be available depending on the remaining objects
    if bpy.ops.object.convert.poll():
        bpy.ops.object.convert(target='MESH')


def reset_parent_inverse(ob):
    if (ob.parent):
        mat_world = ob.matrix_world.copy()
        ob.matrix_parent_inverse.identity()
        ob.matrix_basis = ob.parent.matrix_world.inverted() @ mat_world


def apply_rotation(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


def fix_object(ob):
    # Only fix objects in current view layer
    if ob.name in bpy.context.view_layer.objects:
        # Reset parent's inverse so we can work with local transform directly
        reset_parent_inverse(ob)

        # Create a copy of the local matrix and set a pure X-90 matrix
        mat_original = ob.matrix_local.copy()
        ob.matrix_local = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')

        # Apply the rotation to the object
        apply_rotation(ob)

        # Reapply the previous local transform with an X+90 rotation
        ob.matrix_local = mat_original @ mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')

    # Recursively fix child objects in current view layer.
    # Children may be in the current view layer even if their parent isn't.
    for child in ob.children:
        fix_object(child)


def export_unity_fbx(context, filepath, active_collection, selected_objects, deform_bones,
                     leaf_bones, primary_bone_axis, secondary_bone_axis):
    global shared_data
    global hidden_collections
    global hidden_objects
    global disabled_collections
    global disabled_objects

    print("Preparing 3D model for Unity...")

    # Root objects: Empty, Mesh or Armature without parent
    root_objects = [item for item in bpy.data.objects if (
            item.type == "EMPTY" or item.type == "MESH" or item.type == "ARMATURE") and not item.parent]

    # Preserve current scene
    # undo_push examples, including exporters' execute:
    # https://programtalk.com/python-examples/bpy.ops.ed.undo_push  (Examples 4, 5 and 6)
    # https://sourcecodequery.com/example-method/bpy.ops.ed.undo  (Examples 1 and 2)

    bpy.ops.ed.undo_push(message="Prepare Unity FBX")

    shared_data = dict()
    hidden_collections = []
    hidden_objects = []
    disabled_collections = []
    disabled_objects = []

    selection = bpy.context.selected_objects

    # Object mode
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except:
        pass

    # Ensure all the collections and objects in this view layer are visible
    unhide_collections(bpy.context.view_layer.layer_collection)
    unhide_objects()

    # Create a single copy in multi-user datablocks. Will be restored after fixing rotations.
    make_single_user_data()

    # Apply modifiers to objects (except those affected by an armature)
    apply_object_modifiers()

    try:
        # Fix rotations
        for ob in root_objects:
            print(ob.name)
            fix_object(ob)

        # Restore multi-user meshes
        for item in shared_data:
            bpy.data.objects[item].data = shared_data[item]

        # Recompute the transforms out of the changed matrices
        bpy.context.view_layer.update()

        # Restore hidden and disabled objects
        for ob in hidden_objects:
            ob.hide_set(True)
        for ob in disabled_objects:
            ob.hide_viewport = True

        # Restore hidden and disabled collections
        for col in hidden_collections:
            col.hide_viewport = True
        for col in disabled_collections:
            col.collection.hide_viewport = True

        # Restore selection
        bpy.ops.object.select_all(action='DESELECT')
        for ob in selection:
            ob.select_set(True)

        # Export FBX file

        params = dict(filepath=filepath, apply_scale_options='FBX_SCALE_UNITS',
                      object_types={'EMPTY', 'MESH', 'ARMATURE'},
                      use_active_collection=active_collection, use_selection=selected_objects,
                      use_armature_deform_only=deform_bones, add_leaf_bones=leaf_bones,
                      primary_bone_axis=primary_bone_axis, secondary_bone_axis=secondary_bone_axis)

        print("Invoking default FBX Exporter:", params)
        bpy.ops.export_scene.fbx(**params)

    except Exception as e:
        bpy.ops.ed.undo_push(message="")
        bpy.ops.ed.undo()
        bpy.ops.ed.undo_push(message="Export Unity FBX")
        print(e)
        print("File not saved.")
        # Always finish with 'FINISHED' so Undo is handled properly
        return {'FINISHED'}

    # Restore scene and finish

    bpy.ops.ed.undo_push(message="")
    bpy.ops.ed.undo()
    bpy.ops.ed.undo_push(message="Export Unity FBX")
    print("FBX file for Unity saved.")
    return {'FINISHED'}


# ---------------------------------------------------------------------------------------------------
# Exporter stuff (from the Operator File Export template)

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy.types import Operator


def start_export(call_operator, context, export_target):
    # Get the export path and file name from the current scene.
    if export_target == "unity":
        export_path = context.scene.unity_export_path
        export_file_name = context.scene.unity_export_file_name
    elif export_target == "substance":
        export_path = context.scene.substance_export_path
        export_file_name = context.scene.substance_export_file_name
    else:
        call_operator.report({'WARNING'}, "No valid export target was given.")
        return {'CANCELLED'}
    # Combine the export path with the file name to get the full path.
    full_path = os.path.join(export_path, export_file_name)
    return export_unity_fbx(context, full_path, context.scene.active_collection,
                            context.scene.selected_objects, context.scene.deform_bones,
                            context.scene.leaf_bones, context.scene.primary_bone_axis,
                            context.scene.secondary_bone_axis)


class ExportUnityFbx(Operator):
    """FBX exporter compatible with Unity's coordinate and scaling system"""
    bl_idname = "export_scene.unity_fbx"
    bl_label = "Export Unity FBX"
    bl_options = {'UNDO_GROUPED'}

    def execute(self, context):
        export_target = "unity"
        return start_export(self, context, export_target)

class ExportSubstanceFbx(Operator):
    bl_idname = "export_scene.substance_fbx"
    bl_label = "Export Substance FBX"
    bl_options = {'UNDO_GROUPED'}

    def execute(self, context):
        export_target = "substance"
        return start_export(self, context, export_target)