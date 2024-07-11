import bpy
import bmesh
import mathutils

### variables
_bl_idname = "object.smooth_normal_to_uv_operator"
_bl_label = "Smooth Normal To UV Operator"
_bl_idname_button = _bl_idname + "_button"

class SmoothNormalToUVOperator(bpy.types.Operator):
    ### id name & label
    bl_idname = _bl_idname
    bl_label = _bl_label

    def calculate_tangent_space(mesh):
        mesh.calc_tangents()
        tangents = [None] * len(mesh.loops)
        bitangents = [None] * len(mesh.loops)
        normals = [None] * len(mesh.loops)

        for loop in mesh.loops:
            tangents[loop.index] = loop.tangent
            bitangents[loop.index] = loop.bitangent
            normals[loop.index] = loop.normal

        return tangents, bitangents, normals


    def execute(self, context):
        ### get inputs from property
        source_object = bpy.context.window_manager.source_object
        target_object = bpy.context.window_manager.target_object

        # Ensure the target object has 3 UV maps
        if target_object and target_object.type == 'MESH':
            mesh = target_object.data
            while len(mesh.uv_layers) < 3:
                mesh.uv_layers.new(name=f"UVMap_{len(mesh.uv_layers) + 1}")
            print(f"Target object now has {len(mesh.uv_layers)} UV maps.")
        else:
            print("No valid mesh object selected.")

        # Save original normals of the target object
        if target_object and target_object.type == 'MESH':
            mesh = target_object.data
            bm_original = bmesh.new()
            bm_original.from_mesh(mesh)
            
            if "original_normals" not in bm_original.verts.layers.float_vector:
                original_normals_layer = bm_original.verts.layers.float_vector.new("original_normals")
            else:
                original_normals_layer = bm_original.verts.layers.float_vector["original_normals"]
            
            for vert in bm_original.verts:
                vert[original_normals_layer] = vert.normal
            
            print(f"Save original normals of {target_object.name} to bm_original.")
        else:
            print("No valid mesh object selected.")

        # Apply Data Transfer Modifier to the target object
        if source_object and target_object:
            data_transfer_mod = target_object.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
            data_transfer_mod.object = source_object
            data_transfer_mod.use_loop_data = True
            data_transfer_mod.data_types_loops = {'CUSTOM_NORMAL'}
            data_transfer_mod.loop_mapping = 'NEAREST_POLYNOR'
            # apply data_transfer_mod
            bpy.ops.object.modifier_apply(modifier=data_transfer_mod.name)

        # Save modified normals of the target object
        if target_object and target_object.type == 'MESH':
            mesh = target_object.data
            bm_modified = bmesh.new()
            bm_modified.from_mesh(mesh)
            
            if "modified_normals" not in bm_modified.verts.layers.float_vector:
                modified_normals_layer = bm_modified.verts.layers.float_vector.new("modified_normals")
            else:
                modified_normals_layer = bm_modified.verts.layers.float_vector["modified_normals"]
            
            for vert in bm_modified.verts:
                vert[modified_normals_layer] = vert.normal
            
            print(f"Save modified normals of {target_object.name} to bm_modified.")
        else:
            print("No valid mesh object selected.")

        # Recover original normals of the target object
        if target_object and target_object.type == 'MESH' and bm_original:
            mesh = target_object.data
            bm_original.to_mesh(mesh)
            print(f"Restore original normals of {target_object.name}.")
        else:
            print("No valid mesh object selected or bm_original is None.")

        # Ensure the active object is a mesh
        target_object = bpy.context.active_object
        if target_object and target_object.type == 'MESH':
            mesh = target_object.data

            # Ensure the mesh has a vertex color layer
            if not mesh.vertex_colors:
                mesh.vertex_colors.new()

            # Access the active vertex color layer
            color_layer = mesh.vertex_colors.active.data

            # Calculate tangents using the Mesh object
            mesh.calc_tangents()

            tangents = [None] * len(mesh.loops)
            bitangents = [None] * len(mesh.loops)
            normals = [None] * len(mesh.loops)

            for loop in mesh.loops:
                tangents[loop.index] = loop.tangent
                bitangents[loop.index] = loop.bitangent
                normals[loop.index] = loop.normal

            # Create a dictionary to store the transformed normals for each vertex
            transformed_normals = {}

            for face in bm_modified.faces:
                for loop in face.loops:
                    vert_index = loop.vert.index
                    normal = loop.vert.normal

                    # Access tangent space basis
                    tangent = tangents[loop.index]
                    bitangent = bitangents[loop.index]
                    normal_basis = normals[loop.index]

                    # Create a matrix from tangent space basis
                    tangent_matrix = mathutils.Matrix((tangent, bitangent, normal_basis)).transposed()

                    # Transform the normal into tangent space
                    transformed_normal = tangent_matrix @ normal

                    # Store the transformed normal in the dictionary
                    transformed_normals[vert_index] = transformed_normal

            # Assign the transformed normals to the vertex color layer
            for loop in mesh.loops:
                vert_index = loop.vertex_index
                transformed_normal = transformed_normals[vert_index]
                color_layer[loop.index].color = (
                    transformed_normal.x * 0.5 + 0.5,
                    transformed_normal.y * 0.5 + 0.5,
                    transformed_normal.z * 0.5 + 0.5,
                    1.0  # Full opacity
                )

            print(f"Saved transformed normals of {target_object.name} to the vertex color layer.")
        else:
            print("No valid mesh object selected or bm_original is None.")

        bm_original.free()
        bm_modified.free()
        return {'FINISHED'}


class SmoothNormalToUVButtonOperator(bpy.types.Operator):
    bl_idname = _bl_idname_button
    bl_label = _bl_label

    def execute(self, context):
        ### custom operator execution
        bpy.ops.object.smooth_normal_to_uv_operator()
        return {'FINISHED'}

class SmoothNormalToUVOperatorPanel(bpy.types.Panel):
    bl_label = _bl_label
    bl_idname = _bl_idname
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KrusTool"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.window_manager, 'source_object')

        row = layout.row()
        row.prop(context.window_manager, 'target_object')

        # Button
        row = layout.row()
        row.operator(_bl_idname_button)

def register():
    ### properties
    bpy.types.WindowManager.source_object = bpy.props.PointerProperty(name="Source Object", type=bpy.types.Object)
    bpy.types.WindowManager.target_object = bpy.props.PointerProperty(name="Target Object", type=bpy.types.Object)

    bpy.utils.register_class(SmoothNormalToUVOperator)
    bpy.utils.register_class(SmoothNormalToUVButtonOperator)
    bpy.utils.register_class(SmoothNormalToUVOperatorPanel)

def unregister():
    del bpy.types.WindowManager.custom_input
    bpy.utils.unregister_class(SmoothNormalToUVOperator)
    bpy.utils.unregister_class(SmoothNormalToUVButtonOperator)
    bpy.utils.unregister_class(SmoothNormalToUVOperatorPanel)

if __name__ == "__main__":
    register()