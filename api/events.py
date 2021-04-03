import datetime

from api import google_api_util
from dateutil import tz, parser


# A basic object containing necessary details of a calendar event.
class Event:
    start_time = None
    end_time = None
    title = None

    def __init__(self, start_time, end_time, title):
        self.start_time = start_time
        self.end_time = end_time
        self.title = title

    def __repr__(self):
        return str(self.__dict__)


def _get_timezone(service):
    """ Determine which timezone is used in the calendar. """

    setting = service.settings().get(setting='timezone').execute()
    return tz.gettz(setting['value'])


def _should_filter(event):
    """ Apply filters to the provided event to remove certain types of events from the daily list. """

    # Half-day events don't always cover the same time range, but they usually contains this string in the event title.
    if '(half day)' in event['summary'].lower():
        return True
    # Filter out events I haven't explicitly accepted.
    accepted = next(x['responseStatus'] == 'accepted' for x in event['attendees'] if x.get('self', False) is True)
    if not accepted:
        return True
    return False


def get_todays_events():
    """ Fetch a filtered list of today's events from the Google Calendar API. """

    service = google_api_util.get_calendar_service()

    # First we need to get the timezone of the calendar.
    timezone = _get_timezone(service)

    # Next we calculate the beginning and end of the day based on the calendar's timezone.
    now = datetime.datetime.now(tz=timezone)
    begin_ts = datetime.datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone)
    end_ts = begin_ts + datetime.timedelta(days=1)

    # Get all events within the time window we just calculated.
    events_result = service.events().list(calendarId='primary', timeMin=begin_ts.isoformat(),
                                          timeMax=end_ts.isoformat(), maxResults=10,
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    todays_events = []
    for event in events:
        # Parse the events start and end time into datetime objects.
        start = parser.isoparse(event['start'].get('dateTime'))
        end = parser.isoparse(event['end'].get('dateTime'))
        # Filter out all-day events.
        if end - start >= datetime.timedelta(days=1):
            continue
        # Apply additional filters.
        if _should_filter(event):
            continue
        todays_events.append(Event(start.time(), end.time(), event['summary']))
    return todays_events
