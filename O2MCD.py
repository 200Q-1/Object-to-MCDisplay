import bpy
import mathutils
import os
from re import *
from math import *
from bpy.app.handlers import persistent

bl_info = {
    "name" : "Object to MCDisplay",
    "author" : "200Q",
    "version" : (0, 0, 1),
    "blender" : (3, 4, 1),
    "location" : "",
    "support": "TESTING",
    "description" : "",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "Object"
}

O2MCD_translation_dict = {
    "ja_JP": {
        ("*", "Display Properties"):"Displayプロパティ",
        ("Operator", "Update"):"更新",
        ("*", "Auto Update"):"自動更新",
        ("*", "Show in header"):"ヘッダーに表示",
    }
}

def update(self, context):
    if context.scene.O2MCD_props.enable:
        if "Input" not in bpy.data.texts : bpy.data.texts.new("Input")
        if context.scene.O2MCD_props.auto_reload:
            bpy.app.handlers.frame_change_post.append(command_generate)
            bpy.app.handlers.depsgraph_update_post.append(command_generate)
        else:
            if command_generate in bpy.app.handlers.frame_change_post : bpy.app.handlers.frame_change_post.remove(command_generate)
            if command_generate in bpy.app.handlers.depsgraph_update_post : bpy.app.handlers.depsgraph_update_post.remove(command_generate)
    else:
        #更新を停止
        if command_generate in bpy.app.handlers.frame_change_post : bpy.app.handlers.frame_change_post.remove(command_generate)
        if command_generate in bpy.app.handlers.depsgraph_update_post : bpy.app.handlers.depsgraph_update_post.remove(command_generate)
#位置取得
def get_location(object):
    loc = mathutils.Euler((radians(-90), 0, 0),'XYZ').to_matrix().to_4x4() @ object.matrix_world
    rou = bpy.context.scene.O2MCD_props.rou
    if object.O2MCD_props.Types == "BLOCK":
        loc = loc @ mathutils.Matrix.Translation(mathutils.Vector((0.5,-0.5,-0.5)))
    loc = loc.translation
    loc = (round(loc[0],rou),round(loc[1],rou),round(loc[2],rou))
    return loc
#スケール取得
def get_scale(object):
    scale = object.matrix_world.to_scale()
    rou = bpy.context.scene.O2MCD_props.rou
    if object.parent:
        if object.parent_type == "BONE":
            pscale = object.parent.pose.bones[object.parent_bone].matrix @ object.matrix_world
            pscale = pscale.to_scale()
        else:
            pscale = object.parent.matrix_world.to_scale()
        if not round(pscale[0],rou)==round(pscale[1],rou)==round(pscale[2],rou):
            object.scale=(1,1,1)
            scale=pscale
    scale = (round(scale[0],rou),round(scale[1],rou),round(scale[2],rou))
    return scale
#左回転
def get_left_rotation(object):
    rou = bpy.context.scene.O2MCD_props.rou
    if object.parent:
        if object.parent_type == "BONE":
            l_rot = object.parent.pose.bones[object.parent_bone].matrix
            l_rot = object.parent.matrix_world @ l_rot
            l_rot = l_rot.to_euler()
            l_rot = mathutils.Euler((l_rot[0]-1.5708, l_rot[1], l_rot[2]),'XYZ')
        else:
            l_rot = object.parent.matrix_world.to_euler()
    else:
        l_rot = object.matrix_world.to_euler()
    l_rot_x = mathutils.Euler((-l_rot[0], 0, 0),'XYZ').to_matrix().to_4x4()
    l_rot_y = mathutils.Euler((0, l_rot[2], 0),'XYZ').to_matrix().to_4x4()
    l_rot_z = mathutils.Euler((0, 0, l_rot[1]),'XYZ').to_matrix().to_4x4()
    l_rot = (mathutils.Euler((0, radians(180), 0),'XYZ').to_matrix().to_4x4() @ l_rot_y @ l_rot_z @ l_rot_x).to_quaternion()
    l_rot = [round(l_rot[1],rou),round(l_rot[2],rou),round(l_rot[3],rou),round(l_rot[0],rou)]
    return l_rot
