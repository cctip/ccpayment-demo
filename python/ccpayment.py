import hashlib
import time
import urllib.request
import json
import const
import contextlib


class CCPaymentClass:

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": {
            "order_id": "",
            "amount": "",
            "logo": "",
            "network": "",
            "pay_address": "",
            "crypto": "",
            "token_id: "",
            "memo": "",
            "order_valid_period: 0
        }
    }
    """
    # create api order
    def create_order(self, token_id, product_price, merchant_order_id, denominated_currency, period=None, remark=None):
        data = {
            "product_price": product_price,
            "merchant_order_id": merchant_order_id,
            "token_id": token_id,
            "denominated_currency": denominated_currency,
            "order_valid_period": period,  # s
            "remark": remark
        }
        if remark:
            data["remark"] = remark
        return self._send_post(const.CREATE_ORDER_URL, data)

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": {
            "payment_url": ""
        }
    }
    """
    # get checkout url
    def checkout_url(self, product_price, merchant_order_id, order_valid_period, product_name, return_url=None):
        data = {
            "product_price": product_price,
            "merchant_order_id": merchant_order_id,
            "order_valid_period": order_valid_period,
            "product_name": product_name
        }
        if return_url:
            data["return_url"] = return_url
        return self._send_post(const.CHECKOUT_URL, data)

    def webhook(self, data_str, timestamp, signature):
        if self._hash256(data_str, timestamp) == signature and signature != "":
            return True

        return False
    """
     * return success
     {
         "code": 10000,
         "msg": "",
         "data": {
             "list": [
                 {
                     "crypto": "",
                     "name": "",
                     "logo": "",
                     "min": "",
                     "price": "",
                     "coin_id": ""
                     "tokens": []
                 }
             ]
         }
     }
     """
    def get_support_coin(self):
        data = {}
        return self._send_post(const.SUPPORT_COIN_URL, data)

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": {
            "list": [
                {
                    "crypto": "",
                    "name": "",
                    "logo": "",
                    "min": "",
                    "price": "",
                    "token_id": ""
                }
            ]
        }
    }
    """
    def get_support_token(self):
        data = {}
        return self._send_post(const.SUPPORT_TOKEN_URL, data)

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": {
            "list": [
                {
                    "token_id": "",
                    "chain": "",
                    "contract": "",
                    "crypto": "",
                    "logo": "",
                    "name": "",
                    "network": "",
                    "chain_logo": ""
                }
            ]
        }
    }
    """
    def get_token_chain(self, token_id):
        data = {
            "token_id": token_id
        }
        return self._send_post(const.TOKEN_CHAIN_URL, data)

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": {
            "price": "",
            "value": ""
        }
    }
    """
    def get_token_rate(self, token_id, amount):
        data = {
            "token_id": token_id,
            "amount": amount
        }
        return self._send_post(const.TOKEN_RATE_URL, data)

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": {
            "bill_id": "",
            "type": "",
            "network_fee": ""
        }
    }
    """
    def withdraw(self, token_id, address, value, merchant_order_id, memo=None):
        data = {
            "token_id": token_id,
            "address": address,
            "value": value,
            "merchant_order_id": merchant_order_id
        }
        if memo:
            data["memo"] = memo
        return self._send_post(const.WITHDRAW_API_URL, data)

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": {
            "c_id": "",
            "nickname": ""
        }
    }
    """
    def check_user(self, c_id):
        data = {
            "c_id": c_id
        }
        return self._send_post(const.CHECK_USER_URL, data)

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": [
            {
                "token_id": "",
                "crypto": "",
                "name": "",
                "value": "",
                "price": "",
                "logo": ""
            }
        ]
    }
    """
    def assets(self, token_id):
        data = {
            "token_id": token_id
        }
        return self._send_post(const.ASSETS_URL, data)

    """
    * return success
    {
        "code": 10000,
        "msg": "",
        "data": {
            "token_id": "",
            "crypto": "",
            "fee": ""
        }
    }
    """
    def network_fee(self, token_id, address=None, memo=None):
        data = {
            "token_id": token_id
        }
        if memo:
            data["memo"] = memo
        if address:
            data["address"] = address
        return self._send_post(const.NETWORK_FEE_URL, data)

    """
    {
        "code":10000,
        "msg":"success",
        "data":{
            "detail":{
                "fiat_amount":"10",
                "fiat_currency":"USD",
                "merchant_order_id":"2376655808480575",
                "chain":"ETH",
                "contract":"0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "crypto":"USDT",
                "token_amount":"10",
                "status":"Overpaid",
                "created":1675022332000
            },
            "received":[
                {
                    "amount":"12",
                    "chain":"ETH",
                    "contract":"0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    "crypto":"USDT",
                    "service_fee":"0.006",
                    "pay_time":1675022464000,
                    "token_rate":"1"
                }
            ],
            "refunds":[
                {
                    "amount":"1",
                    "network_fee":"0",
                    "actual_received_amount":"1",
                    "chain":"ETH",
                    "contract":"0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    "crypto":"USDT",
                    "txid":"",
                    "address":"0xA9F422BFBeB46f1FbcBBaf947E15b84D8Fbba80C",
                    "pay_time":1675272545000,
                    "status":"Successful"
                }
            ]
        }
    }
    """
    def get_order_info(self, merchant_order_ids):
        data = {
            "merchant_order_ids": merchant_order_ids
        }
        return self._send_post(const.API_ORDER_INFO_URL, data)

    """
    {
        "code":10000,
        "msg":"success",
        "data":{
            "address":"TWM7um8aucgBbeVnQTNkpccxd9D657Vx9H"
        }
    }
    """
    def payment_address(self, user_id, chain, notify_url):
        data = {
            "user_id": user_id,
            "chain": chain,
            "notify_url": notify_url
        }
        return self._send_post(const.PAYMENT_ADDRESS_RUL, data)

    def _hash256(self, txt, timestamp):
        txt = self.app_id + self.app_secret + str(timestamp) + txt
        return hashlib.sha256(txt.encode("utf-8")).hexdigest()

    def _send_post(self, url, data):
        timestamp = int(time.time())

        data_str = json.dumps(data)
        sign_str = self._hash256(data_str, timestamp)

        req = urllib.request.Request(url=url, method="POST", data=data_str.encode("utf-8"), headers={
            "Content-Type": "application/json;charset=uf8",
            const.APP_ID_HEADER_KEY: self.app_id,
            const.SIGN_HEADER_KEY: sign_str,
            const.TIMESTAMP_HEADER_KEY: str(timestamp)
        })

        req.timeout = 60  # s

        # post
        resp = urllib.request.urlopen(req)

        data, is_valid = self._deal_and_valid(resp)
        if resp:
            resp.close()

        return data, is_valid

    def _deal_and_valid(self, resp):
        if resp.code != 200:
            return {}, False

        data_str = resp.read().decode('utf-8')
        data = json.loads(data_str)

        if data['code'] != 10000:
            return data, True

        # header
        signature = resp.headers[const.SIGN_HEADER_KEY]
        ts = resp.headers[const.TIMESTAMP_HEADER_KEY]

        # verify
        if self._hash256(data_str, ts) == signature and signature != "":
            return data, True
        return data, False
