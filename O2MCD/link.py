# Copyright (c) 2023 200Q

import bpy
from re import *
from math import *
# 関数
def prop_link(self, context):  # プロパティリンクボタン
    self.layout.separator()
    self.layout.operator("object.link_prop")

class OBJECTTOMCDISPLAY_OT_LinkProp(bpy.types.Operator):

    bl_idname = "o2mcd.link_prop"
    bl_label = bpy.app.translations.pgettext("Link display properties")
    bl_description = bpy.app.translations.pgettext("Transfers data from the active object to the selected object")
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行したときに呼ばれる関数
    def execute(self, context):
        for i in bpy.context.selected_objects:
            i.O2MCD_props.prop_id = context.object.O2MCD_props.prop_id
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECTTOMCDISPLAY_OT_LinkProp)


def unregister():
    bpy.utils.unregister_class(OBJECTTOMCDISPLAY_OT_LinkProp)