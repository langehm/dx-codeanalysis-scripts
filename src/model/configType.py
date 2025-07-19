
import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class EnvConfig:
    token: str
    organisation: str

    _instance: "EnvConfig" = None  # class-level cache

    @classmethod
    def load(cls) -> "EnvConfig":
        if cls._instance is not None:
            return cls._instance

        load_dotenv()
        token = os.getenv("GITHUB_TOKEN")
        org = os.getenv("GITHUB_ORGANISATION")

        if not token:
            raise EnvironmentError("GITHUB_TOKEN ist nicht gesetzt.")
        if not org:
            raise EnvironmentError("GITHUB_ORGANISATION ist nicht gesetzt.")

        cls._instance = cls(token=token, organisation=org)
        return cls._instance

    @classmethod
    def token(cls) -> str:
        return cls.load().token

    @classmethod
    def organisation(cls) -> str:
        return cls.load().organisation
