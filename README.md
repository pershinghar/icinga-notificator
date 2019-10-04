# icinga-notificator

Daemon script used to aggregate and send notifications from icinga (elasticsearch)
- works on periodic base, when the script check periodically ES DB, if there are any new notifications
- if they are, it processes them and send them to desired users (icinga users need to have specified options)

There are few channels which you can use to send notification:
- email
- sms (only smseagle modems now, but you can contribute:-))
- pager (custom script called, specify in configuration)
- slack is in development and will be released later after more testing

## Getting Started

Installation and deployment process must be handled by you. I recommend using gitlab CI/CD for example, but there are many ways to do this.


### Prerequisites

- debian server (stretch distro is tested)
- python3
- pypi (python-pip3)
- elasticsearch server (6.8.1 is tested)
- icinga2(2.10.3 tested) with icingabeat(6.5.4 tested) sending notification data to this server 
- configuration for icinga notificator in place - with values matching this server


### Installing & Running

- you need to build it and install
```
python3 setup.py bdist_wheel
pip3 install dist/*
```
- main daemon script will be located in 
```
/usr/local/bin/icinga-notificator.py
```

- you can also run it via systemd (check config folder)
- you need to provide configuration file for icinga notificator (Check config folder for example, location should be /etc/, you can specify own via script parameters)
- you need to fill icinga users configuration with values you need to process notifications:
	- notification settings - something like this
```
[user context]
vars.notification_options = {
	sms = [ "acknowledgement", "critical", "ok", "warning", ]
	email = [ "unknown", "critical", ]
}
```
- script has also debug options(args), so feel free to use them

## Running the tests

Test are created with pytest utility. You can easilly run them by running:
```
pytest -v
```
or via setup (before building)
```
python3 setup.py test
```

## Contributing

No problem :-)

## Versioning

Versioning is done by some simple pattern. There are milestones created, commits under milestone are versioned as subversions (2.0.1, 2.0.2, 2.1.0, etc..); Next level subversions (should be squashed into one commit)
## Authors

* **Jakub Stollmann** 


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

