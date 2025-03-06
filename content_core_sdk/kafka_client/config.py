import os
from dataclasses import dataclass
from typing import Self


@dataclass
class KafkaConfig:
    """
    Configuration for connecting to a Kafka cluster.
    """

    bootstrap_servers: str

    @classmethod
    def from_env(cls) -> Self:
        env_vars = {"KAFKA_BOOTSTRAP_SERVERS": os.getenv("KAFKA_BOOTSTRAP_SERVERS")}

        missing_vars = [key for key, value in env_vars.items() if not value]
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            raise EnvironmentError(error_msg)

        return cls(bootstrap_servers=env_vars["KAFKA_BOOTSTRAP_SERVERS"])


