#!/usr/bin/env python3


def patch():
    import builtins
    from collections.abc import Mapping, Sequence
    from functools import wraps
    from types import ModuleType
    from typing import Optional

    _old_import = __import__

    @wraps(_old_import)
    def _new_import(
        name: str,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        locals: Optional[Mapping[str, object]] = None,  # noqa: A002
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> ModuleType:
        if level == 0 and (name == "playwright" or name.startswith("playwright.")):
            name = name.replace("playwright", "patchright", 1)
        return _old_import(name, globals, locals, fromlist, level)

    builtins.__import__ = _new_import  # noqa: A001
