# Copyright (c) 2023 200Q
import os
import zipfile
import json
import re
from re import *
bl_info = {
    "name": "Object to MCDisplay",
    "author": "200Q",
    "version": (0, 2, 3),
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
        ("*", "Update"): "更新",
        ("*", "Auto Update"): "自動更新",
        ("*", "Get information about the object and generate commands in the Output according to the Input"): "オブジェクトの情報を取得してInputに応じたコマンドをOutputに生成します",
        ("*", "Ensure that an update is performed every time there is a change in the scene or a frame is moved"): "シーンに変更があるか、フレームを移動するたびに更新をするようにします",
        ("*", "Object Number"): "番号",
        ("*", "Generate file in specified path"): "指定したパスにファイルを生成",
        ("*", "Rearrange the order of objects"): "オブジェクトの順番を入れ替える",
        ("*", "Reverse"): "反転",
        ("*", "Reversing the order of objects"): "オブジェクトの順番を反転する",
        ("*", "Sorting Objects"): "オブジェクトを並び替える",
        ("*", "Sort by name"): "名前順",
        ("*", "Sort by creation"): "作成順",
        ("*", "Sort by random"): "ランダム順",
        ("Operator", "Sort by DataPath"): "データパス順",
        ("Operator", "Link display properties"): "ディスプレイプロパティをリンク",
        ("*", "Transfers data from the active object to the selected object"): "アクティブオブジェクトから選択オブジェクトにデータを転送します",
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
        ("*", "move resource pack"): "リソースパックを移動します",
        ("Operator", "open resource pack"): "リソースパックを開く",
        ("*", "Open a resource pack.\nFolders, zips and jars are supported."): "リソースパックを開きます。\nフォルダ、zip、jarに対応しています",
        ("*", "Import json file as object."): "json ファイルをオブジェクトとしてインポートします",
        ("*", "Parent Referrer"): "ペアレントの参照元",
        
        ("*", "You can set default values that are applied when you open a new project."): "新規プロジェクトを開いた際に適応される、デフォルトの値を設定することができます。",
        ("*", "Synchronise version settings with MCPP"): "MCPPとバージョン設定を同期します",
        ("*", "single frame path"): "シングルフレームのパス",
        ("*", "animation path"): "アニメーションのパス",
        ("*", "Output files to the specified path"): "指定したパスにファイルを書き出します",
        ("*", "Object List"): "オブジェクトリスト",
        ("*", "Add property"): "プロパティを追加します",
        ("*", "Unlink property"): "プロパティのリンクを解除します",
        ("*", "Remove property"): "プロパティを削除します",
        ("*", "Display entity type"): "ディスプレイエンティティのタイプ",
        ("*", "Value assigned to /tag(s)"): "/tag(s) に代入される値",
        ("*", "Value assigned to /model"): "/model に代入される値",
        ("*", "Value assigned to /item"): "/item に代入される値",
        ("*", "Value assigned to /prop"): "/prop に代入される値",
        ("*", "Value assigned to /extra"): "/extra に代入される値",
        ("*", "Value assigned to /type"): "/type に代入される値",
        ("*", "Value assigned to /id"): "/id に代入される値",
        ("*", "Minecraft version"): "Minecraftのバージョン",
        ("*", "number of decimal places to round"): "丸める少数の桁数",
        ("*", "Enable O2MCD"): "O2MCDを有効化",
        ("*", "Synchronised with MCPP"): "MCPPと同期",
        ("*", "List of objects for which the Display property is set."): "Displayプロパティが設定されているオブジェクトのリストです",
        ("*", "Add a resource pack to search for files specified as parent when importing a json model"): "jsonモデルをインポートする際にparentに指定されているファイルを検索するリソースパックを追加します",
        ("*", "Add Command"): "コマンドを追加",
        ("*", "Remove Command"): "コマンドを削除",
        ("*", "Add the command to be entered when the Input is generated"): "Inputを生成した際に入力されるコマンドを追加します",
        ("*", "Enable O2MCD"): "O2MCDを有効化",
        ("*", "Enable O2MCD"): "O2MCDを有効化",
        ("*", "Enable O2MCD"): "O2MCDを有効化",
        ("*", "Enable O2MCD"): "O2MCDを有効化",
        ("*", "Enable O2MCD"): "O2MCDを有効化",
    }
}
if "bpy" in locals():
    import imp
    imp.reload(object)
    imp.reload(output)
    imp.reload(command)
    imp.reload(link)
    imp.reload(oblect_list)
    imp.reload(json_import)
