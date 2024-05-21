# mesh_obj and curve_obj must have enough vertices to snap to each other

import bpy
import bmesh
from mathutils import Vector, kdtree

class OBJECT_OT_snap_curve_to_mesh(bpy.types.Operator):
    bl_idname = "object.snap_curve_to_mesh"
    bl_label = "Snap Curve to Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # pre
        curve_obj = context.scene.curve_obj

        mesh_obj_copy =context.scene.mesh_obj.copy()
        mesh_obj_copy.data = context.scene.mesh_obj.data.copy()
        bpy.context.collection.objects.link(mesh_obj_copy)  

        offset = context.scene.offset
        scale = context.scene.scale

        # apply all transforms
        curve_obj.select_set(True)
        mesh_obj_copy.select_set(True)       
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.select_all(action='DESELECT')

        # Get the curve data
        curve_data = curve_obj.data

        # Offset the curve by extruding the mesh 
        bpy.context.view_layer.objects.active = mesh_obj_copy
        mesh_obj_copy.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_region_shrink_fatten(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_shrink_fatten={"value":offset, "use_even_offset":False, "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1.1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')


        # Create a bmesh from the mesh object
        bm = bmesh.new()
        bm.from_mesh(mesh_obj_copy.data)
        bm.transform(mesh_obj_copy.matrix_world)

        bm.faces.ensure_lookup_table()

        # Create a kd-tree from the bmesh
        size = len(bm.verts)
        kd = kdtree.KDTree(size)

        for i, v in enumerate(bm.verts):
            v_co_global = mesh_obj_copy.matrix_world @ v.co
            kd.insert(v_co_global, i)

        kd.balance()

        # Iterate over each spline in the curve
        for spline in curve_data.splines:
            # Iterate over each point in the spline
            for point in spline.bezier_points:
                # Find the closest point on the mesh to the curve point
                co_global = curve_obj.matrix_world @ point.co
                co, index, dist = kd.find(co_global)
                
                # Move the curve point to the location of the closest point on the mesh
                point.co = curve_obj.matrix_world.inverted() @ co
                point.handle_left = point.co + scale * (point.handle_left - point.co)
                point.handle_right = point.co + scale * (point.handle_right - point.co)

        # Set the origin of the curve object to the center of its geometry
        bpy.context.view_layer.objects.active = curve_obj
        curve_obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.ops.object.select_all(action='DESELECT')

        # Free the bmesh memory 
        bm.free()

        # delete the mesh object
        bpy.context.view_layer.objects.active = mesh_obj_copy
        mesh_obj_copy.select_set(True)
        bpy.ops.object.delete(use_global=False, confirm=False)
        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'} 

class OBJECT_PT_snap_curve_to_mesh(bpy.types.Panel):
    bl_idname = "object.snap_curve_to_mesh_panel"
    bl_label = "Snap Curve to Mesh"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KrusTool'

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "curve_obj")
        layout.prop(context.scene, "mesh_obj")
        layout.prop(context.scene, "offset")
        layout.prop(context.scene, "scale")

        layout.operator("object.snap_curve_to_mesh")

def register():
    bpy.utils.register_class(OBJECT_OT_snap_curve_to_mesh)
    bpy.utils.register_class(OBJECT_PT_snap_curve_to_mesh)

    bpy.types.Scene.curve_obj = bpy.props.PointerProperty(type=bpy.types.Object, name="Curve", description="Curve to snap to the mesh", poll=lambda self, obj: obj.type == 'CURVE')
    bpy.types.Scene.mesh_obj = bpy.props.PointerProperty(type=bpy.types.Object, name="Mesh", description="Mesh to snap the curve to", poll=lambda self, obj: obj.type == 'MESH')
    bpy.types.Scene.offset = bpy.props.FloatProperty(name="Offset", description="Offset distance", default=0.0)
    bpy.types.Scene.scale = bpy.props.FloatProperty(name="Scale", description="Scale factor", default=1.0)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_snap_curve_to_mesh)
    bpy.utils.unregister_class(OBJECT_PT_snap_curve_to_mesh)

    del bpy.types.Scene.curve_obj
    del bpy.types.Scene.mesh_obj

if __name__ == "__main__":
    register()