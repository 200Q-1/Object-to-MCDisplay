# Object-to-MCDisplay

Minecraft 1.19でアイテムなどを自由に表示できるディスプレイエンティティが追加されました。  
このエンティティはトランスフォームを直接指定できるので様々な表現をすることが可能です。  
しかし、値を自分で計算し狙った見た目で表示させるのは大変です。  

このアドオンは、オブジェクトのトランスフォームを元にMinecraftのコマンドを生成し、Blenderで作成したオブジェクトと同じ見た目のディスプレイエンティティを作ることができます。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/steve.gif" width="540">

## 使い方

### 1. インストール

1. `編集 > プリファレンス > アドオン > インストール`からダウンロードしたO2MCD.zipを選択します。
2. アドオンを有効化し、プリファレンスを保存します。  
3. 一度Blenderを再起動します。  

### 2. モデルの追加

`ファイル > インポート > O2MCD`からjsonモデルをインポートします。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/import.png" width="540">

### 3. 出力設定

1. プロパティエディタの出力プロパティ、もしくはテキストエディタのサイドバーにあるO2MCDパネルにチェックを入れアドオンを有効化します。  
2. mcfunctionを書き出すパスを指定します。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/output.png" width="540">

### 4. プロパティ設定

1. 追加したモデルを選択し、サイドバーのアイテムにあるDisplayプロパティの`+ 新規`をクリックします。  
2. 表示された各種プロパティを設定します。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/display_prop.png" width="540">

### 5.  コマンド設定

1. テキストエディタからinputを選択します。
2. 任意のコマンドを入力します。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/input.png" width="540">  

### 6. 出力

1. O2MCDパネルの`エクスポート`を押します。もしくは`更新`を押してoutputに表示されたコマンドをコピーします。  

## インターフェイス

### アドオン設定

プロパティのデフォルトの値を設定できます。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/preferences.png" width="540">

+ `有効`：O2MCDパネルを有効化します。
+ `自動更新`：自動更新を切り替えます。
+ `丸め`：取得する値の桁数を設定します。
+ `バージョン` : バージョンを選択します。
+ `シングルフレームのパス`：カレントフレームのコマンドを出力するファイルを指定します。
+ `アニメーションのパス`：先頭フレームから最終フレームまでのコマンドを出力するファイルを指定します。
+ `ペアレントの参照元` : jsonモデルをインポートする際にparentに指定されているファイルを検索するリソースパックを追加します。
+ `Input` : Inputを生成した際に入力されるコマンドを追加します。

### O2MCDパネル

チェックボックスにチェックを入れることでアドオンが有効化され、Displayプロパティパネル、プロパティリンクメニュー、Inputが追加されます。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/output.png" width="540">

+ `バージョン` : バージョンを選択します。回転の値に影響します。
+ `更新`：オブジェクトの情報を取得してInputに応じたコマンドをOutputに生成します。
+ `自動更新`：シーンに変更があるか、フレームを移動するたびに更新をするようにします。
+ `丸め`：取得する値の桁数を設定できます。
+ `現在のフレーム`：カレントフレームのコマンドを出力します。
+ `アニメーション`：先頭フレームから最終フレームまでのコマンドを出力します。
+ `パス`：ファイルの出力場所を設定します。`現在のフレーム`と`アニメーション`で別の値を設定できます。
+ `エクスポート`：指定したパスにファイルを書き出します。
+ `ペアレントの参照元` : jsonモデルをインポートする際にparentに指定されているファイルを検索するリソースパックを追加します。
+ `オブジェクトリスト` : Displayプロパティが設定されているオブジェクトのリストです。移動やソートをすることができます。オブジェクトのチェックを外すとコマンドが生成されなくなります。

### Displayプロパティパネル

O2MCDパネルを有効にするとオブジェクトにDisplayプロパティパネルが追加されます。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/prop.png" width="540">

