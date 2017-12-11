import bpy
import os
import bmesh
import math
from mathutils import Vector
from collections import defaultdict

from . import utilities_uv



class op(bpy.types.Operator):
	bl_idname = "uv.textools_symmetry"
	bl_label = "Symmetry"
	bl_description = "Mirrors selected faces to other half or averages based on selected edge center"

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

		if bpy.context.scene.tool_settings.uv_select_mode != 'EDGE' and bpy.context.scene.tool_settings.uv_select_mode != 'FACE':
		 	return False

		# if bpy.context.scene.tool_settings.use_uv_select_sync:
		# 	return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}



def main(context):
	print("--------------------------- Executing operator_symmetry")

	#Store selection
	utilities_uv.selectionStore()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	if bpy.context.scene.tool_settings.uv_select_mode == 'EDGE':


		# 1.) Collect left and right side verts
		verts_middle = [];

		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop[uvLayer].select and loop.vert not in verts_middle:
						verts_middle.append(loop.vert)
					
		# 2.) Align UV shell
		alignToCenterLine()

		# Convert to Vert selection and extend edge loop in 3D space
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
		bpy.ops.mesh.select_all(action='DESELECT')
		for vert in verts_middle:
			vert.select = True

		bpy.ops.mesh.select_mode(use_extend=True, use_expand=False, type='EDGE')
		bpy.ops.mesh.loop_multi_select(ring=False)
		for vert in bm.verts:
			if vert.select and vert not in verts_middle:
				print("Append extra vert to symmetry line from xyz edge loop")
				verts_middle.append(vert)

		# Select UV shell Again
		bpy.ops.mesh.select_linked(delimit={'UV'})
		verts_island = []
		for vert in bm.verts:
			if vert.select:
				verts_island.append(vert)


		# 3.) Restore UV vert selection
		x_middle = 0
		bpy.ops.uv.select_all(action='DESELECT')
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop.vert in verts_middle:
						loop[uvLayer].select = True
						x_middle = loop[uvLayer].uv.x;


		print("Middle "+str(len(verts_middle))+"x, x pos: "+str(x_middle))

		# Extend selection
		bpy.ops.uv.select_more()

		verts_A = [];
		verts_B = [];
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop[uvLayer].select and loop.vert not in verts_middle:
						if loop[uvLayer].uv.x <= x_middle:
							# Left
							if loop.vert not in verts_A:
								verts_A.append(loop.vert)

						elif loop[uvLayer].uv.x > x_middle:
							# Right
							if loop.vert not in verts_B:
								verts_B.append(loop.vert)

		verts_double = [vert for vert in verts_island if (vert in verts_A and vert in verts_B)]


