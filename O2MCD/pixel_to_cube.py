import bpy
import bmesh
import os


def _load_image_data(image_path):
    img = bpy.data.images.load(image_path, check_existing=True)
    width, height = img.size
    pixel_data = img.pixels[:]
    pixels = []
    for y in range(height - 1, -1, -1):
        for x in range(width):
            idx = (y * width + x) * 4
            r = int(pixel_data[idx] * 255)
            g = int(pixel_data[idx + 1] * 255)
            b = int(pixel_data[idx + 2] * 255)
            a = int(pixel_data[idx + 3] * 255)
            pixels.append((r, g, b, a))
    return width, height, pixels


def _move_object_to_collection(obj, target_collection):
    for coll in list(obj.users_collection):
        if coll != target_collection:
            coll.objects.unlink(obj)
    if target_collection not in obj.users_collection:
        target_collection.objects.link(obj)


def _add_wireframe_to_bmesh(bm, width, height, scale_factor, cube_size, uv_layer):
    origin_x = -width * scale_factor / 2.0
    origin_y = -height * scale_factor / 2.0
    z_base = -cube_size / 2.0
    z_top = cube_size / 2.0

    # グリッド頂点を作成（底面と上面）
    verts_bottom = []
    verts_top = []
    for row in range(height + 1):
        for col in range(width + 1):
            x = origin_x + col * scale_factor
            y = origin_y + row * scale_factor
            verts_bottom.append(bm.verts.new((x, y, z_base)))
            verts_top.append(bm.verts.new((x, y, z_top)))

    # 水平方向の辺を作成（底面と上面）
    for row in range(height + 1):
        for col in range(width):
            idx = row * (width + 1) + col
            bm.edges.new([verts_bottom[idx], verts_bottom[idx + 1]])
            bm.edges.new([verts_top[idx], verts_top[idx + 1]])

    # 垂直方向の辺を作成（縦の辺）
    for row in range(height):
        for col in range(width + 1):
            idx = row * (width + 1) + col
            bm.edges.new([verts_bottom[idx], verts_bottom[idx + (width + 1)]])
            bm.edges.new([verts_top[idx], verts_top[idx + (width + 1)]])


