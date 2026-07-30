# Copyright (c) 2023 200Q

import bpy
import os
from re import *
from math import *
import json
import ast
from . import json_import
from . import object_list
from . import output
# 関数
def set_list_type(self,context):
    if self.list_type == 'LIST' or self.list_type == "COMPOUND":
        for f in self.folders:
            f.prop_type = self.list_type
def add_item_data(mesh,name,prop_type,value):
    item_data = mesh.item_data.folders.add()
    item_data.name = name
    item_data.prop_type = prop_type
    if prop_type == 'COMPOUND' or prop_type == 'LIST':
        pass
    else:
        setattr(item_data,prop_type,value)
    return item_data
def data_to_dict(context,data,is_root=True,use_name=True,to_nbt=True):
    nbt = []
    rou=context.scene.O2MCD_props.rou
    for i in data.folders:
        if i["name"] == "": i["name"] = "\"\""
        if i.prop_type == 'COMPOUND':
            v="{{{}}}".format(data_to_dict(context,i,is_root=False,to_nbt=to_nbt))
        elif i.prop_type == 'LIST':
            v="[{}]".format(data_to_dict(context,i,is_root=False,use_name=False,to_nbt=to_nbt))
        elif i.prop_type == 'COLOR':
            if to_nbt:
                v="["+",".join([str(round(1.055 * (pow(c, (1.0 / 2.4))) - 0.055 if c > 0.0031308 else 12.92 * c,rou)) for c in i.COLOR[:3]])+"]"
            else:
                v=list(i.COLOR)
        else:
            v=getattr(i,i.prop_type)
            if type(v) == float:
                v=round(v,rou)
        if use_name:
            nbt.append("{}:{}".format(i["name"],v))
        else:
            nbt.append("{}".format(v))
    nbt = ",".join(nbt)
    if is_root:
        nbt = f"{{{nbt}}}"
    return nbt
