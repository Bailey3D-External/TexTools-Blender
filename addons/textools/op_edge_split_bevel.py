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
	bl_idname = "uv.textools_edge_split_bevel"
	bl_label = "Split Bevel"
	bl_description = "..."
	bl_options = {'REGISTER', 'UNDO'}

	radius = bpy.props.FloatProperty(
		name = "Space",
		description = "Space for split bevel",
		default = 0.015,
		min = 0,
		max = 0.35
	)


	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		return True


	def execute(self, context):
		main(self, self.radius)
		return {'FINISHED'}



def main(self, radius):

	#Store selection
	utilities_uv.selection_store()

	print("____________\nedge split UV sharp edges {}".format(radius))


	obj  = bpy.context.object
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	
	islands = utilities_uv.getSelectionIslands()
	

	# Collect UV to Vert
	vert_to_uv = {}
	uv_to_vert = {}
	for face in bm.faces:
		for loop in face.loops:
			loop[uvLayer].select = True
			vert = loop.vert
			uv = loop[uvLayer]
			# vert_to_uv
			if vert not in vert_to_uv:
				vert_to_uv[vert] = [uv];
			else:
				vert_to_uv[vert].append(uv)
			# uv_to_vert
			if uv not in uv_to_vert:
				uv_to_vert[ uv ] = vert;


	# Collect hard edges
	edges = []
	for edge in bm.edges:
		if edge.select and not edge.smooth:
			# edge.link_faces
			# print("Hard edge: {} - {}".format(edge.verts[0].index, edge.verts[1].index))
			edges.append(edge)

	# Get vert rails to slide		
	vert_rails = get_vert_edge_rails(edges)

	# Get left and right faces
	edge_face_pairs = get_edge_face_pairs(edges)


	print("Vert rails: {}x".format(len(vert_rails)))
	# for vert in vert_rails:
	# 	print(".. v.idx {} = {}x".format(vert.index, len(vert_rails[vert]) ))



	vert_processed = []
	vert_uv_pos = []

	for edge in edges:
		if len(edge_face_pairs[edge]) == 2:
			v0 = edge.verts[0]
			v1 = edge.verts[1]
			
			f0 = edge_face_pairs[edge][0]
			f1 = edge_face_pairs[edge][1]

			# v0
			if v0 not in vert_processed:
				vert_processed.append(v0)
				faces, delta = slide_uvs(v0, edge, f0, edges, vert_rails, vert_to_uv)
				vert_uv_pos.append( {"v":v0, "f":f0, "delta":delta, "faces":faces} )

				faces, delta = slide_uvs(v0, edge, f1, edges, vert_rails, vert_to_uv)
				vert_uv_pos.append( {"v":v0, "f":f1, "delta":delta, "faces":faces} )

			# V1
			if v1 not in vert_processed:
				vert_processed.append(v1)
				faces, delta = slide_uvs(v1, edge, f0, edges, vert_rails, vert_to_uv)
				vert_uv_pos.append( {"v":v1, "f":f0, "delta":delta, "faces":faces} )
				
				faces, delta = slide_uvs(v1, edge, f1, edges, vert_rails, vert_to_uv)
				vert_uv_pos.append( {"v":v1, "f":f1, "delta":delta, "faces":faces} )
	
	# ...
	for item in vert_uv_pos:
		faces = item["faces"]
		v = item["v"]


		for face in faces:
			if v in face.verts:
				for loop in face.loops:
					if loop.vert == vert:
						loop[uvLayer].uv+= vert_to_uv[v][0].uv + item["delta"] * radius/2
		# for f in faces:
		# 	for loop in f.loops:
		# 		if loop.vert == vert:
		# 			loop[uvLayer].uv= vert_to_uv[vert][0].uv + item["delta"] * radius/2

	



	# for loop in face.loops:
	# 	if loop.vert == vert:
	# 		loop[uvLayer].uv+= avg_uv_delta



	#Restore selection
	utilities_uv.selection_restore()


