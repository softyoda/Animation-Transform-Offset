# <pep8 compliant>
#  Animation Transform Offset - Transform objects while offsetting their animations
#  Copyright (C) 2024 softyoda
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# CHANGELOG
# v 1.0 February 2025 - Animation Transform Offset
#   ☒ Added Shift+G/R/S shortcuts for transform with animation offset
#   ☒ Added multi-object support
#   ☒ Initial release

bl_info = {
    "name": "Animation Transform Offset",
    "description": "Offset entire animation when transforming objects",
    "author": "SoftYoda",
    "version": (1, 0),
    "blender": (4, 3, 2),
    "location": "View3D > Sidebar > Animation > Animation Offset",
    "category": "Animation",
    "doc_url": "https://extensions.blender.org/add-ons/Animation-Transform-Offset/",  
    "tracker_url": "https://github.com/softyoda/Animation-Transform-Offset",
}

import bpy
from mathutils import Vector, Euler
from math import degrees, radians

class ANIMOFFSET_OT_grab(bpy.types.Operator):
    """Grab objects and offset their entire animation by the same amount"""
    bl_idname = "anim_offset.grab"
    bl_label = "Grab and Offset Animation"
    bl_options = {'REGISTER', 'UNDO'}

    start_locs = {}  # Stores initial locations of selected objects

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            return {'PASS_THROUGH'}
            
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            # Apply the translation delta to all keyframes of selected objects
            for obj in context.selected_objects:
                if (obj.animation_data and obj.animation_data.action and 
                    obj in self.start_locs):
                    delta = obj.location - self.start_locs[obj]
                    
                    for fc in obj.animation_data.action.fcurves:
                        if fc.data_path == "location":
                            for kp in fc.keyframe_points:
                                kp.co.y += delta[fc.array_index]
                            fc.update()
            return {'FINISHED'}
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # Restore original positions on cancel
            for obj in context.selected_objects:
                if obj in self.start_locs:
                    obj.location = self.start_locs[obj]
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        animated_objects = False
        self.start_locs.clear()
        
        # Store initial positions of animated objects
        for obj in context.selected_objects:
            if obj.animation_data and obj.animation_data.action:
                animated_objects = True
                self.start_locs[obj] = obj.location.copy()
        
        if not animated_objects:
            self.report({'WARNING'}, "Select at least one animated object")
            return {'CANCELLED'}
            
        context.window_manager.modal_handler_add(self)
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        
        return {'RUNNING_MODAL'}

class ANIMOFFSET_OT_rotate(bpy.types.Operator):
    """Rotate objects and offset their entire animation by the same amount"""
    bl_idname = "anim_offset.rotate"
    bl_label = "Rotate and Offset Animation"
    bl_options = {'REGISTER', 'UNDO'}

    start_rots = {}  # Stores initial rotations of selected objects

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            return {'PASS_THROUGH'}
            
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            # Apply the rotation delta to all keyframes of selected objects
            for obj in context.selected_objects:
                if (obj.animation_data and obj.animation_data.action and 
                    obj in self.start_rots):
                    # Convert rotation difference to degrees for easier handling
                    delta = Vector((
                        degrees(obj.rotation_euler.x - self.start_rots[obj].x),
                        degrees(obj.rotation_euler.y - self.start_rots[obj].y),
                        degrees(obj.rotation_euler.z - self.start_rots[obj].z)
                    ))
                    
                    for fc in obj.animation_data.action.fcurves:
                        if fc.data_path == "rotation_euler":
                            for kp in fc.keyframe_points:
                                kp.co.y += radians(delta[fc.array_index])
                            fc.update()
            return {'FINISHED'}
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # Restore original rotations on cancel
            for obj in context.selected_objects:
                if obj in self.start_rots:
                    obj.rotation_euler = self.start_rots[obj].copy()
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        animated_objects = False
        self.start_rots.clear()
        
        # Store initial rotations of animated objects
        for obj in context.selected_objects:
            if obj.animation_data and obj.animation_data.action:
                animated_objects = True
                self.start_rots[obj] = obj.rotation_euler.copy()
        
        if not animated_objects:
            self.report({'WARNING'}, "Select at least one animated object")
            return {'CANCELLED'}
            
        context.window_manager.modal_handler_add(self)
        bpy.ops.transform.rotate('INVOKE_DEFAULT')
        
        return {'RUNNING_MODAL'}

