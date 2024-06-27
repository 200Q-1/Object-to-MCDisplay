# Copyright (c) 2023 200Q

import bpy
import os
from re import *
from math import *
from . import command
from . import object_list
import numpy as np
# 関数

def update(self, context):  # 更新処理
    if not sync_version in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(sync_version)
    if not object_list.chenge_panel in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(object_list.chenge_panel)
        
    if "O2MCD_input" not in bpy.data.texts:  # Inputが無ければ作成
        input=bpy.data.texts.new("O2MCD_input")
        input.from_string("コマンドリストが選択されていません。")
    if "O2MCD_output" not in bpy.data.texts:  # Outputが無ければ作成
        bpy.data.texts.new("O2MCD_output")
    update_auto_reload(self,context)
        
def update_auto_reload(self,context):
    if context.scene.O2MCD_props.auto_reload:  # 自動更新を有効
        if not command.command_generate in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(command.command_generate)
        if not command.command_generate in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(command.command_generate)
    else:  # 自動更新を無効
        if command.command_generate in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(command.command_generate)
        if command.command_generate in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(command.command_generate)
            
def near_version(prop,prop_list):
    enum_ver=[]
    cur_ver= np.zeros(3)
    version=[]
    for v in prop_list:
        v.split(".")
        ver= np.zeros(3)
        for i,s in enumerate(v.split(".")):
            ver[i]=int(s)
        enum_ver.append(ver)
    enum_ver=np.transpose(enum_ver)
    for i,s in enumerate(prop.split(".")):
        cur_ver[i]=int(s)

    for p,o in zip(enum_ver,cur_ver):
        idx = np.abs(np.asarray(p) - o).argmin()
        version.append(str(int(p[idx])))
    if version[-1]=="0":version.pop(-1)
    version=".".join(version)
    return version

def check_mcpp():
    addons = bpy.context.preferences.addons
    mcpp=[i for i in addons.keys() if match("MC_Particle_pro_[0-9]_[0-9]_[0-9]_[0-9]",i)]
    if mcpp:mcpp= mcpp[0]
    return mcpp
def sync_version(self,context):
    if check_mcpp() and bpy.context.preferences.addons[__package__].preferences.mcpp_sync and not bpy.context.preferences.addons[check_mcpp()].preferences.mc_version_manager == bpy.context.scene.O2MCD_props.mc_version:
        if bpy.context.scene.O2MCD_props.mc_version in [e.name for e in type(bpy.context.preferences.addons[check_mcpp()].preferences).bl_rna.properties["mc_version_manager"].enum_items]:
            bpy.context.scene.O2MCD_props.mc_version=bpy.context.preferences.addons[check_mcpp()].preferences.mc_version_manager
def update_version(self,context):
    if check_mcpp() and bpy.context.preferences.addons[__package__].preferences.mcpp_sync:
        bpy.context.preferences.addons[check_mcpp()].preferences.mc_version_manager=near_version(bpy.context.scene.O2MCD_props.mc_version,[e.name for e in type(bpy.context.preferences.addons[check_mcpp()].preferences).bl_rna.properties["mc_version_manager"].enum_items])

