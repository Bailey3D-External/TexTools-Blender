bl_info = {
	"name": "TexTools",
	"description": "Professional UV and Texture tools for Blender.",
	"author": "renderhjs",
	"version": (1, 2, 00),
	"blender": (2, 79, 0),
	"category": "UV",
	"location": "UV Image Editor > Tools > 'TexTools' panel",
	"wiki_url": "http://renderhjs.net/textools/blender/"
}


# Import local modules
# More info: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
	import imp
	imp.reload(utilities_ui)
	imp.reload(settings)
	imp.reload(utilities_bake)
	imp.reload(utilities_color)
	imp.reload(utilities_texel)
	imp.reload(utilities_uv)
	imp.reload(utilities_meshtex)
	
	imp.reload(op_align)
	imp.reload(op_bake)
	imp.reload(op_bake_explode)
	imp.reload(op_bake_organize_names)
	imp.reload(op_bake_preview_texture)
	imp.reload(op_color_assign)
	imp.reload(op_color_clear)
	imp.reload(op_color_convert_texture)
	imp.reload(op_color_convert_vertex_colors)
	imp.reload(op_color_from_elements)
	imp.reload(op_color_from_materials)
	imp.reload(op_color_from_directions)
	imp.reload(op_color_io_export)
	imp.reload(op_color_io_import)
	imp.reload(op_color_select)
	imp.reload(op_island_align_edge)
	imp.reload(op_island_align_sort)
	imp.reload(op_island_align_world)
	imp.reload(op_island_mirror)
	imp.reload(op_island_rotate_90)
	imp.reload(op_island_straighten_edge_loops)
	imp.reload(op_rectify)
	imp.reload(op_select_islands_identical)
	imp.reload(op_select_islands_outline)
	imp.reload(op_select_islands_overlap)
	imp.reload(op_select_islands_flipped)
	imp.reload(op_smoothing_uv_islands)
	imp.reload(op_meshtex_create)
	imp.reload(op_meshtex_wrap)
	imp.reload(op_meshtex_trim)
	imp.reload(op_meshtex_trim_collapse)
	imp.reload(op_meshtex_pattern)
	imp.reload(op_texel_checker_map)
	imp.reload(op_texel_density_get)
	imp.reload(op_texel_density_set)
	imp.reload(op_texture_reload_all)
	imp.reload(op_unwrap_faces_iron)
	imp.reload(op_unwrap_peel_edge)
	imp.reload(op_uv_channel_add)
	imp.reload(op_uv_channel_swap)
	imp.reload(op_uv_crop)
	imp.reload(op_uv_resize)
	imp.reload(op_uv_size_get)

	
else:
	from . import settings
	from . import utilities_ui
	from . import utilities_bake
	from . import utilities_color
	from . import utilities_texel
	from . import utilities_uv
	from . import utilities_meshtex

	from . import op_align
	from . import op_bake
	from . import op_bake_explode
	from . import op_bake_organize_names
	from . import op_bake_preview_texture
	from . import op_color_assign
	from . import op_color_clear
	from . import op_color_convert_texture
	from . import op_color_convert_vertex_colors
	from . import op_color_from_elements
	from . import op_color_from_materials
	from . import op_color_from_directions
	from . import op_color_io_export
	from . import op_color_io_import
	from . import op_color_select
	from . import op_island_align_edge
	from . import op_island_align_sort
	from . import op_island_align_world
	from . import op_island_mirror
	from . import op_island_rotate_90
	from . import op_island_straighten_edge_loops
	from . import op_rectify
	from . import op_select_islands_identical
	from . import op_select_islands_outline
	from . import op_select_islands_overlap
	from . import op_select_islands_flipped
	from . import op_smoothing_uv_islands
	from . import op_meshtex_create
	from . import op_meshtex_wrap
	from . import op_meshtex_trim
	from . import op_meshtex_trim_collapse
	from . import op_meshtex_pattern
	from . import op_texel_checker_map
	from . import op_texel_density_get
	from . import op_texel_density_set
	from . import op_texture_reload_all
	from . import op_unwrap_faces_iron
	from . import op_unwrap_peel_edge
	from . import op_uv_channel_add
	from . import op_uv_channel_swap
	from . import op_uv_crop
	from . import op_uv_resize
	from . import op_uv_size_get
	

# Import general modules. Important: must be placed here and not on top
import bpy
import os
import math
import string
import bpy.utils.previews

from bpy.props import (
	StringProperty,
	BoolProperty,
	IntProperty,
	FloatProperty,
	FloatVectorProperty,
	EnumProperty,
	PointerProperty,
)



