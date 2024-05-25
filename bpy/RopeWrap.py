import bpy
import bmesh

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

        # select plane_obj
        bpy.context.view_layer.objects.active = plane_obj
        plane_obj.select_set(True)
        bpy.ops.object.make_single_user(object=True, obdata=True)

        # add bool modifier
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
        bpy.context.object.modifiers["Boolean"].object = target_obj
        bpy.ops.object.modifier_apply(modifier="Boolean")

        # select plane_obj only 
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = plane_obj
        plane_obj.select_set(True)

        # bevel 
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=merge_threshold)
        bpy.ops.mesh.bevel(offset=bevel_offset, affect='VERTICES', clamp_overlap=True, segments=2)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # deselect all
        bpy.ops.object.select_all(action='DESELECT')

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

        row = layout.row()
        row.operator("object.rope_wrap")


def register():
    bpy.utils.register_class(OT_rope_wrap)
    bpy.utils.register_class(PT_rope_wrap)

    bpy.types.Scene.plane_obj = bpy.props.PointerProperty(type=bpy.types.Object, name="Plane", description="Plane to wrap around the target", poll=lambda self, obj: obj.type == 'MESH')
    bpy.types.Scene.target_obj = bpy.props.PointerProperty(type=bpy.types.Object, name="Target", description="Object to wrap the plane around", poll=lambda self, obj: obj.type == 'MESH')
    bpy.types.Scene.merge_threshold = bpy.props.FloatProperty(name="Merge Threshold", default=0.01, description="Threshold for merging vertices")
    bpy.types.Scene.bevel_offset = bpy.props.FloatProperty(name="Bevel Offset", default=0.1, description="Offset of the bevel modifier")

def unregister():
    bpy.utils.unregister_class(OT_rope_wrap)
    bpy.utils.unregister_class(PT_rope_wrap)

    del bpy.types.Scene.plane_obj
    del bpy.types.Scene.target_obj


if __name__ == "__main__":
    register()