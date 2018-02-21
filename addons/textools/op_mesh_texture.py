import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv


id_shape_key_mesh = "mesh"
id_shape_key_uv = "uv"




def find_uv_mesh(objects):
	for obj in objects:
		if obj.type == 'MESH' and obj.data.shape_keys:
			if len(obj.data.shape_keys.key_blocks) == 2:
				return obj

	return None



def get_mode():
	if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT' and not find_uv_mesh(bpy.context.active_object):
		# Create UV mesh from face selection
		return 'CREATE'

	if len(bpy.context.selected_objects) >= 2 and find_uv_mesh(bpy.context.selected_objects):
		# for obj in bpy.context.selected_objects:
		return 'WRAP'

	if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
		# if bpy.context.active_object
		return 'CREATE'

	return 'UNDEFINED'



class op(bpy.types.Operator):
	bl_idname = "uv.textools_mesh_texture"
	bl_label = "Swap UV 2 XYZ"
	bl_description = "Swap UV to XYZ coordinates"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False
		
		if bpy.context.active_object.type != 'MESH':
			return False

		#One or more objects selected
		if len(bpy.context.selected_objects) == 0:
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False 	#self.report({'WARNING'}, "Object must have more than one UV map")


		return True


	def execute(self, context):

		#Determine if create UV mesh or wrap Mesh to UV
		mode = get_mode()
		if mode == 'CREATE':
			create_uv_mesh(self, bpy.context.active_object)	
				
		elif mode == 'WRAP':
			wrap_mesh_texture(self)

		return {'FINISHED'}



def wrap_mesh_texture(self):
	# Wrap the mesh texture around the 
	print("Wrap Mesh Texture :)")

	# Collect UV mesh
	obj_uv = find_uv_mesh(bpy.context.selected_objects)
	if not obj_uv:
		self.report({'ERROR_INVALID_INPUT'}, "No UV mesh found" )
		return

	# Collect texture meshes
	obj_textures = []
	for obj in bpy.context.selected_objects:
		if obj != obj_uv:
			obj_textures.append(obj)

	if len(obj_textures) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No UV mesh found" )
		return

	print("Wrap {} texture meshes".format(len(obj_textures)))


	for obj in obj_textures:
		print("Mesh {}".format(obj.name))
		# Set morph back to 0
		# measure bounds (world) of mesh textures
		# set solidify size to size + offset to capture fully

		# unbind if already bind
		# Apply mesh deform modifier (if not existing)
		# enable dynamic bind if other modifiers
		# Set morph to 1
		
		# bind

		# use:
		# bpy.context.object.modifiers["MeshDeform"].use_dynamic_bind = True
		# bpy.context.object.modifiers["MeshDeform"].show_on_cage = True






