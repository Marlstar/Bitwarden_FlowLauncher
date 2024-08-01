import subprocess
import os
import json
import pathlib
import favicon
import urllib

from plugin.consts import DEFAULT_ICON, TEMPDIR

from pyflowlauncher import Result, JsonRPCAction

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

        return self.format(self.serialise(outputStr))
    
    def serialise(self, output: str):
        """Serialise raw bitwarden CLI output into dict items"""

        try: outputDict = json.loads(output)
        except json.JSONDecodeError:
            return [
                Result(
                    Title="Wrong session key",
                    SubTitle="Please update the BW_SESSION environment variable"
                )
            ]

        return [x for x in outputDict if 'login' in x.keys()]

    def format(self, items):
        if len(items) == 0:
            return [
                Result(
                    Title="No results",
                    SubTitle="You do not have any matching items in your vault",
                    IcoPath=DEFAULT_ICON
                )
            ]

        results = []

        for i in range(len(items)):
            item = items[i]

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

    icon = fetch_icon(url.replace("https://","").replace("http://","").split("/")[0])
    if not icon: icon = ".".join(fetch_icon(url.replace("https://","").replace("http://","").split("/")[0]).split(".")[-2:])
    if not icon: return DEFAULT_ICON

    icon_path = f"{TEMPDIR}/{item["name"]}.png"
    try:
        if not os.path.exists(icon_path):
            icon = favicon.get(url)[0]
            urllib.request.urlretrieve(icon.url, icon_path)
        return icon_path
    except:
        return DEFAULT_ICON