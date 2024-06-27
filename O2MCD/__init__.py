# Copyright (c) 2023 200Q
import os
import zipfile
import json
import re
from re import *
bl_info = {
    "name": "Object to MCDisplay",
    "author": "200Q",
    "version": (0, 3, 0),
    "blender": (4, 0, 0),
    "location": "Output Properties",
    "support": "COMMUNITY",
    "description": "Calculate the transformation of the Display entity in Minecraft on Blender.",
    "warning": "",
    "doc_url": "https://github.com/200Q-1/Object-to-MCDisplay",
    "tracker_url": "",
    "category": "Object"
}

O2MCD_translation_dict = {
    "ja_JP": {
        ("*", "Update"): "更新",
        ("*", "Auto Update"): "自動更新",
        ("*", "Generate command in O2MCD_output"): "O2MCD_outputにコマンドを生成します",
        ("*", "Generate a command every time there is a change in the scene or you move a frame"): "シーンに変更があるか、フレームを移動するたびにコマンドを生成します",
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
        ("*", "move resource pack"): "リソースパックを移動",
        ("Operator", "open resource pack"): "リソースパックを開く",
        ("*", "Open a resource pack.\nFolders, zips and jars are supported."): "リソースパックを開きます。\nフォルダ、zip、jarに対応しています",
        ("*", "Import json file as object."): "json ファイルをオブジェクトとしてインポート",
        ("*", "Resource Pack"): "リソースパック",
        ("*", "You can set default values that are applied when you open a new project."): "新規プロジェクトを開いた際に適応される、デフォルトの値を設定することができます。",
        ("*", "Synchronise version settings with MCPP"): "MCPPとバージョン設定を同期します",
        ("*", "single frame path"): "シングルフレームのパス",
        ("*", "animation path"): "アニメーションのパス",
        ("*", "Output files to the specified path"): "指定したパスにファイルを書き出します",
        ("*", "Object List"): "オブジェクトリスト",
        ("*", "Add property"): "プロパティを追加します",
        ("*", "Minecraft version"): "Minecraftのバージョン",
        ("*", "number of decimal places to round"): "丸める少数の桁数",
        ("*", "Enable O2MCD"): "O2MCDを有効化",
        ("*", "Synchronisation of Minecraft versions with MCPP"): "マインクラフトバージョンをMCPPと同期",
        ("*", "List of objects for which the Display property is set."): "Displayプロパティが設定されているオブジェクトのリスト",
        ("*", "Add a resource pack to search for files specified as parent when importing a json model"): "jsonモデルをインポートする際にparentに指定されているファイルを検索するリソースパックを追加します",
        ("*", "Add Command"): "コマンドを追加",
        ("*", "Remove Command"): "コマンドを削除",
        ("*", "Add the command to be entered when the Input is generated"): "Inputを生成した際に入力されるコマンドを追加",
        # ("*", "Set ID"): "IDを設定",
        ("*", "Example:"):"例：",
        ("*", "16 float values in transformation"): "transformationの16個のfloat値",
        ("*", "Value of %s in transformation"):"transformationの%sの値",
        ("*", "Relative %s of entities"):"エンティティの相対%s",
        ("*", "Item ID"):"アイテムID",
        ("*", "entity type"):"エンティティタイプ",
        ("*", "Properties of the block (custom model data)"):"ブロックのProperties(カスタムモデルデータ)",
        ("*", "Object tags"):"オブジェクトのタグ",
        ("*", "Object name"):"オブジェクトの名前",
        ("*", "Object index"):"オブジェクトのインデックス",
        ("*", "formula"):"計算式",
        ("*", "input"):"入力",
        ("*", "Add tags"):"タグを追加",
        ("*", "Remove tags"):"タグを削除",
        ("*", "Mesh list"):"メッシュリスト",
        ("*", "Move the mesh up or down"):"メッシュを上下に移動",
        ("*", "Add mesh"):"メッシュを追加",
        ("*", "Remove mesh"):"メッシュを削除",
        ("*", "Set item ID and add to object list"):"アイテムIDを設定してオブジェクトリストに追加",
        ("*", "Set ID and to object list"):"IDを設定してオブジェクトリストに追加",
        ("*", "Copy mesh list to selected object"):"メッシュリストを選択オブジェクトにコピー",
        ("*", "Copy command list to selected object"):"コマンドリストを選択オブジェクトにコピー",
        ("*", "Copy tag list to selected object"):"タグリストを選択オブジェクトにコピー",
        ("*", "Save user preferences"):"ユーザープリファレンスを保存",
        ("*", "Command list"):"コマンドリスト",
        ("*", "Move the command up or down"):"コマンドを上下に移動",
        ("*", "Add commands"):"コマンドを追加",
        ("*", "Remove commands"):"コマンドを削除",
        ("*", "Move the object up or down"):"オブジェクトを上下に移動",
        ("*", "Move the template up or down"):"メッシュを上下に移動",
        ("*", "Add template"):"テンプレートを追加",
        ("*", "Remove template"):"テンプレートを削除",
        ("*", "Specify the .jar file from the add-on settings"):"アドオン設定から.jarファイルを指定してください。",
        ("*", ".jar file"):".jarファイル",
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
    jar=self.jar_path
    try:
        with zipfile.ZipFile(jar) as zip:
            js=json.load(zip.open('assets/minecraft/lang/en_us.json','r'))
            block_id=[i.replace('block.minecraft.','') for i in js.keys() if re.match('block\.minecraft\..+(?!\.)',i) and len(i.split("."))==3]
            item_id=[i.replace('item.minecraft.','') for i in js.keys() if re.match('item\.minecraft\..+(?!\.)',i) and len(i.split("."))==3]
            bni=[f.split("/")[-1] for f in zip.namelist() if f.startswith("assets/minecraft/models/item/") and not f.endswith('/')]
    except:self.report({'ERROR_INVALID_INPUT'},"jarファイルの読み込みに失敗しました。")
    item_id=[b for b in block_id if b+".json" in bni]+item_id
    item_id.sort()
    ex=['white_banner','orange_banner','magenta_banner','light_blue_banner','yellow_banner','lime_banner','pink_banner','gray_banner','light_gray_banner','cyan_banner','purple_banner','blue_banner','brown_banner','green_banner','red_banner','black_banner','moving_piston','decorated_pot','end_portal','ender_chest','moving_piston','water','lava',"skeleton_skull","wither_skeleton_skull","creeper_head","player_head","zombie_head",'acacia_hanging_sign', 'acacia_sign', 'bamboo_hanging_sign', 'bamboo_sign', 'birch_hanging_sign', 'birch_sign', 'cherry_hanging_sign', 'cherry_sign', 'crimson_hanging_sign', 'crimson_sign', 'dark_oak_hanging_sign', 'dark_oak_sign', 'jungle_hanging_sign', 'jungle_sign', 'mangrove_hanging_sign', 'mangrove_sign', 'oak_hanging_sign', 'oak_sign', 'spruce_hanging_sign', 'spruce_sign', 'warped_hanging_sign', 'warped_sign']
    block_id=list(filter(lambda b: not b in ex, block_id))
    bpy.context.preferences.addons[__package__].preferences.block_list.clear()
    bpy.context.preferences.addons[__package__].preferences.item_list.clear()
    for i in block_id:
        bpy.context.preferences.addons[__package__].preferences.block_list.add().name=i
    for i in item_id:
        bpy.context.preferences.addons[__package__].preferences.item_list.add().name=i
    if not bpy.context.scene.O2MCD_rc_packs:
        bpy.context.scene.O2MCD_rc_packs.add()
        bpy.context.scene.O2MCD_rc_packs.add().path=jar
    else:
        bpy.context.scene.O2MCD_rc_packs[len(context.scene.O2MCD_rc_packs)-1].path=jar
        

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
    cmd_func: bpy.props.StringProperty(name="Func",description="", subtype='FILE_PATH', default="matrix,loc,scale,l_rot,r_rot,pos,rot,id,type,prop,tags?,name,num,frame,math")
    mcpp_sync: bpy.props.BoolProperty(name=bpy.app.translations.pgettext_iface("Synchronisation of Minecraft versions with MCPP"),description=bpy.app.translations.pgettext_tip("Synchronise version settings with MCPP"),default=False)
    
    def draw(self, context):
        layout = self.layout
        br = layout.row(align=True)
        if not self.jar_path or not self.jar_path.endswith(".jar"):
            br.alert=True
        br.prop(self, "jar_path",text=bpy.app.translations.pgettext_iface(".jar file"))
        if output.check_mcpp():
            row=layout.row()
            if not self.jar_path or not self.jar_path.endswith(".jar"):
                row.active = False
            row.alignment = "RIGHT"
            row.label(text="Synchronisation of Minecraft versions with MCPP")
            row.prop(self,"mcpp_sync",text="")
        col= layout.column()
        if not self.jar_path or self.jar_path.endswith(".jar"):
            col.active = False
        layout.separator()
        


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
            case 'UP' | 'DOWN':
                des=bpy.app.translations.pgettext_tip("Move the template up or down")
            case 'ADD':
                des=bpy.app.translations.pgettext_tip("Add template")
            case 'REMOVE':
                des=bpy.app.translations.pgettext_tip("Remove template")
            case 'SAVE':
                des=bpy.app.translations.pgettext_tip("Save user preferences")
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
    
    
def JarSet(self, context):
    if not context.scene.O2MCD_rc_packs:
        context.scene.O2MCD_rc_packs.add()
        context.scene.O2MCD_rc_packs.add().path = context.preferences.addons[__package__].preferences.jar_path
        context.scene.O2MCD_rc_packs.move(len(context.scene.O2MCD_rc_packs)-1,1)
    return {'FINISHED'}

    

classes = (
    O2MCD_BlockList,
    O2MCD_ItemList,
    O2MCD_TempCmd,
    OBJECTTOMCDISPLAY_UL_TemplateList,
    OBJECTTOMCDISPLAY_OT_Temp,
    OBJECTTOMCDISPLAY_OT_TempAction,
    O2MCD_Preferences,
)

# blender起動時に実行
@persistent
def load(self, context):
    output.update(None, bpy.context)
    JarSet(None, bpy.context)


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
    if command.command_generate in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(command.command_generate)
    if command.command_generate in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(command.command_generate)
    if object_list.chenge_panel in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(object_list.chenge_panel)
    output.unregister()
    command.unregister()
    object.unregister()
    object_list.unregister()
    json_import.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load)

if __name__ == "__main__":
    register()