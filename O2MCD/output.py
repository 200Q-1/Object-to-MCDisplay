# Copyright (c) 2023 200Q

import bpy
import os
from re import *
from math import *
from bpy.app.handlers import persistent
from . import link
from . import command
from . import object
from . import list
from . import json_import
# 関数

def set_default(self,context):
    if not bpy.context.blend_data.filepath:
        context.scene.O2MCD_props.mc_version= context.preferences.addons[__package__].preferences.mc_version
        context.scene.O2MCD_props.rou= context.preferences.addons[__package__].preferences.rou
        context.scene.O2MCD_props.anim_path= context.preferences.addons[__package__].preferences.anim_path
        context.scene.O2MCD_props.curr_path= context.preferences.addons[__package__].preferences.curr_path
        context.scene.O2MCD_props.auto_reload= context.preferences.addons[__package__].preferences.auto_reload
        context.scene.O2MCD_props.enable= context.preferences.addons[__package__].preferences.enable
        context.scene.O2MCD_props.mcpp_sync= context.preferences.addons[__package__].preferences.mcpp_sync
        if not context.scene.O2MCD_rc_packs: context.scene.O2MCD_rc_packs.add()
        if context.preferences.addons[__package__].preferences.rc_packs:
            for p in context.preferences.addons[__package__].preferences.rc_packs.split(","):
                context.scene.O2MCD_rc_packs.add().path= p
def update(self, context):  # 更新処理
    if bpy.context.scene.O2MCD_props.enable:  # アドオンを有効
        if not sync_version in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(sync_version)
        if not list.chenge_panel in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(list.chenge_panel)
        bpy.types.VIEW3D_MT_make_links.remove(link.prop_link)
        bpy.types.VIEW3D_MT_make_links.append(link.prop_link)
            
        if "Input" not in bpy.data.texts:  # Inputが無ければ作成
            input=bpy.data.texts.new("Input")
            com= [i.command for i in context.preferences.addons[__package__].preferences.inputs]
            input.write("\n".join(com))
            
        update_auto_reload(self,context)
                
    else:  # アドオンを無効
        if command.command_generate in bpy.app.handlers.frame_change_post :bpy.app.handlers.frame_change_post.remove(command.command_generate)
        if command.command_generate in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(command.command_generate)
        if list.chenge_panel in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(list.chenge_panel)
        bpy.types.VIEW3D_MT_make_links.remove(link.prop_link)
        
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
            
def check_mcpp():
    addons = bpy.context.preferences.addons
    mcpp=[i for i in addons.keys() if match("MC_Particle_pro_[0-9]_[0-9]_[0-9]_[0-9]",i)]
    if mcpp:mcpp= mcpp[0]
    return mcpp
def sync_version(self,context):
    if check_mcpp() and context.scene.O2MCD_props.mcpp_sync and not bpy.context.preferences.addons[check_mcpp()].preferences.mc_version_manager == bpy.context.scene.O2MCD_props.mc_version:
        bpy.context.scene.O2MCD_props.mc_version = bpy.context.preferences.addons[check_mcpp()].preferences.mc_version_manager
        
def update_version(self,context):
    if check_mcpp() and context.scene.O2MCD_props.mcpp_sync:
        context.preferences.addons[check_mcpp()].preferences.mc_version_manager=self.mc_version
# クラス


