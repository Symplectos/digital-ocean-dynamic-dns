########################################################################################################################
# IMPORTS ##############################################################################################################
########################################################################################################################
import configparser     # python config parser module
import requests         # human friendly http requests
import logging          # logger class

########################################################################################################################
# DEFINITIONS ##########################################################################################################
########################################################################################################################
restURL = 'https://api.digitalocean.com/v2/'            # the URL to the REST API of Digital Ocean
configFileStructure = {'DigitalOcean': ['key'],         # the expected structure for the do.conf file
                       'DNS': ['domain', 'records']}

########################################################################################################################
# LOGGER ###############################################################################################################
########################################################################################################################
# create base logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create file handler
fh = logging.FileHandler('doDynDNS.log', mode='w')
fh.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to fh
fh.setFormatter(formatter)

# add fh to logger
logger.addHandler(fh)

########################################################################################################################
# METHODS ##############################################################################################################
########################################################################################################################
def getRecords(header, domain, type):
    try:
        # function to return all domain records of a given type
        recordsDict = []
        recordsArray = []
        result = requests.get(restURL + 'domains/{}/records?type={}'.format(domain, type), headers=header)
        result.raise_for_status()

        if not result.status_code == 200:
            # the domain records could not be retrieved from the server, exit with an error message
            logger.error('Critical Error: Unable to retrieve the domain {} from Digital Ocean!'.format(domain))
            logger.error('Status Code: {}'.format(result.status_code))
            exit(1)

        result = result.json()['domain_records']
        for record in result:
            # create dict and array with the returned results
            recordsDict.append({'Name': record['name'], 'IP': record['data'],
                                'ID': record['id'], 'Type': record['type']})
            recordsArray.append(record['name'])

        # return the dict
        return recordsDict, recordsArray

    except Exception as e:
        logger.error('Critical Error: Unable to get records of {} from Digital Ocean!')
        logger.error('Error Message: {}'.format(e))
        exit(1)

def getPublicIP(ipv4 = True):
    try:
        # function to get an IPv4 or IPv6 address
        type = '' if ipv4 else '64'
        strType = 'v4' if ipv4 else 'v6'

        # get the ip from ipify as json
        ip = requests.get('https://api{}.ipify.org?format=json'.format(type))
        ip.raise_for_status()

        if not ip.status_code == 200:
            # unable to retrieve the ip, exit with an error message
            logger.error('Critical Error: Unable to get public IP!')
            logger.error('Status Code: {}'.format(ip.status_code))
            exit(1)

        # print message and return ip
        endl = '' if ipv4 else '\n\n'
        ip = ip.json()['ip']
        logger.info('Public IP{}: {}{}'.format(strType, ip, endl))
        return ip

    except Exception as e:
        logger.error('Critical Error: Unable to get public IP{} address'.format(strType))
        logger.error('Error Message: {}'.format(e))
        exit(1)

def getPublicIPs():
    try:
        # function retrieve the public IPv4 addresses of the server from the ipify API
        ip4 = getPublicIP(ipv4=True)
        ip6 = getPublicIP(ipv4=False)

        # return the IP addresses
        return ip4, ip6

    except Exception as e:
        logger.error('Critical Error: Unable to get public IP addresses')
        logger.error('Error Message: {}'.format(e))
        exit(1)


def updateRecord(record, domain, ip, digitalOceanRecords, header, br=False):
    # function to check for IP changes for a given record and to update the record if necessary
    try:
        # get the appropriate record from the Digital Ocean records
        # filter: select a specific element in a list of dicts
        # next: get the first element satisfying the filter condition
        digitalOceanRecord = next(filter(lambda l: l['Name'] == record, digitalOceanRecords))

        # check for IP address change
        changed = True
        if not ip == digitalOceanRecord['IP']:
            # the ip address changed -> log and update
            endl = '' if digitalOceanRecord['Type'] == 'A' else '\n'
            endl += '\n' if br and digitalOceanRecord['Type'] == 'A' else ''
            logger.info('{}.{}: {} --> {}{}'.format(record, domain, digitalOceanRecord['IP'], ip, endl))

            # create payload and set PUT request
            payload = {'data': ip}
            result = requests.put(restURL + 'domains/{}/records/{}'.format(domain, digitalOceanRecord['ID']),
                                  json=payload, headers=header)

            # raise for status
            if not result.status_code == 200:
                changed = False
                logger.warning('{}.{}: {}'.format(record, domain, result.status_code))

            return changed

    except Exception as e:
        logger.error('Critical Error: Unable to get update record: {}.{}!'.format(record, domain))
        logger.error('Error Message: {}'.format(e))
        exit(1)

########################################################################################################################
# SCRIPT ###############################################################################################################
########################################################################################################################
def main():
    # main script
    try:
        # READ AND PARSE THE CONFIG FILE ###############################################################################
        doConfig = configparser.ConfigParser()
        doConfig.read('.do.conf')

        # check for a valid file
        for section, parameters in configFileStructure.items():
            # for each section, parameters pair
            if section not in doConfig.sections():
                # if the section is not found in the supplied configuration file -> exit with an error message
                logger.error('Invalid Configuration File! Please provide a [{}] section!'.format(section))
                exit(1)

            # the section exists -> check if the desired parameters are set
            for parameter in parameters:
                if parameter not in doConfig[section].keys():
                    # if the parameter was not set, exit with an error message
                    logger.error('Invalid Configuration File! Please provide a {} parameter!'.format(parameter))
                    exit(1)

        # the configuration file is valid, get the API key, as well as the desired domain and subdomains
        key = doConfig['DigitalOcean']['key']
        domain = doConfig['DNS']['domain']
        records = doConfig['DNS']['records'].split('\n')

        # print starting message
        logger.info('Updating the records of {} ...'.format(domain))

        # HTTPS AUTHORIZATION ##########################################################################################
        header = {'Authorization': 'Bearer {}'.format(key)}

        # GET A and AAAA RECORDS #######################################################################################
        recordsA, namesA = getRecords(header, domain, 'A')
        recordsAAAA, namesAAAA = getRecords(header, domain, 'AAAA')

        # GET PUBLIC IP ADDRESS ########################################################################################
        ip4, ip6 = getPublicIPs()

        # UPDATE A and AAAA RECORDS ####################################################################################
        nChanged = 0
        for i, record in enumerate(records):
            # for each record that should be updated
            if record not in namesA:
                # if the record does not exist in the domain, print a warning and continue
                logger.warning('Warning! The record {} does not exist, and can thus not be updated!'.format(record))
                continue

            # check for IP change and update if necessary
            if updateRecord(record, domain, ip4, recordsA, header):
                nChanged += 1
            if updateRecord(record, domain, ip6, recordsAAAA, header):
                nChanged += 1

        # exit with success
        logger.info('Success! {} DNS records were changed.'.format(nChanged))
        exit(0)

    except Exception as e:
        # on any exception, print an error message and exit
        logger.error('Critical Error: {}'.format(e))
        exit(1)


# run main
if __name__ == '__main__':
    main()