def image_to_3d_cubes(image_path, cube_size=1.0, scale_factor=1.0):
    """
    画像の不透明なピクセルにキューブを配置して3D化する（テクスチャ使用、頂点マージ済み）
    
    Args:
        image_path: 画像ファイルのパス
        cube_size: キューブのサイズ
        scale_factor: ピクセルあたりのスケール係数
    """
    if not os.path.exists(image_path):
        print(f"画像ファイルが見つかりません: {image_path}")
        return
    
    width, height, img_data = _load_image_data(image_path)
    
    # 既存のメッシュを削除
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # コレクションを作成
    collection_name = "image_3d"
    if collection_name not in bpy.data.collections:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
    else:
        collection = bpy.data.collections[collection_name]
    
    # BMeshを作成
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    
    # ピクセルグリッドから不透明ピクセルをマップ
    pixel_map = {}
    for y in range(height):
        for x in range(width):
            pixel_index = (height - 1 - y) * width + x
            r, g, b, a = img_data[pixel_index]
            if a > 1:
                pixel_map[(x, y)] = (r, g, b, a)
    
    # キューブを作成（隣接チェック付き）
    center_x = (width - 1) / 2.0
    center_y = (height - 1) / 2.0
    for (x, y), (r, g, b, a) in pixel_map.items():
        cx = (x - center_x) * scale_factor
        cy = (y - center_y) * scale_factor
        cz = 0
        hs = cube_size / 2.0
        
        # 8頂点を作成
        v0 = bm.verts.new((cx - hs, cy - hs, cz - hs))
        v1 = bm.verts.new((cx + hs, cy - hs, cz - hs))
        v2 = bm.verts.new((cx + hs, cy + hs, cz - hs))
        v3 = bm.verts.new((cx - hs, cy + hs, cz - hs))
        v4 = bm.verts.new((cx - hs, cy - hs, cz + hs))
        v5 = bm.verts.new((cx + hs, cy - hs, cz + hs))
        v6 = bm.verts.new((cx + hs, cy + hs, cz + hs))
        v7 = bm.verts.new((cx - hs, cy + hs, cz + hs))
        
        # 隣接チェック（面を作成するかを決定）
        has_neg_y = (x, y - 1) not in pixel_map
        has_pos_y = (x, y + 1) not in pixel_map
        has_neg_x = (x - 1, y) not in pixel_map
        has_pos_x = (x + 1, y) not in pixel_map
        
        # UV座標
        uv_x = (x + 0.5) / float(width)
        uv_y = (y + 0.5) / float(height)
        
        # 見えている面だけを作成
        face_list = [
            ([v0, v1, v2, v3], True),           # 底面
            ([v4, v5, v6, v7], True),           # 上面
            ([v0, v1, v5, v4], has_neg_y),       # -Y面
            ([v2, v3, v7, v6], has_pos_y),       # +Y面
            ([v0, v3, v7, v4], has_neg_x),       # -X面
            ([v1, v2, v6, v5], has_pos_x),       # +X面
        ]
        
        for face_verts, should_create in face_list:
            if should_create:
                face = bm.faces.new(face_verts)
                for loop in face.loops:
                    loop[uv_layer].uv = (uv_x, uv_y)
    
    # ワイヤーフレームを追加
    _add_wireframe_to_bmesh(bm, width, height, scale_factor, cube_size, uv_layer)
    
    # 頂点をマージ
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    
    # メッシュデータを作成
    mesh = bpy.data.meshes.new("image_3d_mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    # メッシュオブジェクトを作成
    obj = bpy.data.objects.new("image_3d_obj", mesh)
    collection.objects.link(obj)
    mesh.update()
    
    # テクスチャをロード
    tex_img = bpy.data.images.load(image_path, check_existing=True)
    
    # マテリアルを作成（テクスチャ使用）
    mat = bpy.data.materials.new(name="image_3d_material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("プリンシプルBSDF") or mat.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    
    tex_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
    tex_node.image = tex_img
    mat.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    
    obj.data.materials.append(mat)
    
    print(f"3D化完了: {width}x{height}の画像から1つのメッシュを作成しました")


def image_to_height_map(image_path, cube_size=1.0, scale_factor=1.0, height_scale=0.5):
    """
    画像の明度を高さに変換してハイトマップ化する（テクスチャ使用、頂点マージ済み）
    
    Args:
        image_path: 画像ファイルのパス
        cube_size: キューブのサイズ
        scale_factor: ピクセルあたりのスケール係数
        height_scale: 高さのスケール係数
    """
    if not os.path.exists(image_path):
        print(f"画像ファイルが見つかりません: {image_path}")
        return
    
    width, height, img_data = _load_image_data(image_path)
    
    # 既存のメッシュを削除
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # コレクションを作成
    collection_name = "height_map_3d"
    if collection_name not in bpy.data.collections:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
    else:
        collection = bpy.data.collections[collection_name]
    
    # BMeshを作成
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    
    # ピクセルグリッドから見えるピクセルをマップ
    pixel_map = {}
    for y in range(height):
        for x in range(width):
            pixel_index = (height - 1 - y) * width + x
            r, g, b, a = img_data[pixel_index]
            if a > 10:
                brightness = (r + g + b) / 765.0
                pixel_map[(x, y)] = (r, g, b, a, brightness)
    
    # キューブを作成（隣接チェック付き）
    center_x = (width - 1) / 2.0
    center_y = (height - 1) / 2.0
    for (x, y), (r, g, b, a, brightness) in pixel_map.items():
        cx = (x - center_x) * scale_factor
        cy = (y - center_y) * scale_factor
        cz = brightness * height_scale
        hs = cube_size / 2.0
        
        # 8頂点を作成
        v0 = bm.verts.new((cx - hs, cy - hs, cz - hs))
        v1 = bm.verts.new((cx + hs, cy - hs, cz - hs))
        v2 = bm.verts.new((cx + hs, cy + hs, cz - hs))
        v3 = bm.verts.new((cx - hs, cy + hs, cz - hs))
        v4 = bm.verts.new((cx - hs, cy - hs, cz + hs))
        v5 = bm.verts.new((cx + hs, cy - hs, cz + hs))
        v6 = bm.verts.new((cx + hs, cy + hs, cz + hs))
        v7 = bm.verts.new((cx - hs, cy + hs, cz + hs))
        
        # 隣接チェック（面を作成するかを決定）
        has_neg_y = (x, y - 1) not in pixel_map
        has_pos_y = (x, y + 1) not in pixel_map
        has_neg_x = (x - 1, y) not in pixel_map
        has_pos_x = (x + 1, y) not in pixel_map
        
        # UV座標
        uv_x = (x + 0.5) / float(width)
        uv_y = (y + 0.5) / float(height)
        
        # 見えている面だけを作成
        face_list = [
            ([v0, v1, v2, v3], True),           # 底面
            ([v4, v5, v6, v7], True),           # 上面
            ([v0, v1, v5, v4], has_neg_y),       # -Y面
            ([v2, v3, v7, v6], has_pos_y),       # +Y面
            ([v0, v3, v7, v4], has_neg_x),       # -X面
            ([v1, v2, v6, v5], has_pos_x),       # +X面
        ]
        
        for face_verts, should_create in face_list:
            if should_create:
                face = bm.faces.new(face_verts)
                for loop in face.loops:
                    loop[uv_layer].uv = (uv_x, uv_y)
    
    # ワイヤーフレームを追加
    _add_wireframe_to_bmesh(bm, width, height, scale_factor, cube_size, uv_layer)
    
    # 頂点をマージ
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    
    # メッシュデータを作成
    mesh = bpy.data.meshes.new("height_map_mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    # メッシュオブジェクトを作成
    obj = bpy.data.objects.new("height_map_obj", mesh)
    collection.objects.link(obj)
    mesh.update()
    
    # テクスチャをロード
    tex_img = bpy.data.images.load(image_path, check_existing=True)
    
    # マテリアルを作成（テクスチャ使用）
    mat = bpy.data.materials.new(name="height_map_material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("プリンシプルBSDF") or mat.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    
    tex_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
    tex_node.image = tex_img
    mat.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    
    obj.data.materials.append(mat)
    
    print(f"ハイトマップ化完了: {width}x{height}の画像から1つのメッシュを作成しました")
    
# image_to_3d_cubes(bpy.data.images['apple.png'].filepath)

classes = (
    
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)