from os import environ
from enum import Enum
from typing import Any, Callable
import discord
import asyncio
import json
import threading
import websocket

from src.api.franks.FranksAPIResponse import FranksChatID
from src.core.logger import BirbiaLogger


class ParseableEnum(Enum):
    @classmethod
    def from_str(cls, value: str):
        for e in cls:
            if str(e.value).lower() == str(value).lower():
                return e

        raise ValueError(f"Invalid value for {cls.__name__}: {value}")


class FranksWebsocketMessageType(ParseableEnum):
    Post = "post"
    Null = None
    Session = "session"


class FranksWebsocketStatus(ParseableEnum):
    Success = "success"
    Error = "error"
    NewToken = "new_token"
    Connect = "connect"
    LLMDone = "llm_done"


class FranksImageQuality(ParseableEnum):
    HD = "hd"
    SD = "sd"
    Null = ""


class FranksImageStyle(ParseableEnum):
    Natural = "natural"
    Vivid = "vivid"
    Null = None


class FranksImageScale(ParseableEnum):
    Square = "1024x1024"
    Portrait = "1024x1762"
    Landscape = "1762x1024"
    Null = ""


class FranksChatWebsocketSendMessage:
    def __init__(self):
        self.__attachments = []
        self.__generate_image: bool = False
        self.__image_quality: FranksImageQuality = FranksImageQuality.Null
        self.__image_style: FranksImageStyle = FranksImageStyle.Null
        self.__image_orientation: FranksImageScale = FranksImageScale.Null
        self.__init_message: str | None = None
        self.__is_in_session = True
        self.__model = "gpt-4"
        self.__prompt: str = ""
        self.__return_session_uid: FranksChatID | None = None
        self.__session_uid: FranksChatID | None = None
        self.__type: FranksWebsocketMessageType = FranksWebsocketMessageType.Null

    def set_type(self, msg_type: FranksWebsocketMessageType):
        self.__type = msg_type

    def validate(self):
        if self.__type is None or self.__type == "":
            return False

        if self.__return_session_uid is None:
            return False

        if self.__session_uid is None:
            return False

        if self.__generate_image:
            if (
                self.__image_quality == FranksImageQuality.Null
                or self.__image_style == FranksImageStyle.Null
                or self.__image_orientation == FranksImageScale.Null
            ):
                return False

        if self.__prompt == "":
            return False

        return True

    def set_return_session_uid(self, uid: FranksChatID):
        self.__return_session_uid = uid

    def set_session_uid(self, uid: FranksChatID):
        self.__session_uid = uid

    def set_prompt(self, prompt: str):
        self.__prompt = prompt

    def set_generate_image(self, generate: bool):
        self.__generate_image = generate

    def set_image_quality(self, quality: FranksImageQuality):
        self.__image_quality = quality

    def set_image_style(self, style: FranksImageStyle):
        self.__image_style = style

    def set_image_orientation(self, orientation: FranksImageScale):
        self.__image_orientation = orientation

    def set_init_message(self, init_message: str):
        self.__init_message = init_message

    def to_json(self):
        return self.__str__()

    def __str__(self):
        as_dict = {
            "attachments": self.__attachments,
            "generate_image": self.__generate_image,
            "image_style": self.__image_style.value,
            "image_quality": self.__image_quality.value,
            "image_orientation": self.__image_orientation.value,
            "init_message": self.__init_message,
            "is_in_session": self.__is_in_session,
            "model": self.__model,
            "prompt": self.__prompt,
            "return_session_uid": self.__return_session_uid.get(),
            "session_uid": self.__session_uid.get(),
            "type": self.__type.value,
        }

        if not self.__generate_image:
            del as_dict["image_quality"]
            del as_dict["image_orientation"]

        return json.dumps(as_dict)


class FranksChatWebsocketReceiveMessage:
    def __init__(self, raw: str):
        message: dict[str, Any] = json.loads(raw)

        self.__type: FranksWebsocketMessageType = FranksWebsocketMessageType.from_str(
            message["type"]
        )

        self.__status: FranksWebsocketStatus = FranksWebsocketStatus.Error
        if "status" in message.keys():
            self.__status = FranksWebsocketStatus.from_str(message["status"])

        self.__message: str = None
        if "message" in message.keys():
            self.__message = message["message"]

        self.__generate_image: bool = False
        self.__session_uid: FranksChatID | None = None

        if (
            self.__type == FranksWebsocketMessageType.Post
            and self.__status == FranksWebsocketStatus.Success
        ):
            self.__session_uid: FranksChatID = FranksChatID(message["session_uid"])
            self.__generate_image = message["generate_image"]

    @property
    def msg_type(self) -> FranksWebsocketMessageType:
        return self.__type

    @property
    def status(self) -> FranksWebsocketStatus:
        return self.__status

    @property
    def message(self) -> str:
        return self.__message

    @property
    def generate_image(self) -> bool:
        return self.__generate_image

    @property
    def session_uid(self) -> FranksChatID | None:
        return self.__session_uid


class FranksChatResponseState(ParseableEnum):
    WAITING = "waiting"
    SENT_QUERY = "sent_query"
    GENERATING = "generating"
    SUCCESS = "success"


