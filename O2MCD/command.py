# Copyright (c) 2023 200Q

import bpy
import mathutils
from re import *
from math import *
from . import object_list

def cmd_set(context,active):
    pre_obj=context.scene.O2MCD_props.pre_obj
    if pre_obj and pre_obj.O2MCD_props.pre_cmd >= 0:
        pre_obj.O2MCD_props.command_list[pre_obj.O2MCD_props.pre_cmd].command=bpy.data.texts["O2MCD_input"].as_string()
    if active:
        if active.O2MCD_props.command_list and active.O2MCD_props.command_index > -1:
            active.O2MCD_props.pre_cmd=active.O2MCD_props.command_index
            bpy.data.texts["O2MCD_input"].from_string(active.O2MCD_props.command_list[active.O2MCD_props.command_index].command)
        else:
            active.O2MCD_props.pre_cmd=-1
            bpy.data.texts["O2MCD_input"].from_string("コマンドリストが選択されていません。")
        context.scene.O2MCD_props.pre_obj=active


def get_position(context,obj):  # pos取得
    pos = mathutils.Matrix.Rotation(radians(-90),4,'X') @ obj.matrix_world
    rou = context.scene.O2MCD_props.rou
    pos = pos.translation
    pos = (round(pos[0], rou), round(pos[1], rou), round(pos[2], rou))
    return pos


def get_rotation(context,obj):  # 回転取得
    rou = context.scene.O2MCD_props.rou
    if obj.parent:
        if obj.parent_type == "BONE":
            rot = obj.parent.pose.bones[obj.parent_bone].matrix
            rot = obj.parent.matrix_world @ rot
            rot = rot.to_euler()
            rot = mathutils.Euler((rot[0]-1.5708, rot[1], rot[2]), 'XYZ')
        else:
            rot = obj.parent.matrix_world.to_euler()
    else:
        rot = obj.matrix_world.to_euler()  
    rot_y = mathutils.Matrix.Rotation(rot[2],4,'Y')
    if obj.O2MCD_props.disp_type == 'item_display' and context.scene.O2MCD_props.mc_version != "1.19":
        rot_x = mathutils.Matrix.Rotation(rot[0],4,'X')
        rot_z = mathutils.Matrix.Rotation(-rot[1],4,'Z')
    else:
        rot_x = mathutils.Matrix.Rotation(-rot[0],4,'X')
        rot_z = mathutils.Matrix.Rotation(rot[1],4,'Z')
    rot = (rot_y @ rot_z @ rot_x).to_euler()
    rot = [round(degrees(rot[1]), rou), round(degrees(rot[2]), rou),round(degrees(rot[0]), rou)]
    return rot

