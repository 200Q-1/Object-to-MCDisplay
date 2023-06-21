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
from . import json
from . import json_import
# 関数

def update(self, context):  # 更新処理
    if bpy.context.scene.O2MCD_props.enable:  # アドオンを有効
        if not list.chenge_panel in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(list.chenge_panel)
        bpy.types.VIEW3D_MT_make_links.remove(link.prop_link)
        bpy.types.TOPBAR_MT_file_import.remove(json_import.json_import)
        # bpy.types.VIEW3D_MT_mesh_add.remove(json.add_json)
        bpy.types.VIEW3D_MT_make_links.append(link.prop_link)
        bpy.types.TOPBAR_MT_file_import.append(json_import.json_import)
        # bpy.types.VIEW3D_MT_mesh_add.append(json.add_json)
        if "Input" not in bpy.data.texts:  # Inputが無ければ作成
            bpy.data.texts.new("Input")
            
        update_auto_reload(self,context)
                
    else:  # アドオンを無効
        if command.command_generate in bpy.app.handlers.frame_change_post :bpy.app.handlers.frame_change_post.remove(command.command_generate)
        if command.command_generate in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(command.command_generate)
        if list.chenge_panel in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(list.chenge_panel)
        bpy.types.VIEW3D_MT_make_links.remove(link.prop_link)
        bpy.types.VIEW3D_MT_mesh_add.remove(json.add_json)
        bpy.types.TOPBAR_MT_file_import.remove(json_import.json_import)
        
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


# クラス


class OBJECTTOMCDISPLAY_PT_MainPanel(bpy.types.Panel):  # 出力パネル
    bl_label = "O2MCD"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw_header(self, context):
        self.layout.prop(context.scene.O2MCD_props, "enable")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("render.o2mcd_reload")
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
        box.operator("render.o2mcd_export")
        layout.enabled = context.scene.O2MCD_props.enable
        # row= layout.row()
        # row.template_list("OBJECTTOMCDISPLAY_UL_ResourcePacks", "", context.scene, "O2MCD_rc_packs", context.scene.O2MCD_rc_pack, "index", rows=2,sort_lock=True)
        # col = row.column()
        # col1 = col.column()
        # if context.scene.O2MCD_rc_pack.index <= 1 or context.scene.O2MCD_rc_pack.index == len(context.scene.O2MCD_rc_packs)-1:
        #     col1.enabled= False
        # col1.operator(json.OBJECTTOMCDISPLAY_OT_ResourcePackMove.bl_idname, icon='TRIA_UP', text="").action = 'UP'
        # col2 = col.column()
        # if context.scene.O2MCD_rc_pack.index >= len(context.scene.O2MCD_rc_packs)-2 or context.scene.O2MCD_rc_pack.index == 0:
        #     col2.enabled= False
        # col2.operator(json.OBJECTTOMCDISPLAY_OT_ResourcePackMove.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'
        row = layout.row(align = True)
        row.alignment = "LEFT"
        row.prop(context.scene.O2MCD_props, "toggle_list", icon="DISCLOSURE_TRI_DOWN" if context.scene.O2MCD_props.toggle_list else "DISCLOSURE_TRI_RIGHT", emboss=False,text="Object List")
        row = layout.row()
        if context.scene.O2MCD_props.toggle_list:
            row.template_list("OBJECTTOMCDISPLAY_UL_ObjectList", "", context.scene, "O2MCD_object_list", context.scene.O2MCD_props, "obj_index", rows=4,sort_lock=True)
            col = row.column()
            if len(context.scene.O2MCD_object_list) <= 1:col.enabled = False
            col.operator("render.o2mcd_list_move", icon='TRIA_UP', text="").action = 'UP'
            col.operator("render.o2mcd_list_move", icon='TRIA_DOWN', text="").action = 'DOWN'
            col.separator()
            col.menu("OBJECTTOMCDISPLAY_MT_Sort", icon='SORTALPHA')
            col.operator("render.o2mcd_list_move", icon='UV_SYNC_SELECT', text="").action = 'REVERSE'


