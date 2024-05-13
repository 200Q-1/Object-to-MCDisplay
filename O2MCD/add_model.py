# Copyright (c) 2023 200Q
import bpy
import os
from . import json_import
def menu_fn(self, context):
    self.layout.separator()
    self.layout.menu("OBJECTTOMCDISPLAY_MT_ObjectSub", text='O2MCD')

def enum_item(self, context):  # アイテムリスト
    enum_items = []
    for i in context.preferences.addons[__package__].preferences.item_id.split(","):
        enum_items.append((i, i, ""))
    return enum_items
def enum_block(self, context):  # ブロックリスト
    enum_items = []
    for i in context.preferences.addons[__package__].preferences.block_id.split(","):
        enum_items.append((i, i, ""))
    return enum_items

# 新しいサブメニューを定義
class OBJECTTOMCDISPLAY_MT_ObjectSub(bpy.types.Menu):
    bl_label = ""
    bl_description = ""
    def draw(self, context):
        layout = self.layout
        layout.operator("o2mcd.search_item", text="Item")
        layout.operator("o2mcd.search_block", text="Block")

class OBJECTTOMCDISPLAY_OT_SearchItem(bpy.types.Operator):  # アイテム検索
    bl_idname = "o2mcd.search_item"
    bl_label = ""
    bl_description= ""
    bl_property = "enum"
    enum: bpy.props.EnumProperty(name="Objects", description="", items=enum_item)

    def execute(self, context):
        directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","models","item"])+os.sep
        json_import.create_model(self,directory,self.enum)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_SearchBlock(bpy.types.Operator):  # ブロック検索
    bl_idname = "o2mcd.search_block"
    bl_label = ""
    bl_description= ""
    bl_property = "enum"
    enum: bpy.props.EnumProperty(name="Objects", description="", items=enum_block)

    def execute(self, context):
        directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","blockstates"])+os.sep
        json_import.create_model(self,directory,self.enum)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
classes = (
    OBJECTTOMCDISPLAY_MT_ObjectSub,
    OBJECTTOMCDISPLAY_OT_SearchItem,
    OBJECTTOMCDISPLAY_OT_SearchBlock,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.VIEW3D_MT_add.append(menu_fn)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    bpy.types.VIEW3D_MT_add.remove(menu_fn)