# Copyright (c) 2023 200Q

import bpy
import os
from re import *
from math import *
from . import oblect_list
from . import json_import
# 関数
    
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

def mesh_update(self, context):
    context.view_layer.objects.active.data=context.active_object.O2MCD_mesh_list[context.active_object.O2MCD_props.mesh_index].mesh
    for modi in list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) , context.active_object.modifiers)):
        if modi.node_group.name == context.active_object.data.name:
            modi.show_viewport=True
        else:
            modi.show_viewport=False


enum_items = []
def enum_item(self, context):  # プロパティリスト
    global enum_items
    enum_items = []
    for i in range(len(context.scene.O2MCD_prop_list)):
        enum_items.append((str(i), str(i)+":"+context.scene.O2MCD_prop_list[i].name, ""))
    return enum_items

# クラス

class OBJECTTOMCDISPLAY_PT_DisplayProperties(bpy.types.Panel):  # プロパティパネル
    bl_label = "O2MCD"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"


    def draw(self, context):
        layout = self.layout
        if context.active_object.O2MCD_props.disp_id == "":
            layout.menu("OBJECTTOMCDISPLAY_MT_SetId")
        else:
            col=layout.column()
            col.label(text="TYPE: "+context.active_object.O2MCD_props.disp_type)
            
            row=layout.row()
            row.template_list("OBJECTTOMCDISPLAY_UL_MeshList", "", context.active_object, "O2MCD_mesh_list", context.active_object.O2MCD_props, "mesh_index", rows=2)
            col = row.column()
            col2=col.column()
            col2.operator("o2mcd.mesh_list_action", icon='REMOVE', text="").action = 'REMOVE'
            row = col.row()
            if context.active_object.O2MCD_props.mesh_index == 0 :
                row.enabled= False
            row.operator("o2mcd.mesh_list_action", icon='TRIA_UP', text="").action = 'UP'
            row = col.row()
            if context.active_object.O2MCD_props.mesh_index >= len(context.active_object.O2MCD_mesh_list)-1 :
                row.enabled= False
            row.operator("o2mcd.mesh_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
            sp= layout.split(align=True,factor=0.7)
            if context.active_object.O2MCD_props.disp_type=="ITEM":
                sp.prop_search(context.preferences.addons[__package__].preferences, "item_id",context.preferences.addons[__package__].preferences, "item_list",text="")
            elif context.active_object.O2MCD_props.disp_type=="BLOCK":
                sp.prop_search(context.preferences.addons[__package__].preferences, "block_id",context.preferences.addons[__package__].preferences, "block_list",text="")
            sp.operator("o2mcd.mesh_list_action", icon='ADD', text="追加").action = 'ADD'
            
            col=layout.column(align=True)
            col.use_property_split = True
            col.separator()
            box=col.box()
            box.label(text="プロパティ")
            try:
                modi= list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) and m.node_group.name == context.active_object.data.name , context.active_object.modifiers))[0]
                for i,n in enumerate(list(filter(lambda n : n.type=='MENU_SWITCH',modi.node_group.nodes))):
                    box.prop(context.active_object.modifiers[modi.name],f"[\"Socket_{i+2}\"]",text=n.name)
            except:pass
            
            row= layout.row()
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
            


            if context.object.O2MCD_props.prop_id >= 0:
                row=layout.row()
                if len(context.scene.O2MCD_object_list) <= 1:row.enabled = False
                row.operator("o2mcd.list_move", icon='TRIA_LEFT', text="").action = 'UP'
                row.alignment = "CENTER"
                row.label(text=str(context.object.O2MCD_props.number))
                row.operator("o2mcd.list_move", icon='TRIA_RIGHT', text="").action = 'DOWN'
                
            # if context.scene.O2MCD_prop_list:
            #     item = context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index]
            #     layout.prop(item, "Types", expand=True)
            #     if item.Types == "EXTRA":
            #         layout.prop(item, "type")
            #     if item.Types == "ITEM":
                row.prop_search(context.scene.O2MCD_prop_list[context.object.O2MCD_props.prop_id], "item_id",context.scene, "O2MCD_item_list",text="id")
                #     layout.prop(item, "tags")
                #     layout.prop(item,"CustomModelData")
                #     layout.prop(item, "ItemTag")
                # if item.Types == "BLOCK":
                #     layout.prop_search(context.scene.O2MCD_prop_list[context.object.O2MCD_props.prop_id], "block_id",context.scene, "O2MCD_block_list",text="id")
                #     layout.prop(item, "tags")
                #     layout.prop(item, "Properties",text="properties")
                # layout.prop(item, "ExtraNBT")

