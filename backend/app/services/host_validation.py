
import ipaddress
import re
import socket
from urllib.parse import urlsplit

from app.core.config import ENVIRONMENT


def validate_database_host(host: str) -> str:
    """Validate a database hostname or IP address."""

    if not isinstance(host, str) or not host.strip():
        raise ValueError("Database host cannot be empty.")

    host = host.strip()

    if any(char in host for char in ("/", "\\", "@", " ", "\n", "\r", "\t")):
        raise ValueError("Invalid database hostname.")

    if "://" in host:
        raise ValueError("Provide only a hostname or IP address.")

    try:
        if urlsplit(f"//{host}").port is not None:
            raise ValueError("Provide the port separately.")
    except ValueError:
        raise ValueError("Invalid database hostname.") from None

    environment = ENVIRONMENT.lower()

    if environment not in ("development", "local", "dev", "production", "prod"):
        raise ValueError("Unsupported application environment.")

    try:
        address = ipaddress.ip_address(host)
        addresses = {address}

    except ValueError:
        hostname = host.rstrip(".")

        if len(hostname) > 253 or not hostname:
            raise ValueError("Invalid database hostname.")

        labels = hostname.split(".")

        if any(
            not re.fullmatch(
                r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?",
                label,
            )
            for label in labels
        ):
            raise ValueError("Invalid database hostname.")

        if environment in ("development", "local", "dev") and hostname.lower() == "localhost":
            return host

        try:
            addresses = {
                ipaddress.ip_address(result[4][0])
                for result in socket.getaddrinfo(
                    hostname,
                    None,
                    type=socket.SOCK_STREAM,
                )
            }
        except (socket.gaierror, ValueError):
            raise ValueError("Unable to resolve database hostname.") from None

    if not addresses:
        raise ValueError("Database hostname did not resolve.")

    if environment in ("production", "prod"):
        for address in addresses:
            if not address.is_global:
                raise ValueError(
                    "Private, loopback, link-local, and reserved addresses "
                    "are not allowed in production."
                )

    return host
