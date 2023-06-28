# Copyright (c) 2023 200Q
import os
import zipfile
import tempfile
from re import *
bl_info = {
    "name": "Object to MCDisplay",
    "author": "200Q",
    "version": (0, 2, 1),
    "blender": (3, 4, 1),
    "location": "Output Properties",
    "support": "COMMUNITY",
    "description": "オブジェクトのトランスフォームをMinecraftのDisplayエンティティのtransformationを設定するコマンドに変換します。",
    "warning": "",
    "doc_url": "https://github.com/200Q-1/Object-to-MCDisplay",
    "tracker_url": "",
    "category": "Object"
}

O2MCD_translation_dict = {
    "ja_JP": {
        ("*", "Display Properties"): "Displayプロパティ",
        ("*", "Update"): "更新",
        ("*", "Auto Update"): "自動更新",
        ("*", "update commands"): "コマンドを更新",
        ("*", "Update commands automatically"): "コマンドを自動で更新",
        ("*", "Object Number"): "番号",
        ("*", "Generate file in specified path"): "指定したパスにファイルを生成",
        ("*", "Rearrange the order of objects"): "オブジェクトの順番を入れ替える",
        ("*", "Sorting Objects"): "オブジェクトを並び替える",
        ("*", "Sort by name"): "名前順",
        ("*", "Sort by creation"): "作成順",
        ("*", "Sort by random"): "ランダム順",
        ("Operator", "Sort by DataPath"): "データパス順",
        ("Operator", "Link display properties"): "ディスプレイプロパティをリンク",
        ("Operator", "Transfers data from the active object to the selected object"): "アクティブオブジェクトから選択オブジェクトにデータを転送します",
        ("*", "Browse Linked Properties"): "リンクするプロパティを観覧",
        ("*", "File exported"): "ファイルを書き出しました",
        ("*", "File path not found"): "ファイルパスが見つかりません",
        ("*", "Objects have been reordered"): "オブジェクトを並び替えました",
        ("*", "No data available"): "データがありません",
        ("Operator", "import json"): "jsonをインポート",
        ("*", "%s was not found."): "%sが見つかりませんでした。",
        ("*", "There are no elements. It could be a block entity.\nFILE: %s"): "elementsがありません。ブロックエンティティの可能性があります。\nFILE:%s",
        ("*", "Texture not found.\nFILE:%s\nTEXTUR:%s"): "テクスチャが見つかりません。\nFILE:%s\nTEXTUR:%s",
        ("*", "Texture path is not set.\nFILE:%s"): "テクスチャのパスが設定されていません。\nFILE:%s",
        ("*", "move resource pack"): "リソースパックを移動",
        ("Operator", "open resource pack"): "リソースパックを開く",
        ("*", "Open a resource pack.\nFolders, zips and jars are supported."): "リソースパックを開きます。\nフォルダ、zip、jarに対応しています",
        ("*", "Import json file as object."): "json ファイルをオブジェクトとしてインポートします",
        ("*", "Parent Referrer:"): "ペアレントの参照元：",
    }
}
if "bpy" in locals():
    import imp
    imp.reload(object)
    imp.reload(output)
    imp.reload(command)
    imp.reload(link)
    imp.reload(list)
    imp.reload(json_import)
else:
    from . import object
    from . import output
    from . import command
    from . import link
    from . import list
    from . import json_import
import bpy
from bpy.app.handlers import persistent

