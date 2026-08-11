"""
Shared helpers for the scanner package: URL normalization and a
Server-Side-Request-Forgery (SSRF) guard.

Because SecureLens accepts an arbitrary URL from a client and then makes
outbound requests / opens sockets / shells out to nmap & nikto against it,
we must make sure the target isn't a private, loopback, link-local, or
otherwise internal address. Without this check a user (or an attacker
abusing the public API) could point a scan at "127.0.0.1", "169.254.169.254"
(cloud metadata endpoints), or an internal RFC1918 address and use
SecureLens as an internal network scanner / SSRF pivot.
"""

import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeTargetError(Exception):
    """Raised when a scan target resolves to a disallowed address."""


def normalize_url(url: str) -> str:
    """Ensure the URL has a scheme. 'github.com' -> 'https://github.com'."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def extract_hostname(url: str) -> str:
    hostname = urlparse(url).hostname
    if not hostname:
        raise UnsafeTargetError(f"Could not parse a hostname from '{url}'")
    return hostname


def assert_public_target(hostname: str) -> None:
    """
    Resolve `hostname` and raise UnsafeTargetError if any resolved address
    is private, loopback, link-local, multicast, reserved, or otherwise
    not a normal public internet address.

    Call this before running nmap / nikto / nessus against a target.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise UnsafeTargetError(f"Could not resolve host '{hostname}': {e}")

    for info in infos:
        ip_str = info[4][0]
        ip = ipaddress.ip_address(ip_str)

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise UnsafeTargetError(
                f"Refusing to scan '{hostname}' -> {ip_str}: "
                "resolves to a private/internal address."
            )


def safe_target_or_raise(url: str) -> tuple[str, str]:
    """
    Convenience wrapper: normalize the URL, extract the hostname, and
    verify it's safe to scan. Returns (normalized_url, hostname).
    """
    normalized = normalize_url(url)
    hostname = extract_hostname(normalized)
    assert_public_target(hostname)
    return normalized, hostname