class OBJECTTOMCDISPLAY_PT_WindowDisplayProperties(bpy.types.Panel):  # プロパティパネル
    bl_label = "O2MCD"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        br = layout.row(align=True)
        if context.scene.O2MCD_prop_list:
            item = context.scene.O2MCD_prop_list[context.scene.O2MCD_props.list_index]
        br.operator("o2mcd.search_popup", text="", icon='DOWNARROW_HLT')
        if context.scene.O2MCD_props.list_index >= 0 and context.scene.O2MCD_prop_list:
            br.prop(item, "name", text="")
            br.operator("o2mcd.prop_add", icon='DUPLICATE',text="").action='DUP'
            br.operator("o2mcd.prop_unlink", icon='PANEL_CLOSE',text="")
            br.operator("o2mcd.prop_remove", icon='TRASH',text="")
        else:
            br.alignment = "EXPAND"
            br.operator("o2mcd.prop_add", icon='ADD').action='NEW'
        if context.scene.O2MCD_prop_list and context.object.O2MCD_props.prop_id >= 0:
            row=layout.row()
            if len(context.scene.O2MCD_object_list) <= 1:row.enabled = False
            row.operator("o2mcd.list_move", icon='TRIA_LEFT', text="").action = 'UP'
            row.alignment = "CENTER"
            row.label(text=str(context.object.O2MCD_props.number))
            row.operator("o2mcd.list_move", icon='TRIA_RIGHT', text="").action = 'DOWN'
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
            
class OBJECTTOMCDISPLAY_OT_PropAdd(bpy.types.Operator): # プロパティ追加
    bl_idname = "o2mcd.prop_add"
    bl_label = "Add"
    bl_description = bpy.app.translations.pgettext("Add property") 
    action: bpy.props.EnumProperty(items=(('NEW', "New", ""),('DUP', "dup", "")))
    
    def invoke(self,context,event):
        index = context.scene.O2MCD_props.list_index
        prop_list = context.scene.O2MCD_prop_list

        if self.action == 'NEW':
            context.scene.O2MCD_prop_list.add().name = "New"
            index = len(context.scene.O2MCD_prop_list)-1
            context.object.O2MCD_props.prop_id = index
            context.scene.O2MCD_props.list_index = context.object.O2MCD_props.prop_id
        if self.action == 'DUP':
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
        context.scene.O2MCD_props.list_index = context.object.O2MCD_props.prop_id
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_OT_PropUnlink(bpy.types.Operator): #プロパティリンク解除
    bl_idname = "o2mcd.prop_unlink"
    bl_label = "Unlink"
    bl_description = bpy.app.translations.pgettext("Unlink property")
    
    def invoke(self,context,event):
        context.object.O2MCD_props.prop_id = -1
        context.object.O2MCD_props.number =-1
        context.scene.O2MCD_props.list_index = context.object.O2MCD_props.prop_id
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_OT_PropRemove(bpy.types.Operator): #プロパティ削除
    bl_idname = "o2mcd.prop_remove"
    bl_label = "Remove"
    bl_description = bpy.app.translations.pgettext("Remove property")
    
    def invoke(self,context,event):
        prop_list = context.scene.O2MCD_prop_list
        index = context.scene.O2MCD_props.list_index

        prop_list.remove(index)
        index = min(max(0, index - 1), len(prop_list) - 1)
        for i in context.scene.O2MCD_object_list:
            if i.obj.O2MCD_props.prop_id > index:
                i.obj.O2MCD_props.prop_id = -1
                context.object.O2MCD_props.number =-1
        context.scene.O2MCD_props.list_index = context.object.O2MCD_props.prop_id
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_SearchPopup(bpy.types.Operator):  # id検索
    bl_idname = "o2mcd.search_popup"
    bl_label = ""
    bl_description= bpy.app.translations.pgettext("Browse Linked Properties")
    bl_property = "enum"
    enum: bpy.props.EnumProperty(name="Objects", description="", items=enum_item)

    def execute(self, context):
        context.object.O2MCD_props.prop_id = int(self.enum)
        context.scene.O2MCD_props.list_index = context.object.O2MCD_props.prop_id
        oblect_list.chenge_panel(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class O2MCD_Obj_Props(bpy.types.PropertyGroup):  # オブジェクトのプロパティ
    number: bpy.props.IntProperty(name=bpy.app.translations.pgettext("Object Number"), default=-1, min=-1)
    prop_id: bpy.props.IntProperty(name="prop_id", default=-1, min=-1)
    enable : bpy.props.BoolProperty(name="enable", default=True)
    command_index: bpy.props.IntProperty(name="cmd_index", default=0)
    pre_cmd: bpy.props.IntProperty(name="",default=0)
    disp_id: bpy.props.StringProperty(name="id",description="",default="")
    disp_type: bpy.props.StringProperty(name="type",description="",default="")
    mesh_index:bpy.props.IntProperty(name="mesh_index", default=0,update=mesh_update)

class O2MCD_ListItem(bpy.types.PropertyGroup):  # リストのプロパティ
    name: bpy.props.StringProperty(name="Name", default="",update=change_name)
    Types: bpy.props.EnumProperty(name="Object Type",description=bpy.app.translations.pgettext("Display entity type"), items=[('ITEM', "Item", ""), ('BLOCK', "Block", ""), ('EXTRA', "Extra", "")], options={"ANIMATABLE"},update=setid)
    tags: bpy.props.StringProperty(name="tags",description=bpy.app.translations.pgettext("Value assigned to /tag(s)"),default="")
    CustomModelData: bpy.props.IntProperty(name="CustomModelData",description=bpy.app.translations.pgettext("Value assigned to /model"),default=0, min=0)
    ItemTag: bpy.props.StringProperty(name="ItemTag",description=bpy.app.translations.pgettext("Value assigned to /item"),default="")
    Properties:bpy.props.StringProperty(name="Properties",description=bpy.app.translations.pgettext("Value assigned to /prop"),default="")
    ExtraNBT: bpy.props.StringProperty(name="ExtraNBT",description=bpy.app.translations.pgettext("Value assigned to /extra"),default="")
    type: bpy.props.StringProperty(name="type",description=bpy.app.translations.pgettext("Value assigned to /type"),default="")
    id: bpy.props.StringProperty(name="id",description=bpy.app.translations.pgettext("Value assigned to /id"),default="")
    item_id: bpy.props.StringProperty(name="id",description=bpy.app.translations.pgettext("Value assigned to /id"),default="",update=setid)
    block_id: bpy.props.StringProperty(name="id",description=bpy.app.translations.pgettext("Value assigned to /id"),default="",update=setid)

class  O2MCD_ItemList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_BlockList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")

# コマンドリスト
class  O2MCD_CommandList(bpy.types.PropertyGroup): 
    name: bpy.props.StringProperty(name="Name",description="",default="")
    command: bpy.props.StringProperty(name="Command",description="",default="")
    enable: bpy.props.BoolProperty(name="Enable",description="", default=True)

class OBJECTTOMCDISPLAY_UL_CommandList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row(align=True)
        row.alignment="LEFT"
        row.prop(item, "enable", text="")
        row.prop(item, "name", text="", emboss=True)
        col=row.column(align=True)
        col.prop(item, "command", text="", emboss=False)
        col.enabled= False
        
# メッシュリスト
class  O2MCD_MeshList(bpy.types.PropertyGroup):
    mesh: bpy.props.PointerProperty(name="Mesh",type=bpy.types.Mesh)
    
class OBJECTTOMCDISPLAY_UL_MeshList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row()
        row.label(text=item.mesh.name,icon='MESH_DATA')

    def execute(self, context):
        bpy.ops.wm.call_menu(name="OBJECTTOMCDISPLAY_MT_SetId")
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_MeshListAction(bpy.types.Operator): #移動
    bl_idname = "o2mcd.mesh_list_action"
    bl_label = ""
    bl_description = ""
    action: bpy.props.EnumProperty(items=(('UP', "up", ""),('DOWN', "down", ""),('ADD',"add",""),('REMOVE',"remove","")))

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
            if context.active_object.O2MCD_props.disp_type == 'ITEM':
                directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","models","item"])+os.sep
                json_import.create_model(self,context,directory,context.preferences.addons[__package__].preferences.item_id,"item",False)
                context.preferences.addons[__package__].preferences.item_id=""
            elif context.active_object.O2MCD_props.disp_type == 'BLOCK':
                directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","blockstates"])+os.sep
                json_import.create_model(self,context,directory,context.preferences.addons[__package__].preferences.block_id,"block",False)
                context.preferences.addons[__package__].preferences.block_id=""
            mesh_update(self,context)
        elif self.action == 'REMOVE':
            for modi in list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) , context.active_object.modifiers)):
                if modi.node_group.name == mesh_list[mesh_index].mesh.name:
                    context.view_layer.objects.active.modifiers.remove(modi)
            mesh_list.remove(mesh_index)
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
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
    
