# Copyright (c) 2023 200Q

import bpy
import random
from . import command
from re import *

def chenge_panel(self, context):  # オブジェクトリストとオブジェクト番号を更新
    scene=bpy.context.scene
    list=[]
    if bpy.context.view_layer.objects.active:
        scene.O2MCD_props.list_index = bpy.context.view_layer.objects.active.O2MCD_props.prop_id
    for i, l in enumerate(scene.O2MCD_object_list):
        if not l.obj == None and l.obj.name in context.view_layer.objects and l.obj.O2MCD_props.prop_id >=0:
            list.append(l.obj)
    for i in context.view_layer.objects:
        if i.O2MCD_props.prop_id >= 0 and not i in [i.obj for i in scene.O2MCD_object_list]:
            list.append(i)
    scene.O2MCD_object_list.clear()
    for i,o in enumerate(list):
        scene.O2MCD_object_list.add().obj = o
        o.O2MCD_props.number=i
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D' or 'PROPERTIES':
            area.tag_redraw()
    active=bpy.context.object
    if active and active.O2MCD_props.number >=0 and not active == scene.O2MCD_object_list[scene.O2MCD_props.obj_index].obj:
        scene.O2MCD_props.obj_index = active.O2MCD_props.number

def select_object(self, context):
    if context.view_layer.objects.active and not context.view_layer.objects.active == context.scene.O2MCD_object_list[context.scene.O2MCD_props.obj_index].obj:
        context.view_layer.objects.active=context.scene.O2MCD_object_list[context.scene.O2MCD_props.obj_index].obj
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active.select_set(True)

class OBJECTTOMCDISPLAY_OT_ListMove(bpy.types.Operator): #移動
    bl_idname = "o2mcd.list_move"
    bl_label = ""
    bl_description = bpy.app.translations.pgettext("Rearrange the order of objects")
    action: bpy.props.EnumProperty(items=(('UP', "Up", ""),('DOWN', "Down", ""),('REVERSE',"reverse","")))

    def invoke(self, context, event):
        if self.action == 'DOWN' and context.scene.O2MCD_props.obj_index < len(context.scene.O2MCD_object_list) - 1:
            context.scene.O2MCD_object_list.move(context.scene.O2MCD_props.obj_index, context.scene.O2MCD_props.obj_index+1)
            context.scene.O2MCD_props.obj_index += 1
        elif self.action == 'UP' and context.scene.O2MCD_props.obj_index >= 1:
            context.scene.O2MCD_object_list.move(context.scene.O2MCD_props.obj_index, context.scene.O2MCD_props.obj_index-1)
            context.scene.O2MCD_props.obj_index -= 1
        elif self.action == 'REVERSE':
            object_list = [i.obj.name for i in context.scene.O2MCD_object_list]
            object_list=object_list[::-1]
            context.scene.O2MCD_object_list.clear()
            for i in object_list: context.scene.O2MCD_object_list.add().obj=context.scene.objects[i]
        chenge_panel(self, context)
        if context.scene.O2MCD_props.auto_reload:command.command_generate(self, context)
        return {"FINISHED"}
    
class OBJECTTOMCDISPLAY_OT_ListReverse(bpy.types.Operator): #反転
    bl_idname = "o2mcd.list_reverse"
    bl_label = bpy.app.translations.pgettext("Reverse")
    bl_description = bpy.app.translations.pgettext("Reversing the order of objects")

    def invoke(self, context, event):
        object_list = [i.obj.name for i in context.scene.O2MCD_object_list]
        object_list=object_list[::-1]
        context.scene.O2MCD_object_list.clear()
        for i in object_list: context.scene.O2MCD_object_list.add().obj=context.scene.objects[i]
        chenge_panel(self, context)
        if context.scene.O2MCD_props.auto_reload:command.command_generate(self, context)
        return {"FINISHED"}