def slide_uvs(vert, edge, face, edges, vert_rails, vert_to_uv):
	A = edge.verts[0]
	B = edge.verts[1]
	A_links, B_links = get_edge_prev_next(edge, edges)
	
	verts_edges = {edge.verts[0], edge.verts[1]}
	for v in A_links:
		verts_edges.add( v )
	for v in B_links:
		verts_edges.add( v )

	print("_____________\nEdge {} <--> {}  ({})".format(edge.verts[0].index, edge.verts[1].index , vert.index))

	# Collect faces of this side

	'''
	faces = [face]
	face_edges_used = [e for e in face.edges if e in edges]
	for e in face.edges:
		if e not in face_edges_used:
			for f in e.link_faces:
				if f != face:
					faces.append(f)
	'''

	faces = [face]
	edges_main_used = [edge]
	for i in range(2):
		append = []

		for f in faces:
			for e in f.edges:
				if e not in edges_main_used:
					if e in edges:
						edges_main_used.append(e)

					for f_link in e.link_faces:
						if f_link not in faces:
							append.append(f_link)
		faces.extend(append)

	if vert.index == 51 and face.index == 36:
		print("Faces {}x".format(len(faces)))
		for f in faces:
			print("	f{}".format(f.index))


	# Get all face edges that could be valid rails
	face_edges = list(set([e for f in faces for e in f.edges if e not in edges]))

	# The verts influencing the offset
	verts = [A,B]
	if vert == A:
		verts.extend(B_links)
	elif vert == B:
		verts.extend(A_links)

	# print("Verts: {}x = {}".format(len(verts), [v.index for v in verts]))



	delta = Vector((0,0))
	count = 0
	for v in verts:
		rails = [e for e in vert_rails[v] if e in face_edges]
		for e in rails:
			# determine order
			v0 = None
			v1 = None
			if e.verts[0] in verts_edges:
				v0 = e.verts[0]
				v1 = e.verts[1]
			elif e.verts[1] in verts_edges:
				v0 = e.verts[1]
				v1 = e.verts[0]
			uv0 = vert_to_uv[v0][0].uv
			uv1 = vert_to_uv[v1][0].uv
			delta += (uv1-uv0).normalized()
			count += 1

	delta/=count

	return faces, delta
	# print("	V{} = {}".format(v.index, avg_uv_delta))

	# for loop in face.loops:
	# 	if loop.vert == vert:
	# 		loop[uvLayer].uv+= avg_uv_delta



'''
def slide_face_uvs(uvLayer, edge, vert, face, radius, vert_to_uv):
	avg_target = Vector((0,0))
	avg_count = 0

	for e in face.edges:
		if e != edge and vert in e.verts:
			vert_B = e.verts[0]
			if vert == e.verts[0]:
				vert_B = e.verts[1]
			A = vert_to_uv[vert][0].uv
			B = vert_to_uv[vert_B][0].uv

			avg_target+= A +(B - A).normalized() * radius
			avg_count+=1

	avg_target/=avg_count
	avg_target = vert_to_uv[vert][0].uv +(avg_target - vert_to_uv[vert][0].uv).normalized() * radius

	for loop in face.loops:
		if loop.vert == vert:
			loop[uvLayer].uv = avg_target
'''








'''
	# Get all rails (max 3x: current, before and after)
	rails = [e for v in verts_edges for e in vert_rails[v]]

	for x in rails:
		print("       raail: {} x {}".format(x.verts[0].index, x.verts[1].index))

	# Keep only rails shared with faces
	rails = [e for e in rails if e in face_edges]


	# print("...... v{} with {}x rails ".format(vert.index, len(rails)))

	# Filter rails on same side
'''




def get_edge_prev_next(edge, edges):
	A = edge.verts[0]
	B = edge.verts[1]

	print("  get_edge_prev_next {}x edges".format(len(edges)))
	# v0_extends = []	
	# v0_extends = [v for e in edges for v in e.verts if v in edge.verts and e != edge and v != v0]
	# v1_extends = [v for e in edges for v in e.verts if v in edge.verts and e != edge and v != v1]
	# v0_extends = [v_nest for v in edge.verts for e in v.link_edges for v_nest in e.verts if e != edge and if e in edges]
	
	A_extends = [v2 for v1 in edge.verts for e in v1.link_edges for v2 in e.verts if e != edge and e in edges and v2 not in edge.verts and v1 != A]
	B_extends = [v2 for v1 in edge.verts for e in v1.link_edges for v2 in e.verts if e != edge and e in edges and v2 not in edge.verts and v1 != B]

	return A_extends, B_extends


def get_edge_face_pairs(edges):
	edge_faces = {}
	for edge in edges:
		v0 = edge.verts[0]
		v1 = edge.verts[1]
		faces = []
		for face in edge.link_faces:
			if v0 in face.verts and v1 in face.verts:
				faces.append(face)
		edge_faces[edge] = faces

	return edge_faces



def get_vert_edge_rails(edges):

	vert_rails = {}
	for edge in edges:
		v0 = edge.verts[0]
		v1 = edge.verts[1]

		faces = []
		for face in edge.link_faces:
			if v0 in face.verts and v1 in face.verts:
				faces.append(face)

		for face in faces:
			for e in face.edges:
				if e not in edges and len(e.link_faces) > 1:
					if v0 not in vert_rails:
						vert_rails[ v0 ] = []
					if v1 not in vert_rails:
						vert_rails[ v1 ] = []

					if v0 in e.verts and e not in vert_rails[v0]:
						vert_rails[v0].append(e)

					if v1 in e.verts and e not in vert_rails[v1]:
						vert_rails[v1].append(e)

	return vert_rails



