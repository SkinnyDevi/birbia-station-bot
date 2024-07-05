class FranksChatID:
    def __init__(self, chat_id: str):
        self.__chat_id = chat_id

    def get(self) -> str:
        return self.__chat_id

    def __hash__(self) -> int:
        return hash(self.__chat_id)

    def __str__(self) -> str:
        return self.__chat_id


class FranksAPIResponse:
    def __init__(self, response: dict):
        for key, value in response.items():
            self.__dict__[f"__{key}"] = value

    def __setattr__(self, k, v):
        raise AttributeError(
            f"Cannot set attributes on a {self.__class__.__name__} object"
        )

    def __str__(self) -> str:
        return str(self.__dict__)


class FranksAPIUser(FranksAPIResponse):
    def __init__(self, user: dict):
        super().__init__(user)

    @property
    def created_at(self) -> str:
        """Date the user was created at"""
        return self.__getattribute__("__created_at")

    @property
    def id(self) -> str:
        """User's ID"""
        return self.__getattribute__("__id")

    @property
    def modified_at(self) -> str:
        """Date the user was last modified at"""
        return self.__getattribute__("__modified_at")

    @property
    def name(self) -> str:
        """User's name"""
        return self.__getattribute__("__name")

    @property
    def public_username(self) -> str:
        """Public username"""
        return self.__getattribute__("__public_username")

    @property
    def uid(self) -> str:
        """User's UID"""
        return self.__getattribute__("__uid")


class FranksAPISessionResponse(FranksAPIResponse):
    def __init__(self, response: dict):
        super().__init__(response)

    def __setattr__(self, k, v):
        super().__setattr__(k, v)

    @property
    def created_at(self) -> str:
        """Date the session was created at"""
        return self.__getattribute__("__created_at")

    @property
    def creator(self) -> FranksAPIUser:
        """User who created the session"""
        return FranksAPIUser(self.__getattribute__("__creator"))

    @property
    def is_temporary(self) -> bool:
        """Whether the session is temporary"""
        return self.__getattribute__("__is_temporary")

    @property
    def model(self) -> str:
        """Model used in the session"""
        return self.__getattribute__("__model")

    @property
    def name(self) -> str:
        """Name of the session"""
        return self.__getattribute__("__name")

    @property
    def uid(self) -> FranksChatID:
        """Session's UID"""
        return FranksChatID(self.__getattribute__("__uid"))


class FranksAPIGetSessionResponse(FranksAPIResponse):
    def __init__(self, response: dict):
        super().__init__(response)

    def __setattr__(self, k, v):
        super().__setattr__(k, v)

    @property
    def count(self) -> int:
        """Number of sessions"""
        return self.__getattribute__("__count")

    @property
    def results(self) -> list[FranksAPISessionResponse]:
        """List of sessions"""
        results = self.__getattribute__("__results")
        return [FranksAPISessionResponse(session) for session in results]


class FranksAPIDeleteSessionResponse(FranksAPIResponse):
    def __init__(self, response: dict):
        super().__init__(response)

    def __setattr__(self, k, v):
        super().__setattr__(k, v)

    @property
    def success(self) -> bool:
        """Whether the session was successfully deleted"""
        return self.__getattribute__("__success")
