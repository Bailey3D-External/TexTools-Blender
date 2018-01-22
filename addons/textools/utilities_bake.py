import bpy
import bmesh
import operator
import time
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings


keywords_low = ['lowpoly','low','lowp','lp','l']
keywords_high = ['highpoly','high','highp','hp','h']
keywords_cage = ['cage','c']
keywords_float = ['floater','float','f']

split_chars = [' ','_','.','-']


def store_bake_settings():
	print("store_bake_settings")
	# Render Settings
	settings.bake_render_engine = bpy.context.scene.render.engine

	# Disable Objects that are meant to be hidden
	sets = settings.sets
	objects_sets = []
	for set in sets:
		for obj in set.objects_low:
			if obj not in objects_sets:
				objects_sets.append(obj)
		for obj in set.objects_high:
			if obj not in objects_sets:
				objects_sets.append(obj)
		for obj in set.objects_cage:
			if obj not in objects_sets:
				objects_sets.append(obj)

	settings.bake_objects_hide_render = []
	for obj in bpy.context.scene.objects:
		if obj.hide_render == False and obj not in objects_sets:
			# Check if layer is active
			for l in range(0, len(obj.layers)):
				if obj.layers[l] and bpy.context.scene.layers[l]:
					settings.bake_objects_hide_render.append(obj)
					break

	for obj in settings.bake_objects_hide_render:
		obj.hide_render = True
		# obj.cycles_visibility.shadow = False





def restore_bake_settings():
	print("restore_bake_settings")
	
	# Render Settings
	if settings.bake_render_engine != '':
		bpy.context.scene.render.engine = settings.bake_render_engine

	# Disable Objects that are meant to be hidden
	for obj in settings.bake_objects_hide_render:
		if obj:
			obj.hide_render = False
			# obj.cycles_visibility.shadow = True



def get_bake_name(name):
	name = name.lower()
	
	# Split by ' ','_','.' etc.
	split = name.lower()
	for char in split_chars:
		split = split.replace(char,' ')
	strings = split.split(' ')

	# Remove all keys from name
	keys = keywords_cage + keywords_high + keywords_low + keywords_float
	new_strings = []
	for string in strings:
		is_found = False
		for key in keys:
			if string == key:
				is_found = True
				break
		if not is_found:
			new_strings.append(string)

	return "_".join(new_strings)



def get_object_type(obj):
	# Detect by name pattern
	split = obj.name.lower()
	for char in split_chars:
		split = split.replace(char,' ')
	strings = split.split(' ')

	# Detect float, more rare than low
	for string in strings:		
		for key in keywords_float:
			if key == string:
				return 'float'

	# Detect by modifiers
	if obj.modifiers:
		for modifier in obj.modifiers:
			if modifier.type == 'SUBSURF':
				return 'high'
			elif modifier.type == 'BEVEL':
				return 'high'


	# Detect High first, more rare
	for string in strings:
		for key in keywords_high:
			if key == string:
				return 'high'
	
	# Detect cage, more rare than low
	for string in strings:		
		for key in keywords_cage:
			if key == string:
				return 'cage'

	

	# Detect low
	for string in strings:
		for key in keywords_low:
			if key == string:
				return 'low'


	# if nothing was detected, assume its low
	return 'low'



def get_bake_sets():
	filtered = {}
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			filtered[obj] = get_object_type(obj)
	
	groups = []
	# Group by names
	for key in filtered:
		name = get_bake_name(key.name)

		if len(groups)==0:
			groups.append([key])
		else:
			isFound = False
			for group in groups:
				groupName = get_bake_name(group[0].name)
				if name == groupName:
					group.append(key)
					isFound = True
					break

			if not isFound:
				groups.append([key])

	# Sort groups alphabetically
	keys = [get_bake_name(group[0].name) for group in groups]
	keys.sort()
	sorted_groups = []
	for key in keys:
		for group in groups:
			if key == get_bake_name(group[0].name):
				sorted_groups.append(group)
				break
				
	groups = sorted_groups			
	# print("Keys: "+", ".join(keys))


	bake_sets = []
	for group in groups:
		low = []
		high = []
		cage = []
		float = []
		for obj in group:
			if filtered[obj] == 'low':
				low.append(obj)
			elif filtered[obj] == 'high':
				high.append(obj)
			elif filtered[obj] == 'cage':
				cage.append(obj)
			elif filtered[obj] == 'float':
				float.append(obj)


		name = get_bake_name(group[0].name)
		bake_sets.append(BakeSet(name, low, cage, high, float))

	return bake_sets


class BakeSet:
	objects_low = []	#low poly geometry
	objects_cage = []	#Cage low poly geometry
	objects_high = []	#High poly geometry
	objects_float = []	#Floating geometry
	name = ""

	has_issues = False

	def __init__(self, name, objects_low, objects_cage, objects_high, objects_float):
		self.objects_low = objects_low
		self.objects_cage = objects_cage
		self.objects_high = objects_high
		self.objects_float = objects_float
		self.name = name

		# Needs low poly objects to bake onto
		if len(objects_low) == 0:
			self.has_issues = True

		# Check Cage Object count to low poly count
		if len(objects_cage) > 0 and (len(objects_low) != len(objects_cage)):
			self.has_issues = True

		# Check for UV maps
		for obj in objects_low:
			if len(obj.data.uv_layers) == 0:
				self.has_issues = True
				break