class O2MCD_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    index : bpy.props.IntProperty(name="index",default=0)
    rc_packs : bpy.props.StringProperty(default="")
    mcpp_sync : bpy.props.BoolProperty(default=False)
    
    enable: bpy.props.BoolProperty(default=False)
    mc_version: bpy.props.EnumProperty(name="Version", items=[('1.19', "1.19", ""), ('1.20', "1.20", "")], default='1.20')
    rou: bpy.props.IntProperty(name="Round", default=3, max=16, min=1)
    anim_path: bpy.props.StringProperty(name="Path", subtype='FILE_PATH', default="")
    curr_path: bpy.props.StringProperty(name="Path", subtype='FILE_PATH', default="")
    auto_reload: bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Auto Update"), default=False,description=bpy.app.translations.pgettext("Update commands automatically"))
    enable: bpy.props.BoolProperty(name="", default=False)
    mcpp_sync: bpy.props.BoolProperty(default=False)
    
    def draw(self, context):
        layout = self.layout
        layout.label(icon='DOT',text="新規プロジェクトを開いた際に適応される、デフォルトの値を設定することができます。")
        row=layout.row()
        row.alignment = "RIGHT"
        row.label(text="有効化")
        row.prop(self,"enable",text="")
        row=layout.row()
        row.alignment = "RIGHT"
        row.label(text=bpy.app.translations.pgettext("Update commands automatically"))
        row.prop(self, "auto_reload",text="")
        if output.check_mcpp():
            row=layout.row()
            row.alignment = "RIGHT"
            row.label(text="MCPPとバージョン設定を同期")
            row.prop(self,"mcpp_sync",text="")
        col= layout.column()
        col.use_property_split = True
        col.prop(self,"mc_version")
        col.prop(self, "rou")
        col.use_property_split = True
        col.prop(self, "curr_path",text="シングルフレームのパス")
        col.prop(self, "anim_path",text="アニメーションのパス")
        
        col = layout.column()
        col.label(text=bpy.app.translations.pgettext("  ペアレントの参照元："))
        row= col.row()
        row.template_list("OBJECTTOMCDISPLAY_UL_ResourcePacks", "", bpy.context.scene, "O2MCD_df_packs", self, "index", rows=2,sort_lock=True)
        col = row.column()
        row = col.row()
        if self.index <= 1 :
            row.enabled= False
        row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove.bl_idname, icon='TRIA_UP', text="").action = 'UP'
        row = col.row()
        if self.index >= len(bpy.context.scene.O2MCD_df_packs)-1 or self.index == 0:
            row.enabled= False
        row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'
        
def check_path(self,context):
    if self.path:
        if os.path.isfile(self.path):
            if os.path.splitext(self.path)[1] == ".zip" or os.path.splitext(self.path)[1] == ".jar":
                name= self.path.split(os.sep)[-1]
            else:
                self.path=os.path.dirname(self.path)
                name= self.path.split(os.sep)[-1]
        else:
            if os.path.splitext(self.path)[1]:
                self.path= os.sep.join(self.path.split(os.sep)[:-1])+os.sep
            name= self.path.split(os.sep)[-2]
        self.name= name
        self.icon=bpy.data.images[0]

class OBJECTTOMCDISPLAY_UL_DefaultResourcePacks(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row()
        if index == 0:
                row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackAdd.bl_idname)
        else:
            row = row.row()
            row.alignment="LEFT"
            if item.image:
                row.label(text="",icon_value=layout.icon(item.image))
            row.label(text=item.name)
            row = layout.row()
            row.alignment="RIGHT"
            row.label(text=item.path)
            row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove.bl_idname,icon='X').index=index
            
def rc_packs_update(self, context):
    rc_packs=[]
    for p in context.scene.O2MCD_df_packs[1:]:
        rc_packs.append(p.path)
    rc_packs=",".join(rc_packs)
    context.preferences.addons[__package__].preferences.rc_packs=rc_packs
class OBJECTTOMCDISPLAY_OT_DefaultResourcePackAdd(bpy.types.Operator): #追加
    bl_idname = "output.o2mcd_resource_pack_add"
    bl_label = bpy.app.translations.pgettext("open resource pack")
    bl_description =  bpy.app.translations.pgettext("Open a resource pack.\nFolders, zips and jars are supported.")
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename : bpy.props.StringProperty()
    directory : bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.zip;*.jar",options={"HIDDEN"})
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        rc_pack=context.scene.O2MCD_df_packs.add()
        rc_pack.path = self.filepath
        if os.path.isdir(self.filepath):
            rc_pack.type='FOLDER'
            try:image= bpy.data.images.load(os.path.join(self.filepath,"pack.png"))
            except:image=None
            rc_pack.image= image
        elif os.path.splitext(self.filepath)[1] == ".zip" or os.path.splitext(self.filepath)[1] == ".jar":
            rc_pack.type='ZIP'
            with tempfile.TemporaryDirectory() as temp:
                with zipfile.ZipFile(self.filepath) as zip:
                    try:
                        zip.extract('pack.png',temp)
                        image= bpy.data.images.load(os.path.join(temp,"pack.png"))
                        image.pack()
                    except:image=None
                    rc_pack.image= image
        context.scene.O2MCD_df_packs.move(len(context.scene.O2MCD_df_packs)-1,1)
        rc_packs_update(self, context)
        return {'FINISHED'}
    
