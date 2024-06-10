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
        ("*", "Transfers data from the active object to the selected object"): "アクティブオブジェクトから選択オブジェクトにデータを転送します",
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
    imp.reload(object_list)
    imp.reload(json_import)
else:
    from . import object
    from . import output
    from . import command
    from . import object_list
    from . import json_import
import bpy
from bpy.app.handlers import persistent
    
class  O2MCD_BlockList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_ItemList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_TempCmd(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="name", default="")
    cmd: bpy.props.StringProperty(name="cmd", default="")
    
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

def jar_setting(self,context):
    jar=context.preferences.addons[__package__].preferences.jar_path
    try:
        with zipfile.ZipFile(jar) as zip:
            js=json.load(zip.open('assets/minecraft/lang/en_us.json','r'))
            block_id=[i.replace('block.minecraft.','') for i in js.keys() if re.match('block\.minecraft\..+(?!\.)',i) and len(i.split("."))==3]
            item_id=[i.replace('item.minecraft.','') for i in js.keys() if re.match('item\.minecraft\..+(?!\.)',i) and len(i.split("."))==3]
            bni=[f.split("/")[-1] for f in zip.namelist() if f.startswith("assets/minecraft/models/item/") and not f.endswith('/')]
    except:self.report({'ERROR_INVALID_INPUT'},"jarファイルの読み込みに失敗しました。")
    item_id=[b for b in block_id if b+".json" in bni]+item_id
    item_id.sort()
    ex=['moving_piston','decorated_pot','end_portal','ender_chest','moving_piston','water','lava',"skeleton_skull","wither_skeleton_skull","creeper_head","player_head","zombie_head",'acacia_hanging_sign', 'acacia_sign', 'bamboo_hanging_sign', 'bamboo_sign', 'birch_hanging_sign', 'birch_sign', 'cherry_hanging_sign', 'cherry_sign', 'crimson_hanging_sign', 'crimson_sign', 'dark_oak_hanging_sign', 'dark_oak_sign', 'jungle_hanging_sign', 'jungle_sign', 'mangrove_hanging_sign', 'mangrove_sign', 'oak_hanging_sign', 'oak_sign', 'spruce_hanging_sign', 'spruce_sign', 'warped_hanging_sign', 'warped_sign']
    block_id=list(filter(lambda b: not b in ex, block_id))
    bpy.context.preferences.addons[__package__].preferences.block_list.clear()
    bpy.context.preferences.addons[__package__].preferences.item_list.clear()
    for i in block_id:
        bpy.context.preferences.addons[__package__].preferences.block_list.add().name=i
    for i in item_id:
        bpy.context.preferences.addons[__package__].preferences.item_list.add().name=i
    if not context.scene.O2MCD_rc_packs:
        context.scene.O2MCD_rc_packs.add()
        context.scene.O2MCD_rc_packs.add().path=self.filepath

