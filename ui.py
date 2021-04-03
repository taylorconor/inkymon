from PIL import Image, ImageDraw, ImageFont

RESOLUTION = (400, 300)
BOUNDARY = 185
V_LINESPACE = 26
V_MIDPOINT = 2
H_SEPARATOR = 4

STARTTIME = 10
ENDTIME = 22

POCO = ImageFont.truetype('fonts/poco.ttf', 10)
ARIEL = ImageFont.truetype('fonts/ariel.ttf', 8)


def _width(box):
    return box[2] - box[0]


def _height(box):
    return box[3] - box[1]


def _get_event_offsets(event):
    start_offset = V_LINESPACE * (event.start_time.hour - STARTTIME) + 3
    if event.start_time.minute >= 30:
        start_offset += V_LINESPACE / 2
    end_offset = V_LINESPACE * (event.end_time.hour - STARTTIME)
    if event.end_time.minute >= 30:
        end_offset += V_LINESPACE / 2
    return start_offset, end_offset


def _draw_textbox(draw, bounds, text, font, bg="white", fg="black"):
    draw.rectangle(bounds, bg)
    wrapped_text = ''
    for word in text.split():
        box = draw.multiline_textbbox(bounds, wrapped_text + ' ' + word, font)
        if 0 < _height(bounds) < _height(box):
            wrapped_text = wrapped_text[:wrapped_text.rindex('\n')]
            break
        if _width(box) > _width(bounds):
            wrapped_text += '\n'
        elif len(wrapped_text) > 0:
            wrapped_text += ' '
        wrapped_text += word
    draw.multiline_text((bounds[0] + 1, bounds[1]), wrapped_text, fg, font)
    return draw.multiline_textbbox(bounds, wrapped_text, font)


def _draw_calendar_frame(draw):
    lines = [(label, offset) for label, offset in zip(range(STARTTIME, ENDTIME), range(0, 300, V_LINESPACE))]
    max_box = max([draw.textbbox((0, 0), f'{label:02d}', POCO, anchor='lt') for label, _ in lines])
    for label, offset in lines:
        box = draw.textbbox((0, 0), f'{label:02d}', POCO, anchor='lt')
        draw.text((max_box[2] - box[2], offset), f'{label:02d}', 1, POCO, anchor='lt')
        draw.line((max_box[2] + H_SEPARATOR, offset + V_MIDPOINT, BOUNDARY - H_SEPARATOR, offset + V_MIDPOINT), "black")


def _draw_calendar_events(draw, calendar_events):
    for event in calendar_events:
        start_offset, end_offset = _get_event_offsets(event)
        _draw_textbox(draw, (13, start_offset, BOUNDARY - H_SEPARATOR, end_offset), event.title, ARIEL)
        draw.line((10, start_offset, 10, end_offset), width=2, fill="red")


def _draw_todos(draw, todos):
    state_widths = [_width(draw.textbbox((0, 0), x.state, ARIEL)) for x in todos]
    max_state_widths = max(state_widths)
    v_offset = H_SEPARATOR
    for todo, width in zip(todos, state_widths):
        colour = "red"
        if todo.state == "DONE" or todo.state == "CANCEL":
            colour = "black"
        draw.text((BOUNDARY + H_SEPARATOR + max_state_widths - width, v_offset), todo.state, colour, ARIEL)
        box = _draw_textbox(draw, (BOUNDARY + H_SEPARATOR + max_state_widths + H_SEPARATOR, v_offset, 400 - H_SEPARATOR, v_offset), todo.title, ARIEL)
        v_offset += _height(box) + 5


def refresh(calendar_events, todos):
    image = Image.new("P", RESOLUTION, color="white")
    draw = ImageDraw.Draw(image)
    draw.line((BOUNDARY, 0, BOUNDARY, RESOLUTION[1]), width=1, fill=1)

    _draw_calendar_frame(draw)
    _draw_calendar_events(draw, calendar_events)
    _draw_todos(draw, todos)
    return image
