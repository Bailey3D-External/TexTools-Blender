import bpy
import os
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_texel


texture_modes = ['UV_GRID','COLOR_GRID']


class op(bpy.types.Operator):
	bl_idname = "uv.textools_texel_checker_map"
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

		if len(bpy.context.selected_objects) == 1 and bpy.context.active_object.type != 'MESH':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True

	def execute(self, context):
		assign_checker_map(
			bpy.context.scene.texToolsSettings.size[0], 
			bpy.context.scene.texToolsSettings.size[1]
		)
		return {'FINISHED'}



def assign_checker_map(size_x, size_y):
	# Force Object mode
	if bpy.context.scene.objects.active != None and bpy.context.object.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')

	# Collect Objects
	objects = []
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH' and obj.data.uv_layers:
				objects.append(obj)

	#Change View mode to TEXTURED
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			for space in area.spaces:
				if space.type == 'VIEW_3D':
					space.viewport_shade = 'TEXTURED'


	if len(objects) > 0:

		# Detect current Checker modes
		mode_count = {}
		for mode in texture_modes:
			mode_count[mode] = 0
		for obj in objects:
			image = utilities_texel.get_object_texture_image(obj)
			if image and image.generated_type in texture_modes:
				mode_count[image.generated_type]+=1

		# Sort by count (returns tuple list of key,value)
		mode_max_count = sorted(mode_count.items(), key=operator.itemgetter(1))
		mode_max_count.reverse()

		mode = None
		if mode_max_count[0][1] == 0:
			# There are no checker maps
			mode = texture_modes[0]
		elif mode_max_count[0][0] in texture_modes:
			if mode_max_count[-1][1] > 0:
				# There is more than 0 of another mode, complete existing mode first
				mode = mode_max_count[0][0]
			else:
				# Switch to next checker mode
				index = texture_modes.index(mode_max_count[0][0])
				mode = texture_modes[ (index+1)%len(texture_modes) ]


		name = utilities_texel.get_checker_name(mode, size_x, size_y)
		image = get_image(name, mode, size_x, size_y)

		# Assig to all objects
		for obj in objects:
			apply_faces_image(obj, image)
	
	# Restore object selection
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:				
		obj.select = True

	# Clean up images and materials
	utilities_texel.checker_images_cleanup()



def apply_faces_image(obj, image):
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj

	if bpy.context.scene.render.engine == 'BLENDER_RENDER':
		# Assign textures to faces
		if obj.data.uv_textures.active:
			for uvface in obj.data.uv_textures.active.data:
				uvface.image = image

	elif bpy.context.scene.render.engine == 'CYCLES':
		# Assign Cycles material with image

		# Get Material
		material = None
		if image.name in bpy.data.materials:
			material = bpy.data.materials[image.name]
		else:
			material = bpy.data.materials.new(image.name)
			material.use_nodes = True

		# Assign material
		if len(obj.data.materials) > 0:
			obj.data.materials[0] = material
		else:
			obj.data.materials.append(material)

		# Setup Node
		tree = material.node_tree
		node = None
		if "checker" in tree.nodes:
			node = tree.nodes["checker"]
		else:
			node = tree.nodes.new("ShaderNodeTexImage")
		node.name = "checker"
		node.select = True
		tree.nodes.active = node
		node.image = image



def get_image(name, mode, size_x, size_y):
	# Image already exists?
	if name in bpy.data.images:
		# Update texture UV checker mode
		bpy.data.images[name].generated_type = mode
		return bpy.data.images[name];

	# Create new image instead
	image = bpy.data.images.new(name, width=size_x, height=size_y)
	image.generated_type = mode #UV_GRID or COLOR_GRID
	image.generated_width = int(size_x)
	image.generated_height = int(size_y)

	return image