class ANIMOFFSET_OT_scale(bpy.types.Operator):
    """Scale objects and offset their entire animation by the same factor"""
    bl_idname = "anim_offset.scale"
    bl_label = "Scale and Offset Animation"
    bl_options = {'REGISTER', 'UNDO'}

    start_scales = {}  # Stores initial scales of selected objects

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            return {'PASS_THROUGH'}
            
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            # Apply the scale factor to all keyframes of selected objects
            for obj in context.selected_objects:
                if (obj.animation_data and obj.animation_data.action and 
                    obj in self.start_scales):
                    # Calculate scale factors
                    delta = Vector((
                        obj.scale[0] / self.start_scales[obj][0] - 1,
                        obj.scale[1] / self.start_scales[obj][1] - 1,
                        obj.scale[2] / self.start_scales[obj][2] - 1
                    ))
                    
                    for fc in obj.animation_data.action.fcurves:
                        if fc.data_path == "scale":
                            for kp in fc.keyframe_points:
                                kp.co.y *= (1 + delta[fc.array_index])
                            fc.update()
            return {'FINISHED'}
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # Restore original scales on cancel
            for obj in context.selected_objects:
                if obj in self.start_scales:
                    obj.scale = self.start_scales[obj].copy()
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        animated_objects = False
        self.start_scales.clear()
        
        # Store initial scales of animated objects
        for obj in context.selected_objects:
            if obj.animation_data and obj.animation_data.action:
                animated_objects = True
                self.start_scales[obj] = obj.scale.copy()
        
        if not animated_objects:
            self.report({'WARNING'}, "Select at least one animated object")
            return {'CANCELLED'}
            
        context.window_manager.modal_handler_add(self)
        bpy.ops.transform.resize('INVOKE_DEFAULT')
        
        return {'RUNNING_MODAL'}

class ANIMOFFSET_PT_panel(bpy.types.Panel):
    """Panel for Animation Offset tools"""
    bl_label = "Animation Offset"
    bl_idname = "ANIMOFFSET_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animation'
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Animation Offset")
        box.operator("anim_offset.grab", text="Grab and Offset Animation")
        box.operator("anim_offset.rotate", text="Rotate and Offset Animation")
        box.operator("anim_offset.scale", text="Scale and Offset Animation")
        box.label(text="Or use Shift+G/R/S", icon='INFO')

# Collection of all operator and panel classes
classes = (
    ANIMOFFSET_OT_grab,
    ANIMOFFSET_OT_rotate,
    ANIMOFFSET_OT_scale,
    ANIMOFFSET_PT_panel
)

# Store keymaps for cleanup on unregister
addon_keymaps = []

def register():
    """Register the addon and its classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add shortcuts
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode')
        
        # Grab shortcut
        kmi = km.keymap_items.new(
            ANIMOFFSET_OT_grab.bl_idname,
            type='G',
            value='PRESS',
            shift=True
        )
        addon_keymaps.append((km, kmi))
        
        # Rotate shortcut
        kmi = km.keymap_items.new(
            ANIMOFFSET_OT_rotate.bl_idname,
            type='R',
            value='PRESS',
            shift=True
        )
        addon_keymaps.append((km, kmi))
        
        # Scale shortcut
        kmi = km.keymap_items.new(
            ANIMOFFSET_OT_scale.bl_idname,
            type='S',
            value='PRESS',
            shift=True
        )
        addon_keymaps.append((km, kmi))

def unregister():
    """Unregister the addon and clean up"""
    # Remove shortcuts
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