else:
    from . import object
    from . import output
    from . import command
    from . import link
    from . import oblect_list
    from . import json_import
import bpy
from bpy.app.handlers import persistent

class O2MCD_DefaultInputs(bpy.types.PropertyGroup):
    command: bpy.props.StringProperty(
        name="Command",
        description="",
        default=""
    )

class OBJECTTOMCDISPLAY_OT_AddCommand(bpy.types.Operator):  # コマンド追加
    bl_idname = "o2mcd.add_command"
    bl_label = bpy.app.translations.pgettext("Add Command")
    bl_description = ""
    
    def execute(self, context):
        context.preferences.addons[__package__].preferences.inputs.add()
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_OT_RemoveCommand(bpy.types.Operator):  # コマンド削除
    bl_idname = "o2mcd.remove_command"
    bl_label = bpy.app.translations.pgettext("Remove Command")
    bl_description = ""
    
    index: bpy.props.IntProperty(name="Index")
    def execute(self, context):
        context.preferences.addons[__package__].preferences.inputs.remove(self.index)
        return {'FINISHED'}
    
class  O2MCD_BlockList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_ItemList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
    
class O2MCD_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    index : bpy.props.IntProperty(name="index",default=0)
    mc_jar : bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext("mc_jar"), default="")
    rc_packs : bpy.props.StringProperty(default="")
    block_id : bpy.props.StringProperty(default="")
    block_list : bpy.props.CollectionProperty(name="block_list",type=O2MCD_BlockList)
    item_id : bpy.props.StringProperty(default="")
    item_list : bpy.props.CollectionProperty(name="item_list",type=O2MCD_ItemList)
    
    mc_version: bpy.props.EnumProperty(name="Version",description=bpy.app.translations.pgettext("Minecraft version"), items=[('1.19', "1.19", ""), ('1.20', "1.20", "")], default='1.20')
    rou: bpy.props.IntProperty(name="Round",description=bpy.app.translations.pgettext("number of decimal places to round"), default=3, max=16, min=1)
    curr_path: bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext("single frame path"), subtype='FILE_PATH', default="")
    anim_path: bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext("animation path"), subtype='FILE_PATH', default="")
    auto_reload: bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Auto Update"),description=bpy.app.translations.pgettext("Ensure that an update is performed every time there is a change in the scene or a frame is moved"), default=False)
    enable: bpy.props.BoolProperty(name="Enable",description=bpy.app.translations.pgettext("Enable O2MCD"), default=False)
    mcpp_sync: bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Synchronised with MCPP"),description=bpy.app.translations.pgettext("Synchronise version settings with MCPP"),default=False)
    inputs: bpy.props.CollectionProperty(name="Input",description=bpy.app.translations.pgettext("Add the command to be entered when the Input is generated"),type=O2MCD_DefaultInputs)
    
    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "block_id",self, "block_list",text="id")
        layout.prop_search(self, "item_id",self, "item_list",text="id")
        br = layout.row(align=True)
        br.prop(self, "mc_jar",text=".jarファイル")
        br.operator(OBJECTTOMCDISPLAY_OT_JarOpen.bl_idname, text="", icon='FILE_FOLDER')
        layout.label(icon='DOT',text=bpy.app.translations.pgettext("You can set default values that are applied when you open a new project."))
        row=layout.row()
        row.alignment = "RIGHT"
        row.label(text="Enabled")
        row.prop(self,"enable",text="")
        row=layout.row()
        row.alignment = "RIGHT"
        row.label(text=bpy.app.translations.pgettext("Auto Update"))
        row.prop(self, "auto_reload",text="")
        if output.check_mcpp():
            row=layout.row()
            row.alignment = "RIGHT"
            row.label(text=bpy.app.translations.pgettext("Synchronised with MCPP"))
            row.prop(self,"mcpp_sync",text="")
        col= layout.column()
        col.use_property_split = True
        col.prop(self,"mc_version")
        col.prop(self, "rou")
        col.use_property_split = True
        col.prop(self, "curr_path",text=bpy.app.translations.pgettext("single frame path"))
        col.prop(self, "anim_path",text="animation path")
        
        col = layout.column()
        col.split()
        col.label(text="   "+bpy.app.translations.pgettext("Parent Referrer"))
        row= col.row()
        row.template_list("OBJECTTOMCDISPLAY_UL_DefaultResourcePacks", "", bpy.context.scene, "O2MCD_df_packs", self, "index", rows=2,sort_lock=True)
        col = row.column()
        row = col.row()
        if self.index <= 1 :
            row.enabled= False
        row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove.bl_idname, icon='TRIA_UP', text="").action = 'UP'
        row = col.row()
        if self.index >= len(bpy.context.scene.O2MCD_df_packs)-1 or self.index == 0:
            row.enabled= False
        row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'
        box=layout.box()
        row = box.row(align = True)
        row.label(text="Input ")
        row.operator(OBJECTTOMCDISPLAY_OT_AddCommand.bl_idname, icon='ADD', text="", emboss=False)
        col = box.column(align = True)
        for i,item in enumerate(self.inputs):
            row = col.row(align = True)
            row.prop(item,"command",text="")
            row.operator(OBJECTTOMCDISPLAY_OT_RemoveCommand.bl_idname, icon='PANEL_CLOSE', text="", emboss=False).index=i

        layout.separator()
        
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

