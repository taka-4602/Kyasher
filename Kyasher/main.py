import requests
from uuid import uuid4
import datetime
from bs4 import BeautifulSoup
from typing import NamedTuple

class KyashError(Exception):
    pass
class KyashLoginError(Exception):
    pass
class NetWorkError(Exception):
    pass
class Kyash():
    def __init__(self,email:str=None,password:str=None,client_uuid:str=None,installation_uuid:str=None,access_token:str=None,proxy:dict=None):
        if email==password==access_token:
            raise KyashLoginError("電話番号 & パスワードを入力するか、アクセストークンを入力してください")
            
        self.email=email
        self.password=password
        self.proxy=proxy
        self.access_token=access_token

        if client_uuid:
            self.client_uuid=client_uuid
        else:
            self.client_uuid=str(uuid4()).upper()

        if installation_uuid:
            self.installation_uuid=installation_uuid
        else:
            self.installation_uuid=str(uuid4()).upper()

        try:
            iosstore=requests.get("https://apps.apple.com/jp/app/kyash-%E3%82%AD%E3%83%A3%E3%83%83%E3%82%B7%E3%83%A5-%E3%83%81%E3%83%A3%E3%83%BC%E3%82%B8%E5%BC%8Fvisa%E3%82%AB%E3%83%BC%E3%83%89/id1084264883",proxies=proxy)
        except Exception as e:
            raise NetWorkError(e)
        
        self.version=BeautifulSoup(iosstore.text,"html.parser").find(class_="l-column small-6 medium-12 whats-new__latest__version").text.split()[1]
        self.headers={
            "Host": "api.kyash.me",
            "Content-Type": "application/json",
            "X-Kyash-Client-Id": self.client_uuid,
            "Accept": "application/json",
            "X-Kyash-Device-Language": "ja",
            "X-Kyash-Client-Version": self.version,
            "X-Kyash-Device-Info": "iPhone 8, Version:16.7.5",
            "Accept-Language": "ja-jp",
            "X-Kyash-Date": str(round(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).timestamp())),
            "Accept-Encoding": "gzip, deflate, br",
            #"X-Kyash-Device-Uptime-Mills": 540266465,
            "User-Agent": "Kyash/2 CFNetwork/1240.0.4 Darwin/20.6.0",
            "X-Kyash-Installation-Id": self.installation_uuid,
            "X-Kyash-Os": "iOS",
            "Connection": "keep-alive"
        }
        if access_token:
            self.headers["X-Auth"]=access_token
        else:
            payload={
                "email":email,
                "password":password
            }
            login=requests.post("https://api.kyash.me/v2/login",headers=self.headers,json=payload,proxies=proxy).json()
            if login["code"]!=200:
                raise KyashLoginError(login["error"]["message"])
            
            if client_uuid and installation_uuid:
                if not login["result"]["data"]["token"]:
                    raise KyashLoginError("登録されていないUUID")
                
                self.access_token=login["result"]["data"]["token"] #1ヶ月もつよ
                self.refresh_token=login["result"]["data"]["refreshToken"]
                self.headers["X-Auth"]=access_token
                    
    def login(self,otp:str):
        payload={
            "verificationCode":otp,
            "email":self.email
        }
        get_token=requests.post("https://api.kyash.me/v2/login/mobile/verify",headers=self.headers,json=payload,proxies=self.proxy).json()
        if get_token["code"]!=200:
            raise KyashLoginError(get_token["error"]["message"])
        
        self.access_token=get_token["result"]["data"]["token"] #1ヶ月もつよ
        self.refresh_token=get_token["result"]["data"]["refreshToken"]
        self.headers["X-Auth"]=get_token["result"]["data"]["token"]

        return get_token

    def get_profile(self):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        getprofile=requests.get("https://api.kyash.me/v1/me",headers=self.headers,proxies=self.proxy).json()
        if getprofile["code"]!=200:
            raise KyashError(getprofile["error"]["message"])
        
        username=getprofile["result"]["data"]["userName"]
        icon=getprofile["result"]["data"]["imageUrl"]
        myouzi=getprofile["result"]["data"]["lastNameReal"]
        namae=getprofile["result"]["data"]["firstNameReal"]
        phone=getprofile["result"]["data"]["phoneNumber"]
        is_kyc=getprofile["result"]["data"]["kyc"]

        class Profile(NamedTuple):
            username: str
            icon: str
            myouzi: str
            namae: str
            phone: str
            is_kyc: bool
            raw: dict 

        return Profile(
            username=username,
            icon=icon,
            myouzi=myouzi,
            namae=namae,
            phone=phone,
            is_kyc=is_kyc,
            raw=getprofile
        )

    def get_wallet(self):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        getwallet=requests.get("https://api.kyash.me/v1/me/primary_wallet",headers=self.headers,proxies=self.proxy).json()
        if getwallet["code"]!=200:
            raise KyashError(getwallet["error"]["message"])
        
        wallet_uuid=getwallet["result"]["data"]["uuid"]
        all_balance=getwallet["result"]["data"]["balance"]["amount"]
        money=getwallet["result"]["data"]["balance"]["amountBreakdown"]["kyashMoney"]
        value=getwallet["result"]["data"]["balance"]["amountBreakdown"]["kyashValue"]
        point=getwallet["result"]["data"]["pointBalance"]["availableAmount"]

        class Wallet(NamedTuple):
            uuid: str
            all_balance: int
            money: int
            value: int
            point: int
            raw: dict

        return Wallet(
            wallet_uuid=wallet_uuid,
            all_balance=all_balance,
            money=money,
            value=value,
            point=point,
            raw=getwallet
        )
    
    def get_history(self,wallet_uuid:str=None,limit:int=3):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        param={"limit":limit}
        if not wallet_uuid:
            getwallet=requests.get("https://api.kyash.me/v1/me/primary_wallet",headers=self.headers,proxies=self.proxy).json()
            if getwallet["code"]!=200:
                raise KyashError(getwallet["error"]["message"])
            wallet_uuid=getwallet["result"]["data"]["uuid"]

        gethistory=requests.get(f"https://api.kyash.me/v1/me/wallets/{wallet_uuid}/timeline",headers=self.headers,params=param,proxies=self.proxy).json()
        if gethistory["code"]!=200:
            raise KyashError(gethistory["error"]["message"])
        
        timelines=gethistory["result"]["data"]["timelines"]
        
        class History(NamedTuple):
            timelines: list
            raw: dict

        return History(
            timelines=timelines,
            raw=gethistory
        )
    
    def get_summary(self,year:int=None,month:int=None):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        if not year:
            now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            year=now.year
        if not month:
            now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            month=now.month

        if int(month)<10:
            month=f"0{month}"

        getsummary=requests.get(f"https://api.kyash.me/v1/monthly_timeline/summary/{year}-{month}",headers=self.headers,proxies=self.proxy).json()
        if getsummary["code"]!=200:
            raise KyashError(getsummary["error"]["message"])

        summary=getsummary["result"]["data"]["summary"]
        
        class Summary(NamedTuple):
            summary: dict
            raw: dict

        return Summary(
            summary=summary,
            raw=getsummary
        )

    def create_link(self,amount:int,message:str="",is_claim:bool=False):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        payload={
            "uuidClient":str(uuid4()).upper(),
            "amount":amount,
            "repeatable":False,
            "action":1,
            "message":{
                "text":message,
                "uuidClient":str(uuid4()).upper()
                },
            "service":"share"
        }
        if is_claim:
            payload["action"]=2
            payload["repeatable"]=True
        
        create=requests.post("https://api.kyash.me/v1/me/links",headers=self.headers,json=payload,proxies=self.proxy).json()
        if create["code"]!=200:
            raise KyashError(create["error"]["message"])
        
        link=create["result"]["data"]["link"]

        class CreateLink(NamedTuple):
            link: str
            raw: dict

        return CreateLink(
            link=link,
            raw=create
        )

    def link_check(self,url:str):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        if not "https://kyash.me/payments/" in url:
            url="https://kyash.me/payments/" + url

        try:
            link_info=requests.get(url).text
            soup=BeautifulSoup(link_info,"html.parser")
            try:
                link_amount=soup.find(class_="amountText text_send").text.replace("¥","")
                link_uuid=soup.find(class_="btn_send").get("data-href-app").replace("kyash://claim/","")
                send_to_me=True
            except:
                link_amount=soup.find(class_="amountText text_request").text.replace("¥","")
                link_uuid=soup.find(class_="btn_request").get("data-href-app").replace("kyash://request/u/","")
                send_to_me=False
            
            link_info=requests.get(f"https://api.kyash.me/v1/links/{self.link_uuid}",headers=self.headers,proxies=self.proxy).json()
            if link_info["code"]!=200:
                raise KyashError(link_info["error"]["message"])
            
            link_public_id=link_info["result"]["data"]["target"]["publicId"]
            link_sender_name=link_info["result"]["data"]["target"]["userName"]

        except:
            raise KyashError("処理済みのリンクのため、チェックに失敗しました")

        class LinkInfo(NamedTuple):
            amount: int
            uuid: str
            public_id: str
            sender_name: str
            send_to_me: bool
            raw: dict

        return LinkInfo(
            link_amount=int(link_amount),
            link_uuid=link_uuid,
            link_public_id=link_public_id,
            link_sender_name=link_sender_name,
            send_to_me=send_to_me,
            raw=link_info
        )
    
    def link_recieve(self,url:str=None,link_uuid:str=None):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        if not link_uuid:
            if not url:
                raise KyashError("有効な受け取りリンクがありません")
            
            if not "https://kyash.me/payments/" in url:
                url="https://kyash.me/payments/" + url

            try:
                link_info=requests.get(url)
                soup=BeautifulSoup(link_info.text,"html.parser")
                #link_amount=soup.find(class_="amountText text_send").text.replace("¥","")
                link_uuid=soup.find(class_="btn_send").get("data-href-app").replace("kyash://claim/","")
            except:
                raise KyashError("処理済みまたは受け取りリンクではありません")

        recieve=requests.put(f"https://api.kyash.me/v1/links/{link_uuid}/receive",headers=self.headers,proxies=self.proxy).json()
        if recieve["code"]!=200:
            raise KyashError(recieve["error"]["message"])
        
        return recieve
    
    def link_cancel(self,url:str=None,link_uuid:str=None):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        if not link_uuid:
            if not url:
                raise KyashError("有効な受け取りリンクがありません")
            
            if not "https://kyash.me/payments/" in url:
                url="https://kyash.me/payments/" + url

            link_info=requests.get(url)
            soup=BeautifulSoup(link_info.text,"html.parser")
            #link_amount=soup.find(class_="amountText text_send").text.replace("¥","")
            link_uuid=soup.find(class_="btn_send").get("data-href-app").replace("kyash://claim/","")

        cancel=requests.delete(f"https://api.kyash.me/v1/links/{link_uuid}",headers=self.headers,proxies=self.proxy).json()
        if cancel["code"]!=200:
            raise KyashError(cancel["error"]["message"])
        
        return cancel

    def send_to_link(self,url:str=None,message:str="",link_info:str=None):
        if not self.access_token:
            raise KyashLoginError("まずはログインしてください")
        
        if not link_info:
            if not url:
                raise KyashError("有効な受け取りリンクがありません")
            
            if not "https://kyash.me/payments/" in url:
                url="https://kyash.me/payments/" + url

            try:
                link_info=requests.get(url).text
                soup=BeautifulSoup(link_info,"html.parser")
                link_amount=soup.find(class_="amountText text_request").text.replace("¥","")
                link_uuid=soup.find(class_="btn_request").get("data-href-app").replace("kyash://request/u/","")
                link_info=requests.get(f"https://api.kyash.me/v1/links/{link_uuid}",headers=self.headers,proxies=self.proxy).json()
                if link_info["code"]!=200:
                    raise KyashError(link_info["error"]["message"])

                link_public_id=link_info["result"]["data"]["target"]["publicId"]
                link_sender_name=link_info["result"]["data"]["target"]["userName"]
            except:
                raise KyashError("処理済みまたは請求リンクではありません")

        payload={
            "transactionMessage":{
                "text":message,
                "uuidClient":str(uuid4()).upper()
                },
            "amount":int(link_amount),
            "publicId_to":link_public_id,
            "action":1,
            "username_to":link_sender_name,
            "currency":"JPY"
        }

        send=requests.put(f"https://api.kyash.me/v1/links/{link_uuid}",headers=self.headers,json=payload,proxies=self.proxy).json()

        if send["code"]!=200:
            raise KyashError(send["error"]["message"])
        
        return send