from api import events, todos
from inky.auto import auto
import ui

if __name__ == '__main__':
    board = auto()
    calendar_events = events.get_todays_events()
    todos = todos.get_todays_todos()
    image = ui.refresh(calendar_events, todos)
    board.set_image(image)
    board.show()