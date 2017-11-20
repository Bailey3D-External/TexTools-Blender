import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

# if "bpy" in locals():
# 	import imp
# 	imp.reload(utilities_uv)
# else:
from . import utilities_uv


class operator_align(bpy.types.Operator):
	bl_idname = "uv.textools_align"
	bl_label = "Align"
	bl_description = "Align vertices, edges or shells"

	direction = bpy.props.StringProperty(name="Direction", default="top")

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
			return False 	#self.report({'WARNING'}, "Object must have more than one UV map")

		#Not in Synced mode
		# if bpy.context.scene.tool_settings.use_uv_select_sync == True:
		# 	return False

		return True


	def execute(self, context):
		
		align(context, self.direction)
		return {'FINISHED'}


def align(context, direction):

	if bpy.context.space_data.pivot_point != 'CENTER':
		bpy.context.space_data.pivot_point = 'CENTER'

	#B-Mesh
	obj = bpy.context.active_object
	bm = bmesh.from_edit_mesh(obj.data);
	uvLayer = bm.loops.layers.uv.verify();

	# Collect BBox sizes
	boundsAll = utilities_uv.getSelectionBBox()


	mode = bpy.context.scene.tool_settings.uv_select_mode
	if mode == 'FACE' or mode == 'ISLAND':
		print("____ Align Islands")
		
		#Collect UV islands
		islands = utilities_uv.getSelectionIslands()

		#Rotate to minimal bounds
		for i in range(0, len(islands)):
			faces = islands[i]

			# Select Island
			bpy.ops.uv.select_all(action='DESELECT')
			#utilities_uv.setSelectedFaces(faces)

			bounds = utilities_uv.getSelectionBBox()

			# alignIslandMinimalBounds(uvLayer, islands[i])

			# # Collect BBox sizes
			# 
			# allSizes[i] = bounds['area'] + i*0.000001;#Make each size unique
			# allBounds[i] = bounds;
			# print("Size: "+str(allSizes[i]))

	elif mode == 'EDGE' or mode == 'VERTEX':
		print("____ Align Verts")

		for f in bm.faces:
			if f.select:
				for l in f.loops:
					luv = l[uvLayer]
					if luv.select:
						# print("Idx: "+str(luv.uv))
						if direction == "top":
							luv.uv[1] = boundsAll['max'].y
						elif direction == "bottom":
							luv.uv[1] = boundsAll['min'].y
						elif direction == "left":
							luv.uv[0] = boundsAll['min'].x
						elif direction == "right":
							luv.uv[0] = boundsAll['max'].x


		bmesh.update_edit_mesh(obj.data)

	# if(direction is "top"):
		#Align top

	





#if __name__ == "__main__":
 	# test call