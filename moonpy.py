import datetime, time
import dateparser
import math

class MoonPy:
    '''Calculates the phase of the moon for today, or, for a given date.'''

    phase_names = (
        'New Moon',
        'Waxing Crescent',
        'First Quarter',
        'Waxing Gibbous',
        'Full Moon',
        'Waning Gibbous',
        'Third Quarter',
        'Waning Crescent',
    )

    period_in_days = 29.53058867

    period_in_seconds = period_in_days * 86400

    def __init__(self, phase_date=None):
        '''Initialize a moon phase object. If no phase_date is given, return
        the phase data for today.'''
        self._caclulate_position_in_cycle(phase_date)


    def _caclulate_position_in_cycle(self, phase_date=None):
        '''Calculates the position of the moon in the phase for the given
        date.'''
        self._set_phase_date(phase_date)
        date_diff = self.phase_date - self._get_base_full_moon()
        position = (date_diff % MoonPy.period_in_seconds) / MoonPy.period_in_seconds
        if position < 0:
            position = 1 + position
        self.position = position
        self._set_phase_id()

    def _set_phase_date(self, phase_date=None):
        '''Create a timestamp for the given date, or for now, if no date is
        given.'''
        if phase_date == None:
            current_date = datetime.datetime.now()
        else:
            current_date = dateparser.parse(phase_date)
        self.phase_date = time.mktime(current_date.timetuple())

    def _get_base_full_moon(self):
        '''Returns a timestamp for a known past full moon.'''
        known_full_moon = datetime.datetime(2008, 12, 12, 16, 37)
        return time.mktime(known_full_moon.timetuple())

    def _set_phase_id(self):
        '''Set the ID and name based on the moon's position in the phase.'''
        if self.position >= 0.474 and self.position <= 0.53:
            self.phase_id = 0
        elif self.position >= 0.54 and self.position <= 0.724:
            self.phase_id = 1
        elif self.position >= 0.725 and self.position <= 0.776:
            self.phase_id = 2
        elif self.position >= 0.777 and self.position <= 0.974:
            self.phase_id = 3
        elif self.position >= 0.975 and self.position <= 0.026:
            self.phase_id = 4
        elif self.position >= 0.027 and self.position <= 0.234:
            self.phase_id = 5
        elif self.position >= 0.235 and self.position <= 0.295:
            self.phase_id = 6
        else:
            self.phase_id = 7

    def get_phase_name(self):
        '''Returns the name of the phase.'''
        return MoonPy.phase_names[self.phase_id]

    def get_percentage_of_illumination(self):
        '''Returns the percentage of illumination for a given moon.'''
        return (1.0 + math.cos(2.0 * math.pi * self.position)) / 2.0

    def get_days_until_next_moon(self, moon_type):
        '''Return the number of days until the next moon of a given type.'''
        if moon_type == 'Third Quarter':
            days = self._get_days_until_next_moon(0.25)
        elif moon_type == 'New Moon':
            days = self._get_days_until_next_moon(0.5)
        elif moon_type == 'First Quarter':
            days = self._get_days_until_next_moon(0.75)
        else:
            days = self._get_days_until_next_full_moon()
        return "{} days until the next {}".format(days, moon_type)

    def _get_days_until_next_moon(self, delimiter):
        '''Returns the days until the next occurence of the moon of a given
        type'''
        days = 0
        if self.position < delimiter:
            days = (delimiter - self.position) * self.period_in_days
        elif self.position >= delimiter:
            days = ((1 + delimiter) - self.position) * self.period_in_days
        return round(days, 1)

    def _get_days_until_next_full_moon(self):
        '''Calculate the days until the next full moon.'''
        return round((1 - self.position) * self.period_in_days, 2)
