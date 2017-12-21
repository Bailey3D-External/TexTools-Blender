import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi

class op(bpy.types.Operator):
	"""UV Operator description"""
	bl_idname = "uv.textools_texture_checker"
	bl_label = "Checker Map"
	bl_description = "Add a checker map to the selected model and UV view"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):

	idImage = "TT_checkerMap"
	image = None

	#Get Image
	if bpy.data.images.get(idImage) is not None:
		#Already exists
  		image = bpy.data.images[idImage];
	else:
		#Load image
		pathTexture = icons_dir = os.path.join(os.path.dirname(__file__), "resources/checkerMap.jpg")
		image = bpy.ops.image.open(filepath=pathTexture, relative_path=False)
		#Rename
		bpy.data.images["checkerMap.jpg"].name = idImage
	
	#Assign image variable
	image = bpy.data.images[idImage];

	# bpy.context.object.active_material.use_shadeless = True
	mat = bpy.data.materials.new("TT_checkerMap_material")
	mat.diffuse_color = (0,0,0)
	mat.diffuse_shader = 'LAMBERT' 
	mat.diffuse_intensity = 1.0 
	mat.specular_color = (1,1,1)
	mat.specular_shader = 'COOKTORR'
	mat.specular_intensity = 0.5
	# mat.alpha = alpha
	mat.ambient = 1
	mat.use_shadeless = True

	cTex = bpy.data.textures.new('ColorTex', type = 'IMAGE')
	cTex.image = image

	# Add texture slot for color texture
	mtex = mat.texture_slots.add()
	mtex.texture = cTex
	mtex.texture_coords = 'UV'
	mtex.use_map_color_diffuse = True 
	mtex.use_map_color_emission = True 
	mtex.emission_color_factor = 0.5
	mtex.use_map_density = True 
	mtex.mapping = 'FLAT' 


	#Assign image to UV faces
	for obj in context.selected_objects:
		#Only Assign if already UV maps
		if obj.data.uv_layers:
			for uv_face in obj.data.uv_textures.active.data:
				uv_face.image = image

		obj.active_material = mat

	#Change View mode to TEXTURED
	for area in bpy.context.screen.areas: # iterate through areas in current screen
		if area.type == 'VIEW_3D':
			for space in area.spaces: # iterate through spaces in current VIEW_3D area
				if space.type == 'VIEW_3D': # check if space is a 3D view
					space.viewport_shade = 'TEXTURED' # set the viewport shading to rendered

