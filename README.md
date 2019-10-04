# icinga-notificator

Daemon script used to aggregate and send notifications from icinga (elasticsearch)

## Getting Started

Installation and deployment process is handled by puppet and CI/CD deployment and fully automated.

Before deployment we need to supply configuration (in our environment is distributed by puppet from template) - check module icinga - https://gitlab.com/ls-tech-team/puppet/tree/master/modules/icinga



### Prerequisites

Before you set up CI/CD on your server, make sure you have this things:
- debian server (stretch distro)
- python3
- pypi (python-pip3)
- elasticsearch server
- icinga with icingabeat sending notification data to this server
- configuration for icinga notificator in place - with values matching this server


### Installing

Installing is done via CI/CD procedure.
- Edit install.sh to match desired location / server

```
if [[ "$enviro" == "office" ]]; then
    servers="mgm1.srv.lsoffice.cz mgm2.srv.lsoffice.cz"
fi
if [[ "$enviro" == "twr" ]]; then
    servers="icinga1.ls.intra icinga2.ls.intra ns2.ls.intra"
fi
```

Then you need to tag the commit and push it to repo. Deployment will start automatically.

!!! Be careful with this, this process is little bit dangerous - It can make notificator crash If you deploy wrong version with bugs. !!!

Deploy is done via deploy.sh and install.sh scripts, this also includes systemd unit and restarting to reload new version.

## Running the tests

Test are created with pytest utility. You can easilly run them by running:
```
cd projectDir
pytest -v
```

## Contributing

You cannot commit to the master directly, you need to create merge request first.

## Versioning

Versioning is done by some simple pattern. There are milestones created, commits under milestone are versioned as subversions (2.0.1, 2.0.2, 2.1.0, etc..); Next level subversions (should be squashed into one commit)
## Authors

* **Jakub Stollmann** - * * 


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

