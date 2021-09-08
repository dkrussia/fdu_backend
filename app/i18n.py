import gettext
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from fastapi import Request

class LazyString(object):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, attr):
        if attr == "__setstate__":
            raise AttributeError(attr)

        string = str(self)
        if hasattr(string, attr):
            return getattr(string, attr)

        raise AttributeError(attr)

    def __str__(self):
        message = self._func(*self._args)
        return str(message)

    def __repr__(self):
        message = self._func(*self._args)
        return str(message)

    def __len__(self):
        return len(str(self))

    def __getitem__(self, key):
        return str(self)[key]

    def __iter__(self):
        return iter(str(self))

    def __contains__(self, item):
        return item in str(self)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)

    def __mul__(self, other):
        return str(self) * other

    def __rmul__(self, other):
        return other * str(self)

    def __lt__(self, other):
        return str(self) < other

    def __le__(self, other):
        return str(self) <= other

    def __eq__(self, other):
        return str(self) == other

    def __ne__(self, other):
        return str(self) != other

    def __gt__(self, other):
        return str(self) > other

    def __ge__(self, other):
        return str(self) >= other

    def __html__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def __mod__(self, other):
        return str(self) % other

    def __rmod__(self, other):
        return other + str(self)



class i18n:
    @staticmethod
    def gettext_func(text):
        language = {
            "ru": gettext.translation('messages', localedir='locale', languages=['ru'])
        }
        locale = language.get(_Local)
        if locale and locale != 'en':
            locale.install()
            return locale.gettext(text)
        return gettext.gettext(text)

    @staticmethod
    def lazy_gettext_func(text):
        return LazyString(i18n.gettext_func, text)


class i18nMiiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        global _Local
        _Local = request.headers["Accept-Language"]
        response = await call_next(request)
        return response

t_func = i18n.gettext_func
lazy_t_func = i18n.lazy_gettext_func