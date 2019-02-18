import re
import sys
from abc import ABCMeta, abstractmethod

from .exceptions import CallVerifyError
from .response import Response
from .runners import SubprocessRunner


class Call(metaclass=ABCMeta):

    def __init__(self, title, description=None, response=None):
        self.title = title
        self.description = description
        if response is not None and not isinstance(response, Response):
            response = Response(**response)
        self.response = response

    def to_dict(self):
        result = dict(
            title=self.title,
        )

        if self.stdin is not None:
            result['stdin'] = self.stdin

        if self.positionals is not None:
            result['positionals'] = self.positionals

        if self.flags is not None:
            result['flags'] = self.flags

        if self.response is not None:
            result['response'] = self.response.to_dict()

        return result

    def invoke(self, application) -> Response:
        return SubprocessRunner(application).run(
            self.positionals,
            self.flags,
            self.stdin,
            self.extra_environ
        )

    def verify(self, application):
        response = self.invoke(application)
        if self.response != response:
            raise CallVerifyError()

    def conclude(self, application):
        if self.response is None:
            self.response = self.invoke(application)

    @property
    @abstractmethod
    def stdin(self) -> str:  # pragma: no cover
        pass

    @stdin.setter
    @abstractmethod
    def stdin(self, value):  # pragma: no cover
        pass

    @property
    @abstractmethod
    def positionals(self) -> str:  # pragma: no cover
        pass

    @positionals.setter
    @abstractmethod
    def positionals(self, value):  # pragma: no cover
        pass

    @property
    @abstractmethod
    def flags(self) -> dict:  # pragma: no cover
        pass

    @flags.setter
    @abstractmethod
    def flags(self, value):  # pragma: no cover
        pass

    @property
    @abstractmethod
    def extra_environ(self) -> dict:  # pragma: no cover
        pass

    @extra_environ.setter
    @abstractmethod
    def extra_environ(self, value):  # pragma: no cover
        pass


class FirstCall(Call):

    _stdin = None
    _positionals = None
    _flags = None
    _extra_environ = None

    def __init__(self, title, positionals=None, flags=None, stdin=None,
                 extra_environ=None, description=None, response=None):

        super().__init__(title, description=description, response=response)
        self.stdin = stdin
        self.positionals = positionals
        self.flags = flags
        self.extra_environ = extra_environ

    @property
    def stdin(self):
        return self._stdin

    @stdin.setter
    def stdin(self, value):
        self._stdin = value

    @property
    def positionals(self):
        return self._positionals

    @positionals.setter
    def positionals(self, value):
        self._positionals = value

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, value):
        self._flags = value

    @property
    def extra_environ(self):
        return self._extra_environ

    @extra_environ.setter
    def extra_environ(self, value):
        self._extra_environ = value


class Unchanged:
    pass


UNCHANGED = Unchanged()


class AlteredCall(Call):

    def __init__(self, base_call, title, positionals=UNCHANGED,
                 flags=UNCHANGED, stdin=UNCHANGED, extra_environ=None,
                 description=None, response: Response=None):

        self.base_call = base_call
        self.diff = {}
        super().__init__(title, description=description, response=response)
        self.stdin = stdin
        self.positionals = positionals
        self.flags = flags
        self.extra_environ = extra_environ

    def to_dict(self):
        result = dict(title=self.title)
        result.update(self.diff)

        if self.description is not None:
            result['description'] = self.description

        if self.response is not None:
            result['response'] = self.response.to_dict()

        return result

    def update_diff(self, key, value):
        if value is UNCHANGED:
            self.diff.pop(key, None)
            return

        self.diff[key] = value

    @property
    def stdin(self):
        return self.diff.get('stdin', self.base_call.stdin)

    @stdin.setter
    def stdin(self, value):
        self.update_diff('stdin', value)

    @stdin.deleter
    def stdin(self):
        del self.diff['stdin']

    @property
    def positionals(self):
        return self.diff.get('positionals', self.base_call.positionals)

    @positionals.setter
    def positionals(self, value):
        self.update_diff('positionals', value)

    @positionals.deleter
    def positionals(self):
        del self.diff['positionals']

    @property
    def flags(self):
        return self.diff.get('flags', self.base_call.flags)

    @flags.setter
    def flags(self, value):
        self.update_diff('flags', value)

    @flags.deleter
    def flags(self):
        del self.diff['flags']

    @property
    def extra_environ(self):
        return self.diff.get('extra_environ', self.base_call.extra_environ)

    @extra_environ.setter
    def extra_environ(self, value):
        self.update_diff('extra_environ', value)

    @extra_environ.deleter
    def extra_environ(self):
        del self.diff['extra_environ']

