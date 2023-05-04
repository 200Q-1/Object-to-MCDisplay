import bpy
import random
from . import command
from re import *

def chenge_panel(self, context):  # オブジェクトリストとオブジェクト番号を更新
    scene=bpy.context.scene
    list=[]
    for i, l in enumerate(scene.O2MCD_object_list):
        if not l.obj == None and l.obj.name in context.view_layer.objects:
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
            
class OBJECTTOMCDISPLAY_OT_list_move(bpy.types.Operator): #移動
    bl_idname = "render.o2mcd_list_move"
    bl_label = ""
    bl_description = "Rearrange the order of objects"
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
class OBJECTTOMCDISPLAY_OT_Sort(bpy.types.Operator): #ソート
    bl_idname = "render.o2mcd_sort"
    bl_label = ""
    bl_description = "Sorting Objects"
    action: bpy.props.EnumProperty(items=(('NAME', "Name", "名前順"),('CREATE',"Create","作成順"),('SHUFFLE',"Shuffle","ランダム")))
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
        self.report({'INFO'}, "Objects have been reordered")
        return {"FINISHED"}
class OBJECTTOMCDISPLAY_OT_DataPath(bpy.types.Operator): #データパス
    bl_idname = "render.o2mcd_data_path"
    bl_label = ""
    bl_description = "Sorting Objects"
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
            self.report({'INFO'}, "Objects have been reordered")
        except:
            self.report({'ERROR'}, "No data available")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_props_popup(self, event)
        return {'FINISHED'}
class OBJECTTOMCDISPLAY_MT_Sort(bpy.types.Menu):
    bl_label = ""
    bl_description = "Sorting Objects"
    def draw(self, context):
        layout = self.layout
        layout.operator("render.o2mcd_sort", text="Name").action = 'NAME'
        layout.operator("render.o2mcd_sort", text="Create").action = 'CREATE'
        layout.operator("render.o2mcd_sort", text="Shuffle").action = 'SHUFFLE'
        layout.operator("render.o2mcd_data_path", text="DataPath")
        
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
    OBJECTTOMCDISPLAY_OT_list_move,
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