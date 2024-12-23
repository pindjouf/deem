# D33M DNS 

> [!IMPORTANT]
> This is a primitive implementation. It's functional but minimalist. Perfect for learning and hacking, but probably not what you want for your production environment...

### A hackable DNS implementation for those who dare to run their own nameservers

```
 ________  _______   _______   _____ ______           ________  ________   ________     
|\   ___ \|\  ___ \ |\  ___ \ |\   _ \  _   \        |\   ___ \|\   ___  \|\   ____\    
\ \  \_|\ \ \   __/|\ \   __/|\ \  \\\__\ \  \       \ \  \_|\ \ \  \\ \  \ \  \___|    
 \ \  \ \\ \ \  \_|/_\ \  \_|/_\ \  \\|__| \  \       \ \  \ \\ \ \  \\ \  \ \_____  \  
  \ \  \_\\ \ \  \_|\ \ \  \_|\ \ \  \    \ \  \       \ \  \_\\ \ \  \\ \  \|____|\  \ 
   \ \_______\ \_______\ \_______\ \__\     \ \__\       \ \_______\ \__\\ \__\____\_\  \
    \|_______|\|_______|\|_______|\|__|      \|__|        \|_______|\|__| \|__|\_________\
                                                                              \|_________|
```

## What is this?

A primitive, hackable DNS server implementation. No bloat, no unnecessary features - just pure DNS protocol at its core. Perfect for learning, experimenting, or running your own nameserver.

## Features

- ✓ Bare DNS protocol implementation
- ✓ Clean A record resolution
- ✓ NXDOMAIN handling for unsupported queries
- ✓ Zone file parsing
- ✓ Proper UDP socket handling
- ✓ Minimal external dependencies*

## Quick Start

1. Clone this repo

```bash
git clone https://github.com/pindjouf/deem.git
```

2. Create your zone files in `/etc/deem/`

```bash
mkdir -p /etc/deem
touch /etc/deem/example.com.zone
```

3. Run the server

```bash
python server.py
```

4. Test it

```bash
nslookup -port=53053 example.com 127.0.0.1
```

or 

```bash
dig @127.0.0.1 -p 53053 example.com
```

## Zone File Format

```plaintext
$TTL 86400
@       IN      SOA     ns1.example.com. admin.example.com. (
                        2023121801 ; Serial
                        3600       ; Refresh
                        1800       ; Retry
                        604800     ; Expire
                        86400 )    ; Minimum TTL

@       IN      NS      ns1.example.com.
@       IN      A       93.184.216.34
www     IN      A       93.184.216.34
```

## Current Limitations

- Only handles A records (IPv4)
- No caching
- No recursive resolution
- Local zone files only

## Potential Extensions

- [ ] Cache implementation
- [ ] Recursive resolver
- [ ] AAAA record support
- [ ] Additional record types (MX, TXT, etc.)

## License

This project is licensed under the WTFPL License - see the [LICENSE](LICENSE) file for details.
