from enum import Enum
from src.parser import *
import os
import re

class Answer(BaseModel):
    name: str
    a_type: int
    a_class: int
    ttl: int
    rdata: str

class Response(BaseModel):
    header: Header
    question:Question
    answer: Optional[Answer] = None
    authority: int

class RR(BaseModel):
    name: str
    rr_type: str
    rr_class: str
    data: str

class NS(BaseModel):
    ns_type: str
    ns_class: str
    data: str

class SOA(BaseModel):
    domain_name: str
    primary_nameserver: str
    responsible_party: str
    serial_number: int
    refresh_time: int
    retry_time: int
    expire_time: int
    minimum_ttl: int

class ZoneFile(BaseModel):
    ttl: int
    soa_record: SOA
    ns_records: List[NS]
    resource_records: List[RR]

class Tokens(Enum):
    NAME = [
        "@",
        "www",
        "mail",
        "ftp",
        "blog",
        "_service._tcp",
       "_domainkey",
        "dkim",
        "*",
        "ns1",
        "ns2"
    ]

    TYPE = [
        "A",
        "AAAA",
        "NS",
        "CNAME",
        "MX",
        "PTR",
        "SOA",
        "TXT",
        "SRV",
        "CAA",
        "DNSKEY",
        "DS",
        "RRSIG",
        "NSEC",  
        "NSEC3",
        "DNAME",
        "HINFO",
        "RP",
        "AFSDB",
        "NAPTR"
    ]

    CLASS = [
        "IN",
        "CH",
        "HS",
        "NONE",
        "ANY"
    ]

    CONTROL = [
        "$ORIGIN",
        "$TTL",
        "$INCLUDE"
    ]

    COMMENT = ";"


DATA_PATTERNS = {
    "ipv4": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
    
    "ipv6": r'\b(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\b',
    
    "domain_name": r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.?',
    "ttl": r'\b\d+(?:[SMHDWsmhdw])?\b',
}

def get_domain_name(labels: List[DomainLabel]) -> str:
    return ".".join([label.value for label in labels])


def parse_zone_file(domain_name: str) -> dict:

    app_dir = "/etc/deem/"

    def get_zone_file(app_dir: str) -> List:
        for file in os.listdir(app_dir):
            if domain_name in file:
                with open(os.path.join(app_dir, file), "r") as f:
                    return f.read()

    zone_file = get_zone_file(app_dir).splitlines()

    def lexer(zone_file: str):
        in_parentheses = False
        post_parentheses = False
        controls = Tokens.CONTROL.value
        classes = Tokens.CLASS.value
        types = Tokens.TYPE.value
        names = Tokens.NAME.value
        soa_record = list()
        ns_records = list()
        resource_records = list()

        for line in zone_file:
            comment_index = line.find(Tokens.COMMENT.value)
            if comment_index != -1:
                line = line[:comment_index].strip()

            if not line:
                continue
            
            quoted_parts = list()
            while '"' in line:
                start = line.find('"')
                end = line.find('"', start + 1)
                if end == -1:
                    break
                quoted_parts.append(line[start:end+1])
                line = line[:start] + ' QUOTED_STRING ' + line[end+1:]

            words = line.split()
            words = [quoted_parts.pop(0) if word == 'QUOTED_STRING' else word for word in words]

            if "$" in line:
                words = line.split()
                control = [controls for controls in words]
                if control[0] == "$ORIGIN":
                    domain_name = control[1][:-1]
                if control[0] == "$TTL":
                    ttl = control[1]

            if "(" in line:
                soa_record = [i for i in line.split() if i != "("]
                if len(soa_record) != 5 and len(soa_record) != 6:
                    raise ValueError
                else:
                    primary_nameserver = soa_record[-2][:-1]
                    responsible_party = soa_record[-1][:-1]
                in_parentheses = True
                continue

            if ")" in line:
                in_parentheses = False
                post_parentheses = True

            if in_parentheses:
                soa_record.append(line)

            record_tokens = list()

            if post_parentheses:
                for word in words:
                    if word in names:
                        record_tokens.append(word)
                    elif word in types:
                        record_tokens.append(word)
                    elif word in classes:
                        record_tokens.append(word)
                    else:
                        for pattern_name, pattern in DATA_PATTERNS.items():
                            if re.match(pattern, word):
                                record_tokens.append(word)
                                break

                if len(record_tokens) <= 3 and len(record_tokens) > 0:
                    if "NS" in record_tokens:
                        ns = NS(
                            ns_class=record_tokens[0],
                            ns_type=record_tokens[1],
                            data=record_tokens[2]
                        )
                        ns_records.append(ns)
                elif len(record_tokens) > 3:
                    rr = RR(
                        name=record_tokens[0],
                        rr_class=record_tokens[1],
                        rr_type=record_tokens[2],
                        data=record_tokens[-1]
                    )
                    resource_records.append(rr)

        soa_record = SOA(
            domain_name=domain_name,
            primary_nameserver=primary_nameserver,
            responsible_party=responsible_party,
            serial_number=soa_record[-5],
            refresh_time=soa_record[-4],
            retry_time=soa_record[-3],
            expire_time=soa_record[-2],
            minimum_ttl=soa_record[-1]
        )

        zone_file = ZoneFile(
            ttl=ttl,
            soa_record=soa_record,
            ns_records=ns_records,
            resource_records=resource_records
        )

        return zone_file

    zone_file = lexer(zone_file)

    return zone_file

def resolver(query: Query):
    query = parser(query)
    query.header.flags.qr = 1
    
    if query.question.q_type['value'] != 1:
        query.header.flags.response_code = 3
        return Response(
            header=query.header,
            question=query.question,
            answer=None,
            authority=0
        )

    domain_name = get_domain_name(query.question.labels)
    try:
        zone_file = parse_zone_file(domain_name)
        
        def get_ip(zone_file):
            for record in zone_file.resource_records:
                if len(query.question.labels) <= 2:
                    if record.name != "@":
                        continue
                    if record.rr_type == query.question.q_type['meaning'] and record.rr_class == query.question.q_class['meaning']:
                        rdata = record.data
                        return rdata
                else:
                    if record.name == query.question.labels[0].value and record.rr_type == query.question.q_type['meaning'] and record.rr_class == query.question.q_class['meaning']:
                        rdata = record.data
                        return rdata
            raise ValueError(f"No matching record found for {domain_name}")

        rdata = get_ip(zone_file)

        answer = Answer(
            name=zone_file.soa_record.domain_name,
            a_type=query.question.q_type['value'],
            a_class=query.question.q_class['value'],
            ttl=zone_file.ttl,
            rdata=rdata,
        )

        return Response(
            header=query.header,
            question=query.question,
            answer=answer,
            authority=len(zone_file.ns_records),
        )
        
    except (FileNotFoundError, ValueError):
        query.header.flags.response_code = 3
        return Response(
            header=query.header,
            question=query.question,
            answer=None,
            authority=0
        )
