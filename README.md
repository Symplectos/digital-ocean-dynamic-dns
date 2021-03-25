# Digital Ocean Dynamic DNS
Python script to update DNS records managed by Digital Ocean.

Useful for home servers with dynamic IP addresses.

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
```
pip install -r requirements
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