class OBJECTTOMCDISPLAY_OT_Reload(bpy.types.Operator):  # 更新ボタン
    bl_idname = "render.o2mcd_reload"
    bl_label = "Update"
    bl_description = "update command"

    def execute(self, context):
        command.command_generate(self, context)
        return {'FINISHED'}


class OBJECTTOMCDISPLAY_OT_Export(bpy.types.Operator):  # 出力ボタン
    bl_idname = "render.o2mcd_export"
    bl_label = "Export"
    bl_description = "Generate file in specified path"
    def execute(self, context):
        # テキストブロックの名前
        text_name = "Output"
        # シーンのフレーム数を取得
        frame_end = context.scene.frame_end
        # カレントフレームを保存
        current_frame = context.scene.frame_current

        if context.scene.O2MCD_props.output == "ANIMATION":
            # 出力先ディレクトリ
            anim_path = bpy.path.abspath(context.scene.O2MCD_props.anim_path)
            if os.path.isdir(anim_path):
                # フレームを1つずつ進めながら出力する
                for frame in range(1, frame_end+1):

                    # カレントフレームを設定
                    context.scene.frame_set(frame)
                    ofset = sub(".*?([0-9]*)$", "\\1",str(os.path.splitext(anim_path)[0]))
                    ext = str(os.path.splitext(anim_path)[1])
                    if ofset == "":
                        ofset = 1
                    if ext == "":
                        ext = ".mcfunction"
                    # 出力するファイル名を作成
                    output_file = sub("(.*?)([0-9]*)$", "\\1", str(os.path.splitext(anim_path)[0]))+str(int(ofset)-1+frame)+ext

                    # テキストブロックを取得
                    command.command_generate(self, context)
                    text = bpy.data.texts.get(text_name)

                    # 出力
                    if text:
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(text.as_string())
                # カレントフレームを元に戻す
                context.scene.frame_set(current_frame)
                self.report({'INFO'}, "File exported")
            else:
                self.report({'ERROR'},"File path not found")
        else:
            # 出力先ディレクトリ
            curr_path = bpy.path.abspath(context.scene.O2MCD_props.curr_path)
            if os.path.isdir(curr_path):
                ext = str(os.path.splitext(curr_path)[1])
                if ext == "":
                    ext = ".mcfunction"
                output_file = str(os.path.splitext(curr_path)[0])+ext
                # テキストブロックを取得
                command.command_generate(self, context)
                text = bpy.data.texts.get(text_name)
                # 出力
                if text:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(text.as_string())
                self.report({'INFO'}, "File exported")
            else:
                self.report({'ERROR'},"File path not found")
        return {'FINISHED'}


class O2MCD_Meny_Props(bpy.types.PropertyGroup):  # パネルのプロパティ
    rou: bpy.props.IntProperty(name="Round", default=3, max=16, min=1)
    anim_path: bpy.props.StringProperty(name="Path", subtype='FILE_PATH', default="")
    curr_path: bpy.props.StringProperty(name="Path", subtype='FILE_PATH', default="")
    auto_reload: bpy.props.BoolProperty(name="Auto Update", default=False, update=update_auto_reload,description="Update commands automatically")
    output: bpy.props.EnumProperty(name="Output", items=[('CURRENT', "Current Frame", ""), ('ANIMATION', "Animation", "")], default='CURRENT')
    enable: bpy.props.BoolProperty(name="", default=False, update=update)
    Enum: bpy.props.EnumProperty(name="Enum", items=object.enum_item, options={"ANIMATABLE"})
    list_index : bpy.props.IntProperty(name="Index", default=-1)
    obj_index:bpy.props.IntProperty(name="obj_index", default=0)
    toggle_list : bpy.props.BoolProperty(name="")

classes = (
    OBJECTTOMCDISPLAY_PT_MainPanel,
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