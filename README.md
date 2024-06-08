# Kyasher
Kyash APIラッパー Python用
### >> ```pip install kyasher``` <<
## 使い方
#### example.py  
```py
from Kyasher import Kyash

kyash=Kyash("メールアドレス","パスワード",proxy=None)#引数にプロキシを設定できる、proxy=dict
otp=input("OTP? :")#SMSに届いた6桁の認証番号
kyash.login(otp)
print(kyash.access_token)#有効期限は1ヶ月
print(kyash.client_uuid)
print(kyash.installation_uuid)#クライアントUUIDとインストレーションUUIDは2つで1セット

kyash=Kyash("メールアドレス","パスワード","登録済みクライアントUUID","登録済みインストレーションUUID")#これでログイン時のOTP認証をスキップできる
kyash=Kyash(access_token="アクセストークン")#またはトークンでログイン

kyash.get_profile()#プロフィール取得
print(kyash.username)#ユーザーネーム
print(kyash.icon)#アイコン
print(kyash.myouzi)#苗字
print(kyash.namae)#名前
print(kyash.phone)#電話番号
print(kyash.is_kyc)#本人確認されているかどうか、True or False

kyash.get_wallet()#残高照会
print(kyash.wallet_uuid)#おさいふUUID
print(kyash.all_balance)#合計残高
print(kyash.money)#出金可能なキャッシュマネー
print(kyash.value)#出金不可のキャッシュバリュー
print(kyash.point)#ポイント

kyash.get_history(wallet_uuid=kyash.wallet_uuid,limit=3)#支出入の履歴を取得する、wallet_uuidを入力しなかったらその場で取得するので入力しなくてもOK
print(kyash.timelines)#リスト型、支出入履歴

kyash.get_summary(year=2024,month=6)#支出入のカテゴリーを取得する、何も入力しないと今日の西暦と月になる
print(kyash.summary)#↑で取得したレポート

kyash.create_link(amount=100,message="テストリンク",is_claim=False)#送金リンクを作成、is_claim=True で請求リンクを作成する
print(kyash.created_link)#↑で作ったリンク

link_info=kyash.link_check(kyash.created_link)#リンクを確認する、引数名はURLだけど https://kyash.me/payments/ はなくてもOK
print(kyash.link_amount)#金額
print(kyash.link_uuid)#リンクのUUID、必要
print(kyash.send_to_me)#受け取りリンクなら True、請求リンクなら False
print(kyash.link_public_id)#パブリックID、請求リンクにしか必要ない
print(kyash.link_sender_name)#リンク作成者のユーザーネーム

kyash.link_recieve(url="URL",link_uuid="リンクのUUID")#送金リンクを受け取る、引数はどちらか1つでOK、リンクのUUIDをいれるとリンクチェックがスキップされる
kyash.link_cancel(url="URL",link_uuid="リンクのUUID")#リンクをキャンセル、リンク受け取りと同じ
kyash.send_to_link(url="URL",message="Botが請求に応じました",link_info=link_info)#請求リンクに送金する時にリンクチェックをスキップしたい場合だけlink_info全体が必要、もちろんURLだけいれてもちゃんと機能する
```  
#コメントで書いてあることが全部、それ以上は特にない...  
## もう少し知る
### ログイン
ログイン時のワンタイムパスワードをスキップするためにはクライアントUUIDとインストレーションUUID両方が合っている必要がある  
もちろんトークンがあればUUIDはテキトーでもOK  
アクセストークンは1ヶ月経つと失効する  
### リンクチェック
なぜかKyashはリンクのID部分ではなくリンクUUIDが重要視されていてIDはほぼ完全に飾り  
送金 / 請求URLにアクセスするとHTMLが返ってくるのでそこからリンクUUIDをスクレイピングしてる  
json形式で返してくれるAPIもあったけどなぜかそれにもリンクUUIDが必要なためにけっきょくスクレイピングからは逃れられない  
### 余談
ユーザーエージェントはiOS 16.7.5のiPhone8だけどトラフィックを確認した実機はiOS 14.8  
Kyashが最近iOS 15のサポートを終了するって発表してたけど、僕は永遠にiOS 14  
iOSは2,3年落ちになっただけでいろんなアプリに対応を切られてサイドローディングもろくにできないから寿命が短い (＋インストールしたことのないアプリはAppStore++でも使わない限り過去バージョンをダウンロードできないから余計に)  
Androidなんかがんばればロリポップですらまだ使えるのに (32bitはそろそろちょっときついかなぁ)
## コンタクト  
Discord サーバー / https://discord.gg/aSyaAK7Ktm  
Discord ユーザー名 / .taka.  
