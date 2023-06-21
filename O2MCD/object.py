# Copyright (c) 2023 200Q

import bpy
import os
from re import *
from math import *
from . import list
# 関数

def item_regist():  # アイテムとブロックを登録
    file = open(bpy.path.abspath(os.path.dirname(__file__))+'\\item_list.txt', 'r', encoding='UTF-8')
    item = file.read().splitlines()
    bpy.context.scene.O2MCD_item_list.clear()
    for i in item:
        bpy.context.scene.O2MCD_item_list.add().name= i
    file.close()
    
    file = open(bpy.path.abspath(os.path.dirname(__file__))+'\\block_list.txt', 'r', encoding='UTF-8')
    block = file.read().splitlines()
    bpy.context.scene.O2MCD_block_list.clear()
    for i in block:
        bpy.context.scene.O2MCD_block_list.add().name= i
    file.close()

def setid(self,context):  # idを更新
    if context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index].Types == "ITEM":
        context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index].id = context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index].item_id
    elif context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index].Types == "BLOCK":
        context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index].id = context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index].block_id
    
def prop_link(self, context):  # プロパティリンクボタン
    self.layout.separator()
    self.layout.operator("object.link_prop")

def change_name(self,context):  # 名前被りを回避
    if [i.name for i in context.scene.O2MCD_prop_list].count(self.name) > 1:
        name = sub("(.*?)(\.[0-9]+)?","\\1",self.name)
        same_names = [i.name for i in context.scene.O2MCD_prop_list if match(f"{name}(?:\.[0-9]+)?",i.name)]
        same_names.sort()
        if same_names:
            for i in same_names:
                ii = sub(".+?\.([0-9]+)","\\1",i)
                if ii == name:
                    if not name+".001" in same_names:
                        self.name = name+".001"
                        break
                else:
                    ii = str(int(ii)+1).zfill(3)
                    if not name+"."+ii in same_names:
                        self.name = name+"."+ii
                        break


enum_items = []
def enum_item(self, context):  # プロパティリスト
    global enum_items
    enum_items = []
    for i in range(len(context.scene.O2MCD_prop_list)):
        enum_items.append((str(i), str(i)+":"+context.scene.O2MCD_prop_list[i].name, ""))
    return enum_items

# クラス

class OBJECTTOMCDISPLAY_PT_DisplayProperties(bpy.types.Panel):  # プロパティパネル
    bl_label = bpy.app.translations.pgettext("Display Properties") 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.scene.O2MCD_props.enable

    def draw(self, context):
        layout = self.layout
        br = layout.row(align=True)
        br.alignment = "LEFT"
        if context.scene.O2MCD_prop_list:
            item = context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index]
        br.operator("object.search_popup", text="", icon='DOWNARROW_HLT')
        if context.scene.O2MCD_props.list_index >= 0 and context.scene.O2MCD_prop_list:
            br.prop(item, "name", text="")
            br.operator("object.o2mcd_prop_action", icon='DUPLICATE').action = 'DUP'
            br.operator("object.o2mcd_prop_action", icon='PANEL_CLOSE').action = 'UNLINK'
            br.operator("object.o2mcd_prop_action", icon='TRASH').action = 'REMOVE'
        else:
            br.alignment = "EXPAND"
            br.operator("object.o2mcd_prop_action", icon='ADD',text="New").action = 'ADD'
        if context.scene.O2MCD_prop_list and context.object.O2MCD_props.prop_id >= 0:
            row = layout.row()
            row.enabled = False
            row.use_property_split = True
            row.use_property_decorate = False
            row.prop(context.object.O2MCD_props, "number")
            layout.prop(item, "Types", expand=True)
            if item.Types == "EXTRA":
                layout.prop(item, "type")
            if item.Types == "ITEM":
                layout.prop_search(context.scene.O2MCD_prop_list[context.object.O2MCD_props.prop_id], "item_id",context.scene, "O2MCD_item_list",text="id")
                layout.prop(item, "tags")
                layout.prop(item,"CustomModelData")
                layout.prop(item, "ItemTag")
            if item.Types == "BLOCK":
                layout.prop_search(context.scene.O2MCD_prop_list[context.object.O2MCD_props.prop_id], "block_id",context.scene, "O2MCD_block_list",text="id")
                layout.prop(item, "tags")
                layout.prop(item, "Properties",text="properties")
            layout.prop(item, "ExtraNBT")


