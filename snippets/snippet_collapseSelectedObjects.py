import bpy

objects = []

for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        print("Copy Mesh: "+obj.name)
        
        #Create copy
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.animation_data_clear()
        bpy.context.scene.objects.link(copy)
        bpy.context.scene.update()
        
        bpy.ops.object.select_all(action='DESELECT')
        copy.select = True
        copy.name = "merged__"
        
        #Collapse modifiers by converting to base object
        bpy.context.scene.objects.active = copy
        bpy.ops.object.convert()
        
        objects.append(copy)

#Join Selected Copies into one object
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:
    obj.select = True

bpy.ops.object.join()