# temp temp temp temp
		print("Temp  double: "+str(len(verts_double))+"x")
		bpy.ops.mesh.select_all(action='DESELECT')
		for vert in verts_A:
			vert.select = True

		return

		def extend_half_selection(verts_middle, verts_half, verts_other):
			# Select initial half selection
			bpy.ops.uv.select_all(action='DESELECT')
			for face in bm.faces:
				if face.select:
					for loop in face.loops:
						if loop.vert in verts_half:
							loop[uvLayer].select = True

			# Extend selection				
			bpy.ops.uv.select_more()

			count_added = 0
			for face in bm.faces:
				if face.select:
					for loop in face.loops:
						if loop.vert not in verts_half and loop.vert not in verts_middle and loop[uvLayer].select:
							if loop.vert in verts_other:
								..
							else:
								verts_half.append(loop.vert)
								count_added+=1

			if count_added == 0:
				# Break loop, now new items to add
				break;fgdsfdsfsfds


		# Limit iteration loops
		max_loops_extend = 200
		for i in range(0, max_loops_extend):
			extend_half_selection(verts_middle, verts_A, verts_B)
			extend_half_selection(verts_middle, verts_B, verts_A)

		
		# verts_extended = [vert for vert in bm.verts if (vert.select and vert in verts_connected_edges and vert in verts_mask and vert not in verts_processed and vert not in verts_border)]
			# 
		print("Sides: L:"+str(len(verts_A))+" | R:"+str(len(verts_B)))
		if len(verts_double) > 0:
			print("TODO: sort out "+str(len(verts_double))+" double verts by UV -x space")

		# 4.) Mirror Verts
		mirror_verts(verts_middle, verts_A, verts_B, False)



	if bpy.context.scene.tool_settings.uv_select_mode == 'FACE':

		# 1.) Get selected UV faces to vert faces
		selected_faces = []
		for face in bm.faces:
			if face.select:
				# Are all UV faces selected?
				countSelected = 0
				for loop in face.loops:
					if loop[uvLayer].select:
						countSelected+=1
						# print("Vert selected "+str(face.index))
				if countSelected == len(face.loops):
					selected_faces.append(face)


		# if bpy.context.scene.tool_settings.use_uv_select_sync == False:

		bpy.ops.uv.select_linked(extend=False)
		verts_all = []
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if(loop.vert not in verts_all):
						verts_all.append(loop.vert)

		print("Verts shell: "+str(len(verts_all)))


		bpy.ops.mesh.select_all(action='DESELECT')
		for face in selected_faces:
			face.select = True


		# 2.) Select Vert shell's outer edges
		bpy.ops.mesh.select_linked(delimit=set())
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
		bpy.ops.mesh.region_to_loop()
		edges_outer_shell = [e for e in bm.edges if e.select]

		# 3.) Select Half's outer edges
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		bpy.ops.mesh.select_all(action='DESELECT')
		for face in selected_faces:
			face.select = True
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
		bpy.ops.mesh.region_to_loop()
		edges_outer_selected = [e for e in bm.edges if e.select]

		# 4.) Mask edges exclusive to edges_outer_selected (symmetry line)
		edges_middle = [item for item in edges_outer_selected if item not in edges_outer_shell]

		# 5.) Convert to UV selection
		verts_middle = []
		for edge in edges_middle:
			if edge.verts[0] not in verts_middle:
				verts_middle.append(edge.verts[0])
			if edge.verts[1] not in verts_middle:
				verts_middle.append(edge.verts[1])

		#Select all Vert shell faces
		bpy.ops.mesh.select_linked(delimit=set())
		#Select UV matching vert array
		bpy.ops.uv.select_all(action='DESELECT')
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop.vert in verts_middle:
						loop[uvLayer].select = True

		# 5.) Align UV shell
		alignToCenterLine()

		# 7.) Collect left and right side verts
		verts_A = [];
		verts_B = [];

		bpy.ops.uv.select_all(action='DESELECT')
		for face in selected_faces:
			for loop in face.loops:
				if loop.vert not in verts_middle and loop.vert not in verts_A:
					verts_A.append(loop.vert)

		for vert in verts_all:
			if vert not in verts_middle and vert not in verts_A and vert not in verts_B:
				verts_B.append(vert)

		# 8.) Mirror Verts
		mirror_verts(verts_middle, verts_A, verts_B, True)







