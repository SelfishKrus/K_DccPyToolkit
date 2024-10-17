import bpy
import bmesh
from mathutils import Vector

selected_objects = bpy.context.selected_objects

for obj in selected_objects:
    if obj.type == 'MESH':
        mesh = obj.data
        bbox = obj.bound_box

        # Get bbox center and radius
        center = Vector((0, 0, 0))
        for coord in bbox:
            center += Vector(coord)
        center /= 8

        min_corner = Vector(bbox[0])
        max_corner = Vector(bbox[6])
        radius = (max_corner - min_corner).length / 2

        # create a smooth sphere 
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=center)
        sphere = bpy.context.object
        bpy.ops.object.shade_smooth()

        # add DATA_TRANSFER modifier for obj
        bpy.ops.object.select_all(action='DESELECT')

        data_transfer_modifier = obj.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
        data_transfer_modifier.use_loop_data = True
        data_transfer_modifier.data_types_loops = {'CUSTOM_NORMAL'}
        data_transfer_modifier.object = sphere
        
        # apply modifier
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="DataTransfer")

        # delete sphere
        bpy.ops.object.select_all(action='DESELECT')
        sphere.select_set(True)
        bpy.ops.object.delete()