#右回転
def get_right_rotation(object):
    rou = bpy.context.scene.O2MCD_props.rou
    if object.parent:
        r_rot = object.rotation_euler
        r_rot = mathutils.Euler((-r_rot[0], r_rot[2], r_rot[1]),'XYZ').to_quaternion()
    else:
        r_rot = mathutils.Euler((0, 0, 0),'XYZ').to_quaternion()
    r_rot = [round(r_rot[1],rou),round(r_rot[2],rou),round(r_rot[3],rou),round(r_rot[0],rou)]
    return r_rot
#関数変換
def comvert_function(context,object_list,com,num):
    current_frame = context.scene.frame_current
    flist="(?:loc|scale|l_rot|r_rot|name|id|type|model|item|prop|tags?|num|math)"
    com = com.replace("/transf","translation:[/loc],right_rotation:[/r_rot],scale:[/scale],left_rotation:[/l_rot]")
    func=findall(f'(/{flist}(?:\[[^\[\]]*?(?:/{flist}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?)',com)
    for f in range(len(func)) :
        var=sub(f'/({flist})(?:\[[^\[\]]*?(?:/{flist}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?',"\\1",func[f])
        val = sub('/.+?\[(.+)\]',"V\\1",func[f])
        if not val == "" and not val == func[f] and match(f".*/{flist}.*",val) : val = comvert_function(context,object_list,val,num)
        elm=sub('V?([0-9]*?)(,.*)?',"\\1",val)
        frm=sub('V?.*?,((?:\+|\-)?[0-9]*?)(,.*)?',"\\1",val)
        obj=sub('V?.*?,.*?,((?:\+|\-)?.*?)',"\\1",val)
        if not var == "math":
            if frm == "" or frm == val :
                frm=str(current_frame)
            elif match("(?:\+|\-)[0-9]+",frm):
                frm=eval(str(current_frame)+frm)

            if obj == "" or obj == val :
                obj = object_list[num]
            elif match("(?:\+|\-)[0-9]+",obj):
                obj = eval(str(object_list.index(object_list[num]))+obj)
                if len(object_list)-1 < obj :
                    obj = len(object_list)-1
                elif 0 > obj :
                    obj = 0
                obj = object_list[obj]
                num = object_list.index(obj)
            elif match("[^\.][0-9]+",obj):
                obj = object_list[int(obj)]
                num = object_list.index(obj)
            else:
                obj = context.scene.objects[obj]
            context.scene.frame_set(int(frm))
            location = get_location(obj)
            scale = get_scale(obj)
            left_rotation = get_left_rotation(obj)
            right_rotation = get_right_rotation(obj)
            name = obj.name
            if obj.O2MCD_props.Types == "ITEM":
                type = "item_display"
                prop = ""
                model = str(obj.O2MCD_props.CustomModelData)
                item = obj.O2MCD_props.ItemTag
            elif obj.O2MCD_props.Types == "BLOCK":
                type = "block_display"
                prop = obj.O2MCD_props.properties
                model = ""
                item = ""
            elif obj.O2MCD_props.Types == "EXTRA":
                type = obj.O2MCD_props.type
                prop = ""
                model = ""
                item = ""
            id = sub("(\.[0-9]*)*","",name)
            tags=split(",",obj.O2MCD_props.tags)

            if elm == "" or elm == val :
                if var == "loc":
                    com = sub("/loc(\[.*?(,.*?)?\])?",str(location[0])+"f,"+str(location[1])+"f,"+str(location[2])+"f",com,1)
                if var == "scale":com = sub("/scale(\[.*?(,.*?)?\])?",str(scale[0])+"f,"+str(scale[1])+"f,"+str(scale[2])+"f",com,1)
                if var == "r_rot":com = sub("/r_rot(\[.*?(,.*?)?\])?",str(right_rotation[0])+"f,"+str(right_rotation[1])+"f,"+str(right_rotation[2])+"f,"+str(right_rotation[3])+"f",com,1)
                if var == "l_rot":com = sub("/l_rot(\[.*?(,.*?)?\])?",str(left_rotation[0])+"f,"+str(left_rotation[1])+"f,"+str(left_rotation[2])+"f,"+str(left_rotation[3])+"f",com,1)
                if not obj.O2MCD_props.tags == "":
                    if var == "tags" : com = sub("/tags(\[.*?(,.*?)?\])?",",".join(["\""+i+"\"" for i in tags]),com,1)
                    if var == "tag" : com = sub("/tag(\[.*?(,.*?)?\])?",",".join(["tag="+i for i in tags]),com,1)
                else: com = sub("/tags?(\[.*?(,.*?)?\])?","",com)
            else:
                if var == "loc":com = sub("/loc\[.*?(,.*?)?\]",str(location[int(elm)]),com,1)
                if var == "scale":com = sub("/scale\[.*?(,.*?)?\]",str(scale[int(elm)]),com,1)
                if var == "r_rot":com = sub("/r_rot\[.*?(,.*?)?\]",str(right_rotation[int(elm)]),com,1)
                if var == "l_rot":com = sub("/l_rot\[.*?(,.*?)?\]",str(left_rotation[int(elm)]),com,1)
                if not obj.O2MCD_props.tags == "":
                    if var == "tags" : com = sub("/tags\[.*?(,.*?)?\]",tags[int(elm)],com,1)
                    if var == "tag" : com = sub("/tag\[.*?(,.*?)?\]",tags[int(elm)],com,1)
                else:
                    com = sub("/tags?(\[.*?(,.*?)?\])?","",com)
            if not prop == "":
                if var == "prop" : com = sub("/prop(\[.*?(,.*?)?\])?",prop,com,1)
            else:
                com = sub("/prop?(\[.*?(,.*?)?\])?","",com)
            if not model == "":
                if var == "model" : com = sub("/model(\[.*?(,.*?)?\])?",model,com,1)
            else:
                com = sub("/item?(\[.*?(,.*?)?\])?","",com)
            if not item == "":
                if var == "item" : com = sub("/item(\[.*?(,.*?)?\])?",item,com,1)
            else:
                com = sub("/item?(\[.*?(,.*?)?\])?","",com)
            if var == "name" : com = sub("/name(\[.*?(,.*?)?\])?",name,com,1)
            if var == "id" : com = sub("/id(\[.*?(,.*?)?\])?",id,com,1)
            if var == "type" : com = sub("/type(\[.*?(,.*?)?\])?",type,com,1)
            if var == "num" : com = sub("/num(\[.*?(,.*?)?\])?",str(num),com,1)
        if var == "math" :
            com = sub("/math\[.+\]+",str(eval(sub('V?(.+)',"\\1",val))),com,1)
    if not current_frame == context.scene.frame_current : context.scene.frame_set(current_frame)
    return com

