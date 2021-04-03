import io

from api import google_api_util
from googleapiclient.http import MediaIoBaseDownload
from orgparse import loads


# File ID for weekly.org.
FILE_ID = "1-6tE-mTPFa4ZrsAel_jvwEwapLZAwKGK"


class Todo:
    state = None
    title = None
    tag = None

    def __init__(self, state, title, tag=""):
        self.state = state
        self.title = title
        self.tag = tag

    def __repr__(self):
        return str(self.__dict__)


def _download_weekly_file():
    service = google_api_util.get_drive_service()
    request = service.files().get_media(fileId=FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()
    return str(fh.getvalue().decode())


def get_todays_todos():
    """ Fetch a filtered list of today's todos from the Google Drive API. """

    root = loads(_download_weekly_file())
    weekly_node = None
    for node in root[1:]:
        if str(node) == "* Weekly":
            weekly_node = node.children[0]
    if weekly_node is None:
        return []
    todos = []
    for node in weekly_node[1:]:
        stripped = str(node).lstrip('*').strip()
        state = stripped[:stripped.index(' ')]
        title = stripped[stripped.index(' ')+1:]
        tag = ""
        if title.endswith(':'):
            tag = title[title.rindex(' ')+1:].strip(':')
            title = title[:title.rindex(' ')].strip()
        todos.append(Todo(state, title, tag))
    return todos
