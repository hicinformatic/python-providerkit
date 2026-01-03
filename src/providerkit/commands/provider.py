"""Provider command for listing and filtering providers."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from qualitybase.commands.base import Command
from qualitybase.cli import _get_package_name as _get_package_name_from_context  # noqa: TID252

from ..helpers import get_providers, try_providers, try_providers_first  # noqa: TID252

if TYPE_CHECKING:
    from pathlib import Path


def _list_providers(args: list[str]) -> bool:  # noqa: ARG001
    """List providers.

    Args:
        args: Command arguments.

    Returns:
        True if command executed successfully, False otherwise.
    """
    return True

def _provider_command(args: list[str]) -> bool:  # noqa: C901
    """List and filter providers.

    Args:
        args: Command arguments.

    Returns:
        True if command executed successfully, False otherwise.
    """
    output_format = "table"
    dir_path: str | Path | None = None
    json_path: str | Path | None = None
    query_string: str | None = None
    mode: str = "list"
    mode_args: dict[str, str | bool] = {}
    first: bool = False
    raw: bool = False
    additional_args: dict[str, str | bool] = {}
    attribute_search: dict[str, str] = {}

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--mode" and i + 1 < len(args):
            mode = args[i + 1]
            i += 2
            first_positional = True
            while i < len(args) and not args[i].startswith("--"):
                mode_arg = args[i]
                if "=" in mode_arg:
                    key, value = mode_arg.split("=", 1)
                    additional_args[key] = value
                    first_positional = False
                else:
                    if first_positional:
                        additional_args["query"] = mode_arg
                        first_positional = False
                    else:
                        additional_args[mode_arg] = True
                i += 1
        elif arg == "--attr":
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                attr_arg = args[i]
                if "=" in attr_arg:
                    key, value = attr_arg.split("=", 1)
                    attribute_search[key] = value
                else:
                    print(f"Invalid attribute format: {attr_arg}. Expected format: key=value", file=sys.stderr)
                    return False
                i += 1
        elif arg == "--format" and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        elif arg == "--dir" and i + 1 < len(args):
            dir_path = args[i + 1]
            i += 2
        elif arg == "--json" and i + 1 < len(args):
            json_path = args[i + 1]
            i += 2
        elif arg == "--filter" or arg == "--backend":
            query_string = args[i + 1]
            i += 2
        elif arg == "--first":
            first = True
            i += 1
        elif arg == "--raw":
            raw = True
            i += 1
        else:
            print(f"Unknown argument: {arg}", file=sys.stderr)
            return False

    lib_name = _get_package_name_from_context()

    providers_args: dict[str, Any] = {
        "format": output_format,
        "json": json_path,
        "lib_name": lib_name,
        "dir_path": dir_path,
        "query_string": query_string,
    }

    if attribute_search:
        providers_args["attribute_search"] = attribute_search

    if mode_args:
        print(f"\nMode arguments for {mode}: {mode_args}\n")

    if mode == "list":
        providers_result = get_providers(
            format=output_format,
            json=json_path,
            lib_name=lib_name,
            dir_path=dir_path,
            query_string=query_string,
            attribute_search=attribute_search if attribute_search else None,
        )
        print(providers_result)
        return True

    providers_args.update(mode_args)
    if raw:
        additional_args["raw"] = True
    providers_args["additional_args"] = additional_args

    if first:
        result = try_providers_first(
            command=mode,
            **providers_args,
        )
    else:
        result = try_providers(
            command=mode,
            **providers_args,
        )

    print(result)
    return True

provider_command = Command(_provider_command, "List and filter providers (use --list [query] --format [table|json|xml])")
