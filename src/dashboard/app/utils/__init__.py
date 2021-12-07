from typing import Any, Callable, Coroutine, Optional, TypeVar
_T = TypeVar('_T')
def async_cache(func: Callable[[], Coroutine[Any, Any, _T]]):
    value: Optional[_T] = None
    async def wrapper():
        nonlocal value
        if value is None:
            value = await func()
        return value
    return wrapper

def sync_cache(func: Callable[[],  _T]):
    value: Optional[_T] = None
    def wrapper():
        nonlocal value
        if value is None:
            value = func()
        return value
    return wrapper