classes = (
    OBJECTTOMCDISPLAY_PT_DisplayProperties,
    OBJECTTOMCDISPLAY_PT_WindowDisplayProperties,
    OBJECTTOMCDISPLAY_OT_PropAdd,
    OBJECTTOMCDISPLAY_OT_PropUnlink,
    OBJECTTOMCDISPLAY_OT_PropRemove,
    OBJECTTOMCDISPLAY_OT_SearchPopup,
    O2MCD_Obj_Props,
    O2MCD_ListItem,
    O2MCD_ItemList,
    O2MCD_BlockList,
    O2MCD_CommandList,
    OBJECTTOMCDISPLAY_UL_CommandList,
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
    bpy.types.Scene.O2MCD_prop_list = bpy.props.CollectionProperty(type=O2MCD_ListItem)
    bpy.types.Scene.O2MCD_item_list = bpy.props.CollectionProperty(type=O2MCD_ItemList)
    bpy.types.Scene.O2MCD_block_list = bpy.props.CollectionProperty(type=O2MCD_BlockList)
    bpy.types.Object.O2MCD_command_list = bpy.props.CollectionProperty(type=O2MCD_CommandList)
    bpy.types.Object.O2MCD_mesh_list = bpy.props.CollectionProperty(type=O2MCD_MeshList)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)