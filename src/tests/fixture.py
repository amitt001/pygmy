import time
import atexit
import pytest
import subprocess

__all__ = [
    'run_test_server'
]


class PygmyApiTestServer:
    pygmyapi_proc = None

    @classmethod
    def start_pygmy_api_server(cls):
        command = ['coverage', 'run', 'pygmy_api_run.py', 'test']
        cls.pygmyapi_proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for server to start
        time.sleep(1)
        return cls.pygmyapi_proc

    @classmethod
    def terminate_pygmy_api_server(cls):
        if not cls.pygmyapi_proc or not cls.pygmyapi_proc.pid:
            return
        cls.pygmyapi_proc.terminate()


class PygmyUiTestServer:
    pygmyui_proc = None

    @classmethod
    def start_pygmy_ui_server(cls):
        import os
        os.chdir('pyui')
        command = ['gunicorn', '-b 127.0.0.1:8000', '-w 1', 'pyui.wsgi']
        cls.pygmyui_proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for server to start
        time.sleep(1)
        return cls.pygmyui_proc

    @classmethod
    def terminate_pygmy_ui_server(cls):
        if not cls.pygmyui_proc or not cls.pygmyui_proc.pid:
            return
        cls.pygmyui_proc.terminate()


@pytest.fixture(scope='class')
def run_test_server(request):
    # Setup
    request.cls.pygmyapi_proc = PygmyApiTestServer.start_pygmy_api_server()
    request.cls.pygmyui_proc = PygmyUiTestServer.start_pygmy_ui_server()
    yield
    # Teardown can be defined here


atexit.register(PygmyApiTestServer.terminate_pygmy_api_server)
atexit.register(PygmyUiTestServer.terminate_pygmy_ui_server)