def create_uv_mesh(self, obj):
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj


	bpy.ops.object.mode_set(mode='EDIT')

	bm = bmesh.from_edit_mesh(obj.data)
	uvLayer = bm.loops.layers.uv.verify()

	# Select all
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.uv.select_all(action='SELECT')

	#Collect UV islands
	islands = utilities_uv.getSelectionIslands(bm, uvLayer)

	# Get object bounds
	bounds = get_bbox(obj)

	# Map clusters to 
	uvs = {}
	clusters = []
	uv_to_clusters = {}
	vert_to_clusters = {}

	for face in bm.faces:
		for i in range(len(face.loops)):
			v = face.loops[i]
			uv = Get_UVSet(uvs, bm, uvLayer, face.index, i)

			# 	# clusters
			isMerged = False
			for cluster in clusters:
				d = (uv.pos() - cluster.uvs[0].pos()).length
				if d <= 0.0000001:
					#Merge
					cluster.append(uv)
					uv_to_clusters[uv] = cluster
					if v not in vert_to_clusters:
						vert_to_clusters[v] = cluster
					isMerged = True;
					break;
			if not isMerged:
				#New Group
				clusters.append( UVCluster(v, [uv]) )
				uv_to_clusters[uv] = clusters[-1]
				if v not in vert_to_clusters:
					vert_to_clusters[v] = clusters[-1]
	

	print("Islands {}x".format(len(islands)))
	print("Clusters {}x".format(len(clusters)))

	# for key in uv_to_clusters.keys():
	# 	print("Key {}".format(key))

	uv_size = max(bounds['size'].x, bounds['size'].y, bounds['size'].z)
	print("Size: {}".format(uv_size))

	m_vert_cluster = []
	m_verts_org = []
	m_verts_A = []
	m_verts_B = []
	m_faces = []
	
	for island in islands:

		for face in island:
			f = []
			for i in range(len(face.loops)):
				v = face.loops[i].vert
				uv = Get_UVSet(uvs, bm, uvLayer, face.index, i)
				c = uv_to_clusters[ uv ]

				index = 0
				if c in m_vert_cluster:
					index = m_vert_cluster.index(c)

				else:
					index = len(m_vert_cluster)
					m_vert_cluster.append(c)
					m_verts_org.append(v)

					m_verts_A.append( Vector((uv.pos().x*uv_size -uv_size/2, uv.pos().y*uv_size -uv_size/2, 0)) )
					m_verts_B.append( obj.matrix_world * v.co  )
					
				f.append(index)

			m_faces.append(f)




	# https://blender.stackexchange.com/questions/15593/how-to-change-shapekey-vertex-position-through-python


	bpy.ops.object.mode_set(mode='OBJECT')
	# bpy.ops.object.select_all(action='TOGGLE')

	# Create Mesh
	mesh = bpy.data.meshes.new("mesh_texture")
	mesh.from_pydata(m_verts_A, [], m_faces)
	mesh.update()
	mesh_obj = bpy.data.objects.new("mesh_texture_obj", mesh)
	bpy.context.scene.objects.link(mesh_obj)

	# Add shape keys
	mesh_obj.shape_key_add(name="uv", from_mix=True)
	mesh_obj.shape_key_add(name="model", from_mix=True)
	mesh_obj.active_shape_key_index = 1

	# Select
	bpy.context.scene.objects.active = mesh_obj
	mesh_obj.select = True
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(mesh_obj.data)
	if hasattr(bm.faces, "ensure_lookup_table"): 
		bm.faces.ensure_lookup_table()
		bm.verts.ensure_lookup_table()

	for i in range(len(m_verts_B)):
		bm.verts[i].co = m_verts_B[i]
	bpy.ops.object.mode_set(mode='OBJECT')


	# Display as edges only
	mesh_obj.show_wire = True
	mesh_obj.show_all_edges = True
	mesh_obj.draw_type = 'WIRE'

	# Add solidify modifier
	bpy.ops.object.modifier_add(type='SOLIDIFY')
	bpy.context.object.modifiers["Solidify"].offset = 1
	bpy.context.object.modifiers["Solidify"].thickness = 0 #uv_size * 0.1
	bpy.context.object.modifiers["Solidify"].use_even_offset = True
	bpy.context.object.modifiers["Solidify"].thickness_clamp = 0

	# Add empty cube
	bpy.ops.object.empty_add(type='CUBE', location=obj.location)
	cube = bpy.context.object
	cube.empty_draw_size = uv_size/2
	cube.scale = (1, 1, 0)
	cube.parent = mesh_obj

	bpy.ops.object.select_all(action='DESELECT')
	mesh_obj.select = True
	bpy.context.scene.objects.active = mesh_obj
	# mesh_obj.location += Vector((-2.5, 0, 0))



def Get_UVSet(uvs, bm, layer, index_face, index_loop):
	index = get_uv_index(index_face, index_loop)
	if index not in uvs:
		uvs[index] = UVSet(bm, layer, index_face, index_loop)

	return uvs[index]



class UVSet:
	bm = None
	layer = None
	index_face = 0
	index_loop = 0

	def __init__(self, bm, layer, index_face, index_loop):
		self.bm = bm
		self.layer = layer
		self.index_face = index_face
		self.index_loop = index_loop
		
	def uv(self):
		face = self.bm.faces[self.index_face]
		return face.loops[self.index_loop][self.layer]

	def pos(self):
		return self.uv().uv

	def vertex(self):
		return face.loops[self.index_loop].vertex



def get_uv_index(index_face, index_loop):
	return (index_face*1000000)+index_loop
	# return str(index_face)+"_"+str( index_loop)

	

def get_bbox(obj):
	corners = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]

	# Get world space Min / Max
	box_min = Vector((corners[0].x, corners[0].y, corners[0].z))
	box_max = Vector((corners[0].x, corners[0].y, corners[0].z))
	for corner in corners:
		# box_min.x = -8
		box_min.x = min(box_min.x, corner.x)
		box_min.y = min(box_min.y, corner.y)
		box_min.z = min(box_min.z, corner.z)
		
		box_max.x = max(box_max.x, corner.x)
		box_max.y = max(box_max.y, corner.y)
		box_max.z = max(box_max.z, corner.z)

	return {
		'min':box_min, 
		'max':box_max, 
		'size':(box_max-box_min),
		'center':box_min+(box_max-box_min)/2
	}


class UVCluster:
	uvs = []
	vertex = None
	
	def __init__(self, vertex, uvs):
		self.vertex = vertex
		self.uvs = uvs

	def append(self, uv):
		self.uvs.append(uv)