class OBJECTTOMCDISPLAY_PT_MainPanel(bpy.types.Panel):  # 出力パネル
    bl_label = "O2MCD"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw_header(self, context):
        self.layout.prop(context.scene.O2MCD_props, "enable",text="")

    def draw(self, context):
        layout = self.layout
        layout.enabled = context.scene.O2MCD_props.enable
        row=layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(context.scene.O2MCD_props,"mc_version")
        addons = bpy.context.preferences.addons
        mcpp=[i for i in addons.keys() if match("MC_Particle_pro_[0-9]_[0-9]_[0-9]_[0-9]",i)]
        if mcpp:row.prop(context.scene.O2MCD_props,"mcpp_sync")
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
        row = col.row()
        row.prop(context.scene.O2MCD_props, "output", expand=True)
        box = col.box()
        if context.scene.O2MCD_props.output == "ANIMATION":
            box.prop(context.scene.O2MCD_props, "anim_path")
        else:
            box.prop(context.scene.O2MCD_props, "curr_path")
        box.operator("o2mcd.export")
        
        row = layout.row(align = True)
        row.alignment = "LEFT"
        row.prop(context.scene.O2MCD_props, "toggle_rc_pack", icon="DISCLOSURE_TRI_DOWN" if context.scene.O2MCD_props.toggle_rc_pack else "DISCLOSURE_TRI_RIGHT", emboss=False,text=bpy.app.translations.pgettext("Parent Referrer"))
        col = layout.column()
        if context.scene.O2MCD_props.toggle_rc_pack:
            row= col.row()
            row.template_list("OBJECTTOMCDISPLAY_UL_ResourcePacks", "", context.scene, "O2MCD_rc_packs", context.scene, "O2MCD_rc_index", rows=2,sort_lock=True)
            col = row.column()
            row = col.row()
            if context.scene.O2MCD_rc_index <= 1 :
                row.enabled= False
            row.operator(json_import.OBJECTTOMCDISPLAY_OT_ResourcePackMove.bl_idname, icon='TRIA_UP', text="").action = 'UP'
            row = col.row()
            if context.scene.O2MCD_rc_index >= len(context.scene.O2MCD_rc_packs)-1 or context.scene.O2MCD_rc_index == 0:
                row.enabled= False
            row.operator(json_import.OBJECTTOMCDISPLAY_OT_ResourcePackMove.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'
        
        row = layout.row(align = True)
        row.alignment = "LEFT"
        row.prop(context.scene.O2MCD_props, "toggle_list", icon="DISCLOSURE_TRI_DOWN" if context.scene.O2MCD_props.toggle_list else "DISCLOSURE_TRI_RIGHT", emboss=False,text=bpy.app.translations.pgettext("Object List"))
        row = layout.row()
        if context.scene.O2MCD_props.toggle_list:
            row.template_list("OBJECTTOMCDISPLAY_UL_ObjectList", "", context.scene, "O2MCD_object_list", context.scene.O2MCD_props, "obj_index", rows=4,sort_lock=True)
            col = row.column()
            if len(context.scene.O2MCD_object_list) <= 1:col.enabled = False
            col.operator("o2mcd.list_move", icon='TRIA_UP', text="").action = 'UP'
            col.operator("o2mcd.list_move", icon='TRIA_DOWN', text="").action = 'DOWN'
            col.separator()
            col.menu("OBJECTTOMCDISPLAY_MT_Sort", icon='SORTALPHA')
            col.operator("o2mcd.list_reverse", icon='UV_SYNC_SELECT', text="")

class OBJECTTOMCDISPLAY_PT_TextPanel(bpy.types.Panel):  # テキストエディタパネル
    bl_label = "O2MCD"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "O2MCD"
    bl_context = "output"

    def draw_header(self, context):
        self.layout.prop(context.scene.O2MCD_props, "enable",text="")

    def draw(self, context):
        layout = self.layout
        layout.enabled = context.scene.O2MCD_props.enable
        col=layout.column(align=True)
        col.alignment = "RIGHT"
        col.prop(context.scene.O2MCD_props,"mc_version")
        addons = bpy.context.preferences.addons
        mcpp=[i for i in addons.keys() if match("MC_Particle_pro_[0-9]_[0-9]_[0-9]_[0-9]",i)]
        if mcpp:col.prop(context.scene.O2MCD_props,"mcpp_sync")
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.alignment = "LEFT"
        col = layout.column()
        col.operator("o2mcd.reload")
        col.prop(context.scene.O2MCD_props, "auto_reload", toggle=True)
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(context.scene.O2MCD_props, "rou")
        layout.separator()
        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene.O2MCD_props, "output", expand=True)
        box = col.box()
        if context.scene.O2MCD_props.output == "ANIMATION":
            box.prop(context.scene.O2MCD_props, "anim_path")
        else:
            box.prop(context.scene.O2MCD_props, "curr_path")
        box.operator("o2mcd.export")
        
        row = layout.row(align = True)
        row.alignment = "LEFT"
        row.prop(context.scene.O2MCD_props, "toggle_rc_pack", icon="DISCLOSURE_TRI_DOWN" if context.scene.O2MCD_props.toggle_rc_pack else "DISCLOSURE_TRI_RIGHT", emboss=False,text=bpy.app.translations.pgettext("Parent Referrer"))
        col = layout.column()
        if context.scene.O2MCD_props.toggle_rc_pack:
            row= col.row()
            row.template_list("OBJECTTOMCDISPLAY_UL_ResourcePacks", "", context.scene, "O2MCD_rc_packs", context.scene, "O2MCD_rc_index", rows=2,sort_lock=True)
            col = row.column()
            row = col.row()
            if context.scene.O2MCD_rc_index <= 1 :
                row.enabled= False
            row.operator(json_import.OBJECTTOMCDISPLAY_OT_ResourcePackMove.bl_idname, icon='TRIA_UP', text="").action = 'UP'
            row = col.row()
            if context.scene.O2MCD_rc_index >= len(context.scene.O2MCD_rc_packs)-1 or context.scene.O2MCD_rc_index == 0:
                row.enabled= False
            row.operator(json_import.OBJECTTOMCDISPLAY_OT_ResourcePackMove.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'
        
        row = layout.row(align = True)
        row.alignment = "LEFT"
        row.prop(context.scene.O2MCD_props, "toggle_list", icon="DISCLOSURE_TRI_DOWN" if context.scene.O2MCD_props.toggle_list else "DISCLOSURE_TRI_RIGHT", emboss=False,text=bpy.app.translations.pgettext("Object List"))
        row = layout.row()
        if context.scene.O2MCD_props.toggle_list:
            row.template_list("OBJECTTOMCDISPLAY_UL_ObjectList", "", context.scene, "O2MCD_object_list", context.scene.O2MCD_props, "obj_index", rows=4,sort_lock=True)
            col = row.column()
            if len(context.scene.O2MCD_object_list) <= 1:col.enabled = False
            col.operator("o2mcd.list_move", icon='TRIA_UP', text="").action = 'UP'
            col.operator("o2mcd.list_move", icon='TRIA_DOWN', text="").action = 'DOWN'
            col.separator()
            col.menu("OBJECTTOMCDISPLAY_MT_Sort", icon='SORTALPHA')
            col.operator("o2mcd.list_move", icon='UV_SYNC_SELECT', text="").action = 'REVERSE'


class OBJECTTOMCDISPLAY_OT_Reload(bpy.types.Operator):  # 更新ボタン
    bl_idname = "o2mcd.reload"
    bl_label = bpy.app.translations.pgettext("Update")
    bl_description = bpy.app.translations.pgettext("Get information about the object and generate commands in the Output according to the Input")

    def execute(self, context):
        command.command_generate(self, context)
        return {'FINISHED'}


class OBJECTTOMCDISPLAY_OT_Export(bpy.types.Operator):  # 出力ボタン
    bl_idname = "o2mcd.export"
    bl_label = "Export"
    bl_description = bpy.app.translations.pgettext("Generate file in specified path")
    def execute(self, context):
        text_name = "Output"
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
                    except:self.report({'ERROR'},bpy.app.translations.pgettext("File path not found"))
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
                except:self.report({'ERROR'},bpy.app.translations.pgettext("File path not found"))
        return {'FINISHED'}

class O2MCD_Meny_Props(bpy.types.PropertyGroup):  # パネルのプロパティ
    mc_version: bpy.props.EnumProperty(name="Version",description=bpy.app.translations.pgettext("Minecraft version"), items=[('1.19', "1.19", ""), ('1.20', "1.20", "")], default='1.20',update=update_version)
    rou: bpy.props.IntProperty(name="Round",description=bpy.app.translations.pgettext("number of decimal places to round"), default=3, max=16, min=1)
    curr_path: bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext("single frame path"), subtype='FILE_PATH', default="")
    anim_path: bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext("animation path"), subtype='FILE_PATH', default="")
    auto_reload: bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Auto Update"),description=bpy.app.translations.pgettext("Ensure that an update is performed every time there is a change in the scene or a frame is moved"), default=False, update=update_auto_reload)
    output: bpy.props.EnumProperty(name="Output",description=bpy.app.translations.pgettext("Output files to the specified path"), items=[('CURRENT', "Current Frame", ""), ('ANIMATION', "Animation", "")], default='CURRENT')
    enable: bpy.props.BoolProperty(name="Enable",description=bpy.app.translations.pgettext("Enable O2MCD"), default=False, update=update)
    Enum: bpy.props.EnumProperty(name="Enum", items=object.enum_item, options={"ANIMATABLE"})
    list_index : bpy.props.IntProperty(name="Index", default=-1)
    obj_index:bpy.props.IntProperty(name="obj_index", default=0,update=list.select_object)
    mcpp_sync: bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Synchronised with MCPP"),description=bpy.app.translations.pgettext("Synchronise version settings with MCPP"),default=False)
    toggle_list : bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Object List"),description=bpy.app.translations.pgettext("List of objects for which the Display property is set."),default=False)
    toggle_rc_pack: bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Parent Referrer"),description=bpy.app.translations.pgettext("Add a resource pack to search for files specified as parent when importing a json model"),default=False)
    
classes = (
    OBJECTTOMCDISPLAY_PT_MainPanel,
    OBJECTTOMCDISPLAY_PT_TextPanel,
    OBJECTTOMCDISPLAY_OT_Reload,
    OBJECTTOMCDISPLAY_OT_Export,
    O2MCD_Meny_Props,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Meny_Props)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if list.chenge_panel in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(list.chenge_panel)