class Panel_Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	# Addon Preferences https://docs.blender.org/api/blender_python_api_2_67_release/bpy.types.AddonPreferences.html
	swizzle_y_coordinate = bpy.props.EnumProperty(items= 
		[	
			('Y+', 'Y+ OpenGL', 'Used in Blender, Maya, Modo, Toolbag, Unity'), 
			('Y-', 'Y- Direct X', 'Used in 3ds Max, CryENGINE, Source, Unreal Engine')
		], 
		description="Color template",
		name = "Swizzle Coordinates", 
		default = 'Y+'
	)
	bake_32bit_float = bpy.props.EnumProperty(items= 
		[	
			('8', '8 Bit', ''), 
			('32', '32 Bit', '')
		], 
		description="",
		name = "Image depth", 
		default = '8'
	)

	def draw(self, context):
		layout = self.layout

		box = layout.box()
		col = box.column(align=True)
		col.prop(self, "swizzle_y_coordinate", icon='MANIPUL')
		if self.swizzle_y_coordinate == 'Y+':
			col.label(text="Y+ used in: Blender, Maya, Modo, Toolbag, Unity")
		elif self.swizzle_y_coordinate == 'Y-':
			col.label(text="Y- used in: 3ds Max, CryENGINE, Source, Unreal Engine")
		
		box.separator()
		col = box.column(align=True)
		col.prop(self, "bake_32bit_float", icon='IMAGE_RGB')
		if self.bake_32bit_float == '8':
			col.label(text="8 Bit images are used. Banding may appear in normal maps.")
		elif self.bake_32bit_float == '32':
			col.label(text="32 Bit images are used. Images may require dithering to 8 bit.")
		
		
		if not hasattr(bpy.types,"ShaderNodeBevel"):
			box.separator()
			col = box.column(align=True)
		
			col.label("Unlock Bevel Shader", icon='ERROR')
			col.operator("wm.url_open", text="Get Blender with Bevel Shader", icon='BLENDER').url = "https://builder.blender.org/download/"
			col.label("Use nightly builds of Blender 2.79 or 2.8 to access Bevel baking")



		box = layout.box()

		box.label(text="Additional Links")
		col = box.column(align=True)
		col.operator("wm.url_open", text="Donate", icon='HELP').url = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZC9X4LE7CPQN6"
		col.operator("wm.url_open", text="GIT Code", icon='WORDWRAP_ON').url = "https://bitbucket.org/renderhjs/textools-blender/src"
		
		col.label(text="Discussions")
		row = col.row(align=True)
		row.operator("wm.url_open", text="BlenderArtists", icon='BLENDER').url = "https://blenderartists.org/forum/showthread.php?443182-TexTools-for-Blender"
		row.operator("wm.url_open", text="Polycount").url = "http://polycount.com/discussion/197226/textools-for-blender"
		row.operator("wm.url_open", text="Twitter").url = "https://twitter.com/search?q=%23textools"
		


class op_debug(bpy.types.Operator):
	bl_idname = "uv.textools_debug"
	bl_label = "Debug"
	bl_description = "Open console and enable dbug mode"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		bpy.app.debug = True# Debug Vertex indexies
		bpy.context.object.data.show_extra_indices = True
		bpy.app.debug_value = 1 #Set to Non '0
		return {'FINISHED'}



class op_disable_uv_sync(bpy.types.Operator):
	bl_idname = "uv.textools_disable_sync"
	bl_label = "Disable Sync"
	bl_description = "Disable UV sync mode"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		bpy.context.scene.tool_settings.use_uv_select_sync = False
		bpy.ops.mesh.select_all(action='SELECT')
		return {'FINISHED'}




class op_select_bake_set(bpy.types.Operator):
	bl_idname = "uv.textools_select_bake_set"
	bl_label = "Select"
	bl_description = "Select this bake set in scene"

	select_set = bpy.props.StringProperty(default="")

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		print("Set: "+self.select_set)
		if self.select_set != "":
			for set in settings.sets:
				if set.name == self.select_set:
					# Select this entire set
					bpy.ops.object.select_all(action='DESELECT')
					for obj in set.objects_low:
						obj.select = True
					for obj in set.objects_high:
						obj.select = True
					for obj in set.objects_cage:
						obj.select = True
					# Set active object to low poly to better visualize high and low wireframe color
					if len(set.objects_low) > 0:
						bpy.context.scene.objects.active = set.objects_low[0]

					break
		return {'FINISHED'}



class op_select_bake_type(bpy.types.Operator):
	bl_idname = "uv.textools_select_bake_type"
	bl_label = "Select"
	bl_description = "Select bake objects of this type"

	select_type = bpy.props.StringProperty(default='low')

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		objects = []
		for set in settings.sets:
			if self.select_type == 'low':
				objects+=set.objects_low
			elif self.select_type == 'high':
				objects+=set.objects_high
			elif self.select_type == 'cage':
				objects+=set.objects_cage
			elif self.select_type == 'float':
				objects+=set.objects_float
			elif self.select_type == 'issue' and set.has_issues:
				objects+=set.objects_low
				objects+=set.objects_high
				objects+=set.objects_cage
				objects+=set.objects_float

		bpy.ops.object.select_all(action='DESELECT')
		for obj in objects:
			obj.select = True

		return {'FINISHED'}



def on_dropdown_size(self, context):
	# Help: http://elfnor.com/drop-down-and-button-select-menus-for-blender-operator-add-ons.html
	size = int(bpy.context.scene.texToolsSettings.size_dropdown)
	bpy.context.scene.texToolsSettings.size[0] = size;
	bpy.context.scene.texToolsSettings.size[1] = size;

	if size <= 128:
		bpy.context.scene.texToolsSettings.padding = 2
	elif size <= 512:
		bpy.context.scene.texToolsSettings.padding = 4
	else:
		bpy.context.scene.texToolsSettings.padding = 8



def on_dropdown_uv_channel(self, context):
	if bpy.context.active_object != None:
		if bpy.context.active_object.type == 'MESH':
			if bpy.context.object.data.uv_layers:

				# Change Mesh UV Channel
				index = int(bpy.context.scene.texToolsSettings.uv_channel)
				if index < len(bpy.context.object.data.uv_textures):
					bpy.context.object.data.uv_textures.active_index = index
					bpy.context.object.data.uv_textures[index].active_render = True



def on_color_changed(self, context):
	for i in range(0, context.scene.texToolsSettings.color_ID_count):
		utilities_color.assign_color(i)



def on_color_dropdown_template(self, context):
	# Change Mesh UV Channel
	hex_colors = bpy.context.scene.texToolsSettings.color_ID_templates.split(',')
	bpy.context.scene.texToolsSettings.color_ID_count = len(hex_colors)

	# Assign color slots
	for i in range(0, len(hex_colors)):
		color = utilities_color.hex_to_color("#"+hex_colors[i])
		utilities_color.set_color(i, color)
		utilities_color.assign_color(i)



def on_color_count_changed(self, context):
	if bpy.context.active_object != None:
		utilities_color.validate_face_colors(bpy.context.active_object)



