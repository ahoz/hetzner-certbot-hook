# Automatically renew LetsEncrypt wildcard certificates for domains using Hetzner name servers

## Requirements

- Certbot
- Python
- Domain and Nameserver hosted on Hetzner
- Hetzner DNS Api Token

## Set config

1. Move *config.ini.example* to *config.ini*.

2. Get a Hetzner [DNS API Token](https://dns.hetzner.com/settings/api-token)

3. Set Api token in `config.ini`:
```
[DEFAULT]
hdns_api_token = yourToken
```
4. make the script executable:
`chmod +x hetznerdnshook.py` or else certbot will throw an error.

## Usage

### Get first certificate

```bash
sudo certbot certonly --manual --preferred-challenges dns --manual-auth-hook ./hetznerdnshook.py -d domain.de -d *.domain.de
```

### Renew certificate

This line can also be used for automated calls like inside cron scripts.

```bash
sudo certbot certonly  --manual --preferred-challenges dns --manual-auth-hook ./hetznerdnshook.py -d domain.de -d *.domain.de --dry-run --agree-tos  --manual-public-ip-logging-ok
```

### Delete old TXT Entries

In order to delete old ACME TXT entries, you can use following command

```bash
python3 hetznerdnshook.py --delete domain.de
```

**Keep in mind to replace domain.de with your own domain!**
