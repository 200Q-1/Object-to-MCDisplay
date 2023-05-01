bl_info = {
    "name": "Object to MCDisplay",
    "author": "200Q",
    "version": (0, 0, 1),
    "blender": (3, 4, 1),
    "location": "",
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
        ("Operator", "Update"): "更新",
        ("*", "Auto Update"): "自動更新",
        ("*", "Show in header"): "ヘッダーに表示",
        ("*", "Object Number"): "番号"
    }
}
if "bpy" in locals():
    import imp
    imp.reload(object)
    imp.reload(render)
    imp.reload(command)
    imp.reload(link)
    imp.reload(list)
else:
    from . import object
    from . import render
    from . import command
    from . import link
    from . import list
import bpy
from bpy.app.handlers import persistent

# blender起動時に実行
@persistent
def load_handler(self, context):
    render.update(None, bpy.context.scene)
    object.item_regist()
    bpy.types.VIEW3D_MT_make_links.append(link.prop_link)

def register():
    bpy.app.translations.register(__name__, O2MCD_translation_dict)
    bpy.app.handlers.load_post.append(load_handler)
    render.register()
    command.register()
    object.register()
    link.register()
    list.register()


def unregister():
    bpy.app.translations.unregister(__name__)
    render.unregister()
    command.unregister()
    object.unregister()
    link.unregister()
    list.unregister()
    bpy.app.handlers.depsgraph_update_post.remove(O2MCD.chenge_panel)


if __name__ == "__main__":
    register()