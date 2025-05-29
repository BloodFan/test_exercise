from functools import wraps
from inspect import signature
from typing import Any, Callable, TypeVar, get_type_hints

RT = TypeVar("RT")


def strict(func: Callable[..., RT]) -> Callable[..., RT]:
    annotations = get_type_hints(func)
    if not annotations:
        raise TypeError("Function must have type annotations")

    sig = signature(func)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> RT:
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()

        for name, value in bound_args.arguments.items():
            if name in annotations and not isinstance(value, annotations[name]):
                raise TypeError(
                    f"Argument '{name}' must be "
                    f"{annotations[name].__name__}, not {type(value).__name__}"
                )

        extra_args = set(kwargs) - set(sig.parameters)
        if extra_args:
            raise TypeError(
                f"Unexpected keyword argument(s): {list(extra_args)}"
            )

        return func(*args, **kwargs)

    return wrapper
