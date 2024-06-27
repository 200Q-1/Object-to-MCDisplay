# Copyright (c) 2023 200Q

import bpy
import os
from re import *
from math import *
from . import json_import
from . import object_list
# 関数
    
    
def mesh_update(self, context):
    for o in bpy.context.scene.O2MCD_object_list:
        obj=o.obj
        if obj.type == 'MESH':
            if obj.O2MCD_props.mesh_enum.lower() in [n.name for n in bpy.data.meshes]:
                obj.data=bpy.data.meshes[obj.O2MCD_props.mesh_enum.lower()]
                obj.O2MCD_props.disp_id=sub('\.[0-9]+', "",obj.data.name.split("/")[-1])
                for modi in list(filter(lambda m: m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name), obj.modifiers)):
                    if match(f"{modi.node_group.name}(?:\.[0-9]+)?",obj.data.name):
                        modi.show_viewport=True
                    else:
                        modi.show_viewport=False

def panel_object(self,context):
    layout = self.layout
    if context.preferences.addons[__package__].preferences.jar_path:
        if context.active_object:
            if context.active_object and context.active_object.O2MCD_props.disp_id == "":
                if context.active_object.type == "MESH":
                    layout.menu("OBJECTTOMCDISPLAY_MT_SetId")
                else:
                    layout.operator("o2mcd.add_empty", text=bpy.app.translations.pgettext_iface("Set ID"))
            else:
                col=layout.column()
                col.label(text="TYPE: "+context.active_object.O2MCD_props.disp_type)
                col.label(text="ID: "+context.active_object.O2MCD_props.disp_id)
                box=col.box()
                row=box.row()
                row.alignment = "CENTER"
                row.label(text="Index")
                row.operator("o2mcd.list_move", icon='TRIA_LEFT', text="").action = 'UP'
                row.label(text=str(context.object.O2MCD_props.number))
                row.operator("o2mcd.list_move", icon='TRIA_RIGHT', text="").action = 'DOWN'
                if context.active_object.O2MCD_props.disp_type != "empty":
                        col=layout.column(align=True)
                        col.separator()
                        row=col.row()
                        row2=row.row()
                        row2.alignment = "LEFT"
                        row2.label(text="Mesh list")
                        row2.operator("o2mcd.copy_prop",icon='PASTEDOWN').action='MESH'
                        row3=row.row()
                        row3.alignment = "RIGHT"
                        row3.prop(context.window_manager,"O2MCD_mesh_toggle",text="",icon='PREFERENCES',toggle=True)
                        if not context.window_manager.O2MCD_mesh_toggle:
                            row=col.row()
                            row.use_property_split = True
                            row.prop(context.active_object.O2MCD_props,"mesh_enum",icon='MESH_DATA',text="")
                        else:
                            row=col.row()
                            row.template_list("OBJECTTOMCDISPLAY_UL_MeshList", "", context.active_object.O2MCD_props, "mesh_list", context.active_object.O2MCD_props, "mesh_index", rows=2)
                            
                            col2 = row.column(align=True)
                            col2.operator("o2mcd.mesh_list_action", icon='TRIA_UP', text="").action = 'UP'
                            col2.operator("o2mcd.mesh_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
                        
                        sp= col.split(align=True,factor=0.7)
                        if context.active_object.O2MCD_props.disp_type=="item_display":
                            sp.prop_search(context.preferences.addons[__package__].preferences, "item_id",context.preferences.addons[__package__].preferences, "item_list",text="")
                            sp2= sp.split(align=True,factor=1)
                            sp2.enabled=True if context.preferences.addons[__package__].preferences.item_id else False
                            sp2.operator("o2mcd.mesh_list_action", icon='ADD', text="Add").action = 'ADD'
                        elif context.active_object.O2MCD_props.disp_type=="block_display":
                            sp.prop_search(context.preferences.addons[__package__].preferences, "block_id",context.preferences.addons[__package__].preferences, "block_list",text="")
                            row= sp.row()
                            row.enabled=True if context.preferences.addons[__package__].preferences.block_id else False
                            row.operator("o2mcd.mesh_list_action", icon='ADD', text="Add").action = 'ADD'
                        
                        col=layout.column(align=True)
                        col.use_property_split = True
                        col.separator()
                        box=col.box()
                        box.label(text="Properties")
                        try:
                            modi= list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) and match(f"{m.node_group.name}(?:\.[0-9]+)?",context.active_object.data.name), context.active_object.modifiers))[0]
                            for i,n in enumerate(list(filter(lambda n : n.type=='MENU_SWITCH',modi.node_group.nodes))):
                                box.prop(context.active_object.modifiers[modi.name],f"[\"Socket_{i+2}\"]",text=n.name)
                        except:pass
                col=layout.column(align=True)
                col.separator()
                row=col.row()
                row2=row.row()
                row2.alignment = "LEFT"
                row2.label(text="Command list")
                row2.operator("o2mcd.copy_prop",icon='PASTEDOWN').action='COMMAND'
                row= col.row()
                row.template_list("OBJECTTOMCDISPLAY_UL_CommandList", "", context.active_object.O2MCD_props, "command_list", context.active_object.O2MCD_props, "command_index", rows=2,sort_lock=True)
                col = row.column(align=True)
                col.operator("o2mcd.command_list_action", icon='ADD', text="").action = 'ADD'
                col.operator("o2mcd.command_list_action", icon='REMOVE', text="").action = 'REMOVE'
                col.separator()
                col.operator("o2mcd.command_list_action", icon='TRIA_UP', text="").action = 'UP'
                col.operator("o2mcd.command_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
                
                box=layout.box()
                row = box.row(align = True)
                row2=row.row()
                row2.alignment = "LEFT"
                row2.label(text="Tags")
                row2.operator("o2mcd.copy_prop",icon='PASTEDOWN').action='TAG'
                row3=row.row()
                row3.alignment = "RIGHT"
                row3.operator("o2mcd.tag_action", icon='ADD', text="", emboss=False).action='ADD'
                col = box.column(align = True)
                for i,item in enumerate(context.active_object.O2MCD_props.tag_list):
                    row = col.row(align = True)
                    row.prop(item,"tag",text="")
                    ac=row.operator("o2mcd.tag_action", icon='PANEL_CLOSE', text="", emboss=False)
                    ac.action='REMOVE'
                    ac.index=i
    else:
        layout.label(text="Specify the .jar file from the add-on settings")
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

def mesh_items(self,context):
    items=()
    if self.number >=0:
        items=((i.mesh.name.upper(),i.mesh.name,"") for i in context.scene.O2MCD_object_list[self.number].obj.O2MCD_props.mesh_list)
    elif context.active_object and context.active_object.O2MCD_props.mesh_enum:
        items=((i.mesh.name.upper(),i.mesh.name,"") for i in context.active_object.O2MCD_props.mesh_list)
    return items

# メッシュリスト
class  O2MCD_MeshList(bpy.types.PropertyGroup):
    mesh: bpy.props.PointerProperty(name="Mesh",type=bpy.types.Mesh)
# コマンドリスト
def cmd_list_update(self,context):
    if context.active_object and  context.active_object.O2MCD_props.command_list and self == context.active_object.O2MCD_props.command_list[context.active_object.O2MCD_props.command_index]:
        bpy.data.texts["O2MCD_input"].from_string(self.command)
class  O2MCD_CommandList(bpy.types.PropertyGroup): 
    name: bpy.props.StringProperty(name="Name",description="",default="")
    command: bpy.props.StringProperty(name="Command",description="",default="",update=cmd_list_update)
    enable: bpy.props.BoolProperty(name="Enable",description="", default=True)
class  O2MCD_TagList(bpy.types.PropertyGroup): 
    tag: bpy.props.StringProperty(name="tag",description="",default="")


class O2MCD_Obj_Props(bpy.types.PropertyGroup):  # オブジェクトのプロパティ
    number: bpy.props.IntProperty(name=bpy.app.translations.pgettext_iface("Object Number"), default=-1, min=-1)
    enable : bpy.props.BoolProperty(name="enable", default=True)
    command_index: bpy.props.IntProperty(name="cmd_index", default=-1)
    pre_cmd: bpy.props.IntProperty(name="",default=-1)
    disp_id: bpy.props.StringProperty(name="id",description="",default="")
    disp_type: bpy.props.StringProperty(name="type",description="",default="")
    mesh_enum: bpy.props.EnumProperty(items=mesh_items,update=mesh_update)
    mesh_list: bpy.props.CollectionProperty(name="mesh",type=O2MCD_MeshList)
    command_list : bpy.props.CollectionProperty(type=O2MCD_CommandList)
    mesh_index:bpy.props.IntProperty(name="mesh_index", default=0)
    tag_list : bpy.props.CollectionProperty(type=O2MCD_TagList)


class  O2MCD_ItemList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_BlockList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")


class OBJECTTOMCDISPLAY_UL_CommandList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "enable", text="",toggle=True, emboss=False,icon='HIDE_OFF' if item.enable else "HIDE_ON")
        sp = row.split(align=True,factor=0.35)
        sp.prop(item, "name", text="", emboss=False)
        sp.prop(item, "command", text="", emboss=True)
        