def get_dropdown_uv_values(self, context):
	# Requires mesh and UV data
	if bpy.context.active_object != None:
		if bpy.context.active_object.type == 'MESH':
			if bpy.context.object.data.uv_layers:
				options = []
				step = 0
				for uvLoop in bpy.context.object.data.uv_layers:
					# options.append((str(step), "#{}  {}".format(step+1, uvLoop.name), "Change UV channel to '{}'".format(uvLoop.name), step))
					options.append((str(step), "UV {}".format(step+1), "Change UV channel to '{}'".format(uvLoop.name), step))
					step+=1

				return options
	return []



def on_slider_meshtexture_wrap(self, context):
	value = bpy.context.scene.texToolsSettings.meshtexture_wrap
	obj_uv = utilities_meshtex.find_uv_mesh(bpy.context.selected_objects)
	if obj_uv:
		obj_uv.data.shape_keys.key_blocks["model"].value = value



class TexToolsSettings(bpy.types.PropertyGroup):
	#Width and Height
	size = bpy.props.IntVectorProperty(
		name = "Size",
		size=2, 
		description="Texture & UV size in pixels",
		default = (512,512),
		subtype = "XYZ"
	)
	size_dropdown = bpy.props.EnumProperty(
		items = utilities_ui.size_textures, 
		name = "Texture Size", 
		update = on_dropdown_size, 
		default = '512'
	)
	uv_channel = bpy.props.EnumProperty(
		items = get_dropdown_uv_values, 
		name = "UV", 
		update = on_dropdown_uv_channel
	)
	padding = bpy.props.IntProperty(
		name = "Padding",
		description="padding size in pixels",
		default = 4,
		min = 0,
		max = 256
	)
	bake_samples = bpy.props.FloatProperty(
		name = "Samples",
		description = "Samples in Cycles for Baking. The higher the less noise. Default: 64",
		default = 8,
		min = 1,
		max = 4000
	)
	bake_curvature_size = bpy.props.IntProperty(
		name = "Curvature",
		description = "Curvature offset in pixels to process",
		default = 1,
		min = 1,
		max = 64
	)
	bake_wireframe_size = bpy.props.FloatProperty(
		name = "Thickness",
		description = "Wireframe Thickness in pixels",
		default = 1,
		min = 0.1,
		max = 4.0
	)
	bake_bevel_size = bpy.props.FloatProperty(
		name = "Bevel",
		description = "Bevel radius",
		default = 0.05,
		min = 0.0,
		max = 1.0
	)
	bake_ray_distance = bpy.props.FloatProperty(
		name = "Ray Dist.",
		description = "Ray distance when baking. When using cage used as extrude distance",
		default = 0.01,
		min = 0.000,
		max = 100.00
	)
	bake_force_single = bpy.props.BoolProperty(
		name="Single Texture",
		description="Force a single texture bake accross all selected objects",
		default = False
	)
	bake_sampling = bpy.props.EnumProperty(items= 
		[('1', 'None', 'No Anti Aliasing (Fast)'), 
		('2', '2x', 'Render 2x and downsample'), 
		('4', '4x', 'Render 2x and downsample')], name = "AA", default = '1'
	)
	bake_freeze_selection = bpy.props.BoolProperty(
		name="Lock",
		description="Lock baking sets, don't change with selection",
		default = False
	)
	texel_mode_scale = bpy.props.EnumProperty(items= 
		[('ISLAND', 'Islands', 'Scale UV islands to match Texel Density'), 
		('ALL', 'Combined', 'Scale all UVs together to match Texel Density')], 
		name = "Mode", 
		default = 'ISLAND'
	)
	texel_density = bpy.props.FloatProperty(
		name = "Texel",
		description = "Texel size or Pixels per 1 unit ratio",
		default = 256,
		min = 0.0
		# max = 100.00
	)
	meshtexture_wrap = bpy.props.FloatProperty(
		name = "Wrap",
		description = "Transition of mesh texture wrap",
		default = 0,
		min = 0,
		max = 1,
		update = on_slider_meshtexture_wrap, 
		subtype  = 'FACTOR'
	)
	meshtexture_precission = bpy.props.EnumProperty(items= 
		[('5', '5 Low', 'Mesh Deform precession, increase if not wrapping correctly'), 
		('6', '6 Medium', 'Mesh Deform precession, increase if not wrapping correctly'),
		('7', '7 High', 'Mesh Deform precession, increase if not wrapping correctly')], name = "precission", default = '5'
	)

	def get_color(hex = "808080"):
		return bpy.props.FloatVectorProperty(
			name="Color1", 
			description="Set Color 1 for the Palette", 
			subtype="COLOR", 
			default=utilities_color.hex_to_color(hex), 
			size=3, 
			max=1.0, min=0.0,
			update=on_color_changed
		)#, update=update_color_1

	# 10 Color ID's
	color_ID_color_0 = get_color(hex="#ff0000")
	color_ID_color_1 = get_color(hex="#0000ff")
	color_ID_color_2 = get_color(hex="#00ff00")
	color_ID_color_3 = get_color(hex="#ffff00")
	color_ID_color_4 = get_color(hex="#00ffff")
	color_ID_color_5 = get_color()
	color_ID_color_6 = get_color()
	color_ID_color_7 = get_color()
	color_ID_color_8 = get_color()
	color_ID_color_9 = get_color()
	color_ID_color_10 = get_color()
	color_ID_color_11 = get_color()
	color_ID_color_12 = get_color()
	color_ID_color_13 = get_color()
	color_ID_color_14 = get_color()
	color_ID_color_15 = get_color()
	color_ID_color_16 = get_color()
	color_ID_color_17 = get_color()
	color_ID_color_18 = get_color()
	color_ID_color_19 = get_color()

	color_ID_templates = bpy.props.EnumProperty(items= 
		[	
			('3d3d3d,7f7f7f,b8b8b8,ffffff', '4 Gray', '...'), 
			('003153,345d4b,688a42,9db63a,d1e231', '5 Greens', '...'),
			('ff0000,0000ff,00ff00,ffff00,00ffff', '5 Code', '...'),
			('3a4342,2e302f,242325,d5cc9e,d6412b', '5 Sea Wolf', '...'),
			('7f87a0,2d3449,000000,ffffff,f99c21', '5 Mustang', '...'),
			('143240,209d8c,fed761,ffab56,fb6941', '5 Sunset', '...'), 
			('0087ed,23ca7a,eceb1d,e37a29,da1c2c', '5 Heat', '...'), 
			('9e00af,7026b9,4f44b5,478bf4,39b7d5,229587,47b151,9dcf46,f7f235,f7b824,f95f1e,c5513c,78574a,4d4b4b,9d9d9d', '15 Rainbow', '...')
		], 
		description="Color template",
		name = "Preset", 
		update = on_color_dropdown_template,
		default = 'ff0000,0000ff,00ff00,ffff00,00ffff'
	)

	color_ID_count = bpy.props.IntProperty(
		name = "Count",
		description="Number of color IDs",
		default = 5,
		update = on_color_count_changed,
		min = 2,
		max = 20
	)

	# bake_do_save = bpy.props.BoolProperty(
	# 	name="Save",
	# 	description="Save the baked texture?",
	# 	default = False)



