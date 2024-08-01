from pyflowlauncher import JsonRPCAction, Plugin, Result, ResultResponse, Method
import pyflowlauncher
import os;
import subprocess;
import json;
from pyflowlauncher import Result
import favicon, urllib.request
import pathlib, tempfile
from pyperclip import copy as copy_to_clipboard
from plugin.bitwarden import Bitwarden

from plugin.consts import DEFAULT_ICON, TEMPDIR

plugin = Plugin()



def copy(content):
    copy_to_clipboard(content)

bw = Bitwarden()

class Query(Method):
    def __call__(self, query: str) -> ResultResponse:
        if not query.strip(): return self.return_results()
        if query.strip() == "sync":
            subprocess.run("bw sync")
            return self.return_results()

        results = bw.search(query)
        for r in results: self.add_result(r)
        return self.return_results()
    

plugin.add_method(Query())
plugin.add_method(copy)
plugin.run()
