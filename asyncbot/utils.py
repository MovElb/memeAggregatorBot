import hashlib
import hmac
import six


def generate_appsecret_proof(access_token, app_secret):
    '''
        @inputs:
            access_token: page access token
            app_secret_token: app secret key
        @outputs:
            appsecret_proof: HMAC-SHA256 hash of page access token
                using app_secret as the key
    '''
    if six.PY2:
        hmac_object = hmac.new(str(app_secret), unicode(access_token), hashlib.sha256)
    else:
        hmac_object = hmac.new(bytearray(app_secret, 'utf8'), str(access_token).encode('utf8'), hashlib.sha256)
    generated_hash = hmac_object.hexdigest()
    return generated_hash
