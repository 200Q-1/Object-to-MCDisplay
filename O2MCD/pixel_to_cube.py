import bpy
import mathutils

def _load_image_data(image_path):
    width, height = image_path.size
    pixel_data = image_path.pixels[:]
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

def _rot_x_90(x, y, z):
    """Rotate point by +90 degrees around X axis and mirror X: (x,y,z) -> (-x, -z, y)

    X成分を反転することでモデルの左右を入れ替え、テクスチャの左右ミラーを補正します。
    """
    return (-x, -z, y)


def _get_pixel_scale(width, height, cube_size, scale_factor):
    """解像度に関係なくモデルの全体サイズが近くなるように、ピクセル間隔を正規化する。"""
    max_dim = max(width, height)
    if max_dim <= 0:
        return scale_factor * cube_size
    return scale_factor * cube_size / float(max_dim)


def _get_cube_xy_half_size(width, height, cube_size, scale_factor):
    """隣接して重ならないように、キューブのXY方向半サイズをピクセル間隔に合わせる。"""
    pixel_scale = _get_pixel_scale(width, height, cube_size, scale_factor)
    return pixel_scale * 0.5

def _get_cube_z_half_size(cube_size, thickness=000.1):
    """キューブのZ方向の厚みを引数で指定できるようにする。"""
    return max(cube_size * thickness, 0.001)

def image_to_3d_cubes(image_path, bm, uv_layer,index, cube_size=1, scale_factor=1, thickness=0):
    """
    画像の不透明なピクセルにキューブを配置して3D化する（テクスチャ使用、頂点マージ済み）
    
    Args:
        image_path: 画像データ
        bm: bmesh
        uv_layer: UV
        cube_size: キューブのサイズ
        scale_factor: ピクセルあたりのスケール係数
    """
    tintindex=f"tintindex{index}"
    width, height, img_data = _load_image_data(image_path)
    
    #属性を作成
    face_layer = bm.faces.layers.float.get(tintindex)
    if not face_layer:
        face_layer = bm.faces.layers.float.new(tintindex)
        
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
    pixel_scale = _get_pixel_scale(width, height, cube_size, scale_factor)
    xy_hs = _get_cube_xy_half_size(width, height, cube_size, scale_factor)
    z_hs = 1/32 + thickness*0.00002
    for (x, y), (r, g, b, a) in pixel_map.items():
        cx = (x - center_x) * pixel_scale
        cy = (y - center_y) * pixel_scale
        cz = 0.0
        
        # 8頂点を作成（X軸90度回転して生成）
        v0 = bm.verts.new(_rot_x_90(cx - xy_hs, cy - xy_hs, cz - z_hs))
        v1 = bm.verts.new(_rot_x_90(cx + xy_hs, cy - xy_hs, cz - z_hs))
        v2 = bm.verts.new(_rot_x_90(cx + xy_hs, cy + xy_hs, cz - z_hs))
        v3 = bm.verts.new(_rot_x_90(cx - xy_hs, cy + xy_hs, cz - z_hs))
        v4 = bm.verts.new(_rot_x_90(cx - xy_hs, cy - xy_hs, cz + z_hs))
        v5 = bm.verts.new(_rot_x_90(cx + xy_hs, cy - xy_hs, cz + z_hs))
        v6 = bm.verts.new(_rot_x_90(cx + xy_hs, cy + xy_hs, cz + z_hs))
        v7 = bm.verts.new(_rot_x_90(cx - xy_hs, cy + xy_hs, cz + z_hs))
        
        # 隣接チェック（面を作成するかを決定）
        has_neg_y = (x, y - 1) not in pixel_map
        has_pos_y = (x, y + 1) not in pixel_map
        has_neg_x = (x - 1, y) not in pixel_map
        has_pos_x = (x + 1, y) not in pixel_map
        
        # UV座標
        uv_x = 1.0 - ((x + 0.5) / float(width))
        uv_y = (y + 0.5) / float(height)
        
        # 見えている面だけを作成
        face_list = [
            ([v3, v2, v1, v0], True),           # 底面
            ([v4, v5, v6, v7], True),           # 上面
            ([v0, v1, v5, v4], has_neg_y),       # -Y面
            ([v2, v3, v7, v6], has_pos_y),       # +Y面
            ([v0, v3, v7, v4], has_neg_x),       # -X面
            ([v1, v2, v6, v5], has_pos_x),       # +X面
        ]
        
        for face_verts, should_create in face_list:
            if should_create:
                face = bm.faces.new(face_verts)
                face.material_index=index
                face[face_layer]=1
                v0_co = face.verts[0].co
                v1_co = face.verts[1].co
                v2_co = face.verts[2].co
                normal_vec = (v1_co - v0_co).cross(v2_co - v0_co)
                if normal_vec.length != 0.0:
                    normal_vec.normalize()
                    face_center = sum((v.co for v in face.verts), mathutils.Vector((0.0, 0.0, 0.0))) / len(face.verts)
                    cube_center = mathutils.Vector(_rot_x_90(cx, cy, cz))
                    if normal_vec.dot(face_center - cube_center) < 0.0:
                        face.normal_flip()
                for loop in face.loops:
                    loop[uv_layer].uv = (1.0 - uv_x, uv_y)
                    
        

    # bm.verts.ensure_lookup_table()

    
# image_to_3d_cubes(bpy.data.images['apple.png'].filepath)

classes = (
    
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)