def get_matrix(context,obj,typ):
    result=[]
    obj_mat=obj.matrix_world
    rou = context.scene.O2MCD_props.rou
    #右回転
    if typ == "r_rot" or typ == "matrix":
        if obj.parent:
            r_rot = obj.rotation_euler
            r_rot_y = mathutils.Matrix.Rotation(r_rot[2],4,'Y')
            if obj.O2MCD_props.disp_type == 'item_display' and context.scene.O2MCD_props.mc_version != "1.19":
                r_rot_x = mathutils.Matrix.Rotation(r_rot[0],4,'X')
                r_rot_z = mathutils.Matrix.Rotation(-r_rot[1],4,'Z')
            else:
                r_rot_x = mathutils.Matrix.Rotation(-r_rot[0],4,'X')
                r_rot_z = mathutils.Matrix.Rotation(r_rot[1],4,'Z')
            r_rot = r_rot_y @ r_rot_z @ r_rot_x
        else:
            r_rot = mathutils.Matrix.Identity(4)
        if typ == "r_rot":
            r_rot= r_rot.to_quaternion()
            result = (str(round(r_rot[1], rou)), str(round(r_rot[2], rou)),str(round(r_rot[3], rou)), str(round(r_rot[0], rou)))
        
    #スケール    
    if typ == "scale" or typ == "matrix":
        scale = obj_mat
        if obj.parent:
            if obj.parent_type == "BONE":
                pscale = obj.parent.pose.bones[obj.parent_bone].matrix @ obj_mat
                pscale = pscale
            else:
                pscale = obj.parent.matrix_world
            if not round(pscale[0], rou) == round(pscale[1], rou) == round(pscale[2], rou):
                obj.scale = (1, 1, 1)
                scale = pscale
        if typ == "scale":
            scale= scale.to_scale()
            result = (str(round(scale[0], rou)), str(round(scale[2], rou)), str(round(scale[1], rou)))
        else:
            scale=mathutils.Matrix.LocRotScale((0,0,0), mathutils.Euler((0, 0, 0), 'XYZ'), scale.to_scale())
        
    #左回転
    if typ == "l_rot" or typ == "rot" or typ == "matrix":
        if obj.parent:
            if obj.parent_type == "BONE":
                l_rot = obj.parent.pose.bones[obj.parent_bone].matrix
                l_rot = obj.parent.matrix_world @ l_rot
                l_rot = l_rot.to_euler()
                l_rot = mathutils.Euler((l_rot[0]-1.5708, l_rot[1], l_rot[2]), 'XYZ').to_matrix()
            else:
                l_rot = obj.parent.matrix_world
        else:
            l_rot = obj_mat.to_euler()
        l_rot_y = mathutils.Matrix.Rotation(l_rot[2],4,'Y')
        if obj.O2MCD_props.disp_type == 'item_display' and context.scene.O2MCD_props.mc_version != "1.19" and typ !="rot":
            inv=mathutils.Matrix.Rotation(radians(180),4,"Y")
            l_rot_x = mathutils.Matrix.Rotation(l_rot[0],4,'X')
            l_rot_z = mathutils.Matrix.Rotation(-l_rot[1],4,'Z')
        else:
            inv=mathutils.Matrix.Identity(4)
            l_rot_x = mathutils.Matrix.Rotation(-l_rot[0],4,'X')
            l_rot_z = mathutils.Matrix.Rotation(l_rot[1],4,'Z')
        l_rot = inv @ l_rot_y @ l_rot_z @ l_rot_x
        
        if typ == "l_rot":
            l_rot= l_rot.to_quaternion()
            result = (str(round(l_rot[1], rou)), str(round(l_rot[2], rou)),str(round(l_rot[3], rou)), str(round(l_rot[0], rou)))
        elif typ == "rot":
            l_rot= l_rot.to_euler()
            result = [str(round(degrees(l_rot[1]), rou)), str(round(degrees(l_rot[2]), rou)),str(round(degrees(l_rot[0]), rou))]

    # 位置
    if typ == "loc" or typ == "matrix":
        loc = mathutils.Matrix.Rotation(radians(-90),4,'X') @ obj_mat
        if obj.O2MCD_props.disp_type=="block_display" and typ != "pos":
            loc = loc @ mathutils.Matrix.Translation(mathutils.Vector((0.5, -0.5, -0.5)))
        if typ == "loc":
            loc=loc.translation
            result = (str(round(-loc[0], rou)), str(round(loc[1], rou)), str(round(-loc[2], rou)))
        elif typ == "pos":
            loc=loc.translation
            result = (str(round(loc[0], rou)), str(round(loc[1], rou)), str(round(loc[2], rou)))
        else:
            loc=loc.translation
            loc = mathutils.Matrix.Translation(mathutils.Vector((-loc[0], loc[1], -loc[2])))
    
    if typ == "matrix":
        result=[str(round(t,rou)) for m in loc @ l_rot @ scale @ r_rot for t in m]
    return result