def JarSet(self, context):
    context.scene.O2MCD_df_packs.clear()
    context.scene.O2MCD_df_packs.add()
    rc_packs=context.preferences.addons[__package__].preferences.rc_packs
    if len(rc_packs.split(",")) >= 2 :rc_packs=rc_packs.split(",")
    else : rc_packs = [rc_packs]
    for p in rc_packs[::-1]:
        rc_pack=context.scene.O2MCD_df_packs.add()
        rc_pack.path = p
        if os.path.isdir(p):
            rc_pack.type='FOLDER'
            try:image= bpy.data.images.load(os.path.join(p,"pack.png"))
            except:image=None
            rc_pack.image= image
        elif os.path.splitext(p)[1] == ".zip" or os.path.splitext(p)[1] == ".jar":
            rc_pack.type='ZIP'
            with tempfile.TemporaryDirectory() as temp:
                with zipfile.ZipFile(p) as zip:
                    try:
                        zip.extract('pack.png',temp)
                        image= bpy.data.images.load(os.path.join(temp,"pack.png"))
                        image.pack()
                    except:image=None
                    rc_pack.image= image
    return {'FINISHED'}
class OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove(bpy.types.Operator): #削除
    bl_idname = "output.o2mcd_resource_pack_remove"
    bl_label = ""
    bl_description = ""
    index : bpy.props.IntProperty(default=0)
    def execute(self, context):
        context.scene.O2MCD_df_packs.remove(self.index)
        rc_packs_update(self, context)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove(bpy.types.Operator): #移動
    bl_idname = "output.o2mcd_resource_pack_move"
    bl_label = ""
    bl_description = bpy.app.translations.pgettext("move resource pack")
    action: bpy.props.EnumProperty(items=(('UP', "Up", ""),('DOWN', "Down", "")))

    def invoke(self, context, event):
        list=context.scene.O2MCD_df_packs
        index=context.preferences.addons[__package__].preferences.index
        if self.action == 'DOWN' and index < len(list):
            list.move(index, index+1)
            context.preferences.addons[__package__].preferences.index += 1
        elif self.action == 'UP' and index >= 1:
            list.move(index, index-1)
            context.preferences.addons[__package__].preferences.index -= 1
        rc_packs_update(self, context)
        return {"FINISHED"}
    
class O2MCD_DefaultResourcePacks(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="ResourcePack",default="",subtype="FILE_PATH",update=check_path)
    name: bpy.props.StringProperty(name="name",default="")
    image: bpy.props.PointerProperty(name="image",type=bpy.types.Image)
    type: bpy.props.EnumProperty(items=(('ZIP', "zip", ""),('JAR', "jar", ""),('FOLDER', "folder", "")))

classes = (
    O2MCD_DefaultResourcePacks,
    OBJECTTOMCDISPLAY_UL_DefaultResourcePacks,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackAdd,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove
)

# blender起動時に実行
@persistent
def load(self, context):
    output.set_default(None, bpy.context)
    output.update(None, bpy.context)
    object.item_regist()
    JarSet(None, bpy.context)


def register():
    bpy.app.translations.register(__name__, O2MCD_translation_dict)
    bpy.utils.register_class(O2MCD_Preferences)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_df_packs = bpy.props.CollectionProperty(type=O2MCD_DefaultResourcePacks)
    bpy.app.handlers.load_post.append(load)
    output.register()
    command.register()
    object.register()
    link.register()
    list.register()
    json_import.register()
    bpy.types.TOPBAR_MT_file_import.append(json_import.json_import)

def unregister():
    bpy.app.translations.unregister(__name__)
    bpy.utils.unregister_class(O2MCD_Preferences)
    output.unregister()
    command.unregister()
    object.unregister()
    link.unregister()
    list.unregister()
    json_import.unregister()
    bpy.types.TOPBAR_MT_file_import.remove(json_import.json_import)

if __name__ == "__main__":
    register()