def panel_output(self,context):
    layout = self.layout
    if context.preferences.addons[__package__].preferences.jar_path:
        row=layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(context.scene.O2MCD_props,"mc_version")
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.alignment = "LEFT"
        row = layout.row()
        row.operator("o2mcd.reload")
        row.prop(context.scene.O2MCD_props, "auto_reload", toggle=True)
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(context.scene.O2MCD_props, "rou")
        layout.separator()
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.prop_tabs_enum(context.scene.O2MCD_props, "output")
        if context.scene.O2MCD_props.output == "ANIMATION":
            box.prop(context.scene.O2MCD_props, "anim_path")
        else:
            box.prop(context.scene.O2MCD_props, "curr_path")
        box.operator("o2mcd.export")
        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(context.scene.O2MCD_props, "toggle_rc_pack", icon="DISCLOSURE_TRI_DOWN" if context.scene.O2MCD_props.toggle_rc_pack else "DISCLOSURE_TRI_RIGHT", emboss=False,text=bpy.app.translations.pgettext_iface("Resource Pack"))
        col = layout.column()
        if context.scene.O2MCD_props.toggle_rc_pack:
            row= col.row()
            row.template_list("OBJECTTOMCDISPLAY_UL_ResourcePacks", "", context.scene, "O2MCD_rc_packs", context.scene, "O2MCD_rc_index", rows=2,sort_lock=True)
            col = row.column(align = True)
            col.operator("o2mcd.resource_pack_move", icon='TRIA_UP', text="").action = 'UP'
            col.operator("o2mcd.resource_pack_move", icon='TRIA_DOWN', text="").action = 'DOWN'
        
        row = layout.row(align = True)
        row.alignment = "LEFT"
        row.prop(context.scene.O2MCD_props, "toggle_list", icon="DISCLOSURE_TRI_DOWN" if context.scene.O2MCD_props.toggle_list else "DISCLOSURE_TRI_RIGHT", emboss=False,text=bpy.app.translations.pgettext_iface("Object List"))
        row = layout.row()
        if context.scene.O2MCD_props.toggle_list:
            row.template_list("OBJECTTOMCDISPLAY_UL_ObjectList", "", context.scene, "O2MCD_object_list", context.scene.O2MCD_props, "obj_index", rows=4,sort_lock=True)
            col = row.column(align = True)
            col.operator("o2mcd.list_move", icon='TRIA_UP', text="").action = 'UP'
            col.operator("o2mcd.list_move", icon='TRIA_DOWN', text="").action = 'DOWN'
            col.separator()
            col.menu("OBJECTTOMCDISPLAY_MT_Sort", icon='SORTALPHA')
            col.operator("o2mcd.list_reverse", icon='ARROW_LEFTRIGHT', text="")
    else:
        layout.label(text="Specify the .jar file from the add-on settings")
class OBJECTTOMCDISPLAY_PT_MainPanel(bpy.types.Panel):  # 出力パネル
    bl_label = "O2MCD"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        panel_output(self,context)


