import bpy
import os
import bmesh
import math
import operator
from mathutils import Vector
from collections import defaultdict
from itertools import chain # 'flattens' collection of iterables

from . import utilities_uv



class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_align_world"
	bl_label = "Align World"
	bl_description = "Align selected UV islands to world / gravity directions"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):


		if not bpy.context.active_object:
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False


		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False


		# if bpy.context.scene.tool_settings.uv_select_mode != 'FACE':
		#  	return False

		# if bpy.context.scene.tool_settings.use_uv_select_sync:
		# 	return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}



def main(context):
	print("--------------------------- Executing aling_world")

	#Store selection
	utilities_uv.selection_store()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	#Only in Face or Island mode
	if bpy.context.scene.tool_settings.uv_select_mode is not 'FACE' or 'ISLAND':
		bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	
	islands = utilities_uv.getSelectionIslands()

	print("Clusters: {}x".format(len(islands)))

	obj  = bpy.context.object

	for faces in islands:
		# Get average viewport normal of UV island
		avg_normal = Vector((0,0,0))
		for face in faces:
			avg_normal+=face.normal
		avg_normal/=len(faces)

		# avg_normal = (obj.matrix_world*avg_normal).normalized()

		# Which Side
		x = 0
		y = 1
		z = 2
		max_size = max(abs(avg_normal.x), abs(avg_normal.y), abs(avg_normal.z))
		if(abs(avg_normal.x) == max_size):
			print("x normal")

			align_island(obj, faces, y, z)

		elif(abs(avg_normal.y) == max_size):
			print("y normal")
			align_island(obj, faces, y, z)
			pass
		elif(abs(avg_normal.z) == max_size):
			pass

		print("align island: faces {}x n:{}, max:{}".format(len(faces), avg_normal, max_size))

	

	#Restore selection
	utilities_uv.selection_restore()

def align_island(obj, faces, s_x=0, s_y=1):

	# Find lowest and highest verts
	minmax_val  = [0,0]
	minmax_vert = [None, None]

	print("faces {}x".format(len(faces)))

	processed = []
	for face in faces:
		for vert in face.verts:
			if vert not in processed:
				processed.append(vert)

				print("idx {}".format(vert.index))

				vert_y = (obj.matrix_world * vert.co)[s_y]

				if not minmax_vert[0]:
					minmax_vert[0] = vert
					minmax_val[0] = vert_y
					continue

				if not minmax_vert[1]:
					minmax_vert[1] = vert
					minmax_val[1] = vert_y
					continue

				if vert_y < minmax_val[0]:
					# Not yet defined or smaller
					minmax_vert[0] = vert
					minmax_val[0] = vert_y
					continue

				elif vert_y > minmax_val[1]:
					minmax_vert[1] = vert
					minmax_val[1] = vert_y
					continue

	if minmax_vert[0] and minmax_vert[1]:
		print("Min {} , Max {} ".format(minmax_vert[0].index, minmax_vert[1].index))
				