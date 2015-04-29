%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from
%distutils.sysconfig import get_python_lib; print (get_python_lib())")}

Name:           fedocal
Version:        0.13.2
Release:        1%{?dist}
Summary:        A web based calendar application

License:        GPLv3+
URL:            http://fedorahosted.org/fedocal/
Source0:        https://fedorahosted.org/releases/f/e/fedocal/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-flask
BuildRequires:  pytz
BuildRequires:  python-wtforms
BuildRequires:  python-flask-wtf
BuildRequires:  python-vobject
BuildRequires:  python-kitchen
BuildRequires:  python-fedora >= 0.3.33
BuildRequires:  python-fedora-flask >= 0.3.33
BuildRequires:  python-alembic
BuildRequires:  python-dateutil
BuildRequires:  python-setuptools
BuildRequires:  python-markdown
BuildRequires:  python-docutils
BuildRequires:  python-nose
BuildRequires:  python-coverage
BuildRequires:  python-mock
BuildRequires:  python-psutil
BuildRequires:  python-flask-babel
BuildRequires:  babel
BuildRequires:  python-blinker

# EPEL6
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
BuildRequires:  python-sqlalchemy0.7
Requires:  python-sqlalchemy0.7
%else
BuildRequires:  python-sqlalchemy > 0.5
Requires:  python-sqlalchemy > 0.5
%endif

Requires:  python-flask
Requires:  pytz
Requires:  python-wtforms
Requires:  python-flask-wtf
Requires:  python-vobject
Requires:  python-kitchen
Requires:  python-fedora >= 0.3.32.3-3
Requires:  python-fedora-flask
Requires:  python-alembic
Requires:  python-dateutil
Requires:  python-setuptools
Requires:  python-markdown
Requires:  python-docutils
Requires:  python-psutil
Requires:  python-flask-babel
Requires:  python-blinker
Requires:  mod_wsgi

%description
fedocal is a web- based calendar application for Fedora. It aims at replacing
the tables in the wiki which are hard to edit and maintain.
Calendar can be exported to an iCal format allowing read-only integration with
most calendar application.

%prep
%setup -q

sed -i -e 's|script_location = alembic|script_location = /usr/share/fedocal/alembic|' alembic.ini.sample

# Compile the translations
pybabel compile -d fedocal/translations


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# Install apache configuration file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/
install -m 644 fedocal.conf $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/fedocal.conf

# Install configuration file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/fedocal
install -m 644 fedocal.cfg.sample $RPM_BUILD_ROOT/%{_sysconfdir}/fedocal/fedocal.cfg
install -m 644 alembic.ini.sample $RPM_BUILD_ROOT/%{_sysconfdir}/fedocal/alembic.ini

# Install WSGI file
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/fedocal
cp -r alembic/ $RPM_BUILD_ROOT/%{_datadir}/fedocal/
install -m 644 fedocal.wsgi $RPM_BUILD_ROOT/%{_datadir}/fedocal/fedocal.wsgi

# Install the createdb script
install -m 644 createdb.py $RPM_BUILD_ROOT/%{_datadir}/fedocal/fedocal_createdb.py


%check
./run_tests.sh

%files
%doc README.rst LICENSE doc/
%config(noreplace) %{_sysconfdir}/httpd/conf.d/fedocal.conf
%config(noreplace) %{_sysconfdir}/fedocal/fedocal.cfg
%config(noreplace) %{_sysconfdir}/fedocal/alembic.ini
%dir %{_sysconfdir}/fedocal/
%{_datadir}/fedocal/
%{python_sitelib}/fedocal/
%{python_sitelib}/fedocal*.egg-info
%{_bindir}/fedocal_cron.py


%changelog
* Wed Apr 29 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.13.2-1
- Update 0.13.2
- Make fedocal prettier on high resolution displays
- Add fedmenu
- Clean the code with pylint

* Tue Mar 31 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.13.1-1
- Update to 0.13.1
- Prevent non-editor user from beeing offered the possibility to add meetings

* Tue Mar 31 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.13-1
- Update to 0.13
- Add the possibility to get an iCal feed for a single meeting
  (Ratnadeep Debnath)
- Add the possibility to have client side reminder via the iCal feed
  (Ratnadeep Debnath)
- Hide the timezone on full-day meetings instead of de-activating it
- Fix the domain name of the fedoraproject aliases
- Allow adding meeting by clicking on the calendar matrix

* Tue Jan 20 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.12-1
- Update to 0.12
- Drop the hard-coded red * from the form fields and set them in the templates
  instead
- Add support for i18n (Thanks Johan Cwiklinski)
- Fix the mail_logging  module if the pid could not be retrieved
- Adjust the doc for i18n (Thanks Johan Cwiklinski)
- Fix the README on how to get fedocal running
- Fix the handling of the `?from_date` parameter when editing a meeting
- Fix redirecting and editing meetings in recursion

* Mon Oct 6 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.11.1-1
- Update to 0.11.1
- Fix bug when deleting meeting in the middle of a recursion

* Mon Oct 6 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.11-1
- Update to 0.11
- Fix CSS in the agenda view
- Update to jquery-ui 1.11.1
- Fix the CSS for the jquery-ui update to 1.11.1 - Thanks Johan Cwiklinski
- Drop the weekly navigation key on the list view
- Fix meeting overlap for full day meetings - Thanks Johan Cwiklinski
- Fix timespinners that the new jquery-ui seems to have broken
- Fix the home button (top right in calendar view) - Thanks Johan Cwiklinski
- Fix the message displayed in the meeting view when countdown reaches 0
  - Thanks Johan Cwiklinski