class Panel_Units(bpy.types.Panel):
	bl_label = " "
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "TexTools"
	bl_options = {'HIDE_HEADER'}

	def draw_header(self, _):
		layout = self.layout
		layout.label(text="Size: {} x {}".format(bpy.context.scene.texToolsSettings.size[0], bpy.context.scene.texToolsSettings.size[1]))

	def draw(self, context):
		layout = self.layout
		
		if bpy.app.debug_value != 0:
			row = layout.row()
			row.alert =True
			row.operator(op_debug.bl_idname, text="DEBUG", icon="CONSOLE")
		
		#---------- Settings ------------
		# row = layout.row()
		col = layout.column(align=True)
		r = col.row(align = True)
		r.prop(context.scene.texToolsSettings, "size_dropdown", text="Size")
		r.operator(op_uv_size_get.op.bl_idname, text="", icon = 'EYEDROPPER')

		r = col.row(align = True)
		r.prop(context.scene.texToolsSettings, "size", text="")

		r = col.row(align = True)
		r.prop(context.scene.texToolsSettings, "padding", text="Padding")
		r.operator(op_uv_resize.op.bl_idname, text="Resize", icon_value = icon_get("op_extend_canvas_open"))
		
		col.separator()
		col.operator(op_texture_reload_all.op.bl_idname, text="Reload Textures", icon_value = icon_get("op_texture_reload_all"))
		
		# col.operator(op_extend_canvas.op.bl_idname, text="Resize", icon_value = icon_get("op_extend_canvas"))
		

		# UV Channel
		
		row = layout.row()

		has_uv_channel = False
		if bpy.context.active_object and len(bpy.context.selected_objects) == 1:
			if bpy.context.active_object in bpy.context.selected_objects:
				if bpy.context.active_object.type == 'MESH':
					
					# split = row.split(percentage=0.25)
					# c = row.column(align=True)
					# r = row.row(align=True)
					# r.alignment = 'RIGHT'
					# r.expand =
					# row.label(text="UV")#, icon='GROUP_UVS'

					
					if not bpy.context.object.data.uv_layers:
						# c = split.column(align=True)
						# row = c.row(align=True)
						# row.label(text="None", icon= 'ERROR')

						row.operator(op_uv_channel_add.op.bl_idname, text="Add", icon = 'ZOOMIN')
					else:
						# c = split.column(align=True)
						# row = c.row(align=True)
						group = row.row(align=True)
						group.prop(context.scene.texToolsSettings, "uv_channel", text="")
						group.operator(op_uv_channel_add.op.bl_idname, text="", icon = 'ZOOMIN')

						# c = split.column(align=True)
						# row = c.row(align=True)
						# row.alignment = 'RIGHT'
						group = row.row(align=True)
						r = group.column(align=True)
						r.active = bpy.context.object.data.uv_textures.active_index > 0
						r.operator(op_uv_channel_swap.op.bl_idname, text="", icon = 'TRIA_UP_BAR').is_down = False;
						
						r = group.column(align=True)
						r.active = bpy.context.object.data.uv_textures.active_index < (len(bpy.context.object.data.uv_textures)-1)
						r.operator(op_uv_channel_swap.op.bl_idname, text="", icon = 'TRIA_DOWN_BAR').is_down = True;

					has_uv_channel = True
		if not has_uv_channel:
			row.label(text="UV")
			
			

