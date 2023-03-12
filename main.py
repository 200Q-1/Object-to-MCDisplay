import bpy
import mathutils
import os
import re
from math import *

bl_info = {
    "name" : "Object to mcDisplay",
    "author" : "200Q",
    "version" : (0, 0, 1),
    "blender" : (3, 4, 1),
    "location" : "",
    "description" : "",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "Object"
}

#プロパティパネル
class DisplayProperties(bpy.types.Panel):
    bl_idname = "display_properties"
    bl_label = "Display Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    @classmethod
    def poll(cls, context):
        return bpy.context.active_object and bpy.context.scene.my_props.enable
    def draw(self, context):
        layout = self.layout
        layout.prop(context.active_object.my_object_properties, "Type",expand=True)
        if not context.active_object.my_object_properties.Type == "NONE":
            layout.prop(context.active_object.my_object_properties, "Tags")
            if context.active_object.my_object_properties.Type == "ITEM":
                layout.prop(context.active_object.my_object_properties, "CustomModelData")
                layout.prop(context.active_object.my_object_properties, "ItemTag")
            if context.active_object.my_object_properties.Type == "BLOCK":
                layout.prop(context.active_object.my_object_properties, "Properties")
            layout.prop(context.active_object.my_object_properties, "ExtraNBT")
        
#更新ボタン
def reload(self, context):
    layout = self.layout
    row = layout.row()
    row.alignment="LEFT"
    row.operator("render.reload")
    row.prop(context.scene.my_props, "auto_reload")

def update_enable(self, context):
    if bpy.context.scene.my_props.enable == True:
        if "Input" not in bpy.data.texts : bpy.data.texts.new("Input")
        #更新ボタンを追加
        bpy.types.VIEW3D_HT_header.remove(reload)
        bpy.types.VIEW3D_HT_header.append(reload)

        if bpy.context.scene.my_props.auto_reload == True:
            bpy.app.handlers.frame_change_post.append(command_generate)
            bpy.app.handlers.depsgraph_update_post.append(command_generate)
    else:
        #更新ボタンを削除
        bpy.types.VIEW3D_HT_header.remove(reload)
        #     #更新を停止
        bpy.app.handlers.frame_change_post.remove(command_generate)
        bpy.app.handlers.depsgraph_update_post.remove(command_generate)

#更新検知
def update_auto_reload(self, context):
    if bpy.context.scene.my_props.auto_reload == True:
        bpy.app.handlers.frame_change_post.append(command_generate)
        bpy.app.handlers.depsgraph_update_post.append(command_generate)
    else:
        bpy.app.handlers.frame_change_post.remove(command_generate)
        bpy.app.handlers.depsgraph_update_post.remove(command_generate)

# オブジェクトのプロパティ
class MyObjectProperties(bpy.types.PropertyGroup):
    Type: bpy.props.EnumProperty(
    name="Object Type",
    items=[
        ('NONE', "None", ""),
        ('ITEM', "Item", ""),
        ('BLOCK', "Block", ""),
        ('EXTRA', "Extra", "")
    ],
    default='NONE',
    options={"ANIMATABLE"}
    )
    Tags: bpy.props.StringProperty(
        default=""
        )
    CustomModelData: bpy.props.IntProperty(
        default=0
        )
    ItemTag: bpy.props.StringProperty(
        default=""
        )
    Properties: bpy.props.StringProperty(
        default=""
        )
    ExtraNBT: bpy.props.StringProperty(
        default=""
        )

# パネルのプロパティ
class MyProperties(bpy.types.PropertyGroup):
    directory: bpy.props.StringProperty(
        name="パス",
        subtype='DIR_PATH',
        default="",
    )
    auto_reload: bpy.props.BoolProperty(
        name="自動更新",
        default=False,
        update=update_auto_reload
    )
    enable: bpy.props.BoolProperty(
        name="",
        default=False,
        update=update_enable
    )

