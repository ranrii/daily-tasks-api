from flask import request


def get_ip_addr():
    return request.headers.get("x-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))
