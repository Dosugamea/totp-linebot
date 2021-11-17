# totp-linebot
2要素認証のコード発行をLINEでやっちゃうやつ (コンセプト)

## 重要事項
このコードはコンセプトです。実際の利用を想定したコードではありません。
一度登録した認証鍵は、プロセスを終了すると消えます。

## 目的
Googleの2要素認証を LINEのBotでできたら
スマホ壊れたり無くしたりしても PC版クライアントで出せるから便利じゃない?

### メリット
- LINEからお手軽に利用できる

### デメリット
- 公式アカウントとの送受信内容はLINEに見られています
- 送った鍵は自分でトーク履歴から消さないと残り続けます
- セキュリティとは????

## 導入方法
- (なんやかんやをやって、LINE DevelopersでCHANNEL_SECRETとCHANNEL_ACCESS_TOKENを用意します)
- このリポジトリをZIPとしてダウンロードするか、git cloneします
- Pythonをインストールします
- pip install -r requirements.txt します
- .envというファイルをフォルダ内に作成して CHANNEL_SECRET=内容(改行)CHANNEL_ACCESS_TOKEN=内容 と入力します
- python3 main.py します
- (なんやかんやをやって、Webサーバーとしてアクセスできるようにします)

### TIPS
- [ngrok](https://ngrok.io)を使うと、Webサーバーを用意しなくともローカルで一旦試すことができます
  - [Qiitaなど参考](https://qiita.com/mintak21/items/fe9234d4b6a98bfc841a)
- DBにはMariaDBかMySQLかPostgreSQLかSQLiteのどれかを使おう
