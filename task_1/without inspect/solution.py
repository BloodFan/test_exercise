from functools import wraps
from typing import Any, Callable, TypeVar, get_type_hints


RT = TypeVar('RT')


def strict(func: Callable[..., RT]) -> Callable[..., RT]:
    if not func.__annotations__:
        raise TypeError("Function must have type annotations")

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> RT:
        annotations = get_type_hints(func)
        # annotations = func.__annotations__
        expected_arg_names = [k for k in annotations if k != "return"]
        expected_arg_types = {
            name: annotations[name] for name in expected_arg_names
        }

        provided_args = list(args)
        provided_kwargs = kwargs.keys()

        # Проверка на пропущенные аргументы
        if len(provided_args) + len(provided_kwargs) < len(expected_arg_names):
            missing_args = [
                name for name in expected_arg_names
                if name not in kwargs and expected_arg_names.index(name) >= len(provided_args)
            ]
            raise TypeError(f"Missing required arguments: {missing_args}")

        # Проверка на неожиданные именованные аргументы
        unexpected_kwargs = [k for k in kwargs if k not in expected_arg_names]
        if unexpected_kwargs:
            raise TypeError(f"Unexpected keyword argument(s): {unexpected_kwargs}")

        # Проверяем превышение количества аргументов
        if len(provided_args) + len(provided_kwargs) > len(expected_arg_names):
            raise TypeError(
                f"Expected {len(expected_arg_names)} arguments, "
                f"got {len(provided_args) + len(provided_kwargs)}"
            )

        for arg, name in zip(provided_args, expected_arg_names):
            if name in expected_arg_types and not isinstance(
                arg, expected_arg_types[name]
            ):
                raise TypeError(
                    f"Argument '{name}' must be "
                    f"{expected_arg_types[name].__name__}, not {type(arg).__name__}"
                )

        for name, value in kwargs.items():
            if name not in expected_arg_types:
                raise TypeError(f"Unexpected keyword argument '{name}'")
            if not isinstance(value, expected_arg_types[name]):
                raise TypeError(
                    f"Argument '{name}' must be "
                    f"{expected_arg_types[name].__name__}, not {type(value).__name__}"
                )

        return func(*args, **kwargs)

    return wrapper