#コマンド生成
def command_generate(self, context):
    if command_generate in bpy.app.handlers.frame_change_post : bpy.app.handlers.frame_change_post.remove(command_generate)
    if command_generate in bpy.app.handlers.depsgraph_update_post : bpy.app.handlers.depsgraph_update_post.remove(command_generate)
    if "Output" not in bpy.data.texts : bpy.data.texts.new("Output")
    object_list = [i for i in context.scene.objects if not i.O2MCD_props.Types == "NONE" and i.hide_viewport == False and i.hide_render == False and i.type == "MESH"]
    input = list(bpy.data.texts["Input"].as_string().splitlines())
    input = [s for s in input if not match('^#(?! +|#+)', s)]
    output = []
    com = [sub("^start\s?:\s?", "",s) for s in input if match("start\s?:\s?.*",s)]
    if not com == []:
        com = "\n".join(com)
        com = comvert_function(context,object_list,com,0)
        output.append(com)
    for oi in range(len(object_list)):
        o = object_list[oi]
        com = []
        if o.O2MCD_props.Types == "ITEM":
            com = [sub("^item\s?:\s?", "",s) for s in input if match("(?!block|extra|start|end\s?:\s?)",s)]
        elif o.O2MCD_props.Types == "BLOCK":
            com = [sub("^block\s?:\s?", "",s) for s in input if match("(?!item|extra|start|end\s?:\s?)",s)]
        elif o.O2MCD_props.Types == "EXTRA":
            com = [sub("^extra\s?:\s?", "",s) for s in input if match("(?!block|item|start|end\s?:\s?)",s)]
        com = "\n".join(com)
        com = comvert_function(context,object_list,com,oi)
        output.append(com)
    com = [sub("^end\s?:\s?", "",s) for s in input if match("end\s?:\s?.*",s)]
    if not com == []:
        com = "\n".join(com)
        com = comvert_function(context,object_list,com,0)
        output.append(com)
    if context.scene.O2MCD_props.auto_reload:
        bpy.app.handlers.frame_change_post.append(command_generate)
        bpy.app.handlers.depsgraph_update_post.append(command_generate)

    #出力
    bpy.data.texts["Output"].from_string("\n".join(output))
    #テキストエディタの表示を更新
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            area.tag_redraw()