class Panel_Layout(bpy.types.Panel):
	bl_label = " "
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "TexTools"
	bl_options = {'DEFAULT_CLOSED'}

	def draw_header(self, _):
		layout = self.layout
		row = layout.row(align=True)
		row.operator("wm.url_open", text="", icon='INFO').url = "http://renderhjs.net/textools/blender/index.html#uvlayout"
		row.label(text ="Unwrap")

	# def draw_header(self, _):
	# 	layout = self.layout
	# 	layout.label(text="", icon_value=icon("logo"))


	def draw(self, context):
		layout = self.layout
		
		
		if bpy.app.debug_value != 0:
			col = layout.column(align=True)
			col.alert = True
			col.operator(op_island_straighten_edge_loops.op.bl_idname, text="Straight & Relax", icon_value = icon_get("op_island_straighten_edge_loops"))
			row = col.row(align=True)
			row.operator(op_island_mirror.op.bl_idname, text="Mirror", icon_value = icon_get("op_island_mirror")).is_stack = False;
			row.operator(op_island_mirror.op.bl_idname, text="Stack", icon_value = icon_get("op_island_mirror")).is_stack = True;

		#---------- Layout ------------
		# layout.label(text="Layout")
		
		box = layout.box()
		col = box.column(align=True)

		if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT' and bpy.context.scene.tool_settings.use_uv_select_sync:
			row = col.row(align=True)
			row.alert = True
			row.operator(op_disable_uv_sync.bl_idname, text="Disable sync", icon='CANCEL')#, icon='UV_SYNC_SELECT'


		row = col.row(align=True)
		row.operator(op_island_align_edge.op.bl_idname, text="Align Edge", icon_value = icon_get("op_island_align_edge"))
		
		row = col.row(align=True)
		row.operator(op_island_align_world.op.bl_idname, text="Align World", icon_value = icon_get("op_island_align_world"))
		

		row = col.row(align=True)
		row.operator(op_island_rotate_90.op.bl_idname, text="-90°", icon_value = icon_get("op_island_rotate_90_left")).angle = -math.pi / 2
		row.operator(op_island_rotate_90.op.bl_idname, text="+90°", icon_value = icon_get("op_island_rotate_90_right")).angle = math.pi / 2

		
		row = box.row(align=True)
		col = row.column(align=True)
		col.label(text="")
		col.operator(op_align.op.bl_idname, text="←", icon_value = icon_get("op_align_left")).direction = "left"
		
		col = row.column(align=True)
		col.operator(op_align.op.bl_idname, text="↑", icon_value = icon_get("op_align_top")).direction = "top"
		col.operator(op_align.op.bl_idname, text="↓", icon_value = icon_get("op_align_bottom")).direction = "bottom"

		col = row.column(align=True)
		col.label(text="")
		col.operator(op_align.op.bl_idname, text="→", icon_value = icon_get("op_align_right")).direction = "right"


		col = box.column(align=True)
		row = col.row(align=True)
		op = row.operator(op_island_align_sort.op.bl_idname, text="Sort H", icon_value = icon_get("op_island_align_sort_h"))
		op.is_vertical = False;
		op.padding = utilities_ui.get_padding()
		
		op = row.operator(op_island_align_sort.op.bl_idname, text="Sort V", icon_value = icon_get("op_island_align_sort_v"))
		op.is_vertical = True;
		op.padding = utilities_ui.get_padding()

		col.operator(op_uv_crop.op.bl_idname, text="Crop", icon_value = icon_get("op_uv_crop"))
		

		aligned = box.row(align=True)
		col = aligned.column(align=True)

		col.operator(op_rectify.op.bl_idname, text="Rectify", icon_value = icon_get("op_rectify"))
		col.operator(op_unwrap_faces_iron.op.bl_idname, text="Iron Faces", icon_value = icon_get("op_unwrap_faces_iron"))
		col.operator(op_unwrap_peel_edge.op.bl_idname, text="Peel Edge", icon_value = icon_get("op_unwrap_peel_edge"))


		#---------- Selection ------------
		layout.label(text="Select")

		box = layout.box()
		col = box.column(align=True)

		row = col.row(align=True)
		row.operator(op_select_islands_identical.op.bl_idname, text="Similar", icon_value = icon_get("op_select_islands_identical"))
		row.operator(op_select_islands_overlap.op.bl_idname, text="Overlap", icon_value = icon_get("op_select_islands_overlap"))

		row = col.row(align=True)
		row.operator(op_select_islands_outline.op.bl_idname, text="Bounds", icon_value = icon_get("op_select_islands_outline"))
		row.operator(op_select_islands_flipped.op.bl_idname, text="Flipped", icon_value = icon_get('op_select_islands_flipped'))


		
class Panel_Mesh(bpy.types.Panel):
	bl_label = " "
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "TexTools"
	bl_options = {'DEFAULT_CLOSED'}

	def draw_header(self, _):
		layout = self.layout
		row = layout.row(align=True)
		row.operator("wm.url_open", text="", icon='INFO').url = "http://renderhjs.net/textools/blender/index.html#mesh"
		row.label(text ="Topology")

	def draw(self, context):
		layout = self.layout

		box = layout.box()
		col = box.column()
		col.operator(op_smoothing_uv_islands.op.bl_idname, text="UV Smoothing", icon_value = icon_get("op_smoothing_uv_islands"))
		
		#---------- Texel ------------

		layout.label(text="Texels") #, icon_value=icon_get("texel_density")
		box = layout.box()
		row = box.row()
		row.scale_y = 1.75
		row.operator(op_texel_checker_map.op.bl_idname, text ="Checker Map", icon_value = icon_get("op_texel_checker_map"))
		
		col = box.column(align=True)
		row = col.row(align=True)
		row.label(text="" , icon_value = icon_get("texel_density"))
		row.separator()
		row.prop(context.scene.texToolsSettings, "texel_density", text="")
		row.operator(op_texel_density_get.op.bl_idname, text="", icon = 'EYEDROPPER')

		# col = box.column(align=True)
		row = col.row(align=True)
		row.operator(op_texel_density_set.op.bl_idname, text="Apply", icon = 'FACESEL_HLT')
		
		# if bpy.context.object and bpy.context.object.mode == 'EDIT':
		# 	row.enabled  = False
		row.prop(context.scene.texToolsSettings, "texel_mode_scale", text = "", expand=False)


		layout.label(text = "Mesh Texture")
		box = layout.box()
		col = box.column(align=True)

		row = col.row(align=True)
		row.scale_y = 1.75
		row.operator(op_meshtex_create.op.bl_idname, text="UV Mesh", icon_value = icon_get("op_meshtex_create"))
		col.operator(op_meshtex_trim.op.bl_idname, text="Trim", icon_value = icon_get("op_meshtex_trim"))

		# Warning about trimmed mesh
		if op_meshtex_trim_collapse.is_available():
			row = col.row(align=True)
			row.alert = True
			row.operator(op_meshtex_trim_collapse.op.bl_idname, text="Collapse Trim", icon='CANCEL')


		col = box.column(align=True)
		row = col.row(align = True)
		row.operator(op_meshtex_wrap.op.bl_idname, text="Wrap", icon_value = icon_get("op_meshtex_wrap"))
		row.prop(context.scene.texToolsSettings, "meshtexture_precission", text="")

		row = col.row(align = True)
		if not utilities_meshtex.find_uv_mesh(bpy.context.selected_objects):
			row.enabled = False
		row.prop(context.scene.texToolsSettings, "meshtexture_wrap", text="Wrap")

		box.operator(op_meshtex_pattern.op.bl_idname, text="Create Pattern", icon_value = icon_get("op_meshtex_pattern"))



