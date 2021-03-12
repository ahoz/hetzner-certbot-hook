#!/usr/bin/env python3
import requests, json, os, time, re, configparser, sys

_EXITCODE=0

def get_zone_id(api_token, zone_name):
    zones_resp = get_zones(api_token)
    if len(zones_resp) == 0:
        print("No zones existing")
        _EXITCODE=2
        return False
    for zone in zones_resp['zones']:
        if zone['name'] == zone_name:
            return zone['id']
    print("Zone not found")
    _EXITCODE=3
    return False

def get_zones(api_token):
    try:
        response = requests.get(
            url="https://dns.hetzner.com/api/v1/zones",
            headers={
                "Auth-API-Token": api_token,
            },
        )
        return json.loads(response.text)
    except requests.exceptions.RequestException:
        print('Get Zone HTTP Request failed')
        _EXITCODE=4
        return dict()

def create_txt_record(api_token, zone_id, record_key, record_value):
    try:
        response = requests.post(
            url="https://dns.hetzner.com/api/v1/records",
            headers={
                "Content-Type": "application/json",
                "Auth-API-Token": api_token,
            },
            data=json.dumps({
                "value": record_value,
                "type": "TXT",
                "name": record_key,
                "zone_id": zone_id
            })
        )
        if response.status_code == '200':
            print("Successful")
            return True
    except requests.exceptions.RequestException:
        print('Create TXT Record HTTP Request failed')
        _EXITCODE=5
        return False

def get_tld(domain):
    try:
        return re.search(r"^(((?!-))(xn--|_{1,1})?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*(xn--)?([a-z0-9][a-z0-9\-]{0,60}|[a-z0-9-]{1,30}\.[a-z]{2,})$", domain.strip()).group(0)
    except:
        _EXITCODE=6
        return -1

def get_sub(domain):
    try:
        return re.search(r"((\w+\.)*)?\w+\.\w+$", domain.strip()).group(1)[:-1]
    except:
        _EXITCODE=6
        return -1

def get_key(sub):
    if len(sub) > 0:
        sub = "." + sub
    return "_acme-challenge" + sub

def exit_check():
    if _EXITCODE > 0:
        if _EXITCODE == 2:
            raise Exception('No zones existing')
        elif _EXITCODE == 3:
            raise Exception('Zone not found')
        elif _EXITCODE == 4:
            raise Exception('Get Zone HTTP Request failed')
        elif _EXITCODE == 5:
            raise Exception('Create TXT Record HTTP Request failed')
        elif _EXITCODE == 6:
            raise Exception('Could not extract (sub)domain')
        elif _EXITCODE == 7:
            raise Exception('Could not read config file!')
        elif _EXITCODE == 8:
            raise Exception('Get Records HTTP Request failed')
        elif _EXITCODE == 9:
            raise Exception('Delete Record HTTP Request failed')

def read_config():
    try:
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
        return config
    except:
         _EXITCODE=7
         print("Could not read config file!")
    

def get_all_records(api_token, zone_id):
    try:
        response = requests.get(
            url="https://dns.hetzner.com/api/v1/records",
            params={
                "zone_id": zone_id,
            },
            headers={
                "Auth-API-Token": api_token,
            },
        )
        return json.loads(response.text)
    except requests.exceptions.RequestException:
        print('Get Records HTTP Request failed')
        _EXITCODE = 8

def get_all_le_txt_records(api_token, zone_id):
    all_txt_records = get_all_records(api_token, zone_id)
    records_list = list()
    for record in all_txt_records['records']:
        if record['type'] == "TXT" and record['name'][:15] == "_acme-challenge":
            records_list.append(record)
    return records_list

def delete_record(api_token, record_id):
    try:
        response = requests.delete(
            url="https://dns.hetzner.com/api/v1/records/"+record_id,
            headers={
                "Auth-API-Token": api_token,
            },
        )
    except requests.exceptions.RequestException:
        print('Delete Record HTTP Request failed')
        _EXITCODE = 9


def delete_le_txt_records(domain):
    config = read_config()
    hdns_api_token = config['DEFAULT']['hdns_api_token']
    domain = get_tld(domain)
    zone_id = get_zone_id(hdns_api_token, domain)
    for record in get_all_le_txt_records(hdns_api_token, zone_id):
        delete_record(hdns_api_token, record['id'])
    exit_check()

def main():
    config = read_config()
    hdns_api_token = config['DEFAULT']['hdns_api_token']
    domain = get_tld(os.environ["CERTBOT_DOMAIN"])
    sub = get_sub(os.environ["CERTBOT_DOMAIN"])
    zone_id = get_zone_id(hdns_api_token, domain)
    key = get_key(sub)
    key_value = os.environ["CERTBOT_VALIDATION"]
    sleep_time = 15
    exit_check()
    create_txt_record(hdns_api_token, zone_id, key, key_value)
    time.sleep(sleep_time)

if __name__ == "__main__":
    if(len(sys.argv) > 1):
        if sys.argv[1] == '--delete' and len(sys.argv) == 3:
            for domain in sys.argv[2:]:
                delete_le_txt_records(domain)
        else:
            print("Use to delete old records: python3 hetznerdnshook.py --delete <DOMAINNAME>")
    else:
        main()
