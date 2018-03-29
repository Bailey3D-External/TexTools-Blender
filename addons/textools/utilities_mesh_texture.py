import bpy
import bmesh
import operator
import time
import math
from mathutils import Vector

# Find a mesh that contains UV mesh shape keys 
def find_uv_mesh(objects):
	for obj in objects:
		# Requires mesh & UV channel
		if obj and obj.type == 'MESH': # and not obj.data.uv_layers

			if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) == 2:
				if "uv" in obj.data.shape_keys.key_blocks and "model" in obj.data.shape_keys.key_blocks:
					if "Solidify" in obj.modifiers:
						return obj

			if len(obj.modifiers) > 0:
				for modifier in obj.modifiers:
 					if modifier.type == 'MESH_DEFORM':
 						if modifier.object:
 							if modifier.object.data.shape_keys and len(modifier.object.data.shape_keys.key_blocks) == 2:
 								return modifier.object


	return None

