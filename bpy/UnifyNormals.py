import bpy
import bmesh
from mathutils import Vector

class UnifyNormalsOperator(bpy.types.Operator):
    bl_idname = "object.unify_normals_operator"
    bl_label = "Unify Normals Operator"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        color_name = "NormalColor"
        b_write_into_vertex_color = bpy.context.window_manager.b_write_into_vertex_color

        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh = obj.data
                bbox = obj.bound_box

                # Get bbox center and radius
                local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
                global_bbox_center = obj.matrix_world @ local_bbox_center

                min_corner = Vector(bbox[0])
                max_corner = Vector(bbox[6])
                radius = (max_corner - min_corner).length / 2

                # Create a smooth sphere 
                bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=global_bbox_center)
                sphere = bpy.context.object
                bpy.ops.object.shade_smooth()

                # Add DATA_TRANSFER modifier for obj
                bpy.ops.object.select_all(action='DESELECT')

                data_transfer_modifier = obj.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
                data_transfer_modifier.use_loop_data = True
                data_transfer_modifier.data_types_loops = {'CUSTOM_NORMAL'}
                data_transfer_modifier.object = sphere
                
                # Apply modifier
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier="DataTransfer")

                # Delete sphere
                bpy.ops.object.select_all(action='DESELECT')
                sphere.select_set(True)
                bpy.ops.object.delete()

                mesh.update()

                if b_write_into_vertex_color:
                    self.report({'INFO'}, "Writing normals into vertex color")
                    # Ensure the object is in object mode
                    bpy.ops.object.mode_set(mode='OBJECT')

                    if color_name not in mesh.color_attributes:
                        mesh.color_attributes.new(name=color_name, type="FLOAT_COLOR", domain="CORNER")
                    color_layer = mesh.color_attributes[color_name]
                    self.report({'INFO'}, "Created new color attribute")

                    color_data = color_layer.data

                    # Remap normals and store in vertex color
                    for poly in mesh.polygons:
                        for loop_index in poly.loop_indices:
                            loop = mesh.loops[loop_index]
                            normal = loop.normal
                            # Remap normal from (-1, 1) to (0, 1)
                            remapped_normal = normal * 0.5 + Vector((0.5, 0.5, 0.5))
                            color_data[loop_index].color = (remapped_normal.x, remapped_normal.y, remapped_normal.z, 1.0)  # RGBA

                    mesh.update()

                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.mesh.customdata_custom_splitnormals_clear()



        return {'FINISHED'}

class UnifyNormalsButtonOperator(bpy.types.Operator):
    bl_idname = "object.unify_normals_button"
    bl_label = "Unify Normals Button"

    def execute(self, context):
        bpy.ops.object.unify_normals_operator()
        return {'FINISHED'}

class UnifyNormalsOperatorPanel(bpy.types.Panel):
    bl_label = "Unify Normals Operator"
    bl_idname = "OBJECT_PT_unify_normals_operator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KrusTool"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        # Property slider
        row = layout.row()
        row.prop(wm, "b_write_into_vertex_color", text="Write into Vertex Color")

        # Button
        row = layout.row()
        row.operator("object.unify_normals_button")

def register():
    bpy.utils.register_class(UnifyNormalsOperator)
    bpy.utils.register_class(UnifyNormalsButtonOperator)
    bpy.utils.register_class(UnifyNormalsOperatorPanel)
    bpy.types.WindowManager.b_write_into_vertex_color = bpy.props.BoolProperty(
        name="Write into Vertex Color",
        description="A custom boolean property",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(UnifyNormalsOperator)
    bpy.utils.unregister_class(UnifyNormalsButtonOperator)
    bpy.utils.unregister_class(UnifyNormalsOperatorPanel)
    del bpy.types.WindowManager.b_write_into_vertex_color

if __name__ == "__main__":
    register()