from Kyasher import Kyash

kyash = Kyash("メールアドレス","パスワード",proxy=None)#引数にプロキシを設定できる、proxy=dict
otp = input("OTP? :")#SMSに届いた6桁の認証番号
kyash.login(otp)
print(kyash.access_token)#有効期限は1ヶ月
print(kyash.client_uuid)
print(kyash.installation_uuid)#クライアントUUIDとインストレーションUUIDは2つで1セット

kyash = Kyash("メールアドレス","パスワード","登録済みクライアントUUID","登録済みインストレーションUUID")#これでログイン時のOTP認証をスキップできる
kyash = Kyash(access_token="アクセストークン")#またはトークンでログイン

profile = kyash.get_profile()#プロフィール取得

print(profile.username)#ユーザーネーム
print(profile.icon)#アイコン
print(profile.myouzi)#苗字
print(profile.namae)#名前
print(profile.phone)#電話番号
print(profile.is_kyc)#本人確認されているかどうか、True or False

wallet = kyash.get_wallet()#残高照会
print(wallet.uuid)#おさいふUUID
print(wallet.all_balance)#合計残高
print(wallet.money)#出金可能なキャッシュマネー
print(wallet.value)#出金不可のキャッシュバリュー
print(wallet.point)#ポイント

history = kyash.get_history(wallet_uuid=wallet.uuid,limit=3)#支出入の履歴を取得する、wallet_uuidを入力しなかったらその場で取得するので入力しなくてもOK
print(history.timelines)#リスト型、支出入履歴

summary = kyash.get_summary(year=2024,month=6)#支出入のカテゴリーを取得する、何も入力しないと今日の西暦と月になる
print(summary.summary)#↑で取得したレポート

create_link = kyash.create_link(amount=100,message="テストリンク",is_claim=False)#送金リンクを作成、is_claim=True で請求リンクを作成する
print(create_link.link)#↑で作ったリンク

link_info = kyash.link_check(create_link.link)#リンクを確認する、引数名はURLだけど https://kyash.me/payments/ はなくてもOK
print(link_info.amount)#金額
print(link_info.uuid)#リンクのUUID、必要
print(link_info.send_to_me)#受け取りリンクなら True、請求リンクなら False
print(link_info.public_id)#パブリックID、請求リンクにしか必要ない
print(link_info.sender_name)#リンク作成者のユーザーネーム

kyash.link_recieve(url="URL",link_uuid="リンクのUUID")#送金リンクを受け取る、引数はどちらか1つでOK、リンクのUUIDをいれるとリンクチェックがスキップされる
kyash.link_cancel(url="URL",link_uuid="リンクのUUID")#リンクをキャンセル、リンク受け取りと同じ
kyash.send_to_link(url="URL",message="Botが請求に応じました",link_info=link_info)#請求リンクに送金する時にリンクチェックをスキップしたい場合だけlink_info全体が必要、もちろんURLだけいれてもちゃんと機能する