class OBJECTTOMCDISPLAY_OT_TagAction(bpy.types.Operator):
    bl_idname = "o2mcd.tag_action"
    bl_label = ""
    bl_description = ""
    action: bpy.props.EnumProperty(items=(('ADD',"add",""),('REMOVE',"remove","")))
    index: bpy.props.IntProperty(name="Index")

    @classmethod 
    def description(self, context, prop):
        match prop.action:
            case 'ADD':
                des = bpy.app.translations.pgettext_tip("Add tags")
            case 'REMOVE':
                des = bpy.app.translations.pgettext_tip("Remove tags")
        return des

    def execute(self, context):
        match self.action:
            case 'ADD':
                context.object.O2MCD_props.tag_list.add()
            case 'REMOVE':
                context.object.O2MCD_props.tag_list.remove(self.index)
        return {'FINISHED'}
    
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
    action: bpy.props.EnumProperty(items=(('UP', "up", ""),('DOWN', "down", ""),('ADD',"add",""),('REMOVE',"remove","")))
    index : bpy.props.IntProperty(default=0)
    
    @classmethod 
    def description(self, context, prop):
        match prop.action:
            case 'UP' | 'DOWN':
                des = bpy.app.translations.pgettext_tip("Move the mesh up or down")
            case 'ADD':
                des = bpy.app.translations.pgettext_tip("Add mesh")
            case 'REMOVE':
                des = bpy.app.translations.pgettext_tip("Remove mesh")
        return des
    
    def invoke(self, context, event):
        mesh_list=context.view_layer.objects.active.O2MCD_props.mesh_list
        mesh_index=context.view_layer.objects.active.O2MCD_props.mesh_index
        if self.action == 'DOWN' and mesh_index < len(mesh_list)-1:
            mesh_list.move(mesh_index, mesh_index+1)
            context.object.O2MCD_props.mesh_index += 1
        elif self.action == 'UP' and mesh_index > 0:
            mesh_list.move(mesh_index, mesh_index-1)
            context.object.O2MCD_props.mesh_index -= 1
        elif self.action == 'ADD':
            if context.active_object.O2MCD_props.disp_type == 'item_display' and context.preferences.addons[__package__].preferences.item_id:
                directory=context.preferences.addons[__package__].preferences.jar_path+os.sep+os.sep.join(["assets","minecraft","models","item"])+os.sep
                json_import.create_model(self,context,directory,context.preferences.addons[__package__].preferences.item_id,"item",False)
                context.preferences.addons[__package__].preferences.item_id=""
            elif context.active_object.O2MCD_props.disp_type == 'block_display' and context.preferences.addons[__package__].preferences.block_id:
                directory=context.preferences.addons[__package__].preferences.jar_path+os.sep+os.sep.join(["assets","minecraft","blockstates"])+os.sep
                json_import.create_model(self,context,directory,context.preferences.addons[__package__].preferences.block_id,"block",False)
                context.preferences.addons[__package__].preferences.block_id=""
            context.view_layer.objects.active.O2MCD_props.mesh_enum=context.view_layer.objects.active.O2MCD_props.mesh_list[len(mesh_list)-1].mesh.name.upper()
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
    bl_label = bpy.app.translations.pgettext_iface("Set ID")
    bl_description = bpy.app.translations.pgettext_tip("Set ID and to object list")
    def draw(self, context):
        layout = self.layout
        i=layout.operator("o2mcd.set_id", text="Item")
        i.action='ITEM'
        i.new=False
        b=layout.operator("o2mcd.set_id", text="Block")
        b.action='BLOCK'
        b.new=False