class OBJECTTOMCDISPLAY_UL_DefaultResourcePacks(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row()
        if index == 0:
                row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackAdd.bl_idname)
        else:
            row = row.row()
            row.alignment="LEFT"
            row.label(text=item.name)
            row = layout.row()
            row.alignment="RIGHT"
            row.label(text=item.path)
            row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove.bl_idname,text="",icon='X').index=index
            
def rc_packs_update(self, context):
    rc_packs=[]
    for p in context.scene.O2MCD_df_packs[1:]:
        rc_packs.append(p.path)
    rc_packs=",".join(rc_packs)
    context.preferences.addons[__package__].preferences.rc_packs=rc_packs
    
class OBJECTTOMCDISPLAY_OT_JarOpen(bpy.types.Operator): #JAR設定
    bl_idname = "o2mcd.jar_open"
    bl_label = "open .jar"
    bl_description =  bpy.app.translations.pgettext("Open a resource pack.\nFolders, zips and jars are supported.")
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.zip;*.jar",options={"HIDDEN"})
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        
        context.preferences.addons[__package__].preferences.mc_jar = self.filepath
        jar=context.preferences.addons[__package__].preferences.mc_jar
        try:
            with zipfile.ZipFile(jar) as zip:
                js=json.load(zip.open('assets/minecraft/lang/en_us.json','r'))
                block_id=[i.replace('block.minecraft.','') for i in js.keys() if re.match('block\.minecraft\..+(?!\.)',i) and len(i.split("."))==3]
                item_id=[i.replace('item.minecraft.','') for i in js.keys() if re.match('item\.minecraft\..+(?!\.)',i) and len(i.split("."))==3]
                bni=[f.split("/")[-1] for f in zip.namelist() if f.startswith("assets/minecraft/models/item/") and not f.endswith('/')]
        except:pass
        item_id=[b for b in block_id if b in bni]+item_id+["air"]
        item_id.sort()
        for i in block_id:
            bpy.context.preferences.addons[__package__].preferences.block_list.add().name=i
        for i in item_id:
            bpy.context.preferences.addons[__package__].preferences.item_list.add().name=i
        return {'FINISHED'}