#コマンド生成
def command_generate(scene):
    if "Output" not in bpy.data.texts : bpy.data.texts.new("Output")
    object_list = [i for i in bpy.context.scene.objects if not i.my_object_properties.Type == "NONE" and i.hide_viewport == False and i.hide_render == False and i.type == "MESH"]
    input = list(bpy.data.texts["Input"].as_string().splitlines())
    #input = "\n".join([s for s in input if not re.match('^#(?! +|#+)', s)])
    input = [s for s in input if not re.match('^#(?! +|#+)', s)]
    rou = 3
    output = []

    for i in range(len(object_list)):
        o = object_list[i]
        name = o.name
        id = re.sub("(\.[0-9]*)*","",name)
        matrix = o.matrix_world
        com = []
        if o.my_object_properties.Type == "ITEM":
            com = [re.sub("^item\s?:\s?", "",s) for s in input if re.match("(?!block\s?:\s?)",s)]
            type = "item_display"
        elif o.my_object_properties.Type == "BLOCK":
            com = [re.sub("^block\s?:\s?", "",s) for s in input if re.match("(?!item\s?:\s?)",s)]
            type = "block_display"
        com = "\n".join(com)
        #位置
        loc = mathutils.Euler((radians(-90), 0, 0),'XYZ').to_matrix().to_4x4() @ matrix
        if o.my_object_properties.Type == "BLOCK":
            loc = loc @ mathutils.Matrix.Translation(mathutils.Vector((0.5,-0.5,-0.5)))
        loc = loc.translation
        loc = str(round(loc[0],rou))+"f,"+str(round(loc[1],rou))+"f,"+str(round(loc[2],rou))+"f"

        #スケール
        scale = matrix.to_scale()
        scale = str(round(scale[0],rou))+"f,"+str(round(scale[1],rou))+"f,"+str(round(scale[2],rou))+"f"

        #左回転
        if o.parent:
            if o.parent_type == "BONE":
                pass
            o.parent.matrix_world.to_euler()
        l_rot = matrix.to_euler()
        l_rot_x = mathutils.Euler((-l_rot[0], 0, 0),'XYZ').to_matrix().to_4x4()
        l_rot_y = mathutils.Euler((0, l_rot[2], 0),'XYZ').to_matrix().to_4x4()
        l_rot_z = mathutils.Euler((0, 0, l_rot[1]),'XYZ').to_matrix().to_4x4()
        l_rot = (mathutils.Euler((0, radians(180), 0),'XYZ').to_matrix().to_4x4() @ l_rot_y @ l_rot_z @ l_rot_x).to_quaternion()
        l_rot = str(round(l_rot[1],rou))+"f,"+str(round(l_rot[2],rou))+"f,"+str(round(l_rot[3],rou))+"f,"+str(round(l_rot[0],rou))+"f"
        
        #右回転
        if o.parent:
            r_rot = o.rotation_euler
            r_rot = mathutils.Euler((-r_rot[0], r_rot[2], r_rot[1]),'XYZ').to_quaternion()
        else:
            r_rot = mathutils.Euler((0, 0, 0),'XYZ').to_quaternion()
        r_rot = str(round(r_rot[1],rou))+"f,"+str(round(r_rot[2],rou))+"f,"+str(round(r_rot[3],rou))+"f,"+str(round(r_rot[0],rou))+"f"

        #コマンド書き込み
        com = com.replace("/name",name).replace("/id",id).replace("/transf","translation:[/loc],right_rotation:[/right],scale:[/scale],left_rotation:[/left]").replace("/right",r_rot).replace("/scale",scale).replace("/loc",loc).replace("/left",l_rot).replace("/type",type).replace("/model",str(o.my_object_properties.CustomModelData)).replace("/num",str(i))
        
        l=re.findall('/math\[.*?\]',com)
        c=len(l)
        l=[eval(re.sub('/math\[(.+?)\]',"\\1",i)) for i in l]
        for i in range(c) : com = re.sub("/math\[.+?\]",str(l[i]),com,1)

        output.append(com)
    #出力
    bpy.data.texts["Output"].from_string("\n".join(output))
    #テキストエディタの表示を更新
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            area.tag_redraw()


# 出力パネル
class RenderScriptPanel(bpy.types.Panel):
    bl_idname = "RENDER_PT_script_panel"
    bl_label = "Object to mcDisplay"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    
    def draw_header(self, context):
        self.layout.prop(context.scene.my_props, "enable")

    # パネル内に描画する内容
    def draw(self, context):
        reload(self, context)
        layout = self.layout
        layout.prop(context.scene.my_props, "directory")
        layout.operator("render.run_script")
        layout.enabled = context.scene.my_props.enable
# 実行ボタンの定義
class RenderRunReload(bpy.types.Operator):
    bl_idname = "render.reload"
    bl_label = "更新"

    def execute(self, context):
        command_generate(bpy.context.scene)
        return {'FINISHED'}
class RenderRunScript(bpy.types.Operator):
    bl_idname = "render.run_script"
    bl_label = "書き出し"

    def execute(self, context):
        # 出力先ディレクトリ
        directory = context.scene.my_props.directory

        # テキストブロックの名前
        text_name = "Output"

        # シーンのフレーム数を取得
        frame_end = bpy.context.scene.frame_end

        # カレントフレームを保存
        current_frame = bpy.context.scene.frame_current

        # フレームを1つずつ進めながら出力する
        for frame in range(1, frame_end+1):

            # カレントフレームを設定
            bpy.context.scene.frame_set(frame)

            # 出力するファイル名を作成
            output_file = os.path.join(directory, f"{frame}.mcfunction")

            # テキストブロックを取得
            command_generate(bpy.context.scene)
            text = bpy.data.texts.get(text_name)

            # テキストブロックが存在する場合は出力する
            if text:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text.as_string())

        # カレントフレームを元に戻す
        bpy.context.scene.frame_set(current_frame)
        return {'FINISHED'}
# Blenderに登録する関数群
classes = (
    MyProperties,
    RenderScriptPanel,
    RenderRunScript,
    RenderRunReload,
    DisplayProperties,
    MyObjectProperties,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.my_object_properties = bpy.props.PointerProperty(type=MyObjectProperties)
    bpy.types.Scene.my_props = bpy.props.PointerProperty(type=MyProperties)
    update_enable
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()