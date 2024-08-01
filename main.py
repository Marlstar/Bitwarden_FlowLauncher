from pyflowlauncher import JsonRPCAction, Plugin, Result, ResultResponse, Method
import pyflowlauncher
import os;
import subprocess;
import json;
from pyflowlauncher import Result
import favicon, urllib.request
import pathlib, tempfile
from pyperclip import copy as copy_to_clipboard

TEMPDIR = pathlib.Path(tempfile.gettempdir())
DEFAULT_ICON = f"{pathlib.Path(__file__).parent.absolute()}/icons/bitwarden256x256.png"

plugin = Plugin()

class Bitwarden:
    def __init__(self):
        self.session_key = os.getenv("BW_SESSION");
        if not self.session_key: raise Exception("BW_SESSION environment variable not set!");

    def search(self, query: str, args: list = []) -> list[Result]:
        command = f"bw list items --search {query} --session {self.session_key}"
        for i in args: command += f" {i}"

        startup = subprocess.STARTUPINFO()
        startup.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE

        output = subprocess.run(command.split(), capture_output=True, startupinfo=startup)
        outputStr = output.stdout.decode('UTF-8')

        try: outputDict = json.loads(outputStr)
        except json.JSONDecodeError:
            return [
                Result(
                    Title="Wrong session key",
                    SubTitle="Please update the BW_SESSION environment variable"
                )
            ]

        outputDict = [x for x in outputDict if 'login' in x.keys()]

        if len(outputDict) == 0:
            return [
                Result(
                    Title="No results",
                    SubTitle="You do not have any matching items in your vault",
                    IcoPath=DEFAULT_ICON
                )
            ]

        results = []

        for i in range(len(outputDict)):
            item = outputDict[i]

            results.append(entry(item))
        
        return results


def entry(item):
    login = item["login"]
    username = login["username"]
    password = login["password"]
    icon = get_icon(item)

    action = JsonRPCAction(
        method="copy",
        parameters=[password]
    )

    result = Result(
        Title=item["name"],
        SubTitle=username,
        CopyText=password,
        IcoPath=icon,
        JsonRPCAction=action
    )

    return result


def fetch_icon(url):
    try: return favicon.get(url)[0]
    except: return


def get_icon(item) -> str | pathlib.Path:
    urls = item["login"]["uris"]
    if type(urls) == list:
        if len(urls) == 0: return DEFAULT_ICON
        url = urls[0]["uri"]
    else: return DEFAULT_ICON

    icon = fetch_icon(url)
    if not icon: icon = fetch_icon(url.replace("https://","").replace("http://","").split("/")[0])
    if not icon: return DEFAULT_ICON

    icon_path = f"{TEMPDIR}/{item["name"]}.png"
    try:
        if not os.path.exists(icon_path):
            icon = favicon.get(url)[0]
            urllib.request.urlretrieve(icon.url, icon_path)
        return icon_path
    except:
        return DEFAULT_ICON


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
