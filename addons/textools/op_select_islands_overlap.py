import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv
import imp
imp.reload(utilities_uv)

class op(bpy.types.Operator):
	bl_idname = "uv.textools_select_islands_overlap"
	bl_label = "Select outline"
	bl_description = "Select all overlapping UV islands"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		#One or more objects selected
		if len(bpy.context.selected_objects) == 0:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		##Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True


	def execute(self, context):
		
		selectOverlap(context)
		return {'FINISHED'}



def selectOverlap(context):
	print("Execute op_select_islands_overlap")

	# https://developer.blender.org/D2865

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
	bpy.ops.uv.select_all(action='SELECT')

	islands_all = utilities_uv.getSelectionIslands()
	# count = len(islands_all)

	islands_bounds = []
	for island in islands_all:
		islands_bounds.append( Island_bounds( island ) )
	

	groups = []
	unmatched = islands_bounds.copy()

	for islandA in islands_bounds:
		if islandA in unmatched:

			group = [islandA]
			for islandB in unmatched:
				if islandA != islandB and islandA.isEqual(islandB):
					group.append(islandB)

			for item in group:
				unmatched.remove(item)

			groups.append(group)

			print("Group: {} islands, unmatched: {}x".format(len(group), len(unmatched)))
		# groups.append(  )


	bpy.ops.uv.select_all(action='DESELECT')
	for group in groups:
		if len(group) > 1:
			for i in range(1, len(group)):
				utilities_uv.setSelectedFaces( group[i].faces )



	# for i in range(0,count):
	# 	if len(groups) == 0:
	# 		groups.append([ islands_all[i] ])
	# 	else:
	# 		isFound = False
	# 		for j in range(i, count):
	# 			if j > i:
	# 				A = islands_bounds[i]
	# 				B = islands_bounds[j]
	# 				if A.isEqual(B):
	# 					print("Matched: {} | {}".format(i,j))
	# 					isFound = True
	# 					break

	# 		if not isFound:
	# 			print("..")

	print("Groups: "+str(len(groups)))




class Island_bounds:
	faces = []
	center = Vector([0,0])
	min = Vector([0,0])
	max = Vector([0,0])

	def __init__(self, faces):
		bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
		uvLayer = bm.loops.layers.uv.verify();
		
		
		# Collect topology stats
		self.faces = faces

		#Select Island
		bpy.ops.uv.select_all(action='DESELECT')
		utilities_uv.setSelectedFaces(faces)

		bounds = utilities_uv.getSelectionBBox()
		self.center = bounds['center']
		self.min = bounds['min']
		self.max = bounds['max']

		# print("Get bounds "+str(self.center))

	def isInside(self, pos, min, max):

		if pos.x >= min.x and pos.x <= max.x:
			if pos.y >= min.y and pos.y <= max.y:
				return True
		return False
		
	def isEqual(self, other):

		# Center is inside other bounds
		if self.isInside(self.center, other.min, other.max):
			return True

		return False