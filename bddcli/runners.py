import os
import abc
import sys
import subprocess as sp
from os import path


class Runner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run(self, arguments=None, environ=None, **kw):  # pragma: no cover
        pass


class SubprocessRunner(Runner):

    @property
    def bootstrapper(self):
        bootstrapper = 'bddcli-bootstrapper'
        if 'VIRTUAL_ENV' in os.environ:
            bindir = path.join(os.environ['VIRTUAL_ENV'], 'bin')
        else:  # pragma: no cover
            bindir = '/usr/local/bin'

        return path.join(bindir, bootstrapper)

    def __init__(self, application, environ=None):
        self.application = application
        self.environ = environ

    def run(self, arguments=None, working_directory=None, environ=None, **kw):
        command = [
            self.bootstrapper,
            self.application.name,
            self.application.address,
        ]

        if arguments:
            command += arguments

        process = sp.Popen(
            ' '.join(command),
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            shell=True,
            env=environ,
            cwd=working_directory,
            preexec_fn=os.setpgrp,
            **kw,
        )
        return process