class OBJECTTOMCDISPLAY_OT_SetId(bpy.types.Operator):
    bl_idname = "o2mcd.set_id"
    bl_label = ""
    bl_description = bpy.app.translations.pgettext_tip("Set item ID and add to object list")
    bl_property = "enum"
    enum: bpy.props.EnumProperty(name="Objects", description="", items=json_import.enum_item)
    action: bpy.props.EnumProperty(name="action",items=(('BLOCK',"block",""),('ITEM',"item","")))
    new: bpy.props.BoolProperty(name="new")

    def execute(self, context):
        if self.action == 'ITEM':
            path=["assets", "minecraft", "models", "item"]
        elif self.action == 'BLOCK':
            path=["assets","minecraft","blockstates"]
        directory = os.sep.join([context.preferences.addons[__package__].preferences.jar_path]+path)+os.sep
        json_import.create_model(self, context, directory, self.enum, self.action.lower(), self.new)
        if not context.view_layer.objects.active.O2MCD_props.command_list:
            bpy.ops.o2mcd.command_list_action(action='ADD')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
    

class OBJECTTOMCDISPLAY_OT_AddEmpty(bpy.types.Operator):
    bl_idname = "o2mcd.add_empty"
    bl_label = ""
    bl_description = bpy.app.translations.pgettext_tip("Set ID and to object list")
    new: bpy.props.BoolProperty(name="new")
    
    def execute(self, context):
        if self.new:
            empty = bpy.data.objects.new("empty", None)
            bpy.context.collection.objects.link(empty)
            empty.empty_display_size = 0.5
            empty.empty_display_type = 'CUBE'
            context.view_layer.objects.active = empty
        else:
            empty=context.view_layer.objects.active
        empty.O2MCD_props.disp_type = "empty"
        empty.O2MCD_props.disp_id = "empty"
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        if not context.view_layer.objects.active.O2MCD_props.command_list:
            bpy.ops.o2mcd.command_list_action(action='ADD')
        return {'FINISHED'}


