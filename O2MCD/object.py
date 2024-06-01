# Copyright (c) 2023 200Q

import bpy
import os
from re import *
from math import *
from . import json_import
# 関数
    
    
def prop_link(self, context):  # プロパティリンクボタン
    self.layout.separator()
    self.layout.operator("object.link_prop")

def mesh_update(self, context):
    for o in bpy.context.scene.O2MCD_object_list :
        obj=o.obj
        if len(obj.O2MCD_mesh_list)-1 >= obj.O2MCD_props.mesh_index:
            obj.data=obj.O2MCD_mesh_list[obj.O2MCD_props.mesh_index].mesh
            obj.O2MCD_props.disp_id=sub('\.[0-9]+', "",obj.data.name.split("/")[-1])
            for modi in list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) , obj.modifiers)):
                if match(f"{modi.node_group.name}(?:\.[0-9]+)?",obj.data.name):
                    modi.show_viewport=True
                else:
                    modi.show_viewport=False

def panel_object(self,context):
    layout = self.layout
    if context.preferences.addons[__package__].preferences.mc_jar and context.active_object:
        if context.active_object and context.active_object.O2MCD_props.disp_id == "":
            layout.menu("OBJECTTOMCDISPLAY_MT_SetId")
        else:
            col=layout.column()
            col.label(text="TYPE: "+context.active_object.O2MCD_props.disp_type)
            box=col.box()
            row=box.row()
            row.alignment = "CENTER"
            row2=row.row()
            row.label(text="Index")
            if context.object.O2MCD_props.number <= 0 :row2.enabled = False
            row2.operator("o2mcd.list_move", icon='TRIA_LEFT', text="").action = 'UP'
            row.label(text=str(context.object.O2MCD_props.number))
            row2=row.row()
            if context.object.O2MCD_props.number >= len(context.scene.O2MCD_object_list)-1 :row2.enabled = False
            row2.operator("o2mcd.list_move", icon='TRIA_RIGHT', text="").action = 'DOWN'
            col=layout.column(align=True)
            col.label(text="メッシュリスト")
            row=col.row()
            row.template_list("OBJECTTOMCDISPLAY_UL_MeshList", "", context.active_object, "O2MCD_mesh_list", context.active_object.O2MCD_props, "mesh_index", rows=2)
            col2 = row.column()
            row = col2.row()
            if context.active_object.O2MCD_props.mesh_index == 0 :
                row.enabled= False
            row.operator("o2mcd.mesh_list_action", icon='TRIA_UP', text="").action = 'UP'
            row = col2.row()
            if context.active_object.O2MCD_props.mesh_index >= len(context.active_object.O2MCD_mesh_list)-1 :
                row.enabled= False
            row.operator("o2mcd.mesh_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
            row=col.row()
            sp= row.split(align=True,factor=0.7)
            if context.active_object.O2MCD_props.disp_type=="item_display":
                sp.prop_search(context.preferences.addons[__package__].preferences, "item_id",context.preferences.addons[__package__].preferences, "item_list",text="")
                sp2= sp.split(align=True,factor=1)
                sp2.enabled=True if context.preferences.addons[__package__].preferences.item_id else False
                sp2.operator("o2mcd.mesh_list_action", icon='ADD', text="追加").action = 'ADD'
            elif context.active_object.O2MCD_props.disp_type=="block_display":
                sp.prop_search(context.preferences.addons[__package__].preferences, "block_id",context.preferences.addons[__package__].preferences, "block_list",text="")
                row= sp.row()
                row.enabled=True if context.preferences.addons[__package__].preferences.block_id else False
                row.operator("o2mcd.mesh_list_action", icon='ADD', text="追加").action = 'ADD'
            
            col=layout.column(align=True)
            col.use_property_split = True
            col.separator()
            box=col.box()
            box.label(text="プロパティ")
            try:
                modi= list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) and match(f"{m.node_group.name}(?:\.[0-9]+)?",context.active_object.data.name), context.active_object.modifiers))[0]
                for i,n in enumerate(list(filter(lambda n : n.type=='MENU_SWITCH',modi.node_group.nodes))):
                    box.prop(context.active_object.modifiers[modi.name],f"[\"Socket_{i+2}\"]",text=n.name)
            except:pass
            col=layout.column(align=True)
            col.label(text="コマンドリスト")
            row= col.row()
            row.template_list("OBJECTTOMCDISPLAY_UL_CommandList", "", context.active_object, "O2MCD_command_list", context.active_object.O2MCD_props, "command_index", rows=2,sort_lock=True)
            col = row.column()
            col2=col.column()
            col2.operator("o2mcd.command_list_action", icon='ADD', text="").action = 'ADD'
            col2.operator("o2mcd.command_list_action", icon='REMOVE', text="").action = 'REMOVE'
            row = col.row()
            if context.active_object.O2MCD_props.command_index == 0 :
                row.enabled= False
            row.operator("o2mcd.command_list_action", icon='TRIA_UP', text="").action = 'UP'
            row = col.row()
            if context.active_object.O2MCD_props.command_index >= len(context.active_object.O2MCD_command_list)-1 :
                row.enabled= False
            row.operator("o2mcd.command_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
            
            if context.active_object.O2MCD_props.prop_id >= 0:
                row=layout.row()
                if len(context.scene.O2MCD_object_list) <= 1:row.enabled = False
                row.operator("o2mcd.list_move", icon='TRIA_LEFT', text="").action = 'UP'
                row.alignment = "CENTER"
                row.label(text=str(context.active_object.O2MCD_props.number))
                row.operator("o2mcd.list_move", icon='TRIA_RIGHT', text="").action = 'DOWN'
            box=layout.box()
            row = box.row(align = True)
            row.label(text="Tags")
            row.operator("o2mcd.tag_action", icon='ADD', text="", emboss=False).action='ADD'
            col = box.column(align = True)
            for i,item in enumerate(context.active_object.O2MCD_tag_list):
                row = col.row(align = True)
                row.prop(item,"tag",text="")
                ac=row.operator("o2mcd.tag_action", icon='PANEL_CLOSE', text="", emboss=False)
                ac.action='REMOVE'
                ac.index=i
    else:
        layout.label(text="アドオン設定から.jarファイルを指定してください。")
class OBJECTTOMCDISPLAY_PT_ObjectProperties(bpy.types.Panel):  # プロパティパネル
    bl_label = "O2MCD"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"


    def draw(self, context):
        panel_object(self,context)
        
class OBJECTTOMCDISPLAY_PT_WindowObjectProperties(bpy.types.Panel):  # プロパティパネル
    bl_label = "O2MCD"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"


    def draw(self, context):
        panel_object(self,context)

class O2MCD_Obj_Props(bpy.types.PropertyGroup):  # オブジェクトのプロパティ
    number: bpy.props.IntProperty(name=bpy.app.translations.pgettext("Object Number"), default=-1, min=-1)
    prop_id: bpy.props.IntProperty(name="prop_id", default=-1, min=-1)
    enable : bpy.props.BoolProperty(name="enable", default=True)
    command_index: bpy.props.IntProperty(name="cmd_index", default=-1)
    pre_cmd: bpy.props.IntProperty(name="",default=-1)
    disp_id: bpy.props.StringProperty(name="id",description="",default="")
    disp_type: bpy.props.StringProperty(name="type",description="",default="")
    mesh_index:bpy.props.IntProperty(name="mesh_index", default=0,update=mesh_update)


class  O2MCD_ItemList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_BlockList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")

# コマンドリスト
def cmd_list_update(self,context):
    if context.active_object.O2MCD_command_list and self == context.active_object.O2MCD_command_list[context.active_object.O2MCD_props.command_index]:
        bpy.data.texts["Input"].from_string(self.command)
class  O2MCD_CommandList(bpy.types.PropertyGroup): 
    name: bpy.props.StringProperty(name="Name",description="",default="")
    command: bpy.props.StringProperty(name="Command",description="",default="",update=cmd_list_update)
    enable: bpy.props.BoolProperty(name="Enable",description="", default=True)

class OBJECTTOMCDISPLAY_UL_CommandList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row(align=True)
        row.alignment="LEFT"
        row.prop(item, "enable", text="")
        row.label(icon='TEXT')
        row.prop(item, "name", text="", emboss=True)
        row.prop(item, "command", text="", emboss=False)
        
# タグリスト
class  O2MCD_TagList(bpy.types.PropertyGroup): 
    tag: bpy.props.StringProperty(name="tag",description="",default="")
class OBJECTTOMCDISPLAY_UL_TagList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row(align=True)
        row.alignment="LEFT"
        row.prop(item, "enable", text="")
        row.label(icon='TEXT')
        row.prop(item, "name", text="", emboss=True)
        row.prop(item, "command", text="", emboss=False)
class OBJECTTOMCDISPLAY_OT_TagAction(bpy.types.Operator):  # コマンド追加
    bl_idname = "o2mcd.tag_action"
    bl_label = ""
    bl_description = ""
    action: bpy.props.EnumProperty(items=(('ADD',"add",""),('REMOVE',"remove","")))
    index: bpy.props.IntProperty(name="Index")
    
    def execute(self, context):
        match self.action:
            case 'ADD':
                context.object.O2MCD_tag_list.add()
            case 'REMOVE':
                context.object.O2MCD_tag_list.remove(self.index)
        return {'FINISHED'}
# メッシュリスト
class  O2MCD_MeshList(bpy.types.PropertyGroup):
    mesh: bpy.props.PointerProperty(name="Mesh",type=bpy.types.Mesh)
    
class OBJECTTOMCDISPLAY_UL_MeshList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row()
        row.label(text=item.mesh.name,icon='MESH_DATA')
        op = row.operator("o2mcd.mesh_list_action", icon='X', text="")
        op.action = 'REMOVE'
        op.index = index
    def execute(self, context):
        bpy.ops.wm.call_menu(name="OBJECTTOMCDISPLAY_MT_SetId")
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_MeshListAction(bpy.types.Operator): #移動
    bl_idname = "o2mcd.mesh_list_action"
    bl_label = ""
    bl_description = ""
    action: bpy.props.EnumProperty(items=(('UP', "up", ""),('DOWN', "down", ""),('ADD',"add",""),('REMOVE',"remove","")))
    index : bpy.props.IntProperty(default=0)
    def invoke(self, context, event):
        mesh_list=context.view_layer.objects.active.O2MCD_mesh_list
        mesh_index=context.view_layer.objects.active.O2MCD_props.mesh_index
        if self.action == 'DOWN':
            mesh_list.move(mesh_index, mesh_index+1)
            context.object.O2MCD_props.mesh_index += 1
        elif self.action == 'UP':
            mesh_list.move(mesh_index, mesh_index-1)
            context.object.O2MCD_props.mesh_index -= 1
        elif self.action == 'ADD':
            if context.active_object.O2MCD_props.disp_type == 'item_display' and context.preferences.addons[__package__].preferences.item_id:
                directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","models","item"])+os.sep
                json_import.create_model(self,context,directory,context.preferences.addons[__package__].preferences.item_id,"item",False)
                context.preferences.addons[__package__].preferences.item_id=""
            elif context.active_object.O2MCD_props.disp_type == 'block_display' and context.preferences.addons[__package__].preferences.block_id:
                directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","blockstates"])+os.sep
                json_import.create_model(self,context,directory,context.preferences.addons[__package__].preferences.block_id,"block",False)
                context.preferences.addons[__package__].preferences.block_id=""
            context.view_layer.objects.active.O2MCD_props.mesh_index=len(mesh_list)-1
            mesh_update(self,context)
        elif self.action == 'REMOVE':
            for modi in list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) , context.active_object.modifiers)):
                if match(f"{modi.node_group.name}(?:\.[0-9]+)?",mesh_list[self.index].mesh.name):
                    context.view_layer.objects.active.modifiers.remove(modi)
            mesh_list.remove(self.index)
            if len(mesh_list)==0:
                context.view_layer.objects.active.O2MCD_props.disp_id=""
                context.view_layer.objects.active.O2MCD_props.disp_type=""
                    
            else:
                context.view_layer.objects.active.O2MCD_props.mesh_index-=1
                
        return {"FINISHED"}
            
