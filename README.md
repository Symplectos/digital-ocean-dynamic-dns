# Digital Ocean Dynamic DNS
Python script to update DNS records managed by [Digital Ocean](https://digitealocean.com). Useful for home servers with dynamic IP addresses.

Uses the [ipify API](https://www.ipify.org/) to get the public IPv4 and IPv6 addresses of the server running the script.
Each specified record in a specified domain is then updated, if, and only if, the A or AAAA record known by Digital
Ocean does not match the corresponding IP address returned by ipify.

**Note**: This project is managed on GitLab and only mirrored on GitHub.

## Installation
Installation if straightforward.

### Clone the Repository
```
git clone https://gitlab.com/Symplectos/digital-ocean-dynamic-dns.git DigitalOceanDynamicDNS
```

### Create Python Environment
```
cd DigitalOceanDynamicDNS
python3 -m venv env
```

### Install Libraries
The script requires the **[requests](https://2.python-requests.org/en/master/)** library. All requirements can be
installed by invoking pip:

```
pip install -r requirements
```

### Configuration
To configure doDynDNS, a **.do.conf** file must be created in the root folder of the project:

```
touch .do.conf
```

The configuration requires two sections, a **DigitalOcean** section containing a valid API Access Key,
and a **DNS** section, containing the specific domain and specific records to update. Multiple records can be specified
by simply putting each record into a new line:

```
[DigitalOcean]
key = ***

[DNS]
domain = myDomain.eu
records = sub1
          sub2
```

## Cronjob
To automatically run the script periodically, create a cronjob
```
crontab -e
```

```
*/5 * * * * cd /pathToFolder && /pathToFolder/env/bin/python3 /pathToFolder/doDynDNS.py
```

## Manual Run
To manually run the script, activate the environment and then invoke the Python interpreter.

### Activate the Environment
```
source env/bin/activate
```

### Run
```
python doDynDNS.py
```

## Logging
The script automatically logs its last run in the **doDynDNS.log** file.