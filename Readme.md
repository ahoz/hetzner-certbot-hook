# Automatically renew LetsEncrypt wildcard certificates for domains using Hetzner name servers

## Requirements

- Certbot
- Python
- Domain and Nameserver hosted on Hetzner
- Hetzner DNS Api Token

## Set config

Move *config.ini.example* to *config.ini*.

Set Api token.

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


## Todos
Comment will be added in the next few days.