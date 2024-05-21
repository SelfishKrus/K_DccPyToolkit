import bpy

class InsetFacesOperator(bpy.types.Operator):
    bl_idname = "object.inset_faces"
    bl_label = "Inset Faces"

    def execute(self, context):
        inset_depth = context.window_manager.inset_depth

        # Loop through all selected objects
        for obj in bpy.context.selected_objects:
            # Make sure the object is a mesh
            if obj.type == 'MESH':
                # Set the object as the active object
                bpy.context.view_layer.objects.active = obj
                # Go into edit mode
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
                # Select all faces
                bpy.ops.mesh.select_all(action='SELECT')
                # Inset the faces
                bpy.ops.mesh.inset(thickness=inset_depth, use_individual=True, use_select_inset=True)
                #delete selected outer faces
                bpy.ops.mesh.delete(type='FACE')
                # Go back to object mode
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    
class InsetFacesButtonOperator(bpy.types.Operator):
    bl_idname = "object.inset_faces_button"
    bl_label = "Inset Faces"

    def execute(self, context):
        bpy.ops.object.inset_faces()
        return {'FINISHED'}

class InsetFacesPanel(bpy.types.Panel):
    bl_label = "Inset Faces"
    bl_idname = "OBJECT_PT_inset_faces"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KrusTool"

    def draw(self, context):
        layout = self.layout

        # Property slider
        row = layout.row()
        row.prop(context.window_manager, 'inset_depth')

        # Button
        row = layout.row()
        row.operator("object.inset_faces_button")

def register():
    bpy.types.WindowManager.inset_depth = bpy.props.FloatProperty(name="Inset Depth", default=0.01)
    bpy.utils.register_class(InsetFacesOperator)
    bpy.utils.register_class(InsetFacesButtonOperator)
    bpy.utils.register_class(InsetFacesPanel)

def unregister():
    del bpy.types.WindowManager.inset_depth
    bpy.utils.unregister_class(InsetFacesOperator)
    bpy.utils.unregister_class(InsetFacesButtonOperator)
    bpy.utils.unregister_class(InsetFacesPanel)

if __name__ == "__main__":
    register()