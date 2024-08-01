import pathlib, tempfile

TEMPDIR = pathlib.Path(tempfile.gettempdir())
DEFAULT_ICON = f"{pathlib.Path(__file__).parent.parent.absolute()}/icons/bitwarden256x256.png"