+ `追加` : プロパティを追加します。
+ `リンクするプロパティを閲覧` : リストからプロパティを選択することができます。
+ `リンク切断` : プロパティを未設定状態に戻します。
+ `削除` : プロパティを削除します。
+ `アイテム|ブロック|その他`：エンティティのタイプです。タイプごとに別のコマンドを設定することが出来ます。
+ `id` : /id に代入される値です。
+ `tags`：/tag(s) に代入される値です。`,`で区切って複数設定することが出来ます。全てのエンティティに同じ値を持たせる場合はここで設定する必要はありません。
+ `ExtraNBT` : /extra に代入される値です。
+ `CustomModelData` : /model に代入される値です。
+ `ItemTag` : /item に代入される値です。
+ `properties` : /prop に代入される値です。

### プロパティのリンク

O2MCDパネルを有効にすると`オブジェクト > データのリンク/転送`に"ディスプレイプロパティをリンク"が追加されます。  
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/link.png" width="540">  
アクティブオブジェクトのプロパティを選択オブジェクトのプロパティに転送することができます。

### 入力/出力

O2MCDパネルを有効にするとテキストデータブロックにInputが追加されます。
<img src="https://github.com/200Q-1/Object-to-MCDisplay/blob/master/image/input.png" width="540">

ここに任意のコマンドを入力することが出来ます。  
コマンドはObject Listのオブジェクトの数だけ生成されます。  
コマンドを入力した状態で`更新`を押すとテキストデータブロックにOutputが追加され出力結果が表示されます。  

タイプごとに別のコマンドを設定することも出来ます。

```python
item : tellraw @a {"text":"タイプがアイテムのオブジェクトに対して生成されます。"}
block : tellraw @a {"text":"タイプがブロックのオブジェクトに対して生成されます。"}
extra : tellraw @a {"text":"タイプがその他のオブジェクトに対して生成されます。"}
start : tellraw @a {"text":"最初に1つだけ生成されます。"}
end : tellraw @a {"text":"最後に1つだけ生成されます。"}
```

フレーム範囲を指定することもできます。

```python
[1] : tellraw @a {"text":"フレームが1のときだけ生成されます。"}
block[1-20] : tellraw @a {"text":"フレームが1-20の範囲内のときにタイプがブロックのオブジェクトに対して生成されます。"}
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
+ `/transf`：right_rotation、scale、left_rotation、translationが一括で入力されます。
+ `/pos`：オブジェクトの中心の座標です。
+ `/rot`：オブジェクトの回転がオイラー角で入力されます。
+ `/name`：オブジェクト名です。  
+ `/id`：プロパティの`id`の値です。
+ `/type`：オブジェクトのタイプです。`その他`の場合は任意の値を設定できます。
+ `/model`：プロパティの`CustomModelData`の値です。
+ `/item`：プロパティの`ItemTag`の値です。
+ `/prop`：プロパティの`properties`の値です。
+ `/tags`：プロパティの`tags`の値が`""`で囲われて出力されます。
+ `/tag`：プロパティの`tags`の値の前に`tag=`がついて出力されます。
+ `/extra`：プロパティの`ExtraNBT`の値です。
+ `/num`：オブジェクトの番号です。
+ `/frame` : 現在のフレームの値です。

`[]`を付けて引数を渡すことも出来ます。  
`[要素,フレーム,オブジェクト]`

+ 要素：要素番号です。`/loc[0]`でx座標だけを入力することが出来ます。
+ フレーム：`/loc[,0]`でフレームを指定できます。`/loc[,-1] /loc[,+1]`で現在のフレームからの相対値を指定できます。
+ オブジェクト：`/loc[,,stone.001]`でオブジェクト名、`/loc[,,1]`でオブジェクト番号を指定できます。

`/math[]`：`[]`の中に数式を書くことが出来ます。`/math[/scale[0]*10]`のように中に関数を入れることも出来ます。

### サンプル

#### 召喚

```python
item:summon /type ~ ~ ~ {item:{id:"minecraft:/id",Count:1b},Tags:["sample","/num"],item_display:"none",transformation:{/transf}}
block:summon /type ~ ~ ~ {block_state:{Name:"minecraft:/id"},Tags:["sample","/num"],transformation:{/transf}}
```

#### モーション

```python
data merge entity @e[tag=sample,tag=/num,limit=1] {transformation:{/transf}}
```
