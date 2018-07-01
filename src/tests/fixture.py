import os
import time
import atexit
import pytest
import subprocess
import coverage.data

__all__ = [
    'run_test_server',
]


class PygmyApiTestServer:
    pygmyapi_proc = None

    @classmethod
    def start_pygmy_api_server(cls):
        # os.chdir('src')
        command = ['coverage', 'run', 'src/pygmy_api_run.py', 'test']
        cls.pygmyapi_proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for server to start
        time.sleep(1)
        # os.chdir('..')
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
        # os.chdir('src/pyui')
        command = ['gunicorn','-b 127.0.0.1:8000', '--chdir', 'src/pyui', '-w 1', 'pyui.wsgi']
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


# @pytest.fixture(autouse=True)
# def coverage_test_server(cov):
#     return
#     backendcov = coverage.data.CoverageData()
#     root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
#     with open(root_dir + '/' + '.coverage', 'a+') as fp:
#         backendcov.read_fileobj(fp)
#     cov.data.update(backendcov)


atexit.register(PygmyApiTestServer.terminate_pygmy_api_server)
atexit.register(PygmyUiTestServer.terminate_pygmy_ui_server)
