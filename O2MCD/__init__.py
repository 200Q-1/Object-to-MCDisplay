# Copyright (c) 2023 200Q

bl_info = {
    "name": "Object to MCDisplay",
    "author": "200Q",
    "version": (0, 2, 0),
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
        ("*", "Name order"): "名前",
        ("*", "Creation order"): "作成",
        ("*", "Random order"): "ランダム",
        ("*", "DataPath order"): "データパス",
        ("*", "Link display properties"): "ディスプレイプロパティをリンク",
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
    imp.reload(render)
    imp.reload(command)
    imp.reload(link)
    imp.reload(list)
    imp.reload(json_import)
else:
    from . import object
    from . import render
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
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text=bpy.app.translations.pgettext("ペアレントの参照元："))
        row= col.row()
        row.template_list("OBJECTTOMCDISPLAY_UL_ResourcePacks", "", bpy.context.scene, "O2MCD_rc_packs", self, "index", rows=2,sort_lock=True)
        col = row.column()
        if self.index <= 1 :
            col.enabled= False
        col.operator(json_import.OBJECTTOMCDISPLAY_OT_ResourcePackMove.bl_idname, icon='TRIA_UP', text="").action = 'UP'
        if self.index >= len(bpy.context.scene.O2MCD_rc_packs)-1 or self.index == 0:
            col.enabled= False
        col.operator(json_import.OBJECTTOMCDISPLAY_OT_ResourcePackMove.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'
        row = layout.row(align = True)
        row.alignment = "LEFT"
# blender起動時に実行
@persistent
def load(self, context):
    render.update(None, bpy.context)
    object.item_regist()
    json_import.JarSet(None, bpy.context)

def register():
    bpy.app.translations.register(__name__, O2MCD_translation_dict)
    bpy.utils.register_class(O2MCD_Preferences)
    bpy.app.handlers.load_post.append(load)
    render.register()
    command.register()
    object.register()
    link.register()
    list.register()
    json_import.register()
    bpy.types.TOPBAR_MT_file_import.append(json_import.json_import)

def unregister():
    bpy.app.translations.unregister(__name__)
    bpy.utils.unregister_class(O2MCD_Preferences)
    render.unregister()
    command.unregister()
    object.unregister()
    link.unregister()
    list.unregister()
    json_import.unregister()
    bpy.types.TOPBAR_MT_file_import.remove(json_import.json_import)

if __name__ == "__main__":
    register()