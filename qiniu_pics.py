from qiniu import Auth, put_file
from config import *
import requests

cover_url = "http://{}/{key}?imageMogr2/thumbnail/1000x/crop/x562".format(qiniu_domain)
qiniu = Auth(qiniu_accesskey, qiniu_secretkey)
bucket = qiniu_bucket
header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}


def qiniu_upload(local, key):
    token = qiniu.upload_token(bucket, key, 3600)
    ret, info = put_file(token, key, local)
    pic = requests.get(cover_url.format(key=key), headers=header)
    return pic.content
