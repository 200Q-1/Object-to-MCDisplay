# Object-to-MCDisplay
オブジェクトのトランスフォームをMinecraftのDisplayエンティティのtransformationを設定するコマンドに変換します。  

<img src="https://user-images.githubusercontent.com/83889618/226501479-5885f331-2b83-4d56-9347-02660df6d229.gif" width="540">

## 使い方
### モデルの用意
+ [Blockbench](https://www.blockbench.net)で作成したモデルを`.obj`に書き出します。  
  <img src="https://user-images.githubusercontent.com/83889618/226502833-c72aa599-4611-4e2a-a485-ce2c0520bbd4.png" width="540">
+ モデルをblenderにインポートします。  
  エレメントが複数ある場合は`結合[Ctrl]J`で一つのオブジェクトにまとめます。  
+ z軸を180°回転させ、モデルが正面を向いている状態で回転を`適応[Ctrl]A`します。  
  <img src="https://user-images.githubusercontent.com/83889618/226503465-f2b9d1a5-7835-4af7-95dc-f5172bbb54e8.png" width="540">

### インターフェイス
#### O2MCDパネル
アドオンをインストールすると、出力プロパティにO2MCDパネルが追加されます。  
  横のチェックボックスにチェックを入れることでアドオンが有効になります。
+ `更新`：オブジェクトの情報を取得してコマンドを新しくします。
+ `自動更新`：シーンに変更があるか、フレームを移動するたびに更新をするようにします。
+ `丸め`：取得する値の桁数を設定できます。
+ `現在のフレーム`：ファイルを１つだけ生成します。
+ `アニメーション`：先頭フレームから最終フレームまでのファイルを生成します。
+ `パス`：ファイルの出力場所を設定します。`現在のフレーム`と`アニメーション`で別の値を設定できます。
+ `エクスポート`：指定したパスにファイルを書き出します。

#### Displayプロパティパネル
アドオンを有効にするとオブジェクトにDisplayプロパティパネルが追加されます。