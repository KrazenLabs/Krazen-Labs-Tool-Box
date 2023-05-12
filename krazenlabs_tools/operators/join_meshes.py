import bpy

# Recursive function to find layer collection from a collection
def find_layer_collection(layer_coll, coll):
    found = None
    if (layer_coll.collection == coll):
        return layer_coll
    for layer in layer_coll.children:
        found = find_layer_collection(layer, coll)
        if found:
            return found

class KRAZENLABS_OT_join_meshes(bpy.types.Operator):
    bl_idname = "kl_tools.join_meshes"
    bl_label = "Join Meshes"
    bl_description = "Joins child meshes of an armature into a single mesh, based on collections"

    def execute(self, context):
        # Get the selected armature
        armature = context.object

        # Make sure an armature is selected
        if not armature or armature.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature.")
            return {'CANCELLED'}
        else:
            # Create the "Combined" collection if it doesn't exist, or clear it if it does
            combined_collection = bpy.data.collections.get("Combined")
            if combined_collection is None:
                combined_collection = bpy.data.collections.new("Combined")
                context.scene.collection.children.link(combined_collection)
            else:
                for obj in combined_collection.objects:
                    bpy.data.objects.remove(obj)

            valid_submeshes_found = False

            # Go through each collection in the scene
            for collection in bpy.data.collections:
                if collection != combined_collection:  # Skip the "Combined" collection
                    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects

                    # Find all child objects of the armature in the collection
                    child_objects = [obj for obj in collection.objects if obj.parent == armature]

                    if child_objects:
                        valid_submeshes_found = True

                        for obj in child_objects:
                            # Duplicate the object and select the duplicate
                            duplicate = obj.copy()
                            duplicate.data = obj.data.copy()
                            context.collection.objects.link(duplicate)
                            duplicate.select_set(True)

                            # Set the duplicate as the active object
                            context.view_layer.objects.active = duplicate

                        # Join all selected objects
                        bpy.ops.object.join()

                        # Rename the joined object after the collection
                        context.object.name = collection.name

                        # Move the joined object to the "Combined" collection
                        combined_collection.objects.link(context.object)
                        context.collection.objects.unlink(context.object)

                        # Exclude the original collection from the view layer
                        layer_collection = find_layer_collection(
                            context.view_layer.layer_collection, collection)
                        layer_collection.exclude = True

            if not valid_submeshes_found:
                self.report({'WARNING'}, "No valid submeshes found for joining.")
                return {'CANCELLED'}

            self.report({'INFO'}, "Meshes joined successfully.")
            return {'FINISHED'}