class OBJECTTOMCDISPLAY_OT_PropAction(bpy.types.Operator): #プロパティ操作
    bl_idname = "object.o2mcd_prop_action"
    bl_label = ""
    action: bpy.props.EnumProperty(items=(('ADD', "Add", ""),('DUP', "dup", ""),('UNLINK', "unlink", ""),('REMOVE', "remove", "")))
    
    def invoke(self,context,event):
        prop_list = context.scene.O2MCD_prop_list
        index = context.scene.O2MCD_props.list_index

        if self.action =='ADD':
            context.scene.O2MCD_prop_list.add().name = "New"
            index = len(context.scene.O2MCD_prop_list)-1
            context.object.O2MCD_props.prop_id = index
        elif self.action == 'DUP':
            name = sub("(.*?)(\.[0-9]+)?","\\1",prop_list[context.object.O2MCD_props.prop_id].name)
            add = context.scene.O2MCD_prop_list.add()
            add.name = name
            add.Types= prop_list[context.object.O2MCD_props.prop_id].Types
            add.tags= prop_list[context.object.O2MCD_props.prop_id].tags
            add.CustomModelData= prop_list[context.object.O2MCD_props.prop_id].CustomModelData
            add.ItemTag= prop_list[context.object.O2MCD_props.prop_id].ItemTag
            add.Properties= prop_list[context.object.O2MCD_props.prop_id].Properties
            add.ExtraNBT= prop_list[context.object.O2MCD_props.prop_id].ExtraNBT
            add.type= prop_list[context.object.O2MCD_props.prop_id].type
            add.id= prop_list[context.object.O2MCD_props.prop_id].id
            add.item_id= prop_list[context.object.O2MCD_props.prop_id].item_id
            add.block_id= prop_list[context.object.O2MCD_props.prop_id].block_id
            index = len(context.scene.O2MCD_prop_list)-1
            context.object.O2MCD_props.prop_id = index
        elif self.action == 'UNLINK':
            context.object.O2MCD_props.prop_id = -1
        elif self.action == 'REMOVE':
            prop_list.remove(index)
            index = min(max(0, index - 1), len(prop_list) - 1)
            for i in context.scene.O2MCD_object_list:
                if i.obj.O2MCD_props.prop_id >= index:
                    i.obj.O2MCD_props.prop_id -= 1
            context.object.O2MCD_props.prop_id = index
        context.scene.O2MCD_props.list_index = context.object.O2MCD_props.prop_id
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_OT_SearchPopup(bpy.types.Operator):  # id検索
    bl_idname = "object.search_popup"
    bl_label = ""
    bl_property = "enum"
    bl_description= bpy.app.translations.pgettext("Browse Linked Properties")
    enum: bpy.props.EnumProperty(name="Objects", description="", items=enum_item)

    def execute(self, context):
        context.object.O2MCD_props.prop_id = int(self.enum)
        context.scene.O2MCD_props.list_index = context.object.O2MCD_props.prop_id
        list.chenge_panel(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class O2MCD_Obj_Props(bpy.types.PropertyGroup):  # オブジェクトのプロパティ
    number: bpy.props.IntProperty(name=bpy.app.translations.pgettext("Object Number"), default=-1, min=-1)
    prop_id: bpy.props.IntProperty(name="prop_id", default=-1, min=-1)
    enable : bpy.props.BoolProperty(name="", default=True)

class O2MCD_ListItem(bpy.types.PropertyGroup):  # リストのプロパティ
    name: bpy.props.StringProperty(name="Name", default="",update=change_name)
    Types: bpy.props.EnumProperty(name="Object Type", items=[('ITEM', "Item", ""), ('BLOCK', "Block", ""), ('EXTRA', "Extra", "")], options={"ANIMATABLE"},update=setid)
    tags: bpy.props.StringProperty(default="")
    CustomModelData: bpy.props.IntProperty(default=0, min=0)
    ItemTag: bpy.props.StringProperty(default="")
    Properties:bpy.props.StringProperty(default="")
    ExtraNBT: bpy.props.StringProperty(default="")
    type: bpy.props.StringProperty(default="")
    id: bpy.props.StringProperty(default="")
    item_id: bpy.props.StringProperty(default="",update=setid)
    block_id: bpy.props.StringProperty(default="",update=setid)

class  O2MCD_ItemList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_BlockList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")


classes = (
    OBJECTTOMCDISPLAY_PT_DisplayProperties,
    OBJECTTOMCDISPLAY_OT_PropAction,
    OBJECTTOMCDISPLAY_OT_SearchPopup,
    O2MCD_Obj_Props,
    O2MCD_ListItem,
    O2MCD_ItemList,
    O2MCD_BlockList,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Obj_Props)
    bpy.types.Scene.O2MCD_prop_list = bpy.props.CollectionProperty(type=O2MCD_ListItem)
    bpy.types.Scene.O2MCD_item_list = bpy.props.CollectionProperty(type=O2MCD_ItemList)
    bpy.types.Scene.O2MCD_block_list = bpy.props.CollectionProperty(type=O2MCD_BlockList)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)