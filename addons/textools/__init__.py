#    Blender TexTools, 
#    <TexTools, Blender addon for editing UVs and Texture maps.>
#    Copyright (C) <2017> <renderhjs>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
	"name": "TexTools",
	"description": "UV and texture Tools for Blender. Based on ideas of the original TexTools for 3dsMax.",
	"author": "renderhjs",
	"version": (1, 0, 0),
	"blender": (2, 71, 0),
	"category": "UV",
	"location": "UV Image Editor > UVs > Misc : TexTools panel",
	"warning": "",
	"wiki_url": "http://renderhjs.net/textools/"
}

# Import local modules
# More info: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
	import imp
	imp.reload(utilities_gui)

	imp.reload(operator_islandsAlignSort)
	imp.reload(operator_checkerMap)
	imp.reload(operator_align)
	imp.reload(operator_reloadTextures)
	imp.reload(operator_bake)
	imp.reload(operator_swap_uv_xyz)
	imp.reload(operator_island_align_edge)
	
else:
	from . import utilities_gui

	from . import operator_islandsAlignSort
	from . import operator_checkerMap
	from . import operator_align
	from . import operator_reloadTextures
	from . import operator_bake
	from . import operator_swap_uv_xyz
	from . import operator_island_align_edge

# Import general modules. Important: must be placed here and not on top
import bpy
import os
import math
import string
import bpy.utils.previews

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )



#Vector Int Property: https://blender.stackexchange.com/questions/22855/how-to-customise-add-properties-to-existing-blender-data
# Store in Scene for UV: https://blender.stackexchange.com/questions/35007/how-can-i-add-a-checkbox-in-the-tools-ui

class TexToolsSettings(bpy.types.PropertyGroup):
	#Width and Height
	size = bpy.props.IntVectorProperty(
		name = "Size",
		size=2, 
		description="Texture & UV size in pixels",
		default = (1024,1024),
		subtype = "XYZ"
	)

	

	#Padding
	padding = IntProperty(
		name = "Padding",
		description="padding size in pixels",
		default = 4,
		min = 1,
		max = 16384
	)
	
	baking_do_save = bpy.props.BoolProperty(
		name="Save",
    	description="Save the baked texture?",
    	default = False)

	id_palette = None;#bpy.types.UILayout.template_palette()



def getIcon(name):
	return preview_icons[name].icon_id