#プロパティパネル
class OBJECTTOMCDISPLAY_PT_DisplayProperties(bpy.types.Panel):
    bl_label = "Display Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    @classmethod
    def poll(cls, context):
        return context.active_object and context.scene.O2MCD_props.enable
    def draw(self, context):
        layout = self.layout
        layout.prop(context.active_object.O2MCD_props, "Types",expand=True)
        if not context.active_object.O2MCD_props.Types == "NONE":
            if context.active_object.O2MCD_props.Types == "EXTRA":
                layout.prop(context.active_object.O2MCD_props, "type")
            layout.prop(context.active_object.O2MCD_props, "tags")
            if context.active_object.O2MCD_props.Types == "ITEM":
                layout.prop(context.active_object.O2MCD_props, "CustomModelData")
                layout.prop(context.active_object.O2MCD_props, "ItemTag")
            if context.active_object.O2MCD_props.Types == "BLOCK":
                layout.prop(context.active_object.O2MCD_props, "properties")
            layout.prop(context.active_object.O2MCD_props, "ExtraNBT")

# 出力パネル
class OBJECTTOMCDISPLAY_PT_MainPanel(bpy.types.Panel):
    bl_label = "O2MCD"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw_header(self, context):
        self.layout.prop(context.scene.O2MCD_props, "enable")

    # パネル内に描画する内容
    def draw(self, context):
        layout = self.layout
        row=layout.row()
        row.operator("render.reload")
        row.prop(context.scene.O2MCD_props, "auto_reload",toggle=True)
        col =  layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(context.scene.O2MCD_props, "rou")
        layout.separator()
        layout.prop(context.scene.O2MCD_props, "output",expand=True)
        box = layout.box()
        if context.scene.O2MCD_props.output == "ANIMATION":
            box.prop(context.scene.O2MCD_props, "anim_path")
        else:
            box.prop(context.scene.O2MCD_props, "curr_path")
        box.operator("render.run_script")
        layout.enabled = context.scene.O2MCD_props.enable

# 実行ボタンの定義
class OBJECTTOMCDISPLAY_OT_RunReload(bpy.types.Operator):
    bl_idname = "render.reload"
    bl_label = "Update"
    def execute(self, context):
        command_generate(self,context)
        return {'FINISHED'}