class OBJECTTOMCDISPLAY_OT_Sort(bpy.types.Operator): #ソート
    bl_idname = "o2mcd.sort"
    bl_label = "Sort"
    bl_description = bpy.app.translations.pgettext("Sorting Objects")
    action: bpy.props.EnumProperty(items=(('NAME', "Name", ""),('CREATE',"Create",""),('RANDOM',"Random","")))
    def invoke(self, context, event):
        object_list = [i.obj.name for i in context.scene.O2MCD_object_list]
        objects = [i.name for i in context.scene.objects if i.name in object_list]
        if self.action == 'NAME':
            object_list.sort()
            context.scene.O2MCD_object_list.clear()
            for i in object_list: context.scene.O2MCD_object_list.add().obj=context.scene.objects[i]
        elif self.action == 'CREATE':
            context.scene.O2MCD_object_list.clear()
            for i in objects: context.scene.O2MCD_object_list.add().obj=context.scene.objects[i]
        elif self.action == 'SHUFFLE':
            random.shuffle(object_list)
            context.scene.O2MCD_object_list.clear()
            for i in object_list: context.scene.O2MCD_object_list.add().obj=context.scene.objects[i]
        self.report({'INFO'}, bpy.app.translations.pgettext("Objects have been reordered"))
        return {"FINISHED"}
class OBJECTTOMCDISPLAY_OT_DataPath(bpy.types.Operator): #データパス
    bl_idname = "o2mcd.data_path"
    bl_label = bpy.app.translations.pgettext("Sort by DataPath")
    bl_description = bpy.app.translations.pgettext("Sorting Objects")
    bl_options = {'REGISTER', 'UNDO'}
    data_path: bpy.props.StringProperty(default="")
    def execute(self, context):
        if match("\[.+?\]",self.data_path):
            data=self.data_path
        else:
            data="."+self.data_path
        object_list = [i.obj.name for i in context.scene.O2MCD_object_list]
        try:
            data_list=[eval("i.obj"+data) for i in context.scene.O2MCD_object_list]
            d = dict(zip(data_list,object_list))
            s = sorted(d.items())
            context.scene.O2MCD_object_list.clear()
            for i in s:
                context.scene.O2MCD_object_list.add().obj=context.scene.objects[i[1]]
            self.report({'INFO'}, bpy.app.translations.pgettext("Objects have been reordered"))
        except:
            self.report({'ERROR'}, bpy.app.translations.pgettext("No data available"))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_props_popup(self, event)
        return {'FINISHED'}
class OBJECTTOMCDISPLAY_MT_Sort(bpy.types.Menu):
    bl_label = ""
    bl_description = bpy.app.translations.pgettext("Sorting Objects")
    def draw(self, context):
        layout = self.layout
        layout.operator("o2mcd.sort",text=bpy.app.translations.pgettext("Sort by name")).action = 'NAME'
        layout.operator("o2mcd.sort",text=bpy.app.translations.pgettext("Sort by creation")).action = 'CREATE'
        layout.operator("o2mcd.sort",text=bpy.app.translations.pgettext("Sort by random")).action = 'RANDOM'
        layout.operator("o2mcd.data_path")
        
class OBJECTTOMCDISPLAY_UL_ObjectList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row(align=True)
        row.alignment="LEFT"
        row.label(text=str(item.obj.O2MCD_props.number))
        row.prop(item.obj, "name", text="", emboss=False)
        row2=layout.row()
        row2.alignment="RIGHT"
        row2.prop(item.obj.O2MCD_props,"enable",text="")
        
class  O2MCD_ObjectList(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(name="Object",type=bpy.types.Object)

classes = (
    OBJECTTOMCDISPLAY_UL_ObjectList,
    OBJECTTOMCDISPLAY_OT_ListMove,
    OBJECTTOMCDISPLAY_OT_ListReverse,
    OBJECTTOMCDISPLAY_OT_Sort,
    OBJECTTOMCDISPLAY_MT_Sort,
    OBJECTTOMCDISPLAY_OT_DataPath,
    O2MCD_ObjectList,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_object_list = bpy.props.CollectionProperty(type=O2MCD_ObjectList)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if chenge_panel in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(chenge_panel)