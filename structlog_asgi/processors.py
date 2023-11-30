from structlog.typing import EventDict, WrappedLogger


def extract_uvicorn_request_meta(
    _: WrappedLogger,
    __: str,
    event_dict: EventDict,
) -> EventDict:
    record = event_dict.get("_record")
    if (
        record
        and record.name == "uvicorn.access"
        and len(event_dict.get("positional_args", ())) == 5  # noqa: PLR2004
    ):
        (
            client_addr,
            method,
            full_path,
            http_version,
            status_code,
        ) = event_dict["positional_args"]

        event_dict["client_addr"] = client_addr
        event_dict["http_method"] = method
        event_dict["url"] = full_path
        event_dict["http_version"] = http_version
        event_dict["status_code"] = status_code

    return event_dict


def remove_processors_meta(
    _: WrappedLogger,
    __: str,
    event_dict: EventDict,
) -> EventDict:
    del event_dict["_record"]
    del event_dict["_from_structlog"]
    event_dict.pop("positional_args", None)
    return event_dict