def mirror_verts(verts_middle, verts_A, verts_B, isAToB):

	print("Mirror: "+str(len(verts_middle))+"x | L:"+str(len(verts_A))+"x | R:"+str(len(verts_B))+"x, A to B? "+str(isAToB))

	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()




	bpy.ops.mesh.select_all(action='DESELECT')
	for vert in verts_middle:
		vert.select = True

	return


	# 1.) Get Center X
	x_middle = 0
	for face in bm.faces:
		if face.select:
			for loop in face.loops:
				if loop.vert in verts_middle:
					x_middle = loop[uvLayer].uv.x;
					break;
		if x_middle != 0:
			break;

	print("Middle: "+str(x_middle))

	# 2.) Get Vert -> UV dictionary
	vert_to_UV = dict()
	for face in bm.faces:
		if face.select:
			for loop in face.loops:
				if loop.vert not in vert_to_UV:
					vert_to_UV[loop.vert] = loop[uvLayer].uv



	# 3.) Grow layer by layer
	verts_processed = []	

	def select_extend_filter(verts_border, verts_mask):
		print("something")
		connected_verts = []
		for i in range(0, len(verts_border)):
			 # Collect connected edge verts
			verts_connected_edges = []
			for edge in verts_border[i].link_edges:
				if(edge.verts[0] not in verts_connected_edges):
					verts_connected_edges.append(edge.verts[0])
				if(edge.verts[1] not in verts_connected_edges):
					verts_connected_edges.append(edge.verts[1])

			# Select vert on border
			bpy.ops.mesh.select_all(action='DESELECT')
			verts_border[i].select = True

			# Extend selection
			bpy.ops.mesh.select_more()

			# Filter selected verts against mask, connected edges, processed and border
			verts_extended = [vert for vert in bm.verts if (vert.select and vert in verts_connected_edges and vert in verts_mask and vert not in verts_processed and vert not in verts_border)]
			

			print("v "+str(i)+". extended: "+str(len(verts_extended)))



			
			connected_verts.append( [] )

			# Sort by distance
			for vert in verts_extended:
				d = (verts_border[i].co - vert.co).length
				print("   "+str(i)+". d: "+str(d))


			if len(verts_extended) == 3:
				bpy.ops.mesh.select_all(action='DESELECT')
				for vert in verts_extended:
					vert.select = True

				#Position by sorted size in row
	# sortedSizes = sorted(allSizes.items(), key=operator.itemgetter(1))#Sort by values, store tuples
	# sortedSizes.reverse()
	# offset = 0.0
	# for sortedSize in sortedSizes:
	# 	index = sortedSize[0]



		return connected_verts
			# 	v.select = True;
			# 	print("    e: "+str(len(v.link_edges)))




	
	# active_A = []
	# active_B = []

	# Starting values for layer skin
	# active_A.extend(verts_middle)
	# active_B.extend(verts_middle)
	# verts_processed.extend(verts_middle)


	select_extend_filter(verts_middle, verts_A)
	select_extend_filter(verts_middle, verts_B)
	



	# def extend_and_sort():
	# 	print("Extend sort: ")
	# 	for i in range(0, len(active_A)):
	# 		# Select outer layer @ i
	# 		bpy.ops.mesh.select_all(action='DESELECT')
	# 		active_A[i].select = True
	# 		active_B[i].select = True

	# 		#extend selection
	# 		bpy.ops.mesh.select_more()
	# 		for vert in verts_processed:
	# 			vert.select = False

	# 		#extract extended verts into A and B
	# 		extended_A = [vert for vert in bm.verts if (vert.select and vert in verts_A)]
	# 		extended_B = [vert for vert in bm.verts if (vert.select and vert in verts_B)]

	# 		#sort distance towards active_A[i] and B and match by distance
	# 		print("v "+str(i)+". AB: "+str(len(extended_A))+" : "+str(len(extended_B)))
	# 		if len(extended_A) == len(extended_B) and len(extended_A) > 0:
	# 			count = len(extended_A)
	# 			lengthsA = []
	# 			lengthsB = []
	# 			for j in range(0, count):
	# 				dA = (extended_A[j].co - active_A[i].co).length
	# 				lengthsA.append(dA)
	# 				dB = (extended_B[j].co - active_B[i].co).length
	# 				lengthsB.append(dB)
	# 				# print("   > "+str(j)+": "+str(dA)+" : "+str(dB))

	# 			for j in range(0, count):
	# 				# find closest match for each
	# 				print("   > "+str(j)+": ")
	# 				for k in range(0,count):
	# 					diff_A = abs(lengthsA[j] - lengthsB[k])
	# 					diff_B = abs(lengthsB[j] - lengthsA[k])
						
	# 					print("   Ch: "+str(diff_A)+" --> "+str(lengthsA[j])+" : "+str(lengthsB[k]))
					
	
	
	# extend_and_sort()
	



'''
	# Sort sorting
	for vert in verts_middle:
		bpy.ops.mesh.select_all(action='DESELECT')
		vert.select = True
		bpy.ops.mesh.select_more()

		verts_extended = []
		for v in bm.verts:
			if v.select and v not in verts_middle:
				verts_extended.append(v)

		print("Ext: "+str(len(verts_extended))+"x")
'''
	









def alignToCenterLine():
	print("align to center line")

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

	# 1.) Get average edges rotation + center
	average_angle = 0
	average_center = Vector((0,0))
	average_count = 0
	for face in bm.faces:
		if face.select:
			verts = []
			for loop in face.loops:
				if loop[uvLayer].select:
					verts.append(loop[uvLayer].uv)

			if len(verts) == 2:
				diff = verts[1] - verts[0]
				angle = math.atan2(diff.y, diff.x)%(math.pi)
				average_center += verts[0] + diff/2
				average_angle += angle
				average_count+=1

	if average_count >0:
		average_angle/=average_count
		average_center/=average_count

	average_angle-= math.pi/2 #Rotate -90 degrees so aligned horizontally

	# 2.) Rotate UV Shell around edge
	bpy.context.space_data.pivot_point = 'CURSOR'
	bpy.ops.uv.cursor_set(location=average_center)

	bpy.ops.uv.select_linked(extend=False)
	bpy.ops.transform.rotate(value=average_angle, axis=(0, 0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')



