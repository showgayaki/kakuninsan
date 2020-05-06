# kakuninsan
**要MySQLサーバー**
 - 回線速度の計測
 - グローバルIPが更新されたか確認
 - 直近24時間分の回線速度をグラフ化
 - 上記をHTMLメールで通知（24時間に1回）
 - HTMLに書き出すのでnginxとかでアレすれば、ブラウザからデータ閲覧可

## 設定
.env.sampleを.envにリネームして、各項目に入力。  
```
DB_HOST=[データベースサーバーのURL or IPアドレス]
DB_NAME=[データベースの名前]
DB_USER=[データベースのユーザー名]
DB_PASS=[データベースのパスワード]
TABLE_NAME=[テーブル名]

CLM_COMPUTER_NAME=[カラム名]
CLM_GLOBAL_IP_ADDRESS=[カラム名]
CLM_DOWNLOAD=[カラム名]
CLM_UPLOAD=[カラム名]
CLM_IMAGE_URL=[カラム名]
CLM_CREATED_AT=[カラム名]
CLM_UPDATED_AT=[カラム名]

SMTP_SERVER=[SMTPサーバー]
SMTP_PORT=[SMTPポート]
SMTP_USER=[送信元メールアドレス]
SMTP_PASS=[送信元メールアドレスのパスワード]
MAIL_TO=[送信先メールアドレス]
MAIL_SEND_TIME=[メール送信する時間 ex)06:00]

IS_RUNNING_WEB_SERVER=[Webサーバーが動いているかどうか:True or False]
DOCUMENT_ROOT=[HTMLの書き出し場所]
```

## kakuninsanインストール
`$ git clone [ここのURL].git`  
`$ cd kakuninsan`

（仮想環境をプロジェクトディレクトリ配下に作る場合  
`$ export PIPENV_VENV_IN_PROJECT=true`）  
`$ pipenv install`

## cron設定
こんな感じで設定。下記は毎時30分に実行の例。  
`30 * * * * /home/ubuntu/apps/kakuninsan/run.sh`

設定するときは、上記を書いた別ファイルを用意しておいて、  
`$ crontab -u ubuntu cron.txt`  
とやったほうが安全ぽい（ユーザー：ubuntu、別ファイル：cron.txtの場合）。

## nginx設定
`$ sudo vi /etc/nginx/sites-available/default`
以下location〜箇所を追記。
```
server {
        〜〜〜省略〜〜〜
        location /kakuninsan {
                alias /home/ubuntu/apps/kakuninsan/html/;
        }
}
```
追記したら  
`$ sudo nginx -s reload`

## サンプル
![kakuninsample](https://user-images.githubusercontent.com/47170845/81206455-1afa3f00-9007-11ea-8e0d-9fe9e3b7faf2.png)