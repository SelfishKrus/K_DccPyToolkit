import bpy

### variables
_bl_idname = "object.custom_operator"
_bl_label = "Custom Operator"
_bl_idname_button = _bl_idname + "_button"

class CustomOperator(bpy.types.Operator):
    ### id name & label
    bl_idname = _bl_idname
    bl_label = _bl_label

    def execute(self, context):
        ### get inputs from property
        custom_input = context.window_manager.custom_input

        print("button pressed!!!!")

        return {'FINISHED'}
    
class CustomButtonOperator(bpy.types.Operator):
    bl_idname = _bl_idname_button
    bl_label = _bl_label

    def execute(self, context):
        ### custom operator execution
        bpy.ops.object.custom_operator()
        return {'FINISHED'}

class CustomOperatorPanel(bpy.types.Panel):
    bl_label = _bl_label
    bl_idname = _bl_idname
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KrusTool"

    def draw(self, context):
        layout = self.layout

        ### Property slider
        row = layout.row()
        row.prop(context.window_manager, 'custom_input')

        # Button
        row = layout.row()
        row.operator(_bl_idname_button)

def register():
    ### properties
    bpy.types.WindowManager.custom_input = bpy.props.FloatProperty(name="Custom Input", default=0.01)

    bpy.utils.register_class(CustomOperator)
    bpy.utils.register_class(CustomButtonOperator)
    bpy.utils.register_class(CustomOperatorPanel)

def unregister():
    del bpy.types.WindowManager.custom_input
    bpy.utils.unregister_class(CustomOperator)
    bpy.utils.unregister_class(CustomButtonOperator)
    bpy.utils.unregister_class(CustomOperatorPanel)

if __name__ == "__main__":
    register()