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
from src.core.language import BirbiaLanguage


class ParseableEnum(Enum):
    """Enum class that allows for parsing of values from strings."""

    @classmethod
    def from_str(cls, value: str):
        for e in cls:
            if str(e.value).lower() == str(value).lower():
                return e

        raise ValueError(f"Invalid value for {cls.__name__}: {value}")


class FranksWebsocketMessageType(ParseableEnum):
    """Enum for the type of message of the Franks AI websocket."""

    Post = "post"
    Null = None
    Session = "session"


class FranksWebsocketStatus(ParseableEnum):
    """Enum for the status of the Franks AI websocket."""

    Success = "success"
    Error = "error"
    NewToken = "new_token"
    Connect = "connect"
    LLMDone = "llm_done"


class FranksImageQuality(ParseableEnum):
    """Enum for the quality of the image generated by the Franks AI."""

    HD = "hd"
    SD = "sd"
    Null = ""


class FranksImageStyle(ParseableEnum):
    """Enum for the style of the image generated by the Franks AI."""

    Natural = "natural"
    Vivid = "vivid"
    Null = None


class FranksImageScale(ParseableEnum):
    """Enum for the scale of the image generated by the Franks AI."""

    Square = "1024x1024"
    Portrait = "1024x1762"
    Landscape = "1762x1024"
    Null = ""


class FranksChatWebsocketSendMessage:
    """Class for sending a message through the Franks AI websocket."""

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
        self.__is_valid = False

    def set_type(self, msg_type: FranksWebsocketMessageType):
        """Set the type of the message."""

        self.__type = msg_type

    def validate(self):
        """Validate the message."""

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

        self.__is_valid = True
        return True

    def set_return_session_uid(self, uid: FranksChatID):
        """Set the return session UID."""

        self.__return_session_uid = uid

    def set_session_uid(self, uid: FranksChatID):
        """Set the session UID."""

        self.__session_uid = uid

    def set_prompt(self, prompt: str):
        """Set the prompt for the message."""

        self.__prompt = prompt

    def set_generate_image(self, generate: bool):
        """Set whether to generate an image."""

        self.__generate_image = generate

    def set_image_quality(self, quality: FranksImageQuality):
        """Set the quality of the image."""

        self.__image_quality = quality

    def set_image_style(self, style: FranksImageStyle):
        """Set the style of the image."""

        self.__image_style = style

    def set_image_orientation(self, orientation: FranksImageScale):
        """Set the orientation of the image."""

        self.__image_orientation = orientation

    def set_init_message(self, init_message: str):
        """Set the initial message."""

        self.__init_message = init_message

    def to_json(self):
        """Convert the message to a JSON string. This is the same as using `str(this_instance)`."""

        return self.__str__()

    def __str__(self):
        if not self.__is_valid:
            raise ValueError("Message is not valid/has not been validated.")

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
    """Class for receiving a message from the Franks AI websocket."""

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
        """Type of the message."""

        return self.__type

    @property
    def status(self) -> FranksWebsocketStatus:
        """Status of the message."""

        return self.__status

    @property
    def message(self) -> str:
        """Message received from the websocket."""

        return self.__message

    @property
    def generate_image(self) -> bool:
        """Whether the message is to generate an image."""

        return self.__generate_image

    @property
    def session_uid(self) -> FranksChatID | None:
        """Session UID of the message."""

        return self.__session_uid


class FranksChatResponseState(ParseableEnum):
    """Enum for the state of the response from the `FranksChatInstance`."""

    WAITING = "waiting"
    SENT_QUERY = "sent_query"
    GENERATING = "generating"
    SUCCESS = "success"


class FranksChatInstance:
    """Class for a Franks AI chat instance."""

    class _QueryManager:
        """Class for managing the query state of the chat instance."""

        __allow_query = False

        def set_allow_query(self, value: bool):
            self.__allow_query = value

        def get_allow_query(self) -> bool:
            return self.__allow_query

    class _ResponseStateManager:
        """Class for managing the response state of the chat instance."""

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
        self.__lang = BirbiaLanguage.instance()

        self.__websocket = None
        self.__first_message = False
        self.__thread = None
        self.__phrase: list[str] = []

        self.ext_on_message: Callable[[str], None] = None
        """Function to call when a message is received from the AI. Will be executed when it has received last token."""

        self.ext_on_close: Callable[[discord.User], None] = None
        """Function to call when the chat/websocket is closed."""

    @property
    def session_id(self) -> FranksChatID:
        """Session ID of the chat instance."""

        return self.__chat_id

    @property
    def live(self) -> bool:
        """Whether the chat instance is live."""

        return False if self.__websocket is None else self.__active

    def __on_open(self, _: websocket.WebSocketApp):
        """Function to call when the websocket is opened."""

        BirbiaLogger.debug(f"Websocket opened for {self.__user.id}.")
        self.__active = True
        self.__query_manager.set_allow_query(True)

    def __on_message(self, _: websocket.WebSocketApp, message: str):
        """Function to call when a message is received from the websocket."""

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

                    if not self.__first_message:
                        self.__first_message = True

                    if self.ext_on_message is not None:
                        self.ext_on_message(message)
                    return
                case _:
                    return
        except Exception as e:
            msg = f"Failed to decode message for {self.__user.id}, thread: {self.__thread.ident}, stack:"
            BirbiaLogger.error(f"{msg}\n{e.with_traceback(None)}")

    def __on_error(self, _: websocket.WebSocketApp, error: Exception):
        """Function to call when an error occurs with the websocket."""

        msg = f"Websocket error for {self.__user.id}, thread: {self.__thread.ident}, stack:"
        BirbiaLogger.error(f"{msg}\n{error.with_traceback(None)}")

    def __on_close(
        self, _: websocket.WebSocketApp, close_status_code: int, close_msg: str
    ):
        """Function to call when the websocket is closed."""

        BirbiaLogger.debug(f"Websocket closed for {self.__user.id}.")
        if self.ext_on_close is not None:
            self.ext_on_close(self.__user)
        self.__active = False

    def __start_ws(self):
        """Start the websocket connection thread."""

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
        """Start the chat instance."""

        if self.__websocket is None:
            self.__start_ws()

        while not self.__active:
            await asyncio.sleep(0.5)

    async def send_message(self, message: str, requester: discord.User):
        """Send a message to the AI."""

        if self.__websocket is None:
            raise ValueError("Websocket not initialized.")

        if not self.__active:
            raise ValueError("Websocket not active.")

        msg = FranksChatWebsocketSendMessage()
        msg.set_type(FranksWebsocketMessageType.Post)
        msg.set_return_session_uid(self.__chat_id)
        msg.set_session_uid(self.__chat_id)

        formatted_message = f"{requester.name}: {message}"
        if not self.__first_message:
            msg.set_prompt(self.__lang.ai_init_message + formatted_message)
        else:
            msg.set_prompt(formatted_message)

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
        """Whether the chat instance can send a query."""

        return self.__query_manager.get_allow_query()

    def close_chat(self):
        """Close the chat instance."""

        self.__websocket.close()

    def __split_message(self, raw_tokens: list[str]) -> list[str]:
        """Split a message into parts of 2000 characters."""

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
