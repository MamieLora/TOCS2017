from datetime import datetime
import caldav
from caldav.elements import dav, cdav

class CalendarHandler():
    
    _caldav_object = None
    
    _calendar_url = None
    _calendar_name = None
    _user = None
    _password = None
    
    def __init__(self, caldav_url, calendar_name, user, password):
    
        self._calendar_url = caldav_url
        self._calendar_name = calendar_name
        self._user = user
        self._password = password
        
    def connect (self):
    
        client = caldav.DAVClient(self._calendar_url, username=self._user, password=self._password)
        principal = client.principal()
        calendars = principal.calendars()
        
        matched_calendar = None
        
        for calendar in calendars:
            calendar_displayname_property_dict = calendar.get_properties([dav.DisplayName(),])
            value_list = list(calendar_displayname_property_dict.values())
            name = value_list[0]
            
            if self._calendar_name == name:
                matched_calendar = calendar
                break
    
        if matched_calendar:
            self._caldav_object = matched_calendar
            
    def addEvent (self, raw_vcal_event):
        
        self._caldav_object.add_event (raw_vcal_event)
        
        results = self._caldav_object.date_search(
        datetime(2010, 5, 1), datetime(2017, 6, 1))

        for event in results:
            print ("Found: %s" % event)
        
        
if __name__ == '__main__':
    pass