class O2MCD_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    index : bpy.props.IntProperty(name="index",default=0)
    jar_path : bpy.props.StringProperty(name="jar_path",description="", subtype='FILE_PATH', default="",update=jar_setting)
    block_id : bpy.props.StringProperty(default="")
    block_list : bpy.props.CollectionProperty(name="block_list",type=O2MCD_BlockList)
    item_id : bpy.props.StringProperty(default="")
    item_list : bpy.props.CollectionProperty(name="item_list",type=O2MCD_ItemList)
    tmp_cmd: bpy.props.CollectionProperty(name="temp_cmd",type=O2MCD_TempCmd)
    tmp_index: bpy.props.IntProperty(name="index",default=0)
    cmd_func: bpy.props.StringProperty(name="Func",description="", subtype='FILE_PATH', default="matrix,loc,scale,l_rot,r_rot,pos,rot,id,type,prop,tag,name,num,frame,math")
    
    mc_version: bpy.props.EnumProperty(name="Version",description=bpy.app.translations.pgettext("Minecraft version"), items=[('1.19', "1.19", ""), ('1.20', "1.20", "")], default='1.20')
    rou: bpy.props.IntProperty(name="Round",description=bpy.app.translations.pgettext("number of decimal places to round"), default=3, max=16, min=1)
    curr_path: bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext("single frame path"), subtype='FILE_PATH', default="")
    anim_path: bpy.props.StringProperty(name="Path",description=bpy.app.translations.pgettext("animation path"), subtype='FILE_PATH', default="")
    auto_reload: bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Auto Update"),description=bpy.app.translations.pgettext("Ensure that an update is performed every time there is a change in the scene or a frame is moved"), default=False)
    enable: bpy.props.BoolProperty(name="Enable",description=bpy.app.translations.pgettext("Enable O2MCD"), default=False)
    mcpp_sync: bpy.props.BoolProperty(name=bpy.app.translations.pgettext("Synchronised with MCPP"),description=bpy.app.translations.pgettext("Synchronise version settings with MCPP"),default=False)
    
    def draw(self, context):
        layout = self.layout
        br = layout.row(align=True)
        if not self.jar_path or self.jar_path[-4:] != ".jar":
            br.alert=True
        br.prop(self, "jar_path",text=".jarファイル")
        layout.label(icon='DOT',text=bpy.app.translations.pgettext("You can set default values that are applied when you open a new project."))
        row=layout.row()
        if not self.jar_path or self.jar_path[-4:] != ".jar":
            row.active = False
        row.alignment = "RIGHT"
        row.label(text="Enabled")
        row.prop(self,"enable",text="")
        row=layout.row()
        if not self.jar_path or self.jar_path[-4:] != ".jar":
            row.active = False
        row.alignment = "RIGHT"
        row.label(text=bpy.app.translations.pgettext("Auto Update"))
        row.prop(self, "auto_reload",text="")
        if output.check_mcpp():
            row=layout.row()
            if not self.jar_path or self.jar_path[-4:] != ".jar":
                row.active = False
            row.alignment = "RIGHT"
            row.label(text=bpy.app.translations.pgettext("Synchronised with MCPP"))
            row.prop(self,"mcpp_sync",text="")
        col= layout.column()
        if not self.jar_path or self.jar_path[-4:] != ".jar":
            col.active = False
        col.use_property_split = True
        col.prop(self,"mc_version")
        col.prop(self, "rou")
        col.use_property_split = True
        col.prop(self, "curr_path",text=bpy.app.translations.pgettext("single frame path"))
        col.prop(self, "anim_path",text="animation path")
        layout.separator()
        

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
            if index != len(context.scene.O2MCD_rc_packs)-1:
                row.operator(OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove.bl_idname,text="",icon='X').index=index
class OBJECTTOMCDISPLAY_UL_TemplateList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row(align=True)
        if context.window_manager.O2MCD_func_toggle:
            row.label(icon='TEXT')
            sp = row.split(align=True,factor=0.3)
            sp.prop(item,"name",text="")
            sp.prop(item,"cmd",text="")
        else:
            tmp=row.operator("o2mcd.temp", text=item.name)
            tmp.name = item.name
            tmp.cmd = item.cmd