class OBJECTTOMCDISPLAY_OT_Export(bpy.types.Operator):
    bl_idname = "render.run_script"
    bl_label = "Export"

    def execute(self, context):
        # テキストブロックの名前
        text_name = "Output"

        # シーンのフレーム数を取得
        frame_end = context.scene.frame_end

        # カレントフレームを保存
        current_frame = context.scene.frame_current

        if context.scene.O2MCD_props.output == "ANIMATION":
            # 出力先ディレクトリ
            anim_path = bpy.path.abspath(context.scene.O2MCD_props.anim_path)
            # フレームを1つずつ進めながら出力する
            for frame in range(1, frame_end+1):

                # カレントフレームを設定
                context.scene.frame_set(frame)
                ofset = sub(".*?([0-9]*)$","\\1",str(os.path.splitext(anim_path)[0]))
                ext=str(os.path.splitext(anim_path)[1])
                if ofset == "" : ofset = 1
                if ext == "" : ext = ".mcfunction"
                # 出力するファイル名を作成
                output_file = sub("(.*?)([0-9]*)$","\\1",str(os.path.splitext(anim_path)[0]))+str(int(ofset)-1+frame)+ext

                # テキストブロックを取得
                command_generate(self, context)
                text = bpy.data.texts.get(text_name)

                # テキストブロックが存在する場合は出力する
                if text:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(text.as_string())
            # カレントフレームを元に戻す
            context.scene.frame_set(current_frame)
        else:
            # 出力先ディレクトリ
            curr_path = bpy.path.abspath(context.scene.O2MCD_props.curr_path)
            ext=str(os.path.splitext(curr_path)[1])
            if ext == "" : ext = ".mcfunction"
            output_file = str(os.path.splitext(curr_path)[0])+ext
            # テキストブロックを取得
            command_generate(self, context)
            text = bpy.data.texts.get(text_name)

            # テキストブロックが存在する場合は出力する
            if text:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text.as_string())
        return {'FINISHED'}

# オブジェクトのプロパティ
class O2MCD_Obj_Props(bpy.types.PropertyGroup):
    Types: bpy.props.EnumProperty(name="Object Type",items=[('NONE', "None", ""),('ITEM', "Item", ""),('BLOCK', "Block", ""),('EXTRA', "Extra", "")],default='NONE',options={"ANIMATABLE"})
    tags: bpy.props.StringProperty(default="")
    CustomModelData: bpy.props.IntProperty(default=0,min=0)
    ItemTag: bpy.props.StringProperty(default="")
    properties: bpy.props.StringProperty(default="")
    ExtraNBT: bpy.props.StringProperty(default="")
    type: bpy.props.StringProperty(default="")

# パネルのプロパティ
class O2MCD_Meny_Props(bpy.types.PropertyGroup):
    rou: bpy.props.IntProperty(name="Round",default=3,max=16,min=1)
    anim_path: bpy.props.StringProperty(name="Path",subtype='FILE_PATH',default="",)
    curr_path: bpy.props.StringProperty(name="Path",subtype='FILE_PATH',default="",)
    auto_reload: bpy.props.BoolProperty(name="Auto Update",default=False,update=update)
    output: bpy.props.EnumProperty(name="Output",items=[('CURRENT', "Current Frame", ""),('ANIMATION', "Animation", "")],default='CURRENT')
    enable: bpy.props.BoolProperty(name="",default=False,update=update)

# Blenderに登録する関数群
classes = (
    OBJECTTOMCDISPLAY_PT_DisplayProperties,
    OBJECTTOMCDISPLAY_PT_MainPanel,
    OBJECTTOMCDISPLAY_OT_RunReload,
    OBJECTTOMCDISPLAY_OT_Export,
    O2MCD_Meny_Props,
    O2MCD_Obj_Props,
)
@persistent
def load_handler():
    update(None,bpy.context.scene)

def register():
    bpy.app.translations.register(__name__, O2MCD_translation_dict)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Meny_Props)
    bpy.types.Object.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Obj_Props)
    bpy.app.handlers.load_post.append(load_handler)
def unregister():
    bpy.app.translations.unregister(__name__)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(load_handler)

if __name__ == "__main__":
    register()