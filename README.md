# TexTools for Blender #

TexTools is a free addon for Blender with a collection of UV and Texture related tools. Back in 2009 I released the [Original TexTools](http://renderhjs.net/textools/) for 3dsMax. Currently this is an early development release and more features will be added in the future. Most of the tools are context sensitive or perform 2 actions at once.

![](http://renderhjs.net/textools/blender/img/screenshot_version_0.3.0.png)


## Download ##
* [Blender TexTools 0.7.2.zip](http://renderhjs.net/textools/blender/Blender TexTools 0.7.2.zip)
* [Blender TexTools 0.7.1.zip](http://renderhjs.net/textools/blender/Blender TexTools 0.7.1.zip)
* [Blender TexTools 0.6.0.zip](http://renderhjs.net/textools/blender/Blender TexTools 0.6.0.zip)
* [Blender TexTools 0.3.0.zip](http://renderhjs.net/textools/blender/Blender TexTools 0.3.0.zip)

## Links ##
* ![](http://renderhjs.net/textools/blender/img/paypal_donate.png)
 [PayPal Donation](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZC9X4LE7CPQN6) for those that like doing that
* [Git repository](https://bitbucket.org/renderhjs/textools-blender) on BitBucket
* [3dsMax version](http://renderhjs.net/textools/) of TexTools
* Blenderartist [discussion thread](https://blenderartists.org/forum/showthread.php?443182-TexTools-for-Blender)
* Personal website [renderhjs.net](http://www.renderhjs.net/) all written in haxe ;)

---

## Installation ##

1. Download TexTools for Blender
2. In Blender from the **File** menu open **User Preferences** ![](http://renderhjs.net/textools/blender/img/installation_open_preferences.png) 
3. Go to the **Add-ons** tab ![](http://renderhjs.net/textools/blender/img/installation_addons.png).
4. Hit **Install Addon-on from File...** ![](http://renderhjs.net/textools/blender/img/installation_install_addon_from_file.png) and Select the zip file.
5. Enable the TexTools Addon
6. The TexTools panel can be found in the **UV/Image Editor** view ![](http://renderhjs.net/textools/blender/img/installation_uv_image_editor.png) in the left Tool Panel.

---

# Manual #



## ► Units ##

Used to set the texture size for baking but also the padding size for UV operations when spacing UV islands. Use the dropdown menu to quickly assign common square texture sizes. All units are in pixels.

![](http://renderhjs.net/textools/blender/img/screenshot_texture_settings.png)

#### Size
A dropdown with common texture sizes for the Width and Height of the texture in pixels

#### Padding
Padding size in pixels. The padding is used for UV margins and texture baking.

#### Resize
![](http://renderhjs.net/textools/blender/img/op_extend_canvas_open.png)

Opens a resize popup where you can extend or resize the UV layout canvas to either direction.


---


## ► UV Layout ##


#### Align
![](http://renderhjs.net/textools/blender/img/op_align.png)

In UV vertex mode ![Vert mode](http://renderhjs.net/textools/blender/img/selection_uv_vertex.png) it Aligns selected UV verts to either side of the initial selection bounds.
In the UV face mode ![Face mode](http://renderhjs.net/textools/blender/img/selection_uv_face.png) selected UV islands are aligned to either side of the initial selection bounds.

**Shortcut**: ALT + Arrow keys

#### Align Edge
![](http://renderhjs.net/textools/blender/img/op_island_align_edge.png)

Aligns the UV island of the selected UV edge ![Edge mode](http://renderhjs.net/textools/blender/img/selection_uv_edge.png) to the closest 90 degree angle.

#### Rotate 90°
![](http://renderhjs.net/textools/blender/img/op_island_rotate_90.png)

Rotates the UV island 90 degrees left or right and aligns the island to the initial bounding box's top left or right.


#### Sort & Align
![](http://renderhjs.net/textools/blender/img/op_islands_align_sort.png)

Sorts the selected UV islands by longest side and aligns them vertically or horizontally in a row.


#### Mirror
![](http://renderhjs.net/textools/blender/img/op_island_symmetry.png)

Select the mirror UV edge loop ![Edge mode](http://renderhjs.net/textools/blender/img/selection_uv_edge.png) and both sides will be mirrored and averaged in symetry. Alternatively you can select half of the UV island in UV face mode ![Face mode](http://renderhjs.net/textools/blender/img/selection_uv_face.png) and it's layout will be transferred to the other side.


#### Iron Faces
![](http://renderhjs.net/textools/blender/img/op_faces_iron.png)

Unwraps selected viewpoert faces ![Face mode](http://renderhjs.net/textools/blender/img/selection_view_face.png) into a single UV island. This is often a quicker approach of unwrapping as opposed to marking the boundary edges (mark seams).

---

## Select ##

#### Select Similar
![](http://renderhjs.net/textools/blender/img/op_select_islands_identical.png)

Selects similar UV islands based on the UV island input selection and matching UV Island topology.


#### Select Overlap
![](http://renderhjs.net/textools/blender/img/op_select_islands_overlap.png)

Collects all UV islands that overlap each other and select of each group all except for one island.


#### Select Island Bounds
![](http://renderhjs.net/textools/blender/img/op_select_islands_outline.png)

Selects the edge bounds of all UV Islands in the 3D viewport.

---
## Textures ##

#### Checker Map
![](http://renderhjs.net/textools/blender/img/op_texture_checker.png)

Assigns a checker map to the selected object or cycles through 2 checker maps. When a checker map is assigned it changes the view to texture mode.

![](http://renderhjs.net/textools/blender/img/checker_maps.png)


#### Reload Textures
![](http://renderhjs.net/textools/blender/img/op_textures_reload.png)

Reload all textures in the current blend file

---

## ► Texture Baking ##


#### Bake
![](http://renderhjs.net/textools/blender/img/op_bake.png)
Bakes the textures of the selected objects


Baking in TexTools is **super** easy, just select your objects and press Bake. A realtime set list shows you what will be baked and how many objects are part of each. 

![](http://renderhjs.net/textools/blender/img/bake_sets_preview.png)

You'll see a warning icon in front of items that have missing UV's, missing low poly objects or incorrect cage to low poly object counts.


#### AA / Anti Alias
![](http://renderhjs.net/textools/blender/img/bake_anti_alias.png)

Anti Aliasing level, choose from: None, 2x and 4x. When you enable Anti Aliasing the bake render is rendered at a scaled resulution and afterwards down scaled. Anti Aliasing works on any baking mode.


#### Single
With multiple objects selected enable this when you want all items to be baked into a single texture as opposed to multiple. It uses the name or ID from the first item in the bake set list. This is great for multi part objects or exploded bake setups.


#### Baking modes
* **'AO'** Ambient Occlusion pass, use the 'Samples' value below to adjust the amount of samples
* **'Cavity'** Convex and Concarve render pass using vertex color and cycles pointiness for a refined result
* **'Dust'** Uses pointiness shader and top facing areas for brighter values. Great for aging materials
* **'GradientZ'** World space Z axis as gradient mask
* **'ID'** World space Z axis as gradient mask
* **'Normal'** Normal map in tangent space


---

#### Type of baking objects
TexTools automatically groups your scene selection into sets to bake. Objects with common name prefixes are grouped into a set. Objects can be of 3 different object types:

* ![](http://renderhjs.net/textools/blender/img/bake_obj_low.png) **Low poly** objects: when their name used the keyword: 'lowpoly', 'low', 'lp' or 'l' 
* ![](http://renderhjs.net/textools/blender/img/bake_obj_high.png) **High poly** objects: when they contain a **Subdevision Surface** modifier or when their name used the keyword: 'highpoly','high','hp' or 'h' 
* ![](http://renderhjs.net/textools/blender/img/bake_obj_cage.png) **Cage objects**:when their name used the keyword 'cage' or 'c' . Cages are used to project rays from a custom mesh, this match needs to match the face and vertex count of the low poly object.


#### Organize
Declutters your selected object names by matching high and low poly objects by their bounding box location and size. Only high poly objects are renamed to match the low poly names with the ' high' suffix.


#### Explode
![](http://renderhjs.net/textools/blender/img/op_bake_explode.png)

Moves all selected bake pairs apart into 6 directions. Offsets are based on bounding boxes and offset to the center of the whole group. Margins are a 35% of the average side of all bounding boxes. Animation keyframes are added at 0 and 50 of each selected object to transition between the 2 states. Keyframes can be removed aftwards if not desired.


#### Lock Selection
![](http://renderhjs.net/textools/blender/img/bake_lock_selection.png)

Lock or unlock the current bake selection. When locked scene selection changes won't affect the baking list. This is great for tweaking meshes, cages or other settings while baking.


#### Select by type
![](http://renderhjs.net/textools/blender/img/bake_select_by_type.png)

Select from the baking sets all objects that match a critera such as 'Warning', 'Low', 'High' or 'Cage' objects. 

**Tip**: When bake sets are locked you can select scene objects here independently of the bake sets.


---

# Developer notes #

## Using GIT source version in Blender ##
1. Goto user preferences (Ctrl + Alt + U)
2. In the **'File'** tab set the 'Scripts' path to '{GIT Path}\' so that blender will pick up 'addons' folder
3. In the **'Add-ons' ** tab enable TexTools

## Enable debug features ##
1. Press Ctrl + Alt + D for the debug value panel
2. Set the value other than '0'
3. Protoype tools should be shown in red in the interface

![](http://renderhjs.net/textools/blender/img/screenshot_debug_menu.png)

