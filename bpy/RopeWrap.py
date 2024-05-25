import bpy
import bmesh
from mathutils import Vector, kdtree

import KrusUtilities as ku

class OT_rope_wrap(bpy.types.Operator):
    bl_idname = "object.rope_wrap"
    bl_label = "Rope Wrap"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        target_obj = context.scene.target_obj
        plane_obj = ku.copy_and_link_object(context, context.scene.plane_obj)
        bevel_offset = context.scene.bevel_offset
        merge_threshold = context.scene.merge_threshold

        curve_depth = context.scene.curve_depth

        # select plane_obj
        bpy.context.view_layer.objects.active = plane_obj
        plane_obj.select_set(True)
        bpy.ops.object.make_single_user(object=True, obdata=True)

        # apply rotation and scale 
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # get plane's face normal 
        bm = bmesh.new()
        bm.from_mesh(plane_obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        target_face_normal = bm.faces[0].normal # local normal
        target_face_normal = plane_obj.matrix_world.to_3x3() @ target_face_normal # global normal
        bm.free()

        # add bool modifier
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
        bpy.context.object.modifiers["Boolean"].object = target_obj
        bpy.ops.object.modifier_apply(modifier="Boolean")

        # select plane_obj only 
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = plane_obj
        plane_obj.select_set(True)



        # convex hull
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        extrude_val = 0.1
        bpy.ops.mesh.extrude_region_shrink_fatten(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_shrink_fatten={"value":extrude_val, "use_even_offset":False, "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1.1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.convex_hull()

        # select face by normal 
        bm = bmesh.from_edit_mesh(plane_obj.data)
        bpy.ops.mesh.select_all(action='DESELECT')
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        rotation_matrix = plane_obj.matrix_world.to_3x3()
        for face in bm.faces:
            face_normal = rotation_matrix @ face.normal
            face.select = face_normal.angle(-target_face_normal) < 0.1
        
        bmesh.update_edit_mesh(plane_obj.data)
        bm.free()

        # filter out the rim 
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')

        # filp normal 
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.flip_normals()

        # bevel 
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=merge_threshold)
        bpy.ops.mesh.bevel(offset=bevel_offset, affect='VERTICES', clamp_overlap=True, segments=2, profile=1)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=merge_threshold/3)

        # convert to curve 
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.convert(target='CURVE')
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.spline_type_set(type='NURBS')
        bpy.ops.object.editmode_toggle()

        # align with surface normal 
        # find closest face 
        # kd = kdtree.KDTree(len(target_obj.data.polygons))
        

        curve_obj = bpy.context.object
        curve_obj.data.dimensions = '3D'
        bpy.context.object.data.resolution_u = 4
        curve_obj.data.offset = -curve_depth / 2
        curve_obj.data.bevel_depth = curve_depth
        bpy.ops.object.shade_smooth()


        # deselect all
        # bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}


class PT_rope_wrap(bpy.types.Panel):
    bl_label = "Rope Wrap Panel"
    bl_idname = "PT_rope_wrap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KrusTool'

    def draw(self, context):
        layout = self.layout

        box0 = layout.box()
        box0.label(text="Input Objects")
        box0.prop(context.scene, "plane_obj")
        box0.prop(context.scene, "target_obj")

        box1 = layout.box()
        box1.label(text="Parameters")
        box1.prop(context.scene, "merge_threshold")
        box1.prop(context.scene, "bevel_offset")

        box2 = layout.box()
        box2.label(text="Curve Params")
        box2.prop(context.scene, "curve_depth")

        row = layout.row()
        row.operator("object.rope_wrap")

def update_property(self, context):
    bpy.ops.object.rope_wrap()

def register():
    bpy.utils.register_class(OT_rope_wrap)
    bpy.utils.register_class(PT_rope_wrap)

    bpy.types.Scene.plane_obj = bpy.props.PointerProperty(type=bpy.types.Object, name="Plane", description="Plane to wrap around the target", poll=lambda self, obj: obj.type == 'MESH')
    bpy.types.Scene.target_obj = bpy.props.PointerProperty(type=bpy.types.Object, name="Target", description="Object to wrap the plane around", poll=lambda self, obj: obj.type == 'MESH')

    bpy.types.Scene.merge_threshold = bpy.props.FloatProperty(name="Merge Threshold", default=0.01, description="Threshold for merging vertices", precision=5, min=0, update=update_property)
    bpy.types.Scene.bevel_offset = bpy.props.FloatProperty(name="Bevel Offset", default=0.1, description="Offset of the bevel modifier", precision=5, min=0, update=update_property)

    bpy.types.Scene.curve_depth = bpy.props.FloatProperty(name="Curve Depth", default=0.1, description="Depth of the curve", min=0, update=update_property)

def unregister():
    bpy.utils.unregister_class(OT_rope_wrap)
    bpy.utils.unregister_class(PT_rope_wrap)

    del bpy.types.Scene.plane_obj
    del bpy.types.Scene.target_obj


if __name__ == "__main__":
    register()