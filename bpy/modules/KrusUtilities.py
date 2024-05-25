import bpy 

# allow you to edit the copy of the object
# without sabotaging the original object
def copy_and_link_object(context, original_obj):
    # Create a copy of the original object
    copied_obj_name = original_obj.name + "_copy"
    
    # If an object with the same name already exists, delete it
    if copied_obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[copied_obj_name], do_unlink=True)
    
    # Copy the original object and its data
    copied_data = original_obj.data.copy()
    copied_obj = original_obj.copy()
    copied_obj.data = copied_data
    copied_obj.name = copied_obj_name
    
    # Link the copied object to the current collection
    context.collection.objects.link(copied_obj)
    
    return copied_obj