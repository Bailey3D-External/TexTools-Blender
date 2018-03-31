import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi
import math

from . import utilities_mesh_texture




class op(bpy.types.Operator):
	bl_idname = "uv.textools_mesh_texture_trim"
	bl_label = "Trim"
	bl_description = "Trim Mesh Texture"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		# Wrap texture mesh around UV mesh
		if len(bpy.context.selected_objects) >= 2:
			if utilities_mesh_texture.find_uv_mesh(bpy.context.selected_objects):
				return True

		return False

	def execute(self, context):
		trim(self)
		return {'FINISHED'}



def trim(self):
	# Wrap the mesh texture around the 
	print("Trim Mesh Texture :)")

	# Collect UV mesh
	obj_uv = utilities_mesh_texture.find_uv_mesh(bpy.context.selected_objects)
	if not obj_uv:
		self.report({'ERROR_INVALID_INPUT'}, "No UV mesh found" )
		return

	# Collect texture meshes
	obj_textures = []
	for obj in bpy.context.selected_objects:
		if obj != obj_uv:
			if obj.type == 'MESH':
				obj_textures.append(obj)

	if len(obj_textures) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No meshes found for mesh textures" )
		return

	# Setup Thickness
	utilities_mesh_texture.uv_mesh_fit(obj_uv, obj_textures)


	# Apply bool modifier to trim
	for obj in obj_textures:
		name = "Trim UV"

		if name in obj.modifiers:
			obj.modifiers.remove( obj.modifiers[name] )

		modifier_bool = obj.modifiers.new(name=name, type='BOOLEAN')
		modifier_bool.object = obj_uv

	bpy.ops.ui.textools_popup('INVOKE_DEFAULT', message="Collapse modifiers before wrapping")


