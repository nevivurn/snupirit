#!/usr/bin/env python3

from typing import Any

from dataclasses import dataclass
from base64 import b64encode, b64decode
from datetime import datetime
from hashlib import sha1
from zoneinfo import ZoneInfo
import json
import tomllib

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import requests


@dataclass
class Config:
    student_id: str
    term: str
    rooms: dict[str, str]


with open('keys.txt', 'r') as f:
    KEYS = [line.rstrip() for line in f]
KEY_ID = datetime.now(ZoneInfo('Asia/Seoul')).month - 1

API_REFRESH = 'https://scard1.snu.ac.kr/eaas/R002'
API_ATTEND = 'https://scard1.snu.ac.kr/eaas/A002'


def encode(data: str) -> str:
    pad_data = pad(data.encode(), AES.block_size)
    key = KEYS[KEY_ID].encode()
    cipher = AES.new(key, AES.MODE_CBC, iv=bytes(AES.block_size))
    return b64encode(cipher.encrypt(pad_data)).decode()


def decode(data: str) -> str:
    dec_data = b64decode(data)
    key = KEYS[KEY_ID].encode()
    cipher = AES.new(key, AES.MODE_CBC, iv=bytes(AES.block_size))
    return unpad(cipher.decrypt(dec_data), AES.block_size).decode()


def make_payload(sid: str, body: dict[str, str]) -> str:
    body_str = json.dumps(body, separators=(',', ':'))
    header_str = json.dumps({
        'loginId': sid,
        'enc': sha1(body_str.encode()).hexdigest(),
    }, separators=(',', ':'))

    return json.dumps({
        'body': body,
        'header': encode(header_str),
    }, separators=(',', ':'))


def send_request(sid: str, api: str, body: dict[str, Any]) -> Any:
    r = requests.post(
        api,
        data=make_payload(sid, body),
        headers={
            'Content-Type': 'application/json',
            'Accept-Language': 'en_US',
        },
    )
    return json.loads(r.text)


def refresh_class(cfg: Config) -> Any:
    resp = send_request(cfg.student_id, API_REFRESH,
                        {'userId': cfg.student_id, 'yearTerm': cfg.term})
    body = json.loads(resp['body'])
    return body


def attend_class(cfg: Config, lecture: str, room: str) -> str:
    resp = send_request(cfg.student_id, API_ATTEND, {
        'userId': cfg.student_id,
        'lectureId': lecture,
        'yearTerm': cfg.term,
        'bleList': [{
            'bleRssi': '-70',
            'bleMajor': '10000',
            'bleUuid': '2CDBDD00-13EE-11E4-9B6C-0002A5D5C51B',
            'bleMinor': room,
        }],
    })
    header = json.loads(decode(resp['header']))
    return str(header['resMsg'])


def load_config() -> Config:
    with open('config.toml', 'rb') as f:
        cfg = tomllib.load(f)
    return Config(
        student_id=cfg['student_id'],
        term=cfg['term'],
        rooms=cfg['rooms'],
    )


def main() -> None:
    cfg = load_config()

    cur = refresh_class(cfg)

    print('Refresh response:')
    print(json.dumps(cur, indent=2))

    lecture = str(cur['lectureId'])
    status = str(cur['attendStatus'])

    print('Current lecture:', lecture, status)
    if lecture != '' and status != '출석':
        print(attend_class(cfg, lecture, cfg.rooms[lecture]))


if __name__ == '__main__':
    main()
