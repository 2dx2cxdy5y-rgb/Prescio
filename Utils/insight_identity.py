import hashlib


def generate_insight_id(
    domain: str,
    category: str,
    headline: str,
    queue: str = ""
) -> str:
    """
    Generate deterministic insight identity.

    The same operational issue should always
    produce the same ID across runs.
    """

    raw_key = (
        f"{domain}|"
        f"{category}|"
        f"{headline}|"
        f"{queue}"
    )

    return hashlib.md5(
        raw_key.encode("utf-8")
    ).hexdigest()