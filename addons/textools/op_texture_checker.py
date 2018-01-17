import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi


name_images_prefix = "TT_checker_"


class op(bpy.types.Operator):
	"""UV Operator description"""
	bl_idname = "uv.textools_texture_checker"
	bl_label = "Checker Map"
	bl_description = "Add a checker map to the selected model and UV view"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		if bpy.context.object == None:
			return False

		if len(bpy.context.selected_objects) == 0:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True

	def execute(self, context):
		assign_checker_map(
			context,
			bpy.context.scene.texToolsSettings.size[0], 
			bpy.context.scene.texToolsSettings.size[1]
		)
		return {'FINISHED'}



def assign_checker_map(context, size_x, size_y):
	# Disable edit mode
	if bpy.context.scene.objects.active != None and bpy.context.object.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')

	# Collect Objects
	objects = []
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			if obj.data.uv_layers:
				objects.append(obj)

	#Change View mode to TEXTURED
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			for space in area.spaces:
				if space.type == 'VIEW_3D':
					space.viewport_shade = 'TEXTURED'


	if len(objects) > 0:
		name = (name_images_prefix+"{}_{}x{}").format('A', size_x, size_y)
		image = get_image(name, size_x, size_y)

		for obj in objects:
			apply_faces_image(obj, image)
	

	# Restore object selection
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:				
		obj.select = True


	# Clean up unused images
	for image in bpy.data.images:

		if name_images_prefix in image.name:
			print("N: {} | {}x".format(image.name, image.users))
			if not image.users:
				print("Remove unused image {}".format(image.name))
				bpy.data.images.remove(image)



def apply_faces_image(obj, image):
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.uv.select_all(action='SELECT')

	# Assign in UV view
	for area in bpy.context.screen.areas :
		if area.type == 'IMAGE_EDITOR' :
			area.spaces.active.image = image


def get_image(name, size_x, size_y):

	if name in bpy.data.images:
		return bpy.data.images[name];

	image = bpy.data.images.new(name, width=size_x, height=size_y)
	image.generated_type = 'UV_GRID' #COLOR_GRID
	image.generated_width = int(size_x)
	image.generated_height = int(size_y)
	return image


def get_texture_object(obj):
	return None








# def main(context):

# 	if bpy.context.scene.render.engine != 'CYCLES':
# 		bpy.context.scene.render.engine = 'CYCLES'

	
# 	#Change View mode to TEXTURED
# 	for area in bpy.context.screen.areas: # iterate through areas in current screen
# 		if area.type == 'VIEW_3D':
# 			for space in area.spaces: # iterate through spaces in current VIEW_3D area
# 				if space.type == 'VIEW_3D': # check if space is a 3D view
# 					space.viewport_shade = 'TEXTURED' # set the viewport shading to rendered
# 					# space.show_textured_shadeless = True




# 	# Setup Material
# 	material = None
# 	if name_material in bpy.data.materials:
# 		material = bpy.data.materials[name_material]
# 	else:
# 		material = bpy.data.materials.new(name_material)
# 		material.use_nodes = True

# 	if material == None:
# 		return

# 	# Assign material
# 	if len(bpy.context.object.data.materials) > 0:
# 		bpy.context.object.data.materials[0] = material
# 	else:
# 		bpy.context.object.data.materials.append(material)


# 	# Setup Node
# 	tree = material.node_tree
# 	node = None
# 	if name_node in tree.nodes:
# 		node = tree.nodes[name_node]
# 	else:
# 		node = tree.nodes.new("ShaderNodeTexImage")
# 	node.name = name_node
# 	node.select = True
# 	tree.nodes.active = node

	
# 	# Setup Image
# 	if node.image == None:
# 		node.image = get_image( names_checkermap[0] )

# 	else:
# 		print("Current image? {}".format(node.image.name))
# 		if node.image.name not in names_checkermap:
# 			node.image = get_image( names_checkermap[0] )
# 		else:
# 			# Cycle to next image
# 			index = (names_checkermap.index(node.image.name)+ 1) % len(names_checkermap)
# 			node.image = get_image( names_checkermap[index] )



# def get_image(name):

# 	#Get Image
# 	image = None
# 	if bpy.data.images.get(name) is not None:
#   		image = bpy.data.images[name];
# 	else:
# 		#Load image
# 		pathTexture = icons_dir = os.path.join(os.path.dirname(__file__), "resources/{}.png".format(name))
# 		image = bpy.ops.image.open(filepath=pathTexture, relative_path=False)
# 		bpy.data.images["{}.png".format(name)].name = name #remove extension in name
# 		image = bpy.data.images[name];
	
# 	return image