- Fix deleting meetings from the list view

* Fri Oct 3 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.10-1
- Update to 0.10
- Implement the session time-out (defaults to 1h)
- Let the doc retrieve the fedocal version directly from the fedocal module
- Store the list of requirements only in the requirements.txt (in addition
  to the spec file)
- Support sending reminder emails to multiple addresses at once
- New layout for the list view
- New email handler for the logs (providing for example on which host the
  exception occured) - Thanks Ralph Bean for that code
- Avoid reseting the time start/stop when adding or editing a meeting and
  something goes wrong

* Tue Aug 26 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.9.3-1
- Update to 0.9.3
- Fix the iCal output to avoid converting the timezone of the meetings twice
- Fix unit-tests

* Mon Aug 25 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.9.2-1
- Update to 0.9.2
- Fix uploading iCal files generated by fedocal itself
- Fix parsing the timezones information from iCal file
- Fix encoding the cron sending the reminder emails

* Tue Jul 22 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.9.1-1
- Update to 0.9.1
- Adjust the unit-test suite
- Fix requiring the calendar admin and editor groups upon login to handle
  authorization correctly

* Wed Jul 16 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.9-1
- Update to 0.9
- Port the filtering on the list view to be DB side rather than by iterating
  through the meetings retrieved
- Improve unit-tests coverage
- Restrict the groups asked upon login to only those required
- Fix iCal output

* Wed Jun 18 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.8-2
- Activate the unit-tests ain the spec

* Tue Jun 17 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.8-1
- Update to 0.8
- Add the possibility to filter the meetings in the list view

* Mon Jun 16 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.7.1-1
- Update to 0.7.1
- Fix displaying the meeting times properly in the meeting details

* Sat Jun 14 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.7-1
- Update to 0.7
- Rework the meeting detail view
- Add date/time in UTC as titles to the dates on the meeting detail view
- Add shortcuts to interact more easily with the calendars (calendar and
  list views)
- Fix bug in recursive meetings
- Add notifications informing if there are meetings hidden below or above the
  current view
- Add permalink allowing one to copy/paste the url and send it to someone else
- Add countdown on the meeting detail view
- Auto-scroll to today or the future meetings in the list view
- Bug fix in displaying the full day meetings
- Add a dedicated field to set the address used to send fedocal reminder
- Embed the background image in the sources to fix complaints when using https

* Sat May 03 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.6.3-1
- Security update, prevent fedocal to redirect to malicious website

* Wed Apr 23 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.6.2-1
- Update to 0.6.2
- Fix cron job

* Fri Apr 18 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.6.1-1
- Update to 0.6.1
- Use cantarell as default font
- Highlight the current calendar in the list
- Forbid `#` in meeting location
- Fix fedmsg messages to avoid empty meeting_id
- Fix editing one's meeting

* Wed Mar 12 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.6.0-1
- Update to 0.6.0
- CSS fix in the monthly calendar
- Use custom timezone ID in the ical output which should fix importing the iCal
  feed into google calendar or evolution
- Revert the meaning of the orange week in the monthly calendar

* Tue Mar 04 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.5.1-1
- Update to 0.5.1
- Fix the link in the reminder email sent (does not hardcode the url anymore and
  has the appropriate meeting id)

* Tue Mar 04 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.5.0-1
- Update to 0.5.0
- Rework the monthly calendar
- Add a list view to locations
- Fix visualization of full day meeting over multiple days

* Wed Feb 26 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.7-1
- Update to 0.4.7
- Add the 3 and 4 weeks recursion frequency

* Thu Feb 13 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.6-1
- Update to 0.4.6
- Bug fix release fixing bug in the propagation of the manager in recurrent
  meetings

* Sat Feb 08 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.5-1
- Update to 0.4.5
- Bug fix release fixing bug in the reminder/fedmsg msg for recursive meetings

* Thu Jan 30 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.4-1
- Update to 0.4.4
- Bug fix release fixing bug when editing recursive meeting that have never
  occured so far

* Thu Jan 30 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.3-1
- Update to 0.4.3
- Bug fix release fixing bug when deleting recursive meeting that have never
  occured so far

* Thu Jan 30 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.2-1
- Update to 0.4.2
- Bug fix release fixing bug in the iCal output

* Thu Jan 30 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.1-1
- Update to 0.4.1

* Tue Jan 28 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.0-1
- Update to 0.4.0

* Fri Nov 15 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.3.1-1
- Update to 0.3.1

* Thu Nov 14 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.3.0-1
- Update to 0.3.0
- Move the createdb script into %%{_datadir}/fedocal/

* Mon Oct 28 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.2.9-1
- First pre-release before 0.3.0

* Fri Sep 27 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.2.0-1
- Update to release 0.2.0

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Mar 15 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.2.-1
- Update to 0.1.2 which includes the alembic files

* Fri Mar 15 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.1.-1
- Update to 0.1.1
- Include the createdb.py script as %%doc
- Add the alembic.ini into /etc/fedocal

* Fri Mar 08 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.0-3
- Fix import of flask-fas which fixes build on EL6
- Fix Requires and BuilRequires for EL6

* Tue Feb 26 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.0-2
- Fix BR to python2-devel
- Be more specific on the %%{python_sitelib} inclusion in %%files
- Remove flask_fas for a BR and R on python-fedora-flask

* Fri Feb 15 2013 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.0-1
- Initial packaging work for Fedora

