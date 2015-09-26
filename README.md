RoseGuarden
===========

A remote door api and web application for Raspberry Pi.

Quickstart
==========

Initial steps
-------------

- add your `MAIL_USERNAME` to your enviroment variables (for enabling mail service, default mail-server-configuration is for googlemail)
- add your `MAIL_PASSWORD` to your enviroment variables (for enabling mail-service, default mail-server-configuration is for googlemail)
- initialize RoseGuarden database in the `server` - directory with `python db_create`


Running RoseGuarden
-------------------

- start the HTTPServer in the `client` - directory with  `python -m SimpleHTTPServer 8000`
- start the RoseGuarden-app in the `server` - directory witch `python run.py`

Screenshots
===========

![doors](documentation/screenshots/userspace.png)

![doors](documentation/screenshots/admin_doors.png)

![users](documentation/screenshots/admin_users.png)


License
=======

RoseGuarden is published under the terms of the GPL v3 license. See [LICENSE](LICENSE).