class OBJECTTOMCDISPLAY_OT_Temp(bpy.types.Operator):
    bl_idname = "o2mcd.temp"
    bl_label = ""
    bl_description = ""
    name : bpy.props.StringProperty(default="")
    cmd : bpy.props.StringProperty(default="")
    
    def execute(self, context):
        Input=bpy.data.texts.get("O2MCD_input")
        Input.write(self.cmd)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_TempAction(bpy.types.Operator): #移動
    bl_idname = "o2mcd.temp_action"
    bl_label = ""
    bl_description = ""
    action: bpy.props.EnumProperty(items=(('UP', "up", ""),('DOWN', "down", ""),('ADD',"add",""),('REMOVE',"remove",""),('SAVE',"save","")))
    index : bpy.props.IntProperty(default=0)
    
    @classmethod 
    def description(self,context, prop):
        match prop.action:
            case 'UP':
                des="選択中のテンプレートを上に移動します"
            case 'DOWN':
                des="選択中のテンプレートを下に移動します"
            case 'ADD':
                des=""
            case 'REMOVE':
                des="選択中のテンプレートを削除します"
            case 'SAVE':
                des="ユーザープリファレンスを保存します"
            case _:
                des=""
        return des
    def invoke(self, context, event):
        tmp_list=context.preferences.addons[__package__].preferences.tmp_cmd
        tmp_index=context.preferences.addons[__package__].preferences.tmp_index
        if self.action == 'DOWN' and context.preferences.addons[__package__].preferences.tmp_index < len(context.preferences.addons[__package__].preferences.tmp_cmd)-1:
            tmp_list.move(tmp_index, tmp_index+1)
            context.preferences.addons[__package__].preferences.tmp_index += 1
        if self.action == 'UP' and context.preferences.addons[__package__].preferences.tmp_index > 0:
            tmp_list.move(tmp_index, tmp_index-1)
            context.preferences.addons[__package__].preferences.tmp_index -= 1
        if self.action == 'ADD':
            tmp =context.preferences.addons[__package__].preferences.tmp_cmd.add()
            tmp.name = context.window_manager.O2MCD_temp_name
            tmp.cmd = context.window_manager.O2MCD_temp_cmd
            context.window_manager.O2MCD_temp_name=""
            context.window_manager.O2MCD_temp_cmd=""
            context.view_layer.objects.active.O2MCD_props.tmp_index=len(tmp_list)-1
        if self.action == 'REMOVE':
            tmp_list.remove(self.index)
        if self.action == 'SAVE':
            bpy.ops.wm.save_userpref()
        return {"FINISHED"}
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
        rc_pack=context.scene.O2MCD_rc_packs.add()
        rc_pack.path = self.filepath
        context.scene.O2MCD_rc_packs.move(len(context.scene.O2MCD_rc_packs)-1,1)
        return {'FINISHED'}
    
def JarSet(self, context):
    if not context.scene.O2MCD_rc_packs:
        context.scene.O2MCD_rc_packs.add()
        context.scene.O2MCD_rc_packs.add().path = context.preferences.addons[__package__].preferences.jar_path
        context.scene.O2MCD_rc_packs.move(len(context.scene.O2MCD_rc_packs)-1,1)
    return {'FINISHED'}
class OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove(bpy.types.Operator): #削除
    bl_idname = "o2mcd.df_resource_pack_remove"
    bl_label = "Remove"
    bl_description = bpy.app.translations.pgettext("Remove resource packs")
    index : bpy.props.IntProperty(default=0)
    def execute(self, context):
        context.scene.O2MCD_rc_packs.remove(self.index)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove(bpy.types.Operator): #移動
    bl_idname = "o2mcd.df_resource_pack_move"
    bl_label = "Move"
    bl_description = bpy.app.translations.pgettext("move resource pack")
    action: bpy.props.EnumProperty(items=(('UP', "Up", ""),('DOWN', "Down", "")))

    def invoke(self, context, event):
        list=context.scene.O2MCD_rc_packs
        index=context.preferences.addons[__package__].preferences.index
        if self.action == 'DOWN' :
            list.move(index, index+1)
            context.preferences.addons[__package__].preferences.index += 1
        elif self.action == 'UP' :
            list.move(index, index-1)
            context.preferences.addons[__package__].preferences.index -= 1
        return {"FINISHED"}
    

classes = (
    O2MCD_BlockList,
    O2MCD_ItemList,
    OBJECTTOMCDISPLAY_UL_DefaultResourcePacks,
    O2MCD_TempCmd,
    OBJECTTOMCDISPLAY_UL_TemplateList,
    OBJECTTOMCDISPLAY_OT_Temp,
    OBJECTTOMCDISPLAY_OT_TempAction,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackAdd,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackRemove,
    OBJECTTOMCDISPLAY_OT_DefaultResourcePackMove,
    O2MCD_Preferences,
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
    bpy.app.handlers.load_post.append(load)
    output.register()
    command.register()
    object.register()
    object_list.register()
    json_import.register()

def unregister():
    bpy.app.translations.unregister(__name__)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    output.unregister()
    command.unregister()
    object.unregister()
    object_list.unregister()
    json_import.unregister()

if __name__ == "__main__":
    register()