#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
 (c) 2012 - Copyright Pierre-Yves Chibon
 Author: Pierre-Yves Chibon <pingou@pingoured.fr>

 Distributed under License GPLv3 or later
 You can find a copy of this license on the website
 http://www.gnu.org/licenses/gpl.html

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 MA 02110-1301, USA.

 fedocal.model test script
"""

__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources

import flask
import logging
import unittest
import sys
import os

from datetime import date
from datetime import time
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import fedocal
import fedocal.fedocallib as fedocallib
import fedocal.fedocallib.model as model
from tests import Modeltests, FakeUser, flask10_only, user_set, TODAY


# pylint: disable=E1103
class Flasktests(Modeltests):
    """ Flask application tests. """

    def __setup_db(self):
        """ Add a calendar and some meetings so that we can play with
        something. """
        from test_meeting import Meetingtests
        meeting = Meetingtests('test_init_meeting')
        meeting.session = self.session
        meeting.test_init_meeting()

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(Flasktests, self).setUp()

        fedocal.APP.config['TESTING'] = True
        fedocal.APP.debug = True
        fedocal.APP.logger.handlers = []
        fedocal.APP.logger.setLevel(logging.CRITICAL)
        fedocal.SESSION = self.session
        self.app = fedocal.APP.test_client()

    def test_index_empty(self):
        """ Test the index function. """
        output = self.app.get('/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>Home - Fedocal</title>' in output.data)

    def test_index(self):
        """ Test the index function. """
        self.__setup_db()

        output = self.app.get('/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>Home - Fedocal</title>' in output.data)
        self.assertTrue('href="/test_calendar/">' in output.data)
        self.assertTrue('href="/test_calendar2/">' in output.data)
        self.assertTrue('href="/test_calendar4/">' in output.data)

    def test_calendar(self):
        """ Test the calendar function. """
        self.__setup_db()

        output = self.app.get('/test_calendar')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/test_calendar', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test_calendar - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

        output = self.app.get('/test_calendar2/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test_calendar2 - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

        output = self.app.get('/foorbar/', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            'class="errors">No calendar named foorbar could not be found</'
            in output.data)

    def test_location(self):
        """ Test the location calendar function. """
        self.__setup_db()

        output = self.app.get('/location/test')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/location/test/', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

    def test_calendar_fullday(self):
        """ Test the calendar_fullday function. """
        self.__setup_db()

        today = date.today()
        output = self.app.get(
            '/test_calendar/%s/%s/%s/' % (
                today.year, today.month, today.day))
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test_calendar - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

        output = self.app.get(
            '/test_calendar/%s/%s/%s' % (
                today.year, today.month, today.day))
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/test_calendar/%s/%s/%s/' % (
            today.year, today.month, today.day), follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test_calendar - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

    def test_calendar_list(self):
        """ Test the calendar_list function. """
        self.__setup_db()

        output = self.app.get('/list/test_calendar/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test_calendar - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

        output = self.app.get('/list/foorbar/', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            'class="errors">No calendar named foorbar could not be found</'
            in output.data)

        today = date.today()
        output = self.app.get('/list/test_calendar/%s/%s/%s/' % (
            today.year, today.month, today.day))
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test_calendar - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

        output = self.app.get('/list/test_calendar/%s/%s/%s' % (
            today.year, today.month, today.day))
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/list/test_calendar/%s/%s/%s/' % (
            today.year, today.month, today.day), follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test_calendar - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

        output = self.app.get('/list/test_calendar/%s/%s/' % (
            today.year, today.month), follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>test_calendar - Fedocal</title>' in output.data)
        self.assertTrue(' <a href="/test_calendar/">' in output.data)
        self.assertTrue(' <a href="/test_calendar2/">' in output.data)
        self.assertTrue(' <a href="/test_calendar4/">' in output.data)

    def test_ical_out(self):
        """ Test the ical_out function. """
        self.__setup_db()

        output = self.app.get('/ical/test_calendar/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('BEGIN:VCALENDAR' in output.data)
        self.assertTrue('SUMMARY:test-meeting2' in output.data)
        self.assertTrue(
            'DESCRIPTION:This is a test meeting with recursion'
            in output.data)
        self.assertTrue('ORGANIZER:pingou' in output.data)
        self.assertEqual(output.data.count('BEGIN:VEVENT'), 10)
        self.assertEqual(output.data.count('END:VEVENT'), 10)

        output = self.app.get('/ical/foorbar/')
        self.assertEqual(output.status_code, 404)

    def test_ical_all(self):
        """ Test the ical_all function. """
        self.__setup_db()

        output = self.app.get('/ical/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('BEGIN:VCALENDAR' in output.data)
        self.assertTrue('SUMMARY:test-meeting2' in output.data)
        self.assertTrue(
            'DESCRIPTION:This is a test meeting with recursion'
            in output.data)
        self.assertTrue('ORGANIZER:pingou' in output.data)
        self.assertEqual(output.data.count('BEGIN:VEVENT'), 14)
        self.assertEqual(output.data.count('END:VEVENT'), 14)

    def test_view_meeting(self):
        """ Test the view_meeting function. """
        self.__setup_db()

        output = self.app.get('/meeting/5/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>Meeting test-meeting-st-1 - Fedocal</title>'
            in output.data)
        self.assertTrue(
            '<h4> Meeting: test-meeting-st-1</h4>'
            in output.data)
        self.assertTrue(
            'This is a test meeting at the same time'
            in output.data)

    def test_view_meeting_page(self):
        """ Test the view_meeting_page function. """
        self.__setup_db()

        output = self.app.get('/meeting/5/1/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>Meeting test-meeting-st-1 - Fedocal</title>'
            in output.data)
        self.assertTrue(
            '<h4> Meeting: test-meeting-st-1</h4>'
            in output.data)
        self.assertTrue(
            'This is a test meeting at the same time'
            in output.data)

        output = self.app.get('/meeting/5/0/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>Meeting test-meeting-st-1 - Fedocal</title>'
            not in output.data)
        self.assertTrue(
            '<h4> Meeting: test-meeting-st-1</h4>'
            in output.data)
        self.assertTrue(
            'This is a test meeting at the same time'
            in output.data)

        output = self.app.get('/meeting/50/0/', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            'class="errors">No meeting could be found for this identifier</'
            in output.data)

    def test_is_admin(self):
        """ Test the is_admin function. """
        app = flask.Flask('fedocal')

        with app.test_request_context():
            flask.g.fas_user = None
            self.assertFalse(fedocal.is_admin())
            flask.g.fas_user = FakeUser(fedocal.APP.config['ADMIN_GROUP'])
            self.assertTrue(fedocal.is_admin())

    def test_is_calendar_admin(self):
        """ Test the is_calendar_admin function. """
        self.__setup_db()
        app = flask.Flask('fedocal')
        calendar = model.Calendar.by_id(self.session, 'test_calendar')

        with app.test_request_context():
            # No fas user
            flask.g.fas_user = None
            self.assertFalse(fedocal.is_calendar_admin(calendar))

            # User is in the wrong group
            flask.g.fas_user = FakeUser(['gitr2spec'])
            self.assertFalse(fedocal.is_calendar_admin(calendar))

            # User is admin
            flask.g.fas_user = FakeUser(fedocal.APP.config['ADMIN_GROUP'])
            self.assertTrue(fedocal.is_calendar_admin(calendar))

            # User is in the right group
            flask.g.fas_user = FakeUser(['infrastructure-main2'])
            self.assertTrue(fedocal.is_calendar_admin(calendar))

            # Calendar has no admin specified
            calendar = model.Calendar.by_id(self.session, 'test_calendar3')
            flask.g.fas_user = FakeUser(['gitr2spec'])
            self.assertFalse(fedocal.is_calendar_admin(calendar))

    def test_is_calendar_manager(self):
        """ Test the is_calendar_manager function. """
        self.__setup_db()
        app = flask.Flask('fedocal')
        calendar = model.Calendar.by_id(self.session, 'test_calendar')

        with app.test_request_context():
            # No user
            flask.g.fas_user = None
            self.assertFalse(fedocal.is_calendar_manager(calendar))

            # User in the wrong group
            flask.g.fas_user = FakeUser(['gitr2spec'])
            self.assertFalse(fedocal.is_calendar_manager(calendar))

            # User is admin
            flask.g.fas_user = FakeUser(fedocal.APP.config['ADMIN_GROUP'])
            self.assertTrue(fedocal.is_calendar_manager(calendar))

            # User in the right group
            flask.g.fas_user = FakeUser(['fi-apprentice'])
            self.assertTrue(fedocal.is_calendar_manager(calendar))

            calendar = model.Calendar.by_id(self.session, 'test_calendar3')

            # Calendar has no editors set
            flask.g.fas_user = FakeUser(['gitr2spec'])
            self.assertTrue(fedocal.is_calendar_manager(calendar))

    def test_is_meeting_manager(self):
        """ Test the is_meeting_manager function. """
        self.__setup_db()
        app = flask.Flask('fedocal')
        meeting = model.Meeting.by_id(self.session, 1)

        with app.test_request_context():
            # No user
            flask.g.fas_user = None
            self.assertFalse(fedocal.is_meeting_manager(meeting))

            # User is not one of the managers
            flask.g.fas_user = FakeUser(['gitr2spec'])
            flask.g.fas_user.username = 'kevin'
            self.assertFalse(fedocal.is_meeting_manager(meeting))

            # User is one of the manager
            flask.g.fas_user = FakeUser(['gitr2spec'])
            self.assertFalse(fedocal.is_meeting_manager(meeting))

    def test_get_timezone(self):
        """ Test the get_timezone function. """
        app = flask.Flask('fedocal')

        with app.test_request_context():
            flask.g.fas_user = FakeUser(fedocal.APP.config['ADMIN_GROUP'])
            self.assertEqual(fedocal.get_timezone(), 'Europe/Paris')

    def test_is_safe_url(self):
        """ Test the is_safe_url function. """
        app = flask.Flask('fedocal')

        with app.test_request_context():
            self.assertTrue(fedocal.is_safe_url('http://localhost'))

            self.assertTrue(fedocal.is_safe_url('https://localhost'))

            self.assertTrue(fedocal.is_safe_url('http://localhost/test'))

            self.assertFalse(
                fedocal.is_safe_url('http://fedoraproject.org/'))

            self.assertFalse(
                fedocal.is_safe_url('https://fedoraproject.org/'))

    def test_auth_login(self):
        """ Test the auth_login function. """
        app = flask.Flask('fedocal')

        with app.test_request_context():
            flask.g.fas_user = FakeUser(['gitr2spec'])
            output = self.app.get('/login/')
            self.assertEqual(output.status_code, 200)

            output = self.app.get('/login/?next=http://localhost/')
            self.assertEqual(output.status_code, 200)

    @flask10_only
    def test_auth_login_logedin(self):
        """ Test the auth_login function. """
        self.__setup_db()
        user = FakeUser([], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/login/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<title>Home - Fedocal</title>' in output.data)

    def test_locations(self):
        """ Test the locations function. """
        self.__setup_db()

        output = self.app.get('/locations/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<h2>Locations</h2>'
            in output.data)
        self.assertTrue('href="/location/EMEA/">' in output.data)
        self.assertTrue(
            '<span class="calendar_name">EMEA</span>' in output.data)
        self.assertTrue('href="/location/NA/">' in output.data)
        self.assertTrue(
            '<span class="calendar_name">NA</span>' in output.data)

    def test_location(self):
        """ Test the location function. """
        self.__setup_db()

        output = self.app.get('/location/EMEA')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/location/EMEA', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>EMEA - Fedocal</title>' in output.data)
        self.assertTrue('<a href="/location/EMEA/">' in output.data)
        self.assertTrue('title="Previous week">' in output.data)
        self.assertTrue('title="Next week">' in output.data)
        self.assertTrue(
            '<input type="hidden" name="location" value="EMEA"/>'
            in output.data)

        output = self.app.get('/location/NA/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>NA - Fedocal</title>' in output.data)
        self.assertTrue('<a href="/location/NA/">' in output.data)
        self.assertTrue('title="Previous week">' in output.data)
        self.assertTrue('title="Next week">' in output.data)
        self.assertTrue(
            '<input type="hidden" name="location" value="NA"/>'
            in output.data)

        output = self.app.get('/location/foobar/', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            'class="errors">No location named foobar could not be found</'
            in output.data)

    @flask10_only
    def test_add_calendar(self):
        """ Test the add_calendar function. """
        user = None
        with user_set(fedocal.APP, user):
            output = self.app.get('/calendar/add/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<title>OpenID transaction in progress</title>'
                in output.data)

        user = FakeUser(['test'])
        with user_set(fedocal.APP, user):
            output = self.app.get('/calendar/add/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '"errors">You are not a fedocal admin, you are not allowed '
                'to add calendars.</' in output.data)

        user = FakeUser(fedocal.APP.config['ADMIN_GROUP'])
        with user_set(fedocal.APP, user):
            output = self.app.get('/calendar/add/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<title>Add calendar - Fedocal</title>' in output.data)
            self.assertTrue(
                'for="calendar_name">Calendar <span class="error">*</span>'
                in output.data)
            self.assertTrue(
                'contact">Contact email <span class="error">*</span>'
                in output.data)

            csrf_token = output.data.split(
                'name="csrf_token" type="hidden" value="')[1].split('">')[0]

            # calendar should have a name
            data = {
                'calendar_contact': 'election1',
                'calendar_status': 'Enabled',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/calendar/add/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<td>This field is required.</td>' in output.data)

            # Works
            data = {
                'calendar_name': 'election1',
                'calendar_contact': 'election1',
                'calendar_status': 'Enabled',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/calendar/add/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="message">Calendar added</li>' in output.data)

            # This calendar already exists
            data = {
                'calendar_name': 'election1',
                'calendar_contact': 'election1',
                'calendar_status': 'Enabled',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/calendar/add/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '="errors">Could not add this calendar to the database</'
                in output.data)

    @flask10_only
    def test_auth_logout(self):
        """ Test the auth_logout function. """
        user = FakeUser(fedocal.APP.config['ADMIN_GROUP'])
        with user_set(fedocal.APP, user):
            output = self.app.get('/logout/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<title>Home - Fedocal</title>' in output.data)
            self.assertTrue(
                '<li class="message">You have been logged out</li>'
                in output.data)

        user = None
        with user_set(fedocal.APP, user):
            output = self.app.get('/logout/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue('<title>Home - Fedocal</title>' in output.data)
            self.assertFalse(
                '<li class="message">You have been logged out</li>'
                in output.data)

    @flask10_only
    def test_my_meetings(self):
        """ Test the my_meetings function. """
        self.__setup_db()
        user = FakeUser([], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/mine/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '"errors">You must be in one more group than the CLA</li>' in output.data)

        user = FakeUser(['packager'], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/mine/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<title>My meeting - Fedocal</title>' in output.data)
            self.assertTrue(
                '<td> Full-day meeting </td>' in output.data)
            self.assertTrue(
                '<td> test-meeting2 </td>' in output.data)
            self.assertTrue(
                '<td> Test meeting with reminder </td>' in output.data)

    @flask10_only
    def test_add_meeting(self):
        """ Test the add_meeting function. """
        self.__setup_db()
        user = FakeUser(['gitr2spec'], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/calendar_test/add/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '"errors">No calendar named calendar_test could not be found</'
                in output.data)

            output = self.app.get('/test_calendar/add/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="errors">You are not one of the editors of this '
                'calendar, or one of its admins, you are not allowed to add'
                ' new meetings.</li>' in output.data)
            self.assertTrue(
                '<title>test_calendar - Fedocal</title>' in output.data)

        user = FakeUser(['fi-apprentice'], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/test_calendar/add/')
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<title>Add meeting - Fedocal</title>' in output.data)
            self.assertTrue(
                'meeting_name">Meeting name <span class="error">*</span></l'
                in output.data)
            self.assertTrue(
                'for="meeting_date">Date <span class="error">*</span></label'
                in output.data)

            csrf_token = output.data.split(
                'name="csrf_token" type="hidden" value="')[1].split('">')[0]

            # Meeting should have a name
            data = {
                'meeting_date': TODAY,
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/test_calendar/add/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<td>This field is required.</td>' in output.data)

            # End date earlier than the start date
            data = {
                'meeting_name': 'guess what?',
                'meeting_date': TODAY,
                'meeting_date_end': TODAY - timedelta(days=1),
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/test_calendar/add/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="warnings">The start date of your meeting is '
                'later than the stop date.</li>' in output.data)
            self.assertTrue(
                '<title>Add meeting - Fedocal</title>' in output.data)

            # Works
            data = {
                'meeting_name': 'guess what?',
                'meeting_date': TODAY,
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/test_calendar/add/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="message">Meeting added</li>' in output.data)
            self.assertTrue(
                'href="/meeting/15/">' in output.data)

            # Calendar disabled
            data = {
                'meeting_name': 'guess what?',
                'meeting_date': TODAY,
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/test_calendar_disabled/add/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<title>test_calendar_disabled - Fedocal</title>'
                in output.data)
            self.assertTrue(
                '<li class="errors">This calendar is &#34;Disabled&#34;, '
                'you are not allowed to add meetings anymore.</li>'
                in output.data)

    @flask10_only
    def test_edit_meeting(self):
        """ Test the edit_meeting function. """
        self.__setup_db()
        user = FakeUser(['gitr2spec'], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/meeting/edit/50/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                'class="errors">The meeting #50 could not be found</li>'
                in output.data)
            self.assertTrue('<title>Home - Fedocal</title>' in output.data)

            output = self.app.get('/meeting/edit/1/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="errors">You are not one of the editors of this '
                'calendar, or one of its admins, you are not allowed to edit'
                ' meetings.</li>' in output.data)
            self.assertTrue(
                '<title>test_calendar - Fedocal</title>' in output.data)

        user = FakeUser(['fi-apprentice'], username='kevin')
        with user_set(fedocal.APP, user):
            output = self.app.get('/meeting/edit/1/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="errors">You are not one of the manager of this '
                'meeting, or an admin, you are not allowed to edit it.</li>'
                in output.data)
            self.assertTrue(
                '<title>Meeting Fedora-fr-test-meeting - Fedocal</title>'
                in output.data)

        user = FakeUser(['fi-apprentice'], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/meeting/edit/1/')
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<title>Edit meeting - Fedocal</title>' in output.data)
            self.assertTrue(
                'meeting_name">Meeting name <span class="error">*</span></l'
                in output.data)
            self.assertTrue(
                'for="meeting_date">Date <span class="error">*</span></label'
                in output.data)

            csrf_token = output.data.split(
                'name="csrf_token" type="hidden" value="')[1].split('">')[0]

            # Meeting should have a name
            data = {
                'meeting_date': TODAY,
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/meeting/edit/1/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<td>This field is required.</td>' in output.data)

            # No calendar provided
            data = {
                'meeting_name': 'guess what?',
                'meeting_date': TODAY,
                'meeting_date_end': TODAY - timedelta(days=1),
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/meeting/edit/1/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<td>Not a valid choice</td>' in output.data)
            self.assertTrue(
                '<title>Edit meeting - Fedocal</title>' in output.data)

            # End date earlier than the start date
            data = {
                'calendar_name': 'test_calendar',
                'meeting_name': 'guess what?',
                'meeting_date': TODAY,
                'meeting_date_end': TODAY - timedelta(days=1),
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/meeting/edit/1/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="warnings">The start date of your meeting is '
                'later than the stop date.</li>' in output.data)
            self.assertTrue(
                '<title>Edit meeting - Fedocal</title>' in output.data)

            # Works
            data = {
                'calendar_name': 'test_calendar',
                'meeting_name': 'guess what?',
                'meeting_date': TODAY,
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/meeting/edit/1/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<li class="message">Meeting updated</li>' in output.data)
            self.assertTrue(
                '<title>Meeting guess what? - Fedocal</title>' in output.data)

            # Calendar disabled
            data = {
                'calendar_name': 'test_calendar_disabled',
                'meeting_name': 'guess what?',
                'meeting_date': TODAY,
                'meeting_time_start': time(13, 0),
                'meeting_time_stop': time(14, 0),
                'meeting_timezone': 'Europe/Paris',
                'frequency': '',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/meeting/edit/1/', data=data,
                                   follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<title>test_calendar_disabled - Fedocal</title>'
                in output.data)
            self.assertTrue(
                '<li class="errors">This calendar is &#34;Disabled&#34;, '
                'you are not allowed to add meetings to it anymore.</li>'
                in output.data)

        user = FakeUser(['packager'], username='pingou')
        with user_set(fedocal.APP, user):
            # Recursive meeting
            output = self.app.get('/meeting/edit/12/', follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                '<title>Edit meeting - Fedocal</title>' in output.data)
            self.assertTrue(
                '<h2>Edit meeting Another past test meeting</h2>'
                in output.data)
            self.assertTrue(
                'meeting_name">Meeting name <span class="error">*</span></l'
                in output.data)
            self.assertTrue(
                'for="meeting_date">Date <span class="error">*</span></label'
                in output.data)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(Flasktests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