def draw_recursive(layout, folders,is_root=False):
    if is_root: 
        folders=[folders]
    for i,folder in enumerate(folders):
        if folder.prop_type == 'COMPOUND':
            box = layout.box()
            box.use_property_split = True
            row=box.row()
            if not is_root:
                col=row.column()
                col.alignment= "LEFT"
                col.prop(folder,"is_open",emboss=False,text="",icon='DOWNARROW_HLT' if folder.is_open == True else 'RIGHTARROW')
            row.label(text=folder.name+":", icon='FILE_FOLDER')
            # row.operator("o2mcd.properties_edit_data",icon='ADD',text="").path=folder.path_from_id()
            if not is_root:
                pop=row.operator("o2mcd.properties_pop_data",emboss=False,icon='X',text="")
                pop.prop=folders.path_from_id()
                pop.index=i
            if is_root or folder.is_open:
                row=box.row()
                row.alignment= "RIGHT"
                row.operator("o2mcd.properties_edit_data",icon='ADD',text="Add").path=folder.path_from_id()
                # box.prop(folder,"name",text="", icon='FILE_FOLDER')
                draw_recursive(box, folder.folders)
                box.separator()
        elif folder.prop_type == 'LIST':
            box= layout.box()
            row=box.row()
            if not is_root:
                col=row.column()
                col.alignment= "LEFT"
                col.prop(folder,"is_open",emboss=False,text="",icon='DOWNARROW_HLT' if folder.is_open == True else 'RIGHTARROW')
            row.label(text=folder.name+":",icon='PRESET')
            pop=row.operator("o2mcd.properties_pop_data",emboss=False,icon='X',text="")
            pop.prop=folders.path_from_id()
            pop.index=i
            # row.operator("o2mcd.properties_edit_data",icon='ADD',text="").path=folder.path_from_id()
            if folder.is_open:
                box.prop(folder,"list_type")
                row=box.row()
                row.alignment= "RIGHT"
                row.operator("o2mcd.properties_edit_data",icon='ADD',text="Add").path= folder.path_from_id()
                col= box.column(align=True)
                # col.use_property_split = True
                if folder.list_type == 'LIST':
                    draw_recursive(col, folder.folders)
                elif folder.list_type == 'COMPOUND':
                    draw_recursive(col, folder.folders)
                else:
                    for li,f in enumerate(folder.folders):
                        row=col.row(align=True)
                        row.prop(f,folder.list_type,text=f.name+":")
                        pop=row.operator("o2mcd.properties_pop_data",emboss=False,icon='X',text="")
                        pop.is_list=True
                        pop.prop=folder.folders.path_from_id()
                        pop.index=li
                box.separator()
        elif folder.prop_type == 'BOOL':
            row=layout.row()
            row2=row.row()
            row2.alignment= "CENTER"
            row2.label(text=folder.name+":")
            row2.separator()
            row2.prop(folder, folder.prop_type, text="")
            pop=row.operator("o2mcd.properties_pop_data",emboss=False,icon='X',text="")
            pop.prop=folders.path_from_id()
            pop.index=i
        else:
            row=layout.row()
            row.prop(folder, folder.prop_type, text=folder.name+":")
            pop=row.operator("o2mcd.properties_pop_data",emboss=False,icon='X',text="")
            pop.prop=folders.path_from_id()
            pop.index=i
        
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
                if context.active_object.O2MCD_props.disp_type != "empty":
                    col=layout.column()
                    col.use_property_split = True
                    col.use_property_decorate = False
                    col.label(text="TYPE: "+context.active_object.O2MCD_props.disp_type)
                    col.label(text="ID: "+context.active_object.O2MCD_props.disp_id)
                    data_list=context.active_object.O2MCD_props.data_list
                    active_mesh = data_list[context.active_object.O2MCD_props.mesh_index]
                    row= col.row()
                    row.alert = active_mesh.durability_alert
                    row.label(text="max_durability: ")
                    row2= row.row()
                    row2.scale_x=0.5
                    row2.prop(active_mesh,"max_durability",text="")
                    box=col.box()
                    row=box.row()
                    row.alignment = "CENTER"
                    row.label(text="Index")
                    row.operator("o2mcd.list_move", icon='TRIA_LEFT', text="").action = 'UP'
                    row.label(text=str(context.object.O2MCD_props.number))
                    row.operator("o2mcd.list_move", icon='TRIA_RIGHT', text="").action = 'DOWN'
                    row=col.row()
                    row2=row.row()
                    row2.alignment = "LEFT"
                    row2.label(text="Mesh list")
                    row2.operator("o2mcd.copy_prop",icon='PASTEDOWN').action='MESH'
                    row=col.row()
                    row.template_list("OBJECTTOMCDISPLAY_UL_MeshList", "", context.active_object.O2MCD_props, "data_list", context.active_object.O2MCD_props, "mesh_index", rows=2)
                    col2 = row.column(align=True)
                    col2.operator("o2mcd.data_list_action", icon='TRIA_UP', text="").action = 'UP'
                    col2.operator("o2mcd.data_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
                    sp= col.split(align=True,factor=0.7)
                    if context.active_object.O2MCD_props.disp_type=="item_display":
                        sp.prop_search(context.preferences.addons[__package__].preferences, "item_id",context.preferences.addons[__package__].preferences, "item_list",text="")
                        sp2= sp.split(align=True,factor=1)
                        sp2.enabled=True if context.preferences.addons[__package__].preferences.item_id else False
                        sp2.operator("o2mcd.data_list_action", icon='ADD', text="Add").action = 'ADD'
                    elif context.active_object.O2MCD_props.disp_type=="block_display":
                        sp.prop_search(context.preferences.addons[__package__].preferences, "block_id",context.preferences.addons[__package__].preferences, "block_list",text="")
                        row= sp.row()
                        row.enabled=True if context.preferences.addons[__package__].preferences.block_id else False
                        row.operator("o2mcd.data_list_action", icon='ADD', text="Add").action = 'ADD'
                    # context.active_object.O2MCD_props, "data_list", context.active_object.O2MCD_props, "mesh_index"
                    current_mesh = context.active_object.O2MCD_props.data_list[context.active_object.O2MCD_props.mesh_index]
                    draw_recursive(col,current_mesh.item_data,True)
                    
                    if not (output.version_check(context, "1.21.4") and context.active_object.O2MCD_props.disp_type=="item_display"):
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
                row=row.row()
                row.alignment = "LEFT"
                row.label(text="Command list")
                row.operator("o2mcd.copy_prop",icon='PASTEDOWN').action='COMMAND'
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
    bl_idname = "OBJECTTOMCDISPLAY_PT_object_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    def draw(self, context):
        panel_object(self,context)
        
class OBJECTTOMCDISPLAY_PT_WindowObjectProperties(bpy.types.Panel):  # プロパティパネル
    bl_label = "O2MCD"
    bl_idname = "OBJECTTOMCDISPLAY_PT_window_object_properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        panel_object(self,context)

def mesh_items(self,context):
    items=()
    if self.number >=0:
        items=((i.mesh.name.upper(),i.mesh.name,"") for i in context.scene.O2MCD_object_list[self.number].obj.O2MCD_props.data_list)
    elif context.active_object and context.active_object.O2MCD_props.mesh_enum:
        items=((i.mesh.name.upper(),i.mesh.name,"") for i in context.active_object.O2MCD_props.data_list)
    return items

def comp_model(self,context,data,obj,item_data,components,enable=True):
    models = []
    if match("(minecraft:)?model",data["type"]):
        models.append((data["model"].split("/")[-1],enable))
        if "tints" in data:
            for t in data["tints"]:
                if match("(minecraft:)?dye",t["type"]):
                    if components.get("dyed_color"):
                        obj.O2MCD_props["color"]["dyed_color"]=components["dyed_color"]
                    else:
                        obj.O2MCD_props["color"]["dyed_color"]=json_import.decimal_to_rgba(t["default"])
                if match("(minecraft:)?map_color",t["type"]):
                    if components.get("map_color"):
                        obj.O2MCD_props["color"]["map_color"]=components["map_color"]
                    else:
                        obj.O2MCD_props["color"]["map_color"]=json_import.decimal_to_rgba(t["default"])
                if match("(minecraft:)?potion",t["type"]):
                    if components.get("potion_contents"):
                        try:
                            with open(bpy.path.abspath(os.path.dirname(__file__))+os.sep+"potion_list.json", 'r') as f:
                                potions = json.load(f)
                            with open(bpy.path.abspath(os.path.dirname(__file__))+os.sep+"effect_list.json", 'r') as f:
                                effects = json.load(f)
                        except:
                            potions=[]
                        if type(components["potion_contents"]) == str:
                            if components["potion_contents"] in potions:
                                obj.O2MCD_props["color"]["potion_contents"]=[*potions[components["potion_contents"]],1]
                            else:
                                obj.O2MCD_props["color"]["potion_contents"]=json_import.decimal_to_rgba(t["default"])
                        else:
                            if components.get("potion_contents",{}).get("custom_color"):
                                obj.O2MCD_props["color"]["potion_contents"]=components["potion_contents"]["custom_color"]
                            else:
                                colors=[]
                                if components.get("potion_contents",{}).get("potion") in potions:
                                    colors.append(potions[components["potion_contents"]["potion"]])
                                for p in components.get("potion_contents",{}).get("custom_effects",{}):
                                    colors.append(effects[p["id"]])
                                import numpy as np
                                colors=np.array(colors)
                                average_color = np.mean(colors, axis=0)
                                obj.O2MCD_props["color"]["potion_contents"]=json_import.decimal_to_rgba(average_color.tolist())
                    else:
                        obj.O2MCD_props["color"]["potion_contents"]=json_import.decimal_to_rgba(t["default"])
                if match("(minecraft:)?custom_model_data",t["type"]):
                    if len(components.get("custom_model_data",{}).get("colors",[]))-1 >= t["index"]:
                        obj.O2MCD_props["color"]["custom_model_data{}".format(t["index"])]=json_import.decimal_to_rgba(components["custom_model_data"]["colors"][t["index"]])
                    else:
                        obj.O2MCD_props["color"]["custom_model_data{}".format(t["index"])]=json_import.decimal_to_rgba(t["default"])
    elif match("(minecraft:)?special",data["type"]):
        name = ""
        if "texture" in data["model"]:
            name =".".join([data["model"]["type"].split(":")[-1],data["model"]["texture"].split(":")[-1]])
        elif "color" in data["model"]:
            name = ".".join([data["model"]["type"].split(":")[-1],data["model"]["color"]])
        elif data["base"]:
            name = data["base"].split("/")[-1]
        models.append((name,enable))
    elif match("(minecraft:)?composite",data["type"]):
        data["models"].reverse()
        for c in data["models"]:
            models += comp_model(self,context,c,obj,item_data,components,enable)
    elif match("(minecraft:)?condition",data["type"]):
        if match("(minecraft:)?using_item",data["property"]):
            models += comp_model(self,context,data["on_false"],obj,item_data,components)
        elif match("(minecraft:)?has_component",data["property"]):
            if (data["component"].split(":")[-1] in list(components.keys()) or "minecraft:"+data["component"].split(":")[-1]):
                models += comp_model(self,context,data["on_true"],obj,item_data,components)
                models += comp_model(self,context,data["on_false"],obj,item_data,components,False)
            else:
                models += comp_model(self,context,data["on_true"],obj,item_data,components,False)
                models += comp_model(self,context,data["on_false"],obj,item_data,components)
        elif match("(minecraft:)?custom_model_data",data["property"]):
            index = data.get("index",0)
            key=components.get("minecraft:custom_model_data",components.get("custom_model_data"))
            if key and "flags" in key and type(key["flags"]) == list and len(key["flags"])-1 >= index and key["flags"][index] == True:
                models += comp_model(self,context,data["on_true"],obj,item_data,components)
                models += comp_model(self,context,data["on_false"],obj,item_data,components,False)
            else:
                models += comp_model(self,context,data["on_true"],obj,item_data,components,False)
                models += comp_model(self,context,data["on_false"],obj,item_data,components)
        elif match("(minecraft:)?broken",data["property"]):
            key= components.get("minecraft:damage",components.get("damage"))
            if key and int(self.max_durability) - key <= 1:
                models += comp_model(self,context,data["on_true"],obj,item_data,components)
                models += comp_model(self,context,data["on_false"],obj,item_data,components,False)
            else:
                models += comp_model(self,context,data["on_true"],obj,item_data,components,False)
                models += comp_model(self,context,data["on_false"],obj,item_data,components)
    elif match("(minecraft:)?select",data["type"]):
        when = None
        if match("(minecraft:)?charge_type",data["property"]):
            key=components.get("minecraft:charged_projectiles",components.get("charged_projectiles"))
            if key:
                ids = [i["id"] for i in key]
                if match("(minecraft:)?firework_rocket",ids):
                    when = "rocket"
                else:
                    when = "arrow"
        if match("(minecraft:)?block_state",data["property"]):
            key=components.get("minecraft:block_state",components.get("block_state"))
            if key and data["block_state_property"] in key:
                when = key[data["block_state_property"]]
        if match("(minecraft:)?trim_material",data["property"]):
            key=components.get("minecraft:trim",components.get("trim"))
            dkey=data.get("minecraft:trim",data.get("trim"))
            if key and "material" in dkey:
                when = key["material"]
        # case "minecraft:display_context":
        # case "minecraft:local_time":
        # case "minecraft:context_entity_type":
        # case "minecraft:context_dimension":
        if match("(minecraft:)?custom_model_data",data["property"]):
            key=components.get("minecraft:custom_model_data",components.get("custom_model_data"))
            index = data.get("index",0)
            if key and type(key.get("strings")) == list and len(key["strings"])-1 >= index:
                when = key["strings"][index]
            for m in data["cases"]:
                if m["when"] == when:
                    enable=False
                    models += comp_model(self,context,m["model"],obj,item_data,components)
                else:
                    models += comp_model(self,context,m["model"],obj,item_data,components,False)
        if data.get("fallback"):
            models += comp_model(self,context,data["fallback"],obj,item_data,components,enable)
    elif match("(minecraft:)?range_dispatch",data["type"]):
        threshold = None
        scale=data.get("scale",1)
        if match("(minecraft:)?custom_model_data",data["property"]):
            key=components.get("minecraft:custom_model_data",components.get("custom_model_data"))
            index = data.get("index",0)
            if key and "floats" in key and type(key["floats"]) == list and len(key["floats"])-1 >= index:
                threshold = key["floats"][index]
        if match("(minecraft:)?count",data["property"]):
            threshold=1
            if "count" in item_data:
                threshold = item_data["count"]
            if data["normalize"] == True:
                threshold /= 64
        elif match("(minecraft:)?damage",data["property"]):
            key=components.get("minecraft:damage",components.get("damage"))
            if key:
                threshold = key
            if data["normalize"] == True:
                threshold /= int(self.max_durability)
        if threshold is not None:
            for i,m in enumerate(data["entries"]):
                # max_threshold=max([e["threshold"] for e in data["entries"]])
                if i != len(data["entries"])-1:
                    next=data["entries"][i+1]["threshold"]
                else:
                    next=data["entries"][i]["threshold"]
                if m["threshold"] <= threshold*scale and next >= threshold*scale:
                    enable=False
                    models += comp_model(self,context,m["model"],obj,item_data,components)
                else:
                    models += comp_model(self,context,m["model"],obj,item_data,components,False)
        if data.get("fallback"):
            models += comp_model(self,context,data["fallback"],obj,item_data,components,enable)
    return models
    
def change_model(self,context,obj):
    active_data = obj.O2MCD_props.data_list[obj.O2MCD_props.mesh_index]
    nbt=data_to_dict(context,active_data.item_data,to_nbt=False)
    model_id=active_data["model_id"]
    if nbt != active_data.data:
        active_data.data=nbt
        data = context.scene.O2MCD_props["models"][active_data["model_id"]]["model"]
        item_data={}
        components={}
        try:
            item_data = sub(r'(True(?=\s*,\s*))',r'true',active_data.data)
            item_data = sub(r'(false(?=\s*,\s*))',r'false',item_data)
            item_data = sub(r'(?<!")\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*:\s*)',r'"\1"',item_data)
            item_data = sub(r'((?:[0-9]+\.)?[0-9]+)[a-z]\b',"\\1",item_data)
            item_data = json.loads(item_data)
        except:
            item_data={}
        if item_data.get("components"):
            for k,v in item_data["components"].items():
                components[k.replace('minecraft:', '')]=v
        # if components.get("item_model") in [i.name for i in context.preferences.addons[__package__].preferences.item_list]:
        #     active_data["id"] = components.get("item_model")
        #     active_data["models_list"] = [c[1] for c in comp_model(active_data,context,data.to_dict(),obj,item_data,components)] 
        # elif item_data.get("id") in [i.name for i in context.preferences.addons[__package__].preferences.item_list]:
        #     active_data["id"] = item_data.get("id")
        #     active_data["models_list"] = [c[1] for c in comp_model(active_data,context,data.to_dict(),obj,item_data,components)]
        # else:
        #     raise
        if components.get("item_model") and len(components.get("item_model","").split(":")) !=2:
            components["item_model"]="minecraft:"+components.get("item_model","")
        item_data["id"]=item_data["id"].split(":")[-1]
        if components.get("item_model") in context.scene.O2MCD_props["model_ids"]:
            active_data["model_id"] = components.get("item_model")
            active_data["models_list"] = [c[1] for c in comp_model(active_data,context,data.to_dict(),obj,item_data,components)] 
        elif item_data.get("id") in [i.name for i in context.preferences.addons[__package__].preferences.item_list]:
            active_data["model_id"] = ":".join(["minecraft",item_data["id"]])
            active_data["id"] = item_data["id"]
            active_data["models_list"] = [c[1] for c in comp_model(active_data,context,data.to_dict(),obj,item_data,components)]
        # active_data["models_list"] = [c[1] for c in comp_model(active_data,context,data.to_dict(),obj)]
        active_data.data=data_to_dict(context,active_data.item_data)
        if active_data["model_id"] != model_id:
            m=active_data["model_id"].split(":")
            file = ["assets", m[0], "items",m[1]+".json"]
            json_import.create_model(self,context,file,active_data["model_id"],"item",False,active_data)
        for i,(m,a) in enumerate(zip(obj.O2MCD_props["models"].to_list(),active_data["models_list"].to_list())):
            obj.O2MCD_props["models"][i]=a
            


    
class O2MCD_LootFolder(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="item")
    prop_type: bpy.props.EnumProperty(items =(('COMPOUND', "Compound", "Edit a Compound value directly, for unsupported property types"),))
# メッシュリスト
class  O2MCD_MeshList(bpy.types.PropertyGroup):
    def max_durability_updata(self,context):
        try:
            if self.max_durability:
                int(self.max_durability)
            self.durability_alert = False
        except:
            self.durability_alert = True
    name : bpy.props.StringProperty(name="name", default="")
    id : bpy.props.StringProperty(name="id", default="")
    model_id:bpy.props.StringProperty(name="model_id",default="")
    mesh: bpy.props.PointerProperty(name="Mesh",type=bpy.types.Mesh)
    data : bpy.props.StringProperty(name="itemNBT",description="",default="")
    max_durability: bpy.props.StringProperty(name="max_durability", default="",update=max_durability_updata)
    durability_alert : bpy.props.BoolProperty(name="Enable",description="", default=False)
    item_data: bpy.props.PointerProperty(type=O2MCD_LootFolder)
    
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
    
class O2MCD_FolderProp(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Folder Name", default="Folder")
    prop_type: bpy.props.EnumProperty(items =(
        ('STRING', "String", "A string value"),
        ('INT', "Integer", "A single integer"),
        ('FLOAT', "Float", "A single floating-point value"),
        ('BYTE',"Byte", "A Byte value"),
        ('SHORT',"Short", "A Short value"),
        ('LONG',"Long", "A Long value"),
        ('DOUBLE',"Double", "A Double value"),
        ('BOOL', "Boolean", "A true or false value"),
        ('COLOR', "Color", "A color value"),
        ('COMPOUND', "Compound", "A Compound value"),
        ('LIST', "List", "A list value"),))
    STRING: bpy.props.StringProperty(name="String")
    INT: bpy.props.IntProperty(name="Integer")
    FLOAT: bpy.props.FloatProperty(name="Float")
    BYTE: bpy.props.IntProperty(name="Byte",min=-128,max=127)
    SHORT: bpy.props.IntProperty(name="Short",min=-32768,max=32767)
    LONG: bpy.props.IntProperty(name="Long")
    DOUBLE: bpy.props.FloatProperty(name="Double")
    BOOL: bpy.props.BoolProperty(name="Boolean")
    COLOR: bpy.props.FloatVectorProperty(name="Color",min=0,max=1,default=(1.0,1.0,1.0,1.0),size=4,subtype="COLOR")
    list_type: bpy.props.EnumProperty(items =(
        ('STRING', "String", "A string value"),
        ('INT', "Integer", "A single integer"),
        ('FLOAT', "Float", "A single floating-point value"),
        ('BYTE',"Byte", "A Byte value"),
        ('SHORT',"Short", "A Short value"),
        ('LONG',"Long", "A Long value"),
        ('DOUBLE',"Double", "A Double value"),
        ('BOOL', "Boolean", "A true or false value"),
        ('COLOR', "Color", "A color value"),
        ('COMPOUND', "Compound", "A Compound value"),
        ('LIST', "List", "A list value"),),update=set_list_type)
    is_open: bpy.props.BoolProperty(default=True)

# オブジェクトのプロパティ
class O2MCD_Obj_Props(bpy.types.PropertyGroup):
    number: bpy.props.IntProperty(name=bpy.app.translations.pgettext_iface("Object Number"), default=-1, min=-1)
    enable: bpy.props.BoolProperty(name="enable", default=True)
    command_index: bpy.props.IntProperty(name="cmmd_index", default=-1)
    pre_cmd: bpy.props.IntProperty(name="",default=-1)
    disp_id: bpy.props.StringProperty(name="id",description="",default="")
    disp_type: bpy.props.StringProperty(name="type",description="",default="")
    mesh_enum: bpy.props.EnumProperty(items=mesh_items)
    data_list: bpy.props.CollectionProperty(name="mesh",type=O2MCD_MeshList)
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
    
class OBJECTTOMCDISPLAY_OT_pop_data(bpy.types.Operator):
    bl_idname= "o2mcd.properties_pop_data"
    bl_label= "Pop"
    
    prop: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    is_list: bpy.props.BoolProperty(default=False)
    def execute(self,context):
        eval(f"context.view_layer.objects.active.{self.prop}").remove(self.index)
        if self.is_list:
            for i,f in enumerate(eval(f"context.view_layer.objects.active.{self.prop}")):
                f.name=str(i)
        return {'FINISHED'}
class  O2MCD_PropTypeList(bpy.types.PropertyGroup):
    def nbt_update(self,context):
        try:
            nbt= sub(r'(?<=")([a-zA-Z_][a-zA-Z0-9_]*)',r'\"\1\"',self.nbt_val)
            nbt= sub(r'(?<!")\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*:\s*)',r'"\1"',nbt)
            nbt= sub(r'(?=\s*:\s*)(?<!")\b([a-zA-Z_][a-zA-Z0-9_]*)\b',r'"\1"',nbt)
            nbt= sub(r'(\b(?:[0-9]+\.)?[0-9]+[bslfdBSLFD]\b)',r'"\1"',nbt)
            nbt= sub(r'\s*(?<=:)\s*"([a-zA-Z_][a-zA-Z0-9_]*)(?=")',r'\"\1\"',nbt)
            json.loads(nbt)
            self.nbt= nbt
            self.nbt_alert= False
        except:
            self.nbt_alert= True
    STRING: bpy.props.StringProperty(name="String")
    INT: bpy.props.IntProperty(name="Integer")
    FLOAT: bpy.props.FloatProperty(name="Float")
    BYTE: bpy.props.IntProperty(name="Byte",min=-128,max=127)
    SHORT: bpy.props.IntProperty(name="Short",min=-32768,max=32767)
    LONG: bpy.props.IntProperty(name="Long")
    DOUBLE: bpy.props.FloatProperty(name="Double")
    BOOL: bpy.props.BoolProperty(name="Boolean")
    COLOR: bpy.props.FloatVectorProperty(name="Color",min=0,max=1,default=(1.0,1.0,1.0,1.0),size=4,subtype="COLOR")
    nbt_val: bpy.props.StringProperty(default="{}",update=nbt_update)
    nbt_alert: bpy.props.BoolProperty(default=False)
    nbt: bpy.props.StringProperty()
class OBJECTTOMCDISPLAY_OT_edit_data(bpy.types.Operator):
    bl_idname= "o2mcd.properties_edit_data"
    bl_label= "Add"
    bl_options= {'REGISTER', 'INTERNAL'}
    prop_type: bpy.props.EnumProperty(items =(
        ('STRING', "String", "A string value"),
        ('INT', "Integer", "A single integer"),
        ('FLOAT', "Float", "A single floating-point value"),
        ('BYTE',"Byte", "A Byte value"),
        ('SHORT',"Short", "A Short value"),
        ('LONG',"Long", "A Long value"),
        ('DOUBLE',"Double", "A Double value"),
        ('BOOL', "Boolean", "A true or false value"),
        ('COLOR', "Color", "A color value"),
        ('COMPOUND', "Compound", "Edit a Compound value directly, for unsupported property types"),
        ('LIST', "List", "A list value"),),default='STRING')
    name: bpy.props.StringProperty()
    prop_list: bpy.props.CollectionProperty(type=O2MCD_PropTypeList)
    array_length: bpy.props.IntProperty(name="Array Length",default=2,min=1,max=32)
    path: bpy.props.StringProperty()
    list_type: bpy.props.EnumProperty(items =(
        ('STRING', "String", "A string value"),
        ('INT', "Integer", "A single integer"),
        ('FLOAT', "Float", "A single floating-point value"),
        ('BYTE',"Byte", "A Byte value"),
        ('SHORT',"Short", "A Short value"),
        ('LONG',"Long", "A Long value"),
        ('DOUBLE',"Double", "A Double value"),
        ('BOOL', "Boolean", "A true or false value"),
        ('COLOR', "Color", "A color value"),
        ('COMPOUND', "Compound", "A Compound value"),
        ('LIST', "List", "A list value"),))
    def check_type(self,value):
        result= 'STRING'
        if type(value) == str:
            if match(r'(?:[0-9]+\.)?[0-9]+[bB]',value):
                result= 'BYTE'
                value= int(value[:-1])
            elif match(r'(?:[0-9]+\.)?[0-9]+[sS]',value):
                result= 'SHORT'
                value= int(value[:-1])
            elif match(r'(?:[0-9]+\.)?[0-9]+[lL]',value):
                result= 'LONG'
                value= int(value[:-1])
            elif match(r'(?:[0-9]+\.)?[0-9]+[fF]',value):
                result= 'FLOAT'
                value= float(value[:-1])
            elif match(r'(?:[0-9]+\.)?[0-9]+[dD]',value):
                result= 'DOUBLE'
                value= float(value[:-1])
        elif type(value) == int:
            result= 'INT'
        elif type(value) == float:
            result= 'FLOAT'
        elif type(value) == bool:
            result= 'BOOL'
        elif type(value) == dict:
            result= 'COMPOUND'
        elif type(value) == list:
            result= 'LIST'
        return result,value
    def str_to_dict(self,folders,nbt):
        if type(nbt) == list:
            if len(nbt) >= 1:
                for i,n in enumerate(nbt):
                    list_type,n=self.check_type(n)
                    f=folders.add()
                    f.name=str(i)
                    setattr(f,list_type,n)
                    if i==0:
                        f.prop_type=list_type
            return
        for k,v in nbt.items():
            f=folders.add()
            f.name=k
            f.prop_type,v=self.check_type(v)
            if type(v) == dict:
                self.str_to_dict(f.folders,v)
            elif type(v) == list and len(v) >= 1:
                f.list_type,v[0]= self.check_type(v[0])
                l={}
                for i,lv in enumerate(v):
                    l[str(i)]= lv
                self.str_to_dict(f.folders,l)
            else:
                setattr(f,f.prop_type,v)
            
    def execute(self, context):
        obj = context.view_layer.objects.active
        path = eval(f"obj.{self.path}")
        if path.prop_type == 'LIST':
            lst= path.folders.add()
            lst.prop_type = path.list_type
            lst.name= str(len(path.folders)-1)
            return {'FINISHED'}
        path=path.folders
        if self.name in path:
            path = path[self.name]
        else:
            path = path.add()
            path.name = self.name
        path.prop_type = self.prop_type
        if self.prop_type == 'LIST':
            path.folders.clear()
            path.list_type= self.list_type
            for l in range(self.array_length):
                lst=path.folders.add()
                lst.prop_type = self.list_type
                lst.name=str(l)
                if self.list_type == 'LIST':
                    lst.folders.add().name="0"
                elif self.list_type == 'COMPOUND':
                    pass
                else:
                    setattr(lst,self.list_type,getattr(self.prop_list[l],self.list_type))
        elif self.prop_type == 'COMPOUND':
            if len(self.prop_list) >=1:
                if match("^\[.*\]$",self.prop_list[0].nbt):
                    path.prop_type="LIST"
                    nbt=ast.literal_eval(self.prop_list[0].nbt)
                    if len(nbt) >= 1:
                        for n in nbt:
                            path.list_type,n=self.check_type(nbt[0])
                else:
                    nbt=json.loads(self.prop_list[0].nbt)
            else:
                nbt={}
            self.str_to_dict(path.folders,nbt)
        else:
            setattr(path,self.prop_type,getattr(self.prop_list[0],self.prop_type))
        # change_model(self,context,obj,True)
        obj.update_tag()
        return {'FINISHED'}
    def invoke(self, context, _event):
        for prop_name in list(self.properties.keys()):
            if prop_name != "path":
                self.properties.property_unset(prop_name)
        obj = context.view_layer.objects.active
        path = eval(f"obj.{self.path}")
        if path.prop_type == 'LIST':
            return self.execute(context)
        for i in range(32):
            self.prop_list.add()
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)
        col.use_property_split = True
        col.prop(self, "name")
        col.prop(self, "prop_type")
        col.separator()
        if self.prop_type == 'LIST':
            prop= self.list_type
            col.prop(self,"list_type")
            col.prop(self,"array_length")
            col = col.column(align=True)
            col.separator()
            for i in range(self.array_length):
                if prop == 'LIST':
                    col.label(text="[]",icon='PRESET')
                elif prop == 'COMPOUND':
                    col=col.column()
                    col.alert= self.prop_list[i].nbt_alert
                    col.prop(self.prop_list[i],"nbt_val")
                else:
                    col.prop(self.prop_list[i],prop)
        elif self.prop_type == 'COMPOUND':
            col.alert= self.prop_list[0].nbt_alert
            col.prop(self.prop_list[0],"nbt_val",text="")
        else:
            col.prop(self.prop_list[0],self.prop_type)

class OBJECTTOMCDISPLAY_UL_MeshList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row(align=True)
        row.ui_units_x = 1
        row.prop(item,"name",text="",emboss=False)
        op = row.operator("o2mcd.data_list_action", icon='X', text="")
        op.action = 'REMOVE'
        op.index = index
    def execute(self, context):
        bpy.ops.wm.call_menu(name="OBJECTTOMCDISPLAY_MT_SetId")
        return {'FINISHED'}
    
    def execute(self, context):
        data_list=context.view_layer.objects.active.O2MCD_props.data_list
        mesh_index=context.view_layer.objects.active.O2MCD_props.mesh_index
        if self.action == 'DOWN' and mesh_index < len(data_list)-1:
            data_list.move(mesh_index, mesh_index+1)
            context.object.O2MCD_props.mesh_index += 1
        elif self.action == 'UP' and mesh_index > 0:
            data_list.move(mesh_index, mesh_index-1)
            context.object.O2MCD_props.mesh_index -= 1
        elif self.action == 'ADD':
            context.active_object.O2MCD_props.item_data_list.add()
        elif self.action == 'REMOVE':
            context.active_object.O2MCD_props.item_data_list.remove(context.active_object.O2MCD_props.item_data_index)
            if context.active_object.O2MCD_props.item_data_index >= 1:
                context.active_object.O2MCD_props.item_data_index -= 1
            
        return {"FINISHED"}

class OBJECTTOMCDISPLAY_OT_MeshListAction(bpy.types.Operator):
    bl_idname = "o2mcd.data_list_action"
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
        data_list=context.view_layer.objects.active.O2MCD_props.data_list
        mesh_index=context.view_layer.objects.active.O2MCD_props.mesh_index
        if self.action == 'DOWN' and mesh_index < len(data_list)-1:
            data_list.move(mesh_index, mesh_index+1)
            context.object.O2MCD_props.mesh_index += 1
        elif self.action == 'UP' and mesh_index > 0:
            data_list.move(mesh_index, mesh_index-1)
            context.object.O2MCD_props.mesh_index -= 1
        elif self.action == 'ADD':
            name=context.preferences.addons[__package__].preferences.item_id
            if context.active_object.O2MCD_props.disp_type == 'item_display' and context.preferences.addons[__package__].preferences.item_id:
                if output.version_check("1.21.4"):
                    file = ["assets", "minecraft", "items",name+".json"]
                else:
                    file = ["assets", "minecraft", "models", "item",name+".json"]
                json_import.create_model(self,context,file,name,"item",False)
                context.preferences.addons[__package__].preferences.item_id=""
            elif context.active_object.O2MCD_props.disp_type == 'block_display' and context.preferences.addons[__package__].preferences.block_id:
                file = ["assets","minecraft","blockstates",name+".json"]
                json_import.create_model(self,context,file,"block",False)
                context.preferences.addons[__package__].preferences.block_id=""
            context.view_layer.objects.active.O2MCD_props.mesh_enum=context.view_layer.objects.active.O2MCD_props.data_list[len(data_list)-1].mesh.name.upper()
        elif self.action == 'REMOVE':
            for modi in list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) , context.active_object.modifiers)):
                if match(f"{modi.node_group.name}(?:\.[0-9]+)?",data_list[self.index].mesh.name):
                    context.view_layer.objects.active.modifiers.remove(modi)
            data_list.remove(self.index)
            if self.action == 'REMOVE':
                if len(data_list)==0:
                    context.view_layer.objects.active.O2MCD_props.disp_id=""
                    context.view_layer.objects.active.O2MCD_props.disp_type=""
                else:
                    context.view_layer.objects.active.O2MCD_props.mesh_index-=1
                    context.view_layer.objects.active.O2MCD_props.mesh_enum=context.view_layer.objects.active.O2MCD_props.data_list[context.view_layer.objects.active.O2MCD_props.mesh_index].mesh.name.upper()
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
        name = self.enum
        types = self.action.lower()
        new = self.new
        if types == 'item':
            if output.version_check(context,"1.21.4"):
                file = ["assets", "minecraft", "items",name+".json"]
            else:
                file = ["assets", "minecraft", "models", "item",name+".json"]
        elif types == 'block':
            file = ["assets","minecraft","blockstates",name+".json"]
        json_import.create_model(self, context, file, ":".join(["minecraft", name]), types, new)
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
            am=[m.mesh for m in context.active_object.O2MCD_props.data_list]
            active_fcurve=[]
            if context.active_object.animation_data and context.active_object.animation_data.action:
                active_fcurve=list(filter(lambda a: fullmatch("O2MCD_props.mesh_enum|modifiers\[\"O2MCD(.[0-9]+)?\"\]\[\"Socket_[0-9]+\"\]",a.data_path),context.active_object.animation_data.action.fcurves))
            for o in list(filter(lambda s:s != context.active_object and s.type=='MESH',context.selected_objects)):
                o.O2MCD_props.disp_type=context.active_object.O2MCD_props.disp_type
                o.O2MCD_props.data_list.clear()
                if o.animation_data and o.animation_data.action:
                    target_fcurve=list(filter(lambda a: fullmatch("O2MCD_props.mesh_enum|modifiers\[\"O2MCD(.[0-9]+)?\"\]\[\"Socket_[0-9]+\"\]",a.data_path),o.animation_data.action.fcurves))
                    for f in target_fcurve:
                        o.animation_data.action.fcurves.remove(f)
                if am:
                    for m in am:
                        o.O2MCD_props.data_list.add().mesh=m
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
    O2MCD_LootFolder,
    O2MCD_MeshList,
    OBJECTTOMCDISPLAY_UL_MeshList,
    O2MCD_CommandList,
    OBJECTTOMCDISPLAY_UL_CommandList,
    O2MCD_TagList,
    OBJECTTOMCDISPLAY_PT_ObjectProperties,
    OBJECTTOMCDISPLAY_PT_WindowObjectProperties,
    O2MCD_FolderProp,
    O2MCD_Obj_Props,
    O2MCD_ItemList,
    O2MCD_BlockList,
    OBJECTTOMCDISPLAY_OT_TagAction,
    OBJECTTOMCDISPLAY_MT_SetId,
    OBJECTTOMCDISPLAY_OT_SetId,
    OBJECTTOMCDISPLAY_OT_AddEmpty,
    OBJECTTOMCDISPLAY_OT_MeshListAction,
    OBJECTTOMCDISPLAY_OT_CopyProp,
    O2MCD_PropTypeList,
    OBJECTTOMCDISPLAY_OT_pop_data,
    OBJECTTOMCDISPLAY_OT_edit_data,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    O2MCD_LootFolder.folders = bpy.props.CollectionProperty(type=O2MCD_FolderProp)
    O2MCD_FolderProp.folders = bpy.props.CollectionProperty(type=O2MCD_FolderProp)
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