import bpy

bpy.ops.paint.vertex_paint_toggle()
bpy.context.object.data.use_paint_mask_vertex = True
bpy.ops.paint.vertex_color_set()
bpy.ops.object.editmode_toggle()