class OBJECTTOMCDISPLAY_MT_SetId(bpy.types.Menu):
    bl_label = "SetID"
    bl_description = bpy.app.translations.pgettext("Sorting Objects")
    def draw(self, context):
        layout = self.layout
        layout.operator("o2mcd.set_item", text="Item")
        layout.operator("o2mcd.set_block", text="block")
class OBJECTTOMCDISPLAY_OT_SetItem(bpy.types.Operator):  # アイテム検索
    bl_idname = "o2mcd.set_item"
    bl_label = ""
    bl_description= ""
    bl_property = "enum"
    enum: bpy.props.EnumProperty(name="Objects", description="", items=json_import.enum_item)

    def execute(self, context):
        directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","models","item"])+os.sep
        json_import.create_model(self,context,directory,self.enum,"item",False)
        mesh_update(self,context)
        if not context.view_layer.objects.active.O2MCD_command_list:
            bpy.ops.o2mcd.command_list_action(action='ADD')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_SetBlock(bpy.types.Operator):  # ブロック検索
    bl_idname = "o2mcd.set_block"
    bl_label = ""
    bl_description= ""
    bl_property = "enum"
    enum: bpy.props.EnumProperty(name="Objects", description="", items=json_import.enum_block)

    def execute(self, context):
        directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","blockstates"])+os.sep
        json_import.create_model(self,context,directory,self.enum,"block",False)
        mesh_update(self,context)
        if not context.view_layer.objects.active.O2MCD_command_list:
            bpy.ops.o2mcd.command_list_action(action='ADD')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
    