class OBJECTTOMCDISPLAY_PT_TextOutputPanel(bpy.types.Panel):  # テキストエディタパネル
    bl_label = "Object"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "O2MCD"
    bl_context = "text_edit"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.alignment = "LEFT"
        row = layout.row()
        row.operator("o2mcd.reload")
        row.prop(context.scene.O2MCD_props, "auto_reload", toggle=True)
        
        col=layout.column(align=True)
        col.separator()
        col.label(text="Object List")
        row= col.row()
        row.template_list("OBJECTTOMCDISPLAY_UL_ObjectList", "", context.scene, "O2MCD_object_list", context.scene.O2MCD_props, "obj_index", rows=4,sort_lock=True)
        col = row.column(align = True)
        col.operator("o2mcd.list_move", icon='TRIA_UP', text="").action = 'UP'
        col.operator("o2mcd.list_move", icon='TRIA_DOWN', text="").action = 'DOWN'
        col.separator()
        col.menu("OBJECTTOMCDISPLAY_MT_Sort", icon='SORTALPHA')
        col.operator("o2mcd.list_reverse", icon='ARROW_LEFTRIGHT', text="")
        
        col=layout.column(align=True)
        col.separator()
        if context.active_object:
            col.label(text="Command list")
            row= col.row()
            row.template_list("OBJECTTOMCDISPLAY_UL_CommandList", "", context.active_object.O2MCD_props, "command_list", context.active_object.O2MCD_props, "command_index", rows=2,sort_lock=True)
            col = row.column(align=True)
            col.operator("o2mcd.command_list_action", icon='ADD', text="").action = 'ADD'
            col.operator("o2mcd.command_list_action", icon='REMOVE', text="").action = 'REMOVE'
            col.separator()
            col.operator("o2mcd.command_list_action", icon='TRIA_UP', text="").action = 'UP'
            col.operator("o2mcd.command_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        
class OBJECTTOMCDISPLAY_PT_TextFuncPanel(bpy.types.Panel):  # テキストエディタパネル
    bl_label = "Function"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "O2MCD"
    bl_context = "text_edit"
    
    def draw(self, context):
        layout = self.layout
        col=layout.column()
        func=bpy.context.preferences.addons[__package__].preferences.cmd_func.replace("tags?","tag,tags")
        for action in [func.split(",")[i:i + 2] for i in range(0, len(func.split(",")), 2)]:
            row = col.row()
            row.operator("o2mcd.func_button", text=action[0]).action = action[0].upper()
            if len(action) == 2:row.operator("o2mcd.func_button", text=action[1]).action = action[1].upper()
def func_item(sefl,context):
    func=bpy.context.preferences.addons[__package__].preferences.cmd_func.replace("tags?","tag,tags")
    item=((f.upper(),f,"") for f in func.split(","))
    return item
class OBJECTTOMCDISPLAY_OT_FuncButton(bpy.types.Operator):
    bl_idname = "o2mcd.func_button"
    bl_label = "Function"
    action: bpy.props.EnumProperty(items=func_item)
    
    @classmethod 
    def description(self,context, prop):
        match prop.action:
            case "MATRIX":
                des="".join([bpy.app.translations.pgettext_tip("16 float values in transformation"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f"])
            case "LOC":
                des="".join([bpy.app.translations.pgettext_tip("Value of %s in transformation") % ("translation"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "0.0f,0.0f,0.0f"])
            case "SCALE":
                des="".join([bpy.app.translations.pgettext_tip("Value of %s in transformation") % ("scale"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "0.0f,0.0f,0.0f"])
            case "L_ROT":
                des="".join([bpy.app.translations.pgettext_tip("Value of %s in transformation") % ("left_rotation "),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "0.0f,0.0f,0.0f"])
            case "R_ROT":
                des="".join([bpy.app.translations.pgettext_tip("Value of %s in transformation") % ("right_rotation"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "0.0f,0.0f,0.0f"])
            case "POS":
                des="".join([bpy.app.translations.pgettext_tip("Relative %s of entities") % ("coordinates"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "^0.0 ^0.0 ^0.0"])
            case "ROT":
                des="".join([bpy.app.translations.pgettext_tip("Relative %s of entities")% ("rotation"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "^0.0 ^0.0"])
            case "ID":
                des="".join([bpy.app.translations.pgettext_tip("Item ID"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "apple"])
            case "TYPE":
                des="".join([bpy.app.translations.pgettext_tip("entity type"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "item_display"])
            case "PROP":
                des="".join([bpy.app.translations.pgettext_tip("Properties of the block (custom model data)"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "facing:\"east\",half:\"bottom\",open:\"false\""," | ",
                             "\"minecraft:custom_model_data\":0" if context.scene.O2MCD_props.mc_version == "1.20.5" else "CustomModelData:0"])
            case "TAG":
                des="".join([bpy.app.translations.pgettext_tip("Object tags"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "tag=A,tag=B"])
            case "TAGS":
                des="".join([bpy.app.translations.pgettext_tip("Object tags"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "\"A\",\"B\""])
            case "NAME":
                des="".join([bpy.app.translations.pgettext_tip("Object name"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "Cube.001"])
            case "NUM":
                des="".join([bpy.app.translations.pgettext_tip("Object index"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "0"])
            case "FRAME":
                des="".join([bpy.app.translations.pgettext_tip("Current Frame"),
                             " \n",bpy.app.translations.pgettext_tip("Example:"),
                             "0"])
            case "MATH":
                des="".join([bpy.app.translations.pgettext_tip("formula"),
                             " \n",bpy.app.translations.pgettext_tip("input"),bpy.app.translations.pgettext_tip("Example:"),
                             "/math[1+1] | /math[round(pi,2)] | /math[bpy.data.objects[0][\"prop\"]]"])
            case _:
                des=""
        return des
    
    def execute(self, context):
        Input=bpy.data.texts.get("O2MCD_input")
        Input.write("/"+self.action.lower())
        return {'FINISHED'}
            
    
class OBJECTTOMCDISPLAY_PT_TextTempPanel(bpy.types.Panel):  # テキストエディタパネル
    bl_label = "Template"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "O2MCD"
    bl_context = "text_edit"
    
    def draw(self, context):
        layout = self.layout
        sp= layout.split(align=True,factor=0.3)
        col= sp.column(align=True)
        col.label(text="Name:")
        col.prop(context.window_manager,"O2MCD_temp_name")
        sp= sp.split(align=True,factor=0.8)
        col= sp.column(align=True)
        col.label(text="Command:")
        col.prop(context.window_manager,"O2MCD_temp_cmd")
        col= sp.column(align=True)
        if not context.window_manager.O2MCD_temp_name or not context.window_manager.O2MCD_temp_cmd:
            col.enabled=False
        col.separator(factor=3.4)
        col.operator("o2mcd.temp_action", icon='ADD', text="").action = 'ADD'
        row= layout.row()
        row.template_list("OBJECTTOMCDISPLAY_UL_TemplateList", "", context.preferences.addons[__package__].preferences, "tmp_cmd", context.preferences.addons[__package__].preferences, "tmp_index", rows=4)
        col = row.column(align=True)
        col.prop(context.window_manager,"O2MCD_func_toggle",text="",icon='PREFERENCES',toggle=True)
        if context.window_manager.O2MCD_func_toggle:
            col.separator()
            col.operator("o2mcd.temp_action", icon='TRIA_UP', text="").action = 'UP'
            col.operator("o2mcd.temp_action", icon='TRIA_DOWN', text="").action = 'DOWN'
            col.separator()
            col.operator("o2mcd.temp_action", icon='X', text="").action = 'REMOVE'
        elif not context.preferences.use_preferences_save:
            col.operator("o2mcd.temp_action", icon='FILE_TICK', text="").action = 'SAVE'
class OBJECTTOMCDISPLAY_OT_Reload(bpy.types.Operator):  # 更新ボタン
    bl_idname = "o2mcd.reload"
    bl_label = bpy.app.translations.pgettext_iface("Update")
    bl_description = bpy.app.translations.pgettext_tip("Generate command in O2MCD_output")

    def execute(self, context):
        command.command_generate(self, context)
        return {'FINISHED'}


class OBJECTTOMCDISPLAY_OT_Export(bpy.types.Operator):  # 出力ボタン
    bl_idname = "o2mcd.export"
    bl_label = "Export"
    bl_description = bpy.app.translations.pgettext_tip("Generate file in specified path")
    def execute(self, context):
        text_name = "O2MCD_output"
        frame_end = context.scene.frame_end
        current_frame = context.scene.frame_current

        if context.scene.O2MCD_props.output == "ANIMATION":
            anim_path = bpy.path.abspath(context.scene.O2MCD_props.anim_path)
            dire= os.sep.join(anim_path.split(os.sep)[:-1])
            file= anim_path.split(os.sep)[-1]
            name= file.split(".")[0]
            offset = sub(".*?([0-9]*)$", "\\1",name)
            name= sub(offset, "",name)
            if len(file.split(".")) >=2: ext="."+file.split(".")[1]
            else:ext=""
            if not offset: offset = 0
            if not ext: ext = ".mcfunction"
            for frame in range(1, frame_end+1):
                context.scene.frame_set(frame)
                command.command_generate(self, context)
                output_file = os.path.join(dire,name+str(int(offset)-1+frame)+ext)
                text = bpy.data.texts.get(text_name)
                if text:
                    try:
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(text.as_string())
                    except:self.report({'ERROR'},bpy.app.translations.pgettext_tip("File path not found"))
            context.scene.frame_set(current_frame)
                
        else:
            curr_path = bpy.path.abspath(context.scene.O2MCD_props.curr_path)
            dire= os.sep.join(curr_path.split(os.sep)[:-1])
            file= curr_path.split(os.sep)[-1]
            name= file.split(".")[0]
            if len(file.split(".")) >=2 :ext="."+file.split(".")[1]
            else:ext=""
            if not ext: ext = ".mcfunction"
            command.command_generate(self, context)
            output_file = os.path.join(dire,name+ext)
            text = bpy.data.texts.get(text_name)
            if text:
                try:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(text.as_string())
                except:self.report({'ERROR'},bpy.app.translations.pgettext_tip("File path not found"))
        return {'FINISHED'}

def version_items(self,context):
    items=['1.19','1.20','1.20.5']
    if check_mcpp() and context.preferences.addons[__package__].preferences.mcpp_sync:
        items+=[e.name for e in type(bpy.context.preferences.addons[check_mcpp()].preferences).bl_rna.properties["mc_version_manager"].enum_items if not e.name in items]
    items.sort()
    items.reverse()
    items=(((i,i,"") for i in items))
    return items
class O2MCD_Meny_Props(bpy.types.PropertyGroup):  # パネルのプロパティ
    mc_version: bpy.props.EnumProperty(name="Version",description=bpy.app.translations.pgettext_tip("Minecraft version"), items=version_items,update=update_version)
    rou: bpy.props.IntProperty(name="Round",description=bpy.app.translations.pgettext_tip("number of decimal places to round"), default=3, max=16, min=1)
    curr_path: bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext_tip("single frame path"), subtype='FILE_PATH', default="")
    anim_path: bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext_tip("animation path"), subtype='FILE_PATH', default="")
    auto_reload: bpy.props.BoolProperty(name=bpy.app.translations.pgettext_tip("Auto Update"),description=bpy.app.translations.pgettext_tip("Ensure that an update is performed every time there is a change in the scene or a frame is moved"), default=False, update=update_auto_reload)
    output: bpy.props.EnumProperty(name="Output",description=bpy.app.translations.pgettext_tip("Output files to the specified path"), items=[('CURRENT', "Current Frame", ""), ('ANIMATION', "Animation", "")], default='CURRENT')
    obj_index:bpy.props.IntProperty(name="obj_index", default=0,update=object_list.select_object)
    toggle_list : bpy.props.BoolProperty(name=bpy.app.translations.pgettext_iface("Object List"),description=bpy.app.translations.pgettext_tip("List of objects for which the Display property is set."),default=False)
    toggle_rc_pack: bpy.props.BoolProperty(name=bpy.app.translations.pgettext_iface("Resource Pack"),description=bpy.app.translations.pgettext_tip("Add a resource pack to search for files specified as parent when importing a json model"),default=False)
    pre_obj: bpy.props.PointerProperty(name="pre_obj",type=bpy.types.Object)
classes = (
    OBJECTTOMCDISPLAY_PT_MainPanel,
    OBJECTTOMCDISPLAY_PT_TextOutputPanel,
    OBJECTTOMCDISPLAY_PT_TextFuncPanel,
    OBJECTTOMCDISPLAY_PT_TextTempPanel,
    OBJECTTOMCDISPLAY_OT_Reload,
    OBJECTTOMCDISPLAY_OT_Export,
    O2MCD_Meny_Props,
    OBJECTTOMCDISPLAY_OT_FuncButton
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Meny_Props)
    bpy.types.WindowManager.O2MCD_func_toggle = bpy.props.BoolProperty(default = False)
    bpy.types.WindowManager.O2MCD_temp_name= bpy.props.StringProperty(name="",default="")
    bpy.types.WindowManager.O2MCD_temp_cmd= bpy.props.StringProperty(name="",default="")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.O2MCD_props
    del bpy.types.WindowManager.O2MCD_temp_name
    del bpy.types.WindowManager.O2MCD_temp_cmd