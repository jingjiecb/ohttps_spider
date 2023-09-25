import requests
from configparser import ConfigParser
import hashlib
import os

useragent_header = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
headers = {
    "User-Agent": useragent_header,
}

domain = ''
username = ''
password = ''


def init():
    global username, password, domain
    config = ConfigParser()
    config.read("config.ini")
    username = config["OHTTPS"]["username"]
    password = config["OHTTPS"]["password"]
    domain = config["OHTTPS"]["domain"]


def login():
    signin_url = "https://ohttps.com/api/auth/signin"
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    signin_payload = {
        "email": username,
        "password": password_md5,
    }
    response = requests.post(signin_url, headers=headers, data=signin_payload)
    token = response.headers.get("x-user-token")
    authorization_token = f"Bearer {token}"
    headers["Authorization"] = authorization_token

def fetch_cert_id(domain):
    fetch_url = f"https://ohttps.com/api/certificates?searchContent={domain}&offset=0&limit=10&sortKey=&sortOrder="
    response = requests.get(fetch_url, headers=headers)
    response_obj = response.json()
    certificate_id = response_obj["payload"]["rows"][0]["id"]
    return certificate_id


def fetch_version_id(cert_id):
    fetch_url = f"https://ohttps.com/api/certificates/{cert_id}"
    response = requests.get(fetch_url, headers=headers)
    response_obj = response.json()
    version_id = response_obj['payload']['latestValidVersionId']
    return version_id


def fetch_cert(cert_id, version_id):
    fetch_url = f"https://ohttps.com/api/certificates/{cert_id}/versions/{version_id}"
    response = requests.get(fetch_url, headers=headers)
    response_obj = response.json()
    full_chain_cert = response_obj['payload']['detail']['fullChainCerts']
    cert_key = response_obj['payload']['detail']['certKey']
    return (cert_key, full_chain_cert)


def write_cert(cert_key, cert):
    directory_path = "/srv/certs/" + domain.replace("*", "_")
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    cert_key_file_path = os.path.join(directory_path, "cert.key")
    with open(cert_key_file_path, "w") as file:
        file.write(cert_key)

    cert_file_path = os.path.join(directory_path, "fullchain.cer")
    with open(cert_file_path, "w") as file:
        file.write(cert)


if __name__ == '__main__':
    init()
    login()
    cert_id = fetch_cert_id(domain)
    version_id = fetch_version_id(cert_id)
    key, cert = fetch_cert(cert_id, version_id)
    write_cert(key, cert)