class TexToolsPanel(bpy.types.Panel):
#    """TexTools Panel"""
	bl_label = "TexTools"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "TexTools"
	
	def draw(self, context):
		layout = self.layout
		

		layout.operator("wm.console_toggle", text="Console")


		#---------- Settings ------------
		row = layout.row()
		box = row.box()
		# box.label(text="Settings")

		col = box.column(align=True)
		# aligned = col.row(align=True)
		col.prop(context.scene.texToolsSettings, "size", text="")
		col.prop(context.scene.texToolsSettings, "padding", text="Padding")

		layout.separator()

		#---------- Transform ------------


		# boxHeader = layout.box()
		# row = boxHeader.row();
		layout.operator("wm.console_toggle", text="Header", icon = "TRIA_DOWN")
		# row.label(text="Header")


		row = layout.row()
		box = row.box()
		# box.label(text="Trasnform")

		aligned = box.row(align=True)
		aligned.operator("transform.rotate", text="-90°", icon_value = getIcon("turnLeft")).value = -math.pi / 2
		aligned.operator("transform.rotate", text="+90°", icon_value = getIcon("turnRight")).value = math.pi / 2
		
		row = box.row(align=True)
		col = row.column(align=True)
		col.label(text="")
		col.operator(operator_align.operator_align.bl_idname, text="←", icon_value = getIcon("alignLeft")).direction = "left"
		col = row.column(align=True)
		col.operator(operator_align.operator_align.bl_idname, text="↑", icon_value = getIcon("alignTop")).direction = "top"
		col.operator(operator_align.operator_align.bl_idname, text="↓", icon_value = getIcon("alignBottom")).direction = "bottom"
		col = row.column(align=True)
		col.label(text="")
		col.operator(operator_align.operator_align.bl_idname, text="→", icon_value = getIcon("alignRight")).direction = "right"


		aligned = box.row(align=True)
		aligned.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, text="Sort H", icon_value = getIcon("islandsAlignSortH")).is_vertical = False;
		aligned.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, text="Sort V", icon_value = getIcon("islandsAlignSortV")).is_vertical = True;
		aligned = box.row()
		aligned.operator(operator_island_align_edge.operator_island_align_edge.bl_idname, text="Align", icon_value = getIcon("islandAlignByEdge"))

		layout.operator(operator_swap_uv_xyz.operator_swap_uv_xyz.bl_idname, text="Swap UV/XYZ", icon_value = getIcon("swap_uv_xyz"))

		layout.separator()

		#---------- Textures ------------
		row = layout.row()
		box = row.box()
		box.label(text="Textures")
		aligned = box.row(align=True)
		aligned.operator(operator_checkerMap.operator_checkerMap.bl_idname, icon_value = getIcon("checkerMap"))
		aligned.operator(operator_reloadTextures.operator_reloadTextures.bl_idname, text="Reload", icon_value = getIcon("reloadTextures"))

		layout.separator()

		#---------- Baking ------------
		row = layout.row()
		box = row.box()
		box.label(text="Baking")

		aligned = box.row()
		#Alternative VectorBool? https://blender.stackexchange.com/questions/14312/how-can-i-present-an-array-of-booleans-in-a-panel
		
		aligned.template_icon_view(context.scene, "my_thumbnails")

		# Just a way to access which one is selected
		aligned = box.row()
		aligned.label(text="Mode: " + str(bpy.context.scene.my_thumbnails).replace(".png",""))

	
		#Thumbnail grid view: https://blender.stackexchange.com/questions/47504/script-custom-previews-in-a-menu
		
		aligned = box.row(align=True)
		aligned.operator(operator_bake.operator_bake_setup_material.bl_idname, text = "Set Material");
		aligned.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, text = "Set Model");

		aligned = box.row(align=True)
		aligned.operator(operator_bake.operator_bake_render.bl_idname, text = "Bake");
		aligned.prop(context.scene.texToolsSettings, "baking_do_save")
		
		layout.separator()

		#---------- ID Colors ------------
		#Example custom UI list: https://blender.stackexchange.com/questions/47840/is-bpy-props-able-to-create-a-list-of-lists
		#Example assign vertex colors: https://blender.stackexchange.com/questions/30841/how-to-view-vertex-colors
		#Color Palette: https://blender.stackexchange.com/questions/73122/how-do-i-create-palette-ui-object

		row = layout.row()
		box = row.box()
		box.label(text="ID Colors")
		box.operator(bpy.ops.paint.sample_color.idname())
		# box.template_palette(context.scene.texToolsSettings, "id_palette", color=True)



keymaps = []

def registerIcon(fileName):
	# global custom_icons
	name = fileName.split('.')[0]   # Don't include file extension
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")
	preview_icons.load(name, os.path.join(icons_dir, fileName), 'IMAGE')
	
def register():
	bpy.utils.register_module(__name__)
	
	#Register settings
	bpy.types.Scene.texToolsSettings = PointerProperty(type=TexToolsSettings)
	
	#GUI Utilities
	utilities_gui.register()

	# Register global Icons
	global preview_icons
	preview_icons = bpy.utils.previews.new()
	registerIcon("islandsAlignSortH.png")
	registerIcon("islandsAlignSortV.png")
	registerIcon("checkerMap.png")
	registerIcon("swap_uv_xyz.png")
	registerIcon("turnLeft.png")
	registerIcon("turnRight.png")
	registerIcon("reloadTextures.png")
	registerIcon("islandAlignByEdge.png")
	registerIcon("alignBottom.png")
	registerIcon("alignLeft.png")
	registerIcon("alignRight.png")
	registerIcon("alignTop.png")
	
	#Key Maps
	# wm = bpy.context.window_manager
	# km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# kmi = km.keymap_items.new(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
	# keymaps.append((km, kmi))
	
	#bpy.utils.register_module(__name__)
	#handle the keymap
#    wm = bpy.context.window_manager
	
#    km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
#    kmi = km.keymap_items.new(UvSquaresByShape.bl_idname, 'E', 'PRESS', alt=True)
#    addon_keymaps.append((km, kmi))
	
	

def unregister():

	bpy.utils.unregister_module(__name__)

	#Unregister Settings
	del bpy.types.Scene.texToolsSettings

	#GUI Utilities
	utilities_gui.unregister()

	# Unregister icons
	global preview_icons
	bpy.utils.previews.remove(preview_icons)

	#handle the keymap
	for km, kmi in keymaps:
		km.keymap_items.remove(kmi)
	keymaps.clear()

#    bpy.types.IMAGE_MT_uvs.remove(menu_func_uv_squares)
	
	# handle the keymap
#    for km, kmi in addon_keymaps:
#        km.keymap_items.remove(kmi)
	# clear the list
#    addon_keymaps.clear()

if __name__ == "__main__":
	register()

	#Setup Color palette