# mesh_obj and curve_obj must have enough vertices to snap to each other

import bpy
import bmesh
import mathutils
from mathutils import Vector, kdtree

class OBJECT_OT_rope_attacher(bpy.types.Operator):
    bl_idname = "object.rope_attacher"
    bl_label = "Rope Attacher"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # pre
        mesh_obj = context.scene.mesh_obj
        # smooth_factor = context.scene.smooth_factor
        # smooth_iterations = context.scene.smooth_iterations
        curve_extrude = context.scene.curve_extrude
        curve_depth = context.scene.curve_depth
        curve_cyclic = context.scene.curve_cyclic

        # copy curve_obj
        curve_obj_name = context.scene.curve_obj.name + "_copy"
        # delete
        if curve_obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[curve_obj_name], do_unlink=True)
        curve_obj = context.scene.curve_obj.copy()
        curve_obj.data = context.scene.curve_obj.data.copy()
        curve_obj.name = curve_obj_name
        bpy.context.collection.objects.link(curve_obj)

        # select curve_obj
        bpy.context.view_layer.objects.active = curve_obj
        curve_obj.select_set(True)
        bpy.ops.object.make_single_user(object=True, obdata=True)

        # add SHRINKWRAP modifier
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].use_apply_on_spline = True
        curve_obj.modifiers["Shrinkwrap"].target = mesh_obj
        curve_obj.modifiers["Shrinkwrap"].offset = context.scene.offset

        # add SMOOTH modifier
        # bpy.ops.object.modifier_add(type='SMOOTH')
        # curve_obj.modifiers["Smooth"].factor = smooth_factor
        # curve_obj.modifiers["Smooth"].iterations = smooth_iterations

        # apply modifier
        bpy.ops.object.modifier_apply(modifier="Shrinkwrap")
        # bpy.ops.object.modifier_apply(modifier="Smooth")

        # curve params
        curve_obj.data.dimensions = '3D'
        bpy.context.object.data.extrude = curve_extrude
        bpy.context.object.data.bevel_depth = curve_depth
        bpy.context.object.data.splines[0].use_cyclic_u = curve_cyclic
        bpy.context.object.data.splines[0].use_bezier_u = False
        bpy.context.object.data.splines[0].use_endpoint_u = False

        # deselect all
        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}

class OBJECT_PT_rope_attacher(bpy.types.Panel):
    bl_idname = "object.rope_attacher_panel"
    bl_label = "Rope Attacher"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KrusTool'

    def draw(self, context):
        layout = self.layout

        box0 = layout.box()
        box0.label(text="Input Objects")
        box0.prop(context.scene, "curve_obj")
        box0.prop(context.scene, "mesh_obj")

        box1 = layout.box()
        box1.label(text="Skrinkwrap Params")
        box1.prop(context.scene, "offset")

        # box2 = layout.box()
        # box2.label(text="Smooth Params")
        # box2.prop(context.scene, "smooth_factor")
        # box2.prop(context.scene, "smooth_iterations")

        box3 = layout.box()
        box3.label(text="Curve Params")
        box3.prop(context.scene, "curve_depth")
        box3.prop(context.scene, "curve_extrude")
        box3.prop(context.scene, "curve_cyclic")
        
        layout.operator("object.rope_attacher")

def update_property(self, context):
    curve_obj = context.scene.curve_obj
    if curve_obj:
        # Use getattr to get the value of the property with the same name as the update function
        for mod in curve_obj.modifiers:
            if hasattr(mod, self.bl_rna.identifier):
                setattr(mod, self.bl_rna.identifier, getattr(context.scene, self.bl_rna.identifier))

    # Trigger viewport update
    bpy.ops.object.rope_attacher()
    context.view_layer.update()

def register():
    bpy.utils.register_class(OBJECT_OT_rope_attacher)
    bpy.utils.register_class(OBJECT_PT_rope_attacher)

    bpy.types.Scene.curve_obj = bpy.props.PointerProperty(type=bpy.types.Object, name="Curve", description="Curve to snap to the mesh", poll=lambda self, obj: obj.type == 'CURVE')
    bpy.types.Scene.mesh_obj = bpy.props.PointerProperty(type=bpy.types.Object, name="Mesh", description="Mesh to snap the curve to", poll=lambda self, obj: obj.type == 'MESH')
    
    bpy.types.Scene.offset = bpy.props.FloatProperty(name="Offset", description="Offset distance", default=0.0, update=update_property)
    # bpy.types.Scene.smooth_factor = bpy.props.FloatProperty(name="Smooth Factor", description="Smooth factor", default=2.0)
    # bpy.types.Scene.smooth_iterations = bpy.props.IntProperty(name="Smooth Iterations", description="Smooth iterations", default=20)

    bpy.types.Scene.curve_depth = bpy.props.FloatProperty(name="Curve Depth", description="Curve depth", default=0.05, update=update_property)
    bpy.types.Scene.curve_extrude = bpy.props.FloatProperty(name="Curve Extrude", description="Curve extrude", default=0.0, update=update_property)
    bpy.types.Scene.curve_cyclic = bpy.props.BoolProperty(name="Curve Cyclic", description="Curve cyclic", default=False, update=update_property)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_rope_attacher)
    bpy.utils.unregister_class(OBJECT_PT_rope_attacher)

    del bpy.types.Scene.curve_obj
    del bpy.types.Scene.mesh_obj

if __name__ == "__main__":
    register()