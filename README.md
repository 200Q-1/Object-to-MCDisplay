# Object-to-MCDisplay
オブジェクトのトランスフォームをMinecraftのDisplayエンティティのtransformationを設定するコマンドに変換します。  

<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/steve.gif" width="540">

# 使い方
## モデルの用意
+ [Blockbench](https://www.blockbench.net)で作成したモデルを`.obj`に書き出します。  
  <img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/blockbench.png" width="540">
+ モデルをblenderにインポートします。  
  エレメントが複数ある場合は`結合[Ctrl]J`で一つのオブジェクトにまとめます。  
+ z軸を180°回転させ、モデルが正面を向いている状態で回転を`適応[Ctrl]A`します。  
  <img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/apply.png" width="540">

## インターフェイス
### O2MCDパネル
アドオンをインストールすると、出力プロパティにO2MCDパネルが追加されます。  
横のチェックボックスにチェックを入れることでアドオンが有効になります。 
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/enable.png" width="540">
#### プロパティ
+ `更新`：オブジェクトの情報を取得してコマンドを新しくします。
+ `自動更新`：シーンに変更があるか、フレームを移動するたびに更新をするようにします。
+ `丸め`：取得する値の桁数を設定できます。
+ `現在のフレーム`：ファイルを１つだけ生成します。
+ `アニメーション`：先頭フレームから最終フレームまでのファイルを生成します。
+ `パス`：ファイルの出力場所を設定します。`現在のフレーム`と`アニメーション`で別の値を設定できます。
+ `エクスポート`：指定したパスにファイルを書き出します。


### Displayプロパティパネル
アドオンを有効にするとオブジェクトにDisplayプロパティパネルが追加されます。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/prop.gif" width="540">
#### プロパティ
##### 共通
+ `なし|アイテム|ブロック|その他`：エンティティのタイプです。タイプごとに別のコマンドを設定することが出来ます。
+ `tags`：個々のエンティティに持たせるタグです。","で区切って複数設定することが出来ます。全てのエンティティに同じ値を持たせる場合はここで設定する必要はありません。
+ `ExtraNBT`
##### アイテム
+ `CustomModelData`
+ `ItemTag`
##### ブロック
+ `properties`
## 入力/出力
アドオンを有効にするとテキストデータブロックにInputが追加されます。
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/input.png" width="540">

ここに任意のコマンドを入力することが出来ます。  
コマンドはタイプが`なし`以外のオブジェクトの数だけ生成されます。  
コマンドを入力した状態で`更新`を押すとテキストデータブロックにOutputが追加され出力結果が表示されます。  

タイプごとに別のコマンドを設定することも出来ます。
```python
item : tellraw @a {"text":"タイプがアイテムのオブジェクトに対して生成されます。"}
block : tellraw @a {"text":"タイプがブロックのオブジェクトに対して生成されます。"}
extra : tellraw @a {"text":"タイプがその他のオブジェクトに対して生成されます。"}
```
`[Ctrl]/`でコマンドをエスケープすることも出来ます。
```python
#Outputに生成されません
##「#」を重ねるか、
# スペースを入れることでmcfunctionのコメントとして出力することも出来ます
```
