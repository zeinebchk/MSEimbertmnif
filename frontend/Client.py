import requests
from requests import session

from frontend.SessionManager import SessionManager
from frontend.SessionManager import SessionManager
BASE_URL = "http://127.0.0.1:5000"
def make_request(method,endpoint,**kwargs):
    session=SessionManager.get_instance()
    headers=kwargs.pop("headers",{})
    headers["Authorization"]=f"Bearer {session.get_access_token()}"

    try:
        print("access_token", session.get_access_token())
        response=requests.request(method,BASE_URL+endpoint,headers=headers,**kwargs)
        print("make request",response)
        if response.status_code ==401:
            res=refrech_token()
            if res:
                print("refresh make request")
                headers["Authorization"]=f"Bearer {session.get_access_token()}"
                response = requests.request(method,BASE_URL+ endpoint, headers=headers, **kwargs)
                print("make requestttt rsult in refresh",response)
                return response
        return response
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def refrech_token():
    print("refrech_tokennnnnnnnnnnnnnnnnn")
    session=SessionManager.get_instance()
    refresh_token=session.get_refresh_token()
    url = BASE_URL+"/auth/refreshtoken"
    headers = {
        "Authorization": f"Bearer {refresh_token}"
    }
    response=requests.post(url,headers=headers)
    if response.status_code == 200:
        data=response.json()
        print(data)
        session.set_tokens(data.get("access_token"),refresh_token)
        return True
    return False



