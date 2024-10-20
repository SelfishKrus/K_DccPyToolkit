import bpy
import bmesh
from mathutils import Vector

def remap(value, old_min, old_max, new_min, new_max):
    return new_min + (value - old_min) * (new_max - new_min) / (old_max - old_min)

selected_objects = bpy.context.selected_objects

for obj in selected_objects:
    if obj.type == 'MESH':
        mesh = obj.data
        bbox = obj.bound_box

        # Store original mesh data 
        bm_original = bmesh.new()
        bm_original.from_mesh(mesh)

        # Get bbox center and radius
        center = Vector((0, 0, 0))
        for coord in bbox:
            center += Vector(coord)
        center /= 8

        min_corner = Vector(bbox[0])
        max_corner = Vector(bbox[6])
        radius = (max_corner - min_corner).length / 2

        # Create a smooth sphere 
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=center)
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

        # Ensure the mesh is updated
        mesh.update()

        # Create or access the vertex color layer
        if "NormalColor" not in mesh.vertex_colors:
            color_layer = mesh.vertex_colors.new(name="NormalColor")
        else:
            color_layer = mesh.vertex_colors["NormalColor"]

        color_data = color_layer.data

        # Remap normals and store in vertex color
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                loop = mesh.loops[loop_index]
                normal = loop.normal
                # Remap normal from (-1, 1) to (0, 1)
                remapped_normal = normal * 0.5 + Vector((0.5, 0.5, 0.5))
                color_data[loop_index].color = (remapped_normal.x, remapped_normal.y, remapped_normal.z, 1.0)  # RGBA

        # Update the mesh to apply changes
        mesh.update()

        # Recover original mesh data
        bm_original.to_mesh(mesh)
        bm_original.free()
        mesh.update()