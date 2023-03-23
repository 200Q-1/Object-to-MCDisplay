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
start : tellraw @a {"text":"最初に1つだけ生成されます。"}
end : tellraw @a {"text":"最後に1つだけ生成されます。"}
```
`[Ctrl]/`でコマンドをエスケープすることも出来ます。
```python
#Outputに生成されません
##「#」を重ねるか、
# スペースを入れることでmcfunctionのコメントとして出力することも出来ます
```
関数を使用してオブジェクトのプロパティを代入することも出来ます。
#### 関数
+ `/loc`：translationの値です。  
+ `/scale`：scaleの値です。  
+ `/l_rot`：left_rotationの値です。デフォルトで180°回転しているので必ず入力してください。  
+ `/r_rot`：right_rotationの値です。ペアレントの回転がここに代入されます。  
+ `transf`：right_rotation、scale、left_rotation、translationが一括で入力されます。
+ `/name`：オブジェクト名です。  
+ `/id`：オブジェクト名から.001を除いた値です。
+ `/type`：オブジェクトのタイプです。`その他`の場合は任意の値を設定できます。
+ `/model`：プロパティの`CustomModelData`の値です。
+ `/item`：プロパティの`ItemTag`の値です。
+ `prop`：プロパティの`properties`の値です。
+ `/tags`：プロパティの`tags`の値が`""`で囲われて出力されます。
+ `/tag`：プロパティの`tags`の値の前に`tag=`がついて出力されます。
+ `/extra`：プロパティの`ExtraNBT`の値です。
+ `/num`：オブジェクトの番号です。

`[]`を付けて引数を渡すことも出来ます。  
`[エレメント,フレーム数,オブジェクト]`
+ エレメント：要素番号です。`/loc[0]`でx座標だけを入力することが出来ます。
+ フレーム数：`/loc[,0]`でフレームを指定できます。`/loc[,-1] /loc[,+1]`で現在のフレームからの相対値を指定できます。
+ オブジェクト：`/loc[,,stone.001]`でオブジェクト名、`/loc[,,1]`でオブジェクト番号を指定できます。

`/math[]`：`[]`の中に数式を書くことが出来ます。`/math[/scale[0]*10]`のように中に関数を入れることも出来ます。
### サンプル
```python
#召喚
item:summon /type ~ ~ ~ {item:{id:"minecraft:/id",Count:1b,tag:{CustomModelData:/model}},Tags:["sample/num"],item_display:"none",transformation:{/transf}}
block:summon /type ~ ~ ~ {block_state:{Name:"minecraft:/id"},Tags:["sample/num"],transformation:{/transf}}

#モーション
data merge entity @e[tag=sample/num,limit=1] {transformation:{/transf}}

#前フレームとの差分をスコアに入れて加算
scoreboard players set @e[tag=sample/num] loc_x_diff /math[int((/loc[0]-/loc[0,-1])*1000)]
execute as @e[tag=sample/num] run scoreboard players operation @s loc_x += @s loc_x_diff
```
