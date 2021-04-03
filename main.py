from api import events, todos
import ui

if __name__ == '__main__':
    calendar_events = events.get_todays_events()
    todos = todos.get_todays_todos()
    ui.refresh(calendar_events, todos)