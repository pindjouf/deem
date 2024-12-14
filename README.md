# Deem and Nets

**Deem and Nets** is a primitive DNS implementation. The name was chosen at random, you could see it in multiple ways:
- Say deem and nets fast and it sounds like DNS
- See it as "Demand nets" since DNS places several demands on networks

You can choose it means whatever.

## Features

- Parses the DNS message header (including flags and counts).
- Server provides structured output to help visualize DNS query components.
- Serves as a foundation for future expansions, such as resolving DNS queries and supporting various DNS record types.

## Directory Structure

```
deem-and-nets
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
└── src/                   # Source code
    ├── message/
    │   ├── builder.py     # Future DNS message builder
    │   ├── parser.py      # Current DNS message parser
    ├── records/
    │   └── types.py       # DNS record types (e.g., A, CNAME, etc.)
    ├── resolver/
    │   ├── cache.py       # Future caching mechanism
    │   └── resolver.py    # Future DNS resolver logic
    └── server.py          # UDP DNS server
```

## Getting Started

### Prerequisites

- Python 3.12+ (as indicated by the virtual environment)
- `pip` for installing dependencies

### Installation

1. Clone the repository:

```bash
git clone https://github.com/pindjouf/deem-and-nets.git
cd deem-and-nets
```

2. Set up a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Usage

1. Start the UDP server:

```bash
python src/server.py
```

2. Send a DNS query to the server:

```bash
dig @127.0.0.1 -p 53053 example.com
```

or

```bash
nslookup -port=53053 -querytype=A example.com 127.0.0.1
```

I recommend `nslookup` since it provides valid flags, unlike `dig`.

3. Analyze the parsed DNS header output.

### Current Limitations

- Only parses the DNS message header.
- No support for response generation or DNS record resolution yet.

## Roadmap

- Add DNS response generation.
- Implement caching for better performance.
- Expand support for DNS record types (A, AAAA, CNAME, etc.).
- Implement advanced features like recursion and authoritative responses.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the WTFPL License - see the [LICENSE](LICENSE) file for details.
