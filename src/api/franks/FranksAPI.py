from os import environ
import json
import http.client
from fake_useragent import UserAgent

from src.api.franks.FranksAPIResponse import (
    FranksAPISessionResponse,
    FranksAPIGetSessionResponse,
    FranksAPIDeleteSessionResponse,
    FranksChatID,
)
from src.core.logger import BirbiaLogger


class FranksAPI:
    """
    Franks API class for interacting with a GPT4 model.
    """

    __api_host = "api.franks.ai"
    __session_url = "/v1/sessions/"
    __health_url = "/v1/health/"

    __web_ua = UserAgent(os="linux")
    __headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://franks.ai",
        "priority": "u=1, i",
        "referer": "https://franks.ai/",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": __web_ua.random,
    }

    def __init__(self):
        self.__auth_token = environ.get("AI_MODEL_AUTH_TOKEN")
        if self.__auth_token is None:
            BirbiaLogger.error("AI_MODEL_AUTH_TOKEN not set.")
            raise ValueError("AI_MODEL_AUTH_TOKEN not set.")

        FranksAPI.__headers["authorization"] = self.__auth_token.replace("%20", " ")

    def __api_conn(self):
        return http.client.HTTPSConnection(FranksAPI.__api_host)

    def health_check(self):
        """
        Checks the health of the API.
        """

        conn = self.__api_conn()
        conn.request("GET", FranksAPI.__health_url, headers=FranksAPI.__headers)

        response = conn.getresponse()
        if response.status not in [200, 201]:
            return False

        conn.close()
        return True

    def create_session(self, session_name: str):
        """
        Creates a new session.
        """

        if self.health_check() is False:
            return None

        conn = self.__api_conn()
        raw_body = json.dumps({"name": session_name})

        conn.request(
            "POST", FranksAPI.__session_url, raw_body, headers=FranksAPI.__headers
        )

        response = conn.getresponse()
        if response.status not in [200, 201]:
            return None

        api_response = FranksAPISessionResponse(
            json.loads(response.read().decode("utf-8"))
        )
        conn.close()
        return api_response

    def get_sessions(self):
        """
        Gets all sessions.
        """

        if self.health_check() is False:
            return None

        conn = self.__api_conn()
        conn.request("GET", FranksAPI.__session_url, headers=FranksAPI.__headers)

        response = conn.getresponse()
        if response.status not in [200, 201]:
            return None

        api_response = FranksAPIGetSessionResponse(
            json.loads(response.read().decode("utf-8"))
        )
        conn.close()
        return api_response

    def delete_session(self, session_id: FranksChatID):
        """
        Deletes a session.
        """

        if self.health_check() is False:
            return None

        conn = self.__api_conn()
        conn.request(
            "DELETE",
            f"{FranksAPI.__session_url}{session_id.get()}/",
            headers=FranksAPI.__headers,
        )

        response = conn.getresponse()
        if response.status not in [200, 201]:
            return None

        api_response = FranksAPIDeleteSessionResponse(
            json.loads(response.read().decode("utf-8"))
        )
        conn.close()
        return api_response
