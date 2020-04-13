import json, requests, hashlib

def load(filename="./.data/access_token.txt"):
    try:
        access_token = open(filename, "r").read()
    except FileNotFoundError:
        print("Token file not found!")
        return False
    if ("username" in json.loads(requests.get(f"https://graph.facebook.com/me/?access_token={access_token}", timeout=100).text)):
        return access_token
    else:
        print("Invalid access token!")
        return False

def generate(email, pw, filename="./.data/access_token.txt"):
    data = {
        "api_key":"882a8490361da98702bf97a021ddc14d",
        "credentials_type":"password",
        "email": email,
        "format":"JSON",
        "generate_machine_id":"1",
        "generate_session_cookies":"1",
        "locale":"en_US",
        "method":"auth.login",
        "password": pw,
        "return_ssl_resources":"0",
        "v":"1.0"
    }
    sig = (f'api_key=882a8490361da98702bf97a021ddc14dcredentials_type=passwordemail={email}format=JSONgenerate_machine_id=1generate_session_cookies=1locale=en_USmethod=auth.loginpassword={pw}return_ssl_resources=0v=1.062f8ce9f74b12f84c123cc23437a4a32').encode('utf-8')
    x = hashlib.new('md5')
    x.update(sig)
    data.update({
        "sig": x.hexdigest()
    })
    result = json.loads(requests.post("https://api.facebook.com/restserver.php", data=data, timeout=100).text)
    if ("access_token" in result):
        access_token = result["access_token"]
        print("create new file access_token.txt")
        with open(filename, "w+") as f:
            f.write(access_token)
            f.close()
        return access_token
    else:
        if result.get("error_code", False) == 400:
            print("Account Checkpoint.")
            return False
        else:
            print(result["error_msg"])
            return False