class OBJECTTOMCDISPLAY_OT_CopyProp(bpy.types.Operator):
    bl_idname = "o2mcd.copy_prop"
    bl_label = ""
    action: bpy.props.EnumProperty(items=(('MESH',"mesh",""),('COMMAND',"command",""),('TAG',"tag","")))
    
    @classmethod 
    def description(self,context, prop):
        match prop.action:
            case "MESH":
                des=bpy.app.translations.pgettext_tip("Copy mesh list to selected object")
            case "COMMAND":
                des=bpy.app.translations.pgettext_tip("Copy command list to selected object")
            case "TAG":
                des=bpy.app.translations.pgettext_tip("Copy tag list to selected object")
        return des
    
    def execute(self, context):
        if self.action=='MESH':
            am=[m.mesh for m in context.active_object.O2MCD_props.mesh_list]
            active_fcurve=[]
            if context.active_object.animation_data and context.active_object.animation_data.action:
                active_fcurve=list(filter(lambda a: fullmatch("O2MCD_props.mesh_enum|modifiers\[\"O2MCD(.[0-9]+)?\"\]\[\"Socket_[0-9]+\"\]",a.data_path),context.active_object.animation_data.action.fcurves))
            for o in list(filter(lambda s:s != context.active_object and s.type=='MESH',context.selected_objects)):
                o.O2MCD_props.disp_type=context.active_object.O2MCD_props.disp_type
                o.O2MCD_props.mesh_list.clear()
                if o.animation_data and o.animation_data.action:
                    target_fcurve=list(filter(lambda a: fullmatch("O2MCD_props.mesh_enum|modifiers\[\"O2MCD(.[0-9]+)?\"\]\[\"Socket_[0-9]+\"\]",a.data_path),o.animation_data.action.fcurves))
                    for f in target_fcurve:
                        o.animation_data.action.fcurves.remove(f)
                if am:
                    for m in am:
                        o.O2MCD_props.mesh_list.add().mesh=m
                        if not o.O2MCD_props.command_list:
                            o.O2MCD_props.command_list.add().name="cmd1"
                o.O2MCD_props.mesh_enum=context.active_object.O2MCD_props.mesh_enum
                o.O2MCD_props.disp_id=context.active_object.O2MCD_props.mesh_enum
                for modi in list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) , context.active_object.modifiers)):
                    if not modi.node_group.name in [m.node_group.name for m in o.modifiers if m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name)]:
                        new_modi=o.modifiers.new("O2MCD", "NODES")
                        node_tree=bpy.data.node_groups[modi.node_group.name]
                        new_modi.node_group=node_tree
                    else:
                        modi_name=[(m.name,m.node_group.name) for m in o.modifiers if m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) and m.node_group.name == modi.node_group.name][0]
                        new_modi=o.modifiers[modi_name[0]]
                        node_tree=bpy.data.node_groups[modi_name[1]]
                    for m in range(len(list(filter(lambda x: x.type=='MENU_SWITCH', [n for n in node_tree.nodes])))):
                        new_modi["Socket_"+str(m+2)]=modi["Socket_"+str(m+2)]
                for active_action in active_fcurve:
                    if not o.animation_data:
                        o.animation_data_create()
                    if not o.animation_data.action:
                        n=o.name
                        o.animation_data.action = bpy.data.actions.new(name=f"{n}Action")
                    action=o.animation_data.action
                    target_fcurve = action.fcurves.new(data_path=active_action.data_path,index=active_action.array_index)
                    for keyframe in active_action.keyframe_points:
                        kfp = target_fcurve.keyframe_points.insert(frame=keyframe.co[0], value=keyframe.co[1])
                        kfp.handle_left = keyframe.handle_left
                        kfp.handle_right = keyframe.handle_right
                        kfp.interpolation = keyframe.interpolation
                        kfp.easing = keyframe.easing
                        kfp.back = keyframe.back
                        kfp.amplitude = keyframe.amplitude
                        kfp.period = keyframe.period
            object_list.chenge_panel(self,context)
        elif self.action=='COMMAND':
            ac=[(m.name,m.command,m.enable) for m in context.active_object.O2MCD_props.command_list]
            active_fcurve=[]
            if context.active_object.animation_data and context.active_object.animation_data.action:
                active_fcurve=list(filter(lambda a:fullmatch("O2MCD_props.command_list\[[0-9]+\].enable",a.data_path),context.active_object.animation_data.action.fcurves))
            for o in list(filter(lambda s:s != context.active_object,context.selected_objects)):
                o.O2MCD_props.command_list.clear()
                if o.animation_data and o.animation_data.action:
                    target_fcurve=list(filter(lambda a:fullmatch("O2MCD_props.command_list\[[0-9]+\].enable",a.data_path),o.animation_data.action.fcurves))
                    for f in target_fcurve:
                        o.animation_data.action.fcurves.remove(f)
                if ac:
                    for c in ac:
                        cmd=o.O2MCD_props.command_list.add()
                        cmd.name=c[0]
                        cmd.command=c[1]
                        cmd.enable=c[2]
                for active_action in active_fcurve:
                    if not o.animation_data:
                        o.animation_data_create()
                    if not o.animation_data.action:
                        n=o.name
                        o.animation_data.action = bpy.data.actions.new(name=f"{n}Action")
                    action=o.animation_data.action
                    target_fcurve = action.fcurves.new(data_path=active_action.data_path,index=active_action.array_index)
                    for keyframe in active_action.keyframe_points:
                        kfp = target_fcurve.keyframe_points.insert(frame=keyframe.co[0], value=keyframe.co[1])
                        kfp.handle_left = keyframe.handle_left
                        kfp.handle_right = keyframe.handle_right
                        kfp.interpolation = keyframe.interpolation
                        kfp.easing = keyframe.easing
                        kfp.back = keyframe.back
                        kfp.amplitude = keyframe.amplitude
                        kfp.period = keyframe.period
                        
        elif self.action=='TAG':
            at=[m.tag for m in context.active_object.O2MCD_props.tag_list]
            for o in list(filter(lambda s:s != context.active_object,context.selected_objects)):
                o.O2MCD_props.tag_list.clear()
                if at:
                    for t in at:
                        o.O2MCD_props.tag_list.add().tag=t
        return {'FINISHED'}