class OBJECTTOMCDISPLAY_OT_DefaultResourcePackAdd(bpy.types.Operator): #追加
    bl_idname = "o2mcd.df_resource_pack_add"
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
        context.scene.O2MCD_df_packs.move(len(context.scene.O2MCD_df_packs)-1,1)
        rc_packs_update(self, context)
        return {'FINISHED'}
    
def JarSet(self, context):
    context.scene.O2MCD_df_packs.clear()
    context.scene.O2MCD_df_packs.add()
    rc_packs=context.preferences.addons[__package__].preferences.rc_packs
    if rc_packs:
        if len(rc_packs.split(",")) >= 2 :rc_packs=rc_packs.split(",")
        else : rc_packs = [rc_packs]
        for p in rc_packs:
            rc_pack=context.scene.O2MCD_df_packs.add()
            rc_pack.path = p
    return {'FINISHED'}
class OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove(bpy.types.Operator): #削除
    bl_idname = "o2mcd.df_resource_pack_remove"
    bl_label = "Remove"
    bl_description = bpy.app.translations.pgettext("Remove resource packs")
    index : bpy.props.IntProperty(default=0)
    def execute(self, context):
        context.scene.O2MCD_df_packs.remove(self.index)
        rc_packs_update(self, context)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove(bpy.types.Operator): #移動
    bl_idname = "o2mcd.df_resource_pack_move"
    bl_label = "Move"
    bl_description = bpy.app.translations.pgettext("move resource pack")
    action: bpy.props.EnumProperty(items=(('UP', "Up", ""),('DOWN', "Down", "")))

    def invoke(self, context, event):
        list=context.scene.O2MCD_df_packs
        index=context.preferences.addons[__package__].preferences.index
        if self.action == 'DOWN' :
            list.move(index, index+1)
            context.preferences.addons[__package__].preferences.index += 1
        elif self.action == 'UP' :
            list.move(index, index-1)
            context.preferences.addons[__package__].preferences.index -= 1
        rc_packs_update(self, context)
        return {"FINISHED"}
    
class O2MCD_DefaultResourcePacks(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="ResourcePack",default="",subtype="FILE_PATH",update=check_path)
    name: bpy.props.StringProperty(name="name",default="")
    type: bpy.props.EnumProperty(items=(('ZIP', "zip", ""),('JAR', "jar", ""),('FOLDER', "folder", "")))

classes = (
    O2MCD_BlockList,
    O2MCD_ItemList,
    O2MCD_DefaultInputs,
    OBJECTTOMCDISPLAY_OT_AddCommand,
    OBJECTTOMCDISPLAY_OT_RemoveCommand,
    O2MCD_Preferences,
    O2MCD_DefaultResourcePacks,
    OBJECTTOMCDISPLAY_UL_DefaultResourcePacks,
    OBJECTTOMCDISPLAY_OT_JarOpen,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackAdd,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove,
)

# blender起動時に実行
@persistent
def load(self, context):
    output.update(None, bpy.context)
    JarSet(None, bpy.context)
    output.set_default(None, bpy.context)


def register():
    bpy.app.translations.register(__name__, O2MCD_translation_dict)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_df_packs = bpy.props.CollectionProperty(type=O2MCD_DefaultResourcePacks)
    bpy.app.handlers.load_post.append(load)
    output.register()
    command.register()
    object.register()
    link.register()
    oblect_list.register()
    json_import.register()

def unregister():
    bpy.app.translations.unregister(__name__)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    output.unregister()
    command.unregister()
    object.unregister()
    link.unregister()
    oblect_list.unregister()
    json_import.unregister()

if __name__ == "__main__":
    register()