def comvert_function(context, funk_list, com, num):    # 関数変換
    object_list= context.scene.O2MCD_object_list                    #オブジェクトリスト
    current_frame = context.scene.frame_current                     # 現在のフレーム
    func = findall(f'(/{funk_list}(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?)', com)              # 入力から関数のリストを作成
    for f in func:                                                  # 関数を1つずつ処理
        var = sub(f'/({funk_list})(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?', "\\1", f)          # 関数名
        val = sub('/.+?\[(.+)\]', "V\\1", f)                        # 引数
        if val and not val == f and match(f".*/{funk_list}.*", val):  # 引数の中の関数を変換
            val = comvert_function(context, funk_list, val, num)
        elm = sub('V?([0-9]*?)(,.*)?', "\\1", val)                  # 要素番号
        obj = sub('V?.*?,((?:\+|\-)?.*?)', "\\1", val)          # オブジェクト
        if not var == "math" and not var == "frame":                                       # math以外の関数を処理
            if obj == "" or obj == val:              # オブジェクトを設定
                obj = object_list[num].obj
            elif match("(?:\+|\-)[0-9]+", obj):
                obj = eval(str(object_list[num].obj.O2MCD_props.number)+obj)
                if len(object_list)-1 < obj:
                    obj = len(object_list)-1
                elif 0 > obj:
                    obj = 0
                obj = object_list[obj].obj
                num = obj.O2MCD_props.number
            elif match("^[0-9]+", obj):
                obj = object_list[int(obj)].obj
                num = obj.O2MCD_props.number
            else:
                obj = context.scene.objects[obj]
            if match("loc|pos|scale|r_rot|l_rot|rot|matrix",var):
                result = get_matrix(context,obj,var)
            elif var == "prop":     # ブロックのプロパティを取得
                prop=""
                if obj.O2MCD_props.disp_type == "item_display" or obj.O2MCD_props.disp_type == "block_display":
                    modi= list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) and match(f"{m.node_group.name}(?:\.[0-9]+)?",obj.data.name), obj.modifiers))[0]
                    for i,n in enumerate(list(filter(lambda n : n.type=='MENU_SWITCH',modi.node_group.nodes))):
                        if val[1:]== n.name:
                            if n.name == "CustomModelData":
                                if context.scene.O2MCD_props.mc_version == "1.19" or context.scene.O2MCD_props.mc_version == "1.20":
                                    prop=n.name+":"+str(obj.modifiers[modi.name][f"Socket_{i+2}"])
                                else:
                                    prop="components:{\"minecraft:custom_model_data\":"+str(obj.modifiers[modi.name][f"Socket_{i+2}"])+"}"
                            else:
                                prop=n.name+":"+"\""+str(obj.modifiers[modi.name][f"Socket_{i+2}"])+"\""
            elif var == "tag" or var == "tags":     # タグをリスト化
                tags = ",".join([t.tag for t in obj.O2MCD_props.tag_list])
                if tags and not tags == f and match(f"/{funk_list}", tags):  # 引数の中の関数を変換
                    tags = comvert_function(context, funk_list, tags, num)
                tags=tags.split(",")
                    
            if elm == "" or elm == val:             # 置き換え
                if match("loc|pos|scale|r_rot|l_rot|rot|matrix",var): com = com.replace(f, ",".join(list(map(lambda x : x+"f",result))), 1)
                elif var == "pos": com = com.replace(f, "^"+result[0] +" ^"+result[1]+" ^"+result[2], 1)
                elif var == "rot": com = com.replace(f, "~"+str(result[0])+" ~"+str(result[2]), 1)
                elif var == "tag" or var == "tags":
                    if tags:
                        if var == "tags": com = com.replace(f, ",".join(["\""+i+"\"" for i in tags]), 1)
                        if var == "tag": com = com.replace(f, ",".join(["tag="+i for i in tags]), 1)
                    else: com = com.replace(f, "", 1)
            else:
                if match("loc|pos|scale|r_rot|l_rot|rot|matrix",var) : com = sub(f"/{var}\[.*?(,.*?)?\]",str(result[int(elm)]),com, 1)
                elif var == "tag" or var == "tags":
                    if tags:
                        if var == "tags": com = sub("/tags\[.*?(,.*?)?\]",tags[int(elm)],com, 1)
                        if var == "tag": com = sub("/tag\[.*?(,.*?)?\]",tags[int(elm)],com, 1)
                    else: com = com.replace(f, "", 1)
            if var == "prop":
                if prop: com = com.replace(f, prop, 1)
                else: com = com.replace(f, "", 1)
            elif var == "name": com = com.replace(f, obj.name, 1)
            elif var == "id": com = com.replace(f, obj.O2MCD_props.disp_id, 1)
            elif var == "type": com = com.replace(f, obj.O2MCD_props.disp_type, 1)
            elif var == "num": com = com.replace(f, str(num), 1)
        elif var == "frame": com = com.replace(f, str(current_frame), 1)
        if var == "math" :
            if elm == "" or elm == val:
                com= com.replace(f,"",1)
            else:
                com = com.replace(f,str(eval(sub('V?(.+)', "\\1", val))), 1)   # mathを処理
            
    return com


