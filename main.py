import bpy
import os
import bpy

def my_handler(scene):
    print("Scene updated:", scene.name)

bpy.app.handlers.scene_update_pre.append(my_handler)

def update_bool(self, context):
    bpy.data.node_groups["アマスタ計算機"].autoExecution.sceneChanged = self.auto_reload

# プロパティを定義するクラス
class MyProperties(bpy.types.PropertyGroup):
    directory: bpy.props.StringProperty(
        name="パス",
        subtype='DIR_PATH',
        default="",
    )
    reload: bpy.props.BoolProperty(
        name="更新",
        default=False
    )
    auto_reload: bpy.props.BoolProperty(
        name="自動更新",
        default=False,
        update=update_bool
    )

# パネルの定義
class RenderScriptPanel(bpy.types.Panel):
    bl_idname = "RENDER_PT_script_panel"
    bl_label = "mcfunction"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='TEXT')

    # パネル内に描画する内容
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.my_props, "directory")
        layout.operator("render.run_script")


class ReloadPanel(bpy.types.Panel):
    bl_idname = "reload_panel"
    bl_label = "コマンド"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "コマンド"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='TEXT')

    # パネル内に描画する内容
    def draw(self, context):
        layout = self.layout
        layout.operator("render.reload")
        layout.prop(context.scene.my_props, "auto_reload")
        
# 実行ボタンの定義
class RenderRunReload(bpy.types.Operator):
    bl_idname = "render.reload"
    bl_label = "更新"

    def execute(self, context):
        # ここに実行するスクリプトを記述
        context.scene.my_props.reload = not context.scene.my_props.reload
        return {'FINISHED'}


class RenderRunScript(bpy.types.Operator):
    bl_idname = "render.run_script"
    bl_label = "書き出し"

    def execute(self, context):
        # ここに実行するスクリプトを記述
        # 出力先ディレクトリ
        directory = context.scene.my_props.directory

        # テキストブロックの名前
        text_name = "出力"

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
            text = bpy.data.texts.get(text_name)

            # テキストブロックが存在する場合は出力する
            if text:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text.as_string())

            # テキストブロックが存在しない場合はエラーメッセージを表示
            else:
                print(f"テキストブロック {text_name} が見つかりません。")

        # カレントフレームを元に戻す
        bpy.context.scene.frame_set(current_frame)
        return {'FINISHED'}


# Blenderに登録する関数群
classes = (
    MyProperties,
    RenderScriptPanel,
    RenderRunScript,
    RenderRunReload,
    ReloadPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_props = bpy.props.PointerProperty(type=MyProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.my_props


if __name__ == "__main__":
    register()
