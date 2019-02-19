import os
import abc
import sys
import subprocess as sp
from os import path

from .response import Response


class Runner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run(self, positionals=None, flags=None, stdin=None,
            environ=None, **kw) -> Response:
        pass


class SubprocessRunner(Runner):

    @property
    def bootstrapper(self):
        bootstrapper = 'bddcli-bootstrapper'
        if 'VIRTUAL_ENV' in os.environ:
            bindir = path.join(os.environ['VIRTUAL_ENV'], 'bin')
        else:
            bindir = '/usr/local/bin'
        return path.join(bindir, bootstrapper)

    def __init__(self, application, environ=None):
        self.application = application
        self.environ = environ

    def run(self, positionals=None, flags=None, stdin=None,
            working_directory=None, environ=None, **kw) -> Response:
        command = [
            self.bootstrapper,
            self.application.name,
            self.application.address,
        ]

        if flags:
            command += flags

        if positionals:
            command += positionals

        result = sp.run(
            ' '.join(command),
            input=stdin,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            shell=True,
            encoding='utf8',
            env=environ,
            cwd=working_directory,
        )
        return Response(result.returncode, result.stdout, result.stderr)