classes = (
    O2MCD_MeshList,
    OBJECTTOMCDISPLAY_UL_MeshList,
    O2MCD_CommandList,
    OBJECTTOMCDISPLAY_UL_CommandList,
    O2MCD_TagList,
    OBJECTTOMCDISPLAY_PT_ObjectProperties,
    OBJECTTOMCDISPLAY_PT_WindowObjectProperties,
    O2MCD_Obj_Props,
    O2MCD_ItemList,
    O2MCD_BlockList,
    OBJECTTOMCDISPLAY_OT_TagAction,
    OBJECTTOMCDISPLAY_MT_SetId,
    OBJECTTOMCDISPLAY_OT_SetId,
    OBJECTTOMCDISPLAY_OT_AddEmpty,
    OBJECTTOMCDISPLAY_OT_MeshListAction,
    OBJECTTOMCDISPLAY_OT_CopyProp
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Obj_Props)
    bpy.types.Scene.O2MCD_item_list = bpy.props.CollectionProperty(type=O2MCD_ItemList)
    bpy.types.Scene.O2MCD_block_list = bpy.props.CollectionProperty(type=O2MCD_BlockList)
    bpy.types.WindowManager.O2MCD_mesh_toggle = bpy.props.BoolProperty(default = False)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.O2MCD_props
    del bpy.types.Scene.O2MCD_item_list
    del bpy.types.Scene.O2MCD_block_list
    del bpy.types.WindowManager.O2MCD_mesh_toggle