class Panel_Bake(bpy.types.Panel):
	bl_label = " "
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "TexTools"
	bl_options = {'DEFAULT_CLOSED'}

	def draw_header(self, _):
		layout = self.layout
		row = layout.row(align=True)
		row.operator("wm.url_open", text="", icon='INFO').url = "http://renderhjs.net/textools/blender/index.html#texturebaking"
		row.label(text ="Baking")

	def draw(self, context):
		layout = self.layout
		
		#----------- Baking -------------
		row = layout.row()
		box = row.box()
		col = box.column(align=True)

		if not (bpy.context.scene.texToolsSettings.bake_freeze_selection and len(settings.sets) > 0):
			# Update sets
			settings.sets = utilities_bake.get_bake_sets()


		# Bake Button
		count = 0
		if bpy.context.scene.texToolsSettings.bake_force_single and len(settings.sets) > 0:
			count = 1
		else:
			count = len(settings.sets)
		
		row = col.row(align=True)
		row.scale_y = 1.75
		row.operator(op_bake.op.bl_idname, text = "Bake {}x".format(count), icon_value = icon_get("op_bake"));

		# anti aliasing
		col.prop(context.scene.texToolsSettings, "bake_sampling", icon_value =icon_get("bake_anti_alias"))
		
		# Force Single
		row = col.row(align=True)
		row.active = len(settings.sets) > 0
		row.prop(context.scene.texToolsSettings, "bake_force_single", text="Single")
		if len(settings.sets) > 0 and bpy.context.scene.texToolsSettings.bake_force_single:
			row.label(text="'{}'".format(settings.sets[0].name))
		else:
			row.label(text="")


		if bpy.app.debug_value != 0:
			row = col.row()
			row.alert = True
			row.prop(context.scene.texToolsSettings, "bake_force_single", text="Dither Floats")

		col.separator()


		# Bake Mode
		col.operator(op_bake_preview_texture.op.bl_idname, text = "Preview Texture", icon = 'TEXTURE_SHADED');
		col.template_icon_view(bpy.context.scene, "TT_bake_mode")
		
		
		if bpy.app.debug_value != 0:
			row = col.row()
			row.label(text="--> Mode: '{}'".format(settings.bake_mode))


		# Warning: Wrong bake mode, require 
		if settings.bake_mode == 'diffuse':
			if bpy.context.scene.render.engine != 'CYCLES':
				if bpy.context.scene.render.engine != op_bake.modes[settings.bake_mode].engine:
					col.label("Requires '{}'".format(op_bake.modes[settings.bake_mode].engine), icon='ERROR')
				
				


		# Optional Parameters
		col.separator()
		for set in settings.sets:
			if len(set.objects_low) > 0 and len(set.objects_high) > 0:
				col.prop(context.scene.texToolsSettings, "bake_ray_distance")
				break		

		# Display Bake mode properties / parameters
		if settings.bake_mode in op_bake.modes:
			params = op_bake.modes[settings.bake_mode].params
			if len(params) > 0:
				for param in params:
					col.prop(context.scene.texToolsSettings, param)


		box = layout.box()
		col = box.column(align=True)
		
		# Select by type
		if len(settings.sets) > 0:
			row = col.row(align=True)
			row.active = len(settings.sets) > 0

			count_types = {
				'low':0, 'high':0, 'cage':0, 'float':0, 'issue':0, 
			}
			for set in settings.sets:
				if set.has_issues:
					count_types['issue']+=1
				if len(set.objects_low) > 0:
					count_types['low']+=1
				if len(set.objects_high) > 0:
					count_types['high']+=1
				if len(set.objects_cage) > 0:
					count_types['cage']+=1
				if len(set.objects_float) > 0:
					count_types['float']+=1

			# Freeze Selection
			c = row.column(align=True)
			c.active = len(settings.sets) > 0 or bpy.context.scene.texToolsSettings.bake_freeze_selection
			icon = 'LOCKED' if bpy.context.scene.texToolsSettings.bake_freeze_selection else 'UNLOCKED'
			c.prop(context.scene.texToolsSettings, "bake_freeze_selection",text="Lock {}x".format(len(settings.sets)), icon=icon)

			# Select by type
			if count_types['issue'] > 0:
				row.operator(op_select_bake_type.bl_idname, text = "", icon = 'ERROR').select_type = 'issue'

			row.operator(op_select_bake_type.bl_idname, text = "", icon_value = icon_get("bake_obj_low")).select_type = 'low'
			row.operator(op_select_bake_type.bl_idname, text = "", icon_value = icon_get("bake_obj_high")).select_type = 'high'
			
			if count_types['float'] > 0:
				row.operator(op_select_bake_type.bl_idname, text = "", icon_value = icon_get("bake_obj_float")).select_type = 'float'
			
			if count_types['cage'] > 0:
				row.operator(op_select_bake_type.bl_idname, text = "", icon_value = icon_get("bake_obj_cage")).select_type = 'cage'
			

			# List bake sets
			box2 = box.box()
			row = box2.row()
			split = None

			countTypes = (0 if count_types['low'] == 0 else 1) + (0 if count_types['high'] == 0 else 1) + (0 if count_types['cage'] == 0 else 1) + (0 if count_types['float'] == 0 else 1)
			if countTypes > 2:
				# More than 3 types, use less space for label
				split = row.split(percentage=0.45)
			else:
				# Only 2 or less types, use more space for label
				split = row.split(percentage=0.55)

			c = split.column(align=True)
			for s in range(0, len(settings.sets)):
				set = settings.sets[s]
				r = c.row(align=True)
				r.active = not (bpy.context.scene.texToolsSettings.bake_force_single and s > 0)

				if set.has_issues:
					r.operator(op_select_bake_set.bl_idname, text=set.name, icon='ERROR').select_set = set.name
				else:
					r.operator(op_select_bake_set.bl_idname, text=set.name).select_set = set.name


			c = split.column(align=True)
			for set in settings.sets:
				r = c.row(align=True)
				r.alignment = "LEFT"

				if len(set.objects_low) > 0:
					r.label(text="{}".format(len(set.objects_low)), icon_value = icon_get("bake_obj_low"))
				elif count_types['low'] > 0:
					r.label(text="")

				if len(set.objects_high) > 0:
					r.label(text="{}".format(len(set.objects_high)), icon_value = icon_get("bake_obj_high"))
				elif count_types['high'] > 0:
					r.label(text="")

				if len(set.objects_float) > 0:
					r.label(text="{}".format(len(set.objects_float)), icon_value = icon_get("bake_obj_float"))
				elif count_types['float'] > 0:
					r.label(text="")

				if len(set.objects_cage) > 0:
					r.label(text="{}".format(len(set.objects_cage)), icon_value = icon_get("bake_obj_cage"))
				elif count_types['cage'] > 0:
					r.label(text="")

		
		col = box.column(align=True)
		col.operator(op_bake_organize_names.op.bl_idname, text = "Organize {}x".format(len(bpy.context.selected_objects)), icon = 'BOOKMARKS')
		col.operator(op_bake_explode.op.bl_idname, text = "Explode", icon_value = icon_get("op_bake_explode"));
		


