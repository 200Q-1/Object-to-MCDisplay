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
    imp.reload(O2MCD)
else:
    from . import O2MCD
import bpy
from bpy.app.handlers import persistent

classes = (
    O2MCD.OBJECTTOMCDISPLAY_PT_DisplayProperties,
    O2MCD.OBJECTTOMCDISPLAY_PT_MainPanel,
    O2MCD.OBJECTTOMCDISPLAY_OT_Reload,
    O2MCD.OBJECTTOMCDISPLAY_OT_Export,
    O2MCD.OBJECTTOMCDISPLAY_OT_prop_action,
    O2MCD.OBJECTTOMCDISPLAY_OT_searchPopup,
    O2MCD.OBJECTTOMCDISPLAY_UL_ObjectList,
    O2MCD.OBJECTTOMCDISPLAY_OT_list_move,
    O2MCD.O2MCD_Meny_Props,
    O2MCD.O2MCD_Obj_Props,
    O2MCD.O2MCD_ListItem,
    O2MCD.O2MCD_ObjectList,
    O2MCD.O2MCD_ItemList,
    O2MCD.O2MCD_BlockList
)

# blender起動時に実行
@persistent
def load_handler(self, context):
    O2MCD.update(None, bpy.context.scene)
    O2MCD.item_regist()

def register():
    bpy.app.translations.register(__name__, O2MCD_translation_dict)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_props = bpy.props.PointerProperty(type=O2MCD.O2MCD_Meny_Props)
    bpy.types.Object.O2MCD_props = bpy.props.PointerProperty(type=O2MCD.O2MCD_Obj_Props)
    bpy.types.Scene.prop_list = bpy.props.CollectionProperty(type=O2MCD.O2MCD_ListItem)
    bpy.types.Scene.object_list = bpy.props.CollectionProperty(type=O2MCD.O2MCD_ObjectList)
    bpy.types.Scene.item_list = bpy.props.CollectionProperty(type=O2MCD.O2MCD_ItemList)
    bpy.types.Scene.block_list = bpy.props.CollectionProperty(type=O2MCD.O2MCD_BlockList)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.app.translations.unregister(__name__)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.frame_change_post.remove(O2MCD.command_generate)
    bpy.app.handlers.depsgraph_update_post.remove(O2MCD.command_generate)
    bpy.app.handlers.depsgraph_update_post.remove(O2MCD.chenge_panel)


if __name__ == "__main__":
    register()