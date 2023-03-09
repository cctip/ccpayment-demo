import hashlib
import time
import urllib.request
import json
import const


class CCPaymentClass:
    app_id = ''
    app_secret = ''

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
            "crypto": ""
        }
    }
    """
    # create api deposit order
    def create_deposit_order(self, token_id, amount, merchant_order_id, fiat_currency, remark=None):
        data = {
            "amount": amount,
            "merchant_order_id": merchant_order_id,
            "token_id": token_id,
            "fiat_currency": fiat_currency
        }
        if remark:
            data["remark"] = remark
        return _send_post(const.CREATE_ORDER_URL, data, self.app_id, self.app_secret)

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
    def get_checkout_url(self, amount, merchant_order_id, valid_timestamp, product_name, return_url=None):
        data = {
            "amount": amount,
            "merchant_order_id": merchant_order_id,
            "valid_timestamp": valid_timestamp,
            "product_name": product_name
        }
        if return_url:
            data["return_url"] = return_url
        return _send_post(const.CHECKOUT_URL, data, self.app_id, self.app_secret)

    def webhook_validate(self, data_str, timestamp, signature):
        if _hash256(self.app_id, self.app_secret, data_str, timestamp) == signature and signature != "":
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
                    "token_id": ""
                }
            ]
        }
    }
    """
    def get_support_tokens(self):
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
        data = {}
        return _send_post(const.SUPPORT_TOKEN_URL, data, self.app_id, self.app_secret)

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
        return _send_post(const.TOKEN_CHAIN_URL, data, self.app_id, self.app_secret)

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
        return _send_post(const.TOKEN_RATE_URL, data, self.app_id, self.app_secret)

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
    def create_withdraw_order(self, token_id, address, value, merchant_order_id, memo=None):
        data = {
            "token_id": token_id,
            "address": address,
            "value": value,
            "merchant_order_id": merchant_order_id
        }
        if memo:
            data["memo"] = memo
        return _send_post(const.WITHDRAW_API_URL, data, self.app_id, self.app_secret)

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
        return _send_post(const.CHECK_USER_URL, data, self.app_id, self.app_secret)

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
    def get_token_assets(self, token_id):
        data = {
            "token_id": token_id
        }
        return _send_post(const.ASSETS_URL, data, self.app_id, self.app_secret)

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
    def get_network_fee(self, token_id, address=None, memo=None):
        data = {
            "token_id": token_id
        }
        if memo:
            data["memo"] = memo
        if address:
            data["address"] = address
        return _send_post(const.NETWORK_FEE_URL, data, self.app_id, self.app_secret)


def _hash256(app_id, app_secret, txt, timestamp):
    txt = app_id + app_secret + str(timestamp) + txt
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def _send_post(url, data, app_id, app_secret):
    timestamp = int(time.time())

    data_str = json.dumps(data)
    sign_str = _hash256(app_id, app_secret, data_str, timestamp)

    req = urllib.request.Request(url=url, method="POST", data=data_str.encode("utf-8"))

    req.add_header(const.APP_ID_HEADER_KEY, app_id)
    req.add_header(const.SIGN_HEADER_KEY, sign_str)
    req.add_header(const.TIMESTAMP_HEADER_KEY, str(timestamp))

    req.timeout = 30  # s

    # post
    resp = urllib.request.urlopen(req)
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
    if _hash256(app_id, app_secret, data_str, ts) == signature and signature != "":
        return data, True

    return data, False