class op_color_dropdown_io(bpy.types.Menu):
	bl_idname = "ui.textools_color_dropdown_io"
	bl_label = "IO"

	def draw(self, context):
		layout = self.layout

		layout.operator(op_color_io_export.op.bl_idname, text="Export Colors", icon = 'EXPORT')
		layout.operator(op_color_io_import.op.bl_idname, text="Import Colors", icon = 'IMPORT')



class op_color_dropdown_convert_from(bpy.types.Menu):
	bl_idname = "ui.textools_color_dropdown_convert_from"
	bl_label = "From"
	bl_description = "Create Color IDs from ..."

	def draw(self, context):
		layout = self.layout
		layout.operator(op_color_from_elements.op.bl_idname, text="Mesh Elements", icon_value = icon_get('op_color_from_elements'))
		layout.operator(op_color_from_materials.op.bl_idname, text="Materials", icon_value = icon_get('op_color_from_materials'))
		layout.operator(op_color_from_directions.op.bl_idname, text="Directions", icon_value = icon_get('op_color_from_directions'))

		if bpy.app.debug_value != 0:
			col = layout.column(align=True)
			col.alert = True
			col.operator(op_color_clear.op.bl_idname, text="Texture map", icon = 'CANCEL')
			col.operator(op_color_clear.op.bl_idname, text="Vertex Colors", icon = 'CANCEL')
			


class op_color_dropdown_convert_to(bpy.types.Menu):
	bl_idname = "ui.textools_color_dropdown_convert_to"
	bl_label = "To"
	bl_description = "Convert Color IDs into ..."

	def draw(self, context):
		layout = self.layout
		layout.operator(op_color_convert_texture.op.bl_idname, text="Texture Atlas", icon_value = icon_get('op_color_convert_texture'))
		layout.operator(op_color_convert_vertex_colors.op.bl_idname, text="Vertex Colors", icon = 'COLOR')


class op_enable_cycles(bpy.types.Operator):
	bl_idname = "uv.textools_enable_cycles"
	bl_label = "Enable Cycles"
	bl_description = "Enable Cycles render engine"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		bpy.context.scene.render.engine = 'CYCLES'
		return {'FINISHED'}