def command_generate(self, context):    # コマンド生成
    if command_generate in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(command_generate)
    if command_generate in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(command_generate)
    if "O2MCD_output" not in bpy.data.texts:  # Outputが無ければ作成
        bpy.data.texts.new("O2MCD_output")
        
    object_list.chenge_panel(self, context)
    funk_list = "(?:"+"|".join(bpy.context.preferences.addons[__package__].preferences.cmd_func.split(","))+")"    # 関数名
    output = []                                                     # 出力をリセット
    #   メインコマンドを出力に追加
    for l in context.scene.O2MCD_object_list:
        o = l.obj
        if not o.hide_viewport and o.O2MCD_props.enable:
            input=[]
            input=[c for cl in o.O2MCD_props.command_list if cl.enable for c in cl.command.split("\n")]
            # for c in o.O2MCD_props.command_list:
            #     if c.enable: input+=[*c.command.split("\n")]
            input = [s for s in input if not match('^#(?! +|#+)', s)]       # エスケープ
            if input:
                if [i for i in  input if match(f".*/({funk_list}).*", i)]:
                    input = "\n".join(input)
                    input = comvert_function(context, funk_list, input, o.O2MCD_props.number)
                else:input = "\n".join(input)
                output.append(input)

    # Outputに書き込み
    output = "\n".join(output)
    output = sub("[,\.][,\.]|([\{\[\(])[,\.]|[,\.]([\]\}\)])", "\\1\\2", output)
    bpy.data.texts["O2MCD_output"].from_string(output)
    # テキストエディタの表示を更新
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            area.tag_redraw()
    if bpy.context.scene.O2MCD_props.auto_reload:  # 自動更新を有効
        bpy.app.handlers.frame_change_post.append(command_generate)
        bpy.app.handlers.depsgraph_update_post.append(command_generate)

class OBJECTTOMCDISPLAY_OT_CommandListAction(bpy.types.Operator): #移動
    bl_idname = "o2mcd.command_list_action"
    bl_label = ""
    bl_description = ""
    action: bpy.props.EnumProperty(items=(('UP', "up", ""),('DOWN', "down", ""),('ADD',"add",""),('REMOVE',"remove","")))

    def execute(self, context):
        cmd_list=context.view_layer.objects.active.O2MCD_props.command_list
        cmd_index=context.view_layer.objects.active.O2MCD_props.command_index
        if self.action == 'DOWN' and context.active_object.O2MCD_props.command_index < len(context.active_object.O2MCD_props.command_list)-1:
            cmd_list.move(cmd_index, cmd_index+1)
            context.object.O2MCD_props.command_index += 1
            context.view_layer.objects.active.O2MCD_props.pre_cmd=context.view_layer.objects.active.O2MCD_props.pre_cmd+1
        elif self.action == 'UP' and context.active_object.O2MCD_props.command_index > 0:
            cmd_list.move(cmd_index, cmd_index-1)
            context.object.O2MCD_props.command_index -= 1
            context.view_layer.objects.active.O2MCD_props.pre_cmd=context.view_layer.objects.active.O2MCD_props.pre_cmd-1
        elif self.action == 'ADD':
            if "O2MCD_input" not in bpy.data.texts:
                bpy.data.texts.new("O2MCD_input")
            newcmd=cmd_list.add()
            newcmd.name = "cmd"+str(len(context.view_layer.objects.active.O2MCD_props.command_list))
            object_list.chenge_panel(self, context)
            context.view_layer.objects.active.O2MCD_props.command_index=len(cmd_list)-1
        elif self.action == 'REMOVE':
            cmd_list.remove(cmd_index)
        return {"FINISHED"}
    
    
classes = (
    OBJECTTOMCDISPLAY_OT_CommandListAction,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    if command_generate in bpy.app.handlers.frame_change_post :bpy.app.handlers.frame_change_post.remove(command_generate)
    if command_generate in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(command_generate)