class FranksChatInstance:
    class _QueryManager:
        __allow_query = False

        def set_allow_query(self, value: bool):
            self.__allow_query = value

        def get_allow_query(self) -> bool:
            return self.__allow_query

    class _ResponseStateManager:
        __state: FranksChatResponseState = FranksChatResponseState.WAITING
        __response: list[str] = []

        def set_state(self, state: FranksChatResponseState):
            self.__state = state

        def get_state(self) -> FranksChatResponseState:
            return self.__state

        def set_response(self, response: list[str]):
            self.__response = response

        def get_response(self) -> list[str]:
            return self.__response

    def __init__(self, user: discord.User, session_id: FranksChatID):
        self.__user = user
        self.__chat_id = session_id
        self.__active = False
        self.__query_manager = self._QueryManager()
        self.__state_manager = self._ResponseStateManager()

        auth = environ.get("AI_MODEL_AUTH_TOKEN")
        if auth is None:
            raise ValueError("AI_MODEL_AUTH_TOKEN not set.")
        self.__socket_url = f"wss://api.franks.ai/?Authorization={auth}"
        self.__websocket = None
        self.__thread = None
        self.__phrase: list[str] = []

        self.ext_on_message: Callable[[str], None] = None
        self.ext_on_close: Callable[[discord.User], None] = None

    @property
    def session_id(self) -> FranksChatID:
        return self.__chat_id

    @property
    def live(self) -> bool:
        if self.__websocket is None:
            return False

        return self.__active

    def __on_open(self, _: websocket.WebSocketApp):
        BirbiaLogger.debug(f"Websocket opened for {self.__user.id}.")
        self.__active = True
        self.__query_manager.set_allow_query(True)

    def __on_message(self, _: websocket.WebSocketApp, message: str):
        try:
            encoded = FranksChatWebsocketReceiveMessage(message)

            match encoded.status.value:
                case FranksWebsocketStatus.NewToken.value:
                    if (
                        self.__state_manager.get_state()
                        == FranksChatResponseState.GENERATING
                    ):
                        self.__state_manager.set_state(
                            FranksChatResponseState.GENERATING
                        )

                    if self.__query_manager.get_allow_query():
                        self.__query_manager.set_allow_query(False)

                    self.__phrase.append(encoded.message)
                    return
                case FranksWebsocketStatus.LLMDone.value:
                    parts = self.__split_message(self.__phrase)
                    self.__state_manager.set_response(parts)
                    self.__phrase.clear()
                    return
                case FranksWebsocketStatus.Success.value:
                    self.__state_manager.set_state(FranksChatResponseState.SUCCESS)

                    if self.ext_on_message is not None:
                        self.ext_on_message(message)
                    return
                case _:
                    return
        except Exception as e:
            msg = f"Failed to decode message for {self.__user.id}, thread: {self.__thread.ident}, stack:"
            BirbiaLogger.error(f"{msg}\n{e.with_traceback(None)}")

    def __on_error(self, _: websocket.WebSocketApp, error: Exception):
        msg = f"Websocket error for {self.__user.id}, thread: {self.__thread.ident}, stack:"
        BirbiaLogger.error(f"{msg}\n{error.with_traceback(None)}")

    def __on_close(
        self, _: websocket.WebSocketApp, close_status_code: int, close_msg: str
    ):
        BirbiaLogger.debug(f"Websocket closed for {self.__user.id}.")
        if self.ext_on_close is not None:
            self.ext_on_close(self.__user)
        self.__active = False

    def __start_ws(self):
        # create websocket connection
        websocket.enableTrace(False)
        self.__websocket = websocket.WebSocketApp(
            url=self.__socket_url,
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_error=self.__on_error,
            on_close=self.__on_close,
        )

        self.__thread = threading.Thread(
            target=lambda: self.__websocket.run_forever(reconnect=5),
        )
        self.__thread.daemon = True
        self.__thread.start()

    async def start_chat(self):
        # start websocket connection
        if self.__websocket is None:
            self.__start_ws()

        while not self.__active:
            await asyncio.sleep(0.5)

    async def send_message(self, message: str):
        # send message to AI
        if self.__websocket is None:
            raise ValueError("Websocket not initialized.")

        if not self.__active:
            raise ValueError("Websocket not active.")

        msg = FranksChatWebsocketSendMessage()
        msg.set_type(FranksWebsocketMessageType.Post)
        msg.set_return_session_uid(self.__chat_id)
        msg.set_session_uid(self.__chat_id)
        msg.set_prompt(message)

        if not msg.validate():
            return -1

        self.__websocket.send(str(msg))
        self.__state_manager.set_state(FranksChatResponseState.SENT_QUERY)
        self.__state_manager.set_response([])
        while self.__state_manager.get_state() != FranksChatResponseState.SUCCESS:
            await asyncio.sleep(0.5)

        self.__state_manager.set_state(FranksChatResponseState.WAITING)
        self.__query_manager.set_allow_query(True)
        return self.__state_manager.get_response()

    def can_ask(self) -> bool:
        return self.__query_manager.get_allow_query()

    def close_chat(self):
        # close websocket connection
        self.__websocket.close()

    def __split_message(self, raw_tokens: list[str]) -> list[str]:
        # split message if longer that 2000 characters
        if len("".join(raw_tokens)) <= 2000:
            return ["".join(raw_tokens)]

        parts = []
        current_part = ""
        backtick_count = 0

        max_length = 2000
        for token in raw_tokens:
            if len(current_part) + len(token) > max_length:
                # If adding this token exceeds the limit
                if backtick_count % 2 != 0:
                    # If we have an odd number of backticks, move the last one to the next part
                    new_part = current_part[: current_part.rfind("`")]
                    leftover = current_part[current_part.rfind("`") :]
                    parts.append(new_part)
                    current_part = leftover + token
                    backtick_count = 1
                else:
                    parts.append(current_part)
                    current_part = token
                    backtick_count = token.count("`")
            else:
                current_part += token
                backtick_count += token.count("`")

        if current_part:
            parts.append(current_part)

        return parts