class Panel_Colors(bpy.types.Panel):
	bl_label = " "
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "TexTools"
	bl_options = {'DEFAULT_CLOSED'}

	def draw_header(self, _):
		layout = self.layout
		row = layout.row(align=True)
		row.operator("wm.url_open", text="", icon='INFO').url = "http://renderhjs.net/textools/blender/index.html#colorid"
		row.label(text ="Color ID")

	def draw(self, context):
		layout = self.layout
		
		# layout.label(text="Select face and color")
		
		if bpy.context.scene.render.engine != 'CYCLES' and bpy.context.scene.render.engine != 'BLENDER_RENDER':
			row = layout.row(align=True)
			row.alert = True
			row.operator(op_enable_cycles.bl_idname, text="Enable 'CYCLES'", icon='CANCEL')#, icon='UV_SYNC_SELECT'
			return


		box = layout.box()
		col = box.column(align=True)
		


		row = col.row(align=True)
		split = row.split(percentage=0.60, align=True)
		c = split.column(align=True)
		c.prop(context.scene.texToolsSettings, "color_ID_templates", text="")
		c = split.column(align=True)
		c.prop(context.scene.texToolsSettings, "color_ID_count", text="", expand=False)

		row = box.row(align=True)
		row.operator(op_color_clear.op.bl_idname, text="Clear", icon = 'X')
		row.menu(op_color_dropdown_io.bl_idname, '', icon='COLOR')


		max_columns = 5
		if context.scene.texToolsSettings.color_ID_count < max_columns:
			max_columns = context.scene.texToolsSettings.color_ID_count

		count = math.ceil(context.scene.texToolsSettings.color_ID_count / max_columns)*max_columns

		for i in range(count):

			if i%max_columns == 0:
				row = box.row(align=True)

			col = row.column(align=True)
			if i < context.scene.texToolsSettings.color_ID_count:
				col.prop(context.scene.texToolsSettings, "color_ID_color_{}".format(i), text="")
				col.operator(op_color_assign.op.bl_idname, text="", icon = "FILE_TICK").index = i
	
				if bpy.context.active_object:
					if bpy.context.active_object in bpy.context.selected_objects:
						if len(bpy.context.selected_objects) == 1:
							if bpy.context.active_object.type == 'MESH':
								col.operator(op_color_select.op.bl_idname, text="", icon = "FACESEL").index = i
			else:
				col.label(text=" ")

		
		# split = row.split(percentage=0.25, align=True)
		# c = split.column(align=True)
		# c.operator(op_color_clear.op.bl_idname, text="", icon = 'X')
		# c = split.column(align=True)
		# c.operator(op_color_from_elements.op.bl_idname, text="Color Elements", icon_value = icon_get('op_color_from_elements'))
		

		
		col = box.column(align=True)
		col.label(text="Convert")
		row = col.row(align=True)
		row.menu(op_color_dropdown_convert_from.bl_idname)#, icon='IMPORT'
		row.menu(op_color_dropdown_convert_to.bl_idname,)# icon='EXPORT'
		



		# row = col.row(align=True)
		# row.operator(op_color_convert_texture.op.bl_idname, text="From Atlas", icon_value = icon_get('op_color_convert_texture'))
			


		# for i in range(context.scene.texToolsSettings.color_ID_count):



		# 	col = row.column(align=True)
		# 	col.prop(context.scene.texToolsSettings, "color_ID_color_{}".format(i), text="")
		# 	col.operator(op_color_assign.op.bl_idname, text="", icon = "FILE_TICK").index = i
			
		# 	if bpy.context.active_object:
		# 		if bpy.context.active_object.type == 'MESH':
		# 			if bpy.context.active_object.mode == 'EDIT':
		# 				col.operator(op_color_select.op.bl_idname, text="", icon = "FACESEL").index = i

		

		# https://github.com/blenderskool/kaleidoscope/blob/fb5cb1ab87a57b46618d99afaf4d3154ad934529/spectrum.py
	
			


keymaps = []

def icon_get(name):
	return utilities_ui.icon_get(name)

	
def register():
	bpy.utils.register_module(__name__)
	
	#Register settings
	bpy.types.Scene.texToolsSettings = bpy.props.PointerProperty(type=TexToolsSettings)

	#GUI Utilities
	utilities_ui.register()

	# Register Icons
	icons = [
		"bake_anti_alias.png", 
		"bake_obj_cage.png", 
		"bake_obj_float.png", 
		"bake_obj_high.png", 
		"bake_obj_low.png", 
		"op_align_bottom.png", 
		"op_align_left.png", 
		"op_align_right.png", 
		"op_align_top.png", 
		"op_bake.png", 
		"op_bake_explode.png", 
		"op_color_convert_texture.png", 
		"op_color_from_directions.png", 
		"op_color_from_elements.png", 
		"op_color_from_materials.png", 
		"op_extend_canvas_open.png",
		"op_island_align_edge.png", 
		"op_island_align_world.png", 
		"op_island_align_sort_h.png", 
		"op_island_align_sort_v.png", 
		"op_island_mirror.png", 
		"op_island_rotate_90_left.png", 
		"op_island_rotate_90_right.png", 
		"op_island_straighten_edge_loops.png", 
		"op_meshtex_create.png",
		"op_meshtex_pattern.png",
		"op_meshtex_trim.png",
		"op_meshtex_wrap.png",
		"op_rectify.png", 
		"op_select_islands_flipped.png", 
		"op_select_islands_identical.png", 
		"op_select_islands_outline.png", 
		"op_select_islands_overlap.png", 
		"op_smoothing_uv_islands.png", 
		"op_texel_checker_map.png", 
		"op_texture_reload_all.png",
		"op_unwrap_faces_iron.png", 
		"op_unwrap_peel_edge.png", 
		"op_uv_crop.png", 
		"texel_density.png"
	]
	for icon in icons:
		utilities_ui.icon_register(icon)
	
	# #Key Maps
	# wm = bpy.context.window_manager
	# if wm.keyconfigs.addon is not None:
	# 	# https://github.com/RayMairlot/UV-Rotate-Shortcuts/blob/master/UV%20Rotate.py

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_align.op.bl_idname, 'UP_ARROW', 'PRESS', alt=True)
	# 	kmi.properties.direction = "top"
	# 	keymaps.append((km, kmi))

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_align.op.bl_idname, 'DOWN_ARROW', 'PRESS', alt=True)
	# 	kmi.properties.direction = "bottom"
	# 	keymaps.append((km, kmi))

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_align.op.bl_idname, 'LEFT_ARROW', 'PRESS', alt=True)
	# 	kmi.properties.direction = "left"
	# 	keymaps.append((km, kmi))

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_align.op.bl_idname, 'RIGHT_ARROW', 'PRESS', alt=True)
	# 	kmi.properties.direction = "right"
	# 	keymaps.append((km, kmi))

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_island_mirror.op.bl_idname, 'M', 'PRESS', alt=True)
	# 	kmi.properties.is_stack = False
	# 	keymaps.append((km, kmi))



def unregister():
	#GUI Utilities
	utilities_ui.unregister()

	bpy.utils.unregister_module(__name__)

	#Unregister Settings
	del bpy.types.Scene.texToolsSettings

	#handle the keymap
	for km, kmi in keymaps:
		km.keymap_items.remove(kmi)
	keymaps.clear()


if __name__ == "__main__":
	register()