classes = (
    OBJECTTOMCDISPLAY_PT_ObjectProperties,
    OBJECTTOMCDISPLAY_PT_WindowObjectProperties,
    O2MCD_Obj_Props,
    O2MCD_ItemList,
    O2MCD_BlockList,
    O2MCD_CommandList,
    OBJECTTOMCDISPLAY_UL_CommandList,
    O2MCD_TagList,
    OBJECTTOMCDISPLAY_UL_TagList,
    OBJECTTOMCDISPLAY_OT_TagAction,
    OBJECTTOMCDISPLAY_MT_SetId,
    OBJECTTOMCDISPLAY_OT_SetItem,
    OBJECTTOMCDISPLAY_OT_SetBlock,
    O2MCD_MeshList,
    OBJECTTOMCDISPLAY_UL_MeshList,
    OBJECTTOMCDISPLAY_OT_MeshListAction
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Obj_Props)
    bpy.types.Scene.O2MCD_item_list = bpy.props.CollectionProperty(type=O2MCD_ItemList)
    bpy.types.Scene.O2MCD_block_list = bpy.props.CollectionProperty(type=O2MCD_BlockList)
    bpy.types.Object.O2MCD_command_list = bpy.props.CollectionProperty(type=O2MCD_CommandList)
    bpy.types.Object.O2MCD_tag_list = bpy.props.CollectionProperty(type=O2MCD_TagList)
    bpy.types.Object.O2MCD_mesh_list = bpy.props.CollectionProperty(type=O2MCD_MeshList)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)