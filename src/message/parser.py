from pydantic import BaseModel
from typing import List

class DomainLabel(BaseModel):
    length: int
    value: str

class Flags(BaseModel):
    qr: int
    opcode: int
    authoritative_answer: int
    truncation: int
    recursion_desired: int
    recursion_available: int
    zero: int
    response_code: int

class Header(BaseModel):
    id: bytes
    flags: Flags
    question_count: int
    answer_count: int
    authority_count: int
    additional_records_count: int

class Question(BaseModel):
    labels: List[DomainLabel]
    zero_byte_terminator: int
    q_type: int
    q_class: int

class Query(BaseModel):
    header: Header
    question: Question

class OpcodeToken:
    def get_token(self, flags: str) -> dict:
        bin_opcode = "0b" + flags
        opcode_value = int(bin_opcode, 2)

        opcode_token = ""
        match opcode_value:
            case 0:
                opcode_token = "Standard query"
            case 1:
                opcode_token = "Inverse query"
            case 2:
                opcode_token = "Server status request"
            case 3:
                opcode_token = "Reserved"

        return { 'value': opcode_value, 'meaning': opcode_token }

class rCodeToken:
    def get_token(self, flags: str) -> dict:
        bin_rcode = "0b" + flags
        rcode_value = int(bin_rcode, 2)

        rcode_token = ""
        match rcode_value:
            case 0:
                rcode_token = "Success"
            case 1:
                rcode_token = "Format specification error"
            case 2:
                rcode_token = "Server Failure"
            case 3:
                rcode_token = "Query does not exist in domain"
            case 4:
                rcode_token = "Type is not supported by the server"
            case 5:
                rcode_token = "Nonexecution of queries by server due to policy reasons"

        return { 'value': rcode_value, 'meaning': rcode_token }

def hex_to_bin(hex_string: str) -> str:
    return bin(int(hex_string, 16))[2:].zfill(16)

def parse_flags(flags: str) -> dict:
    opcode = OpcodeToken()
    rcode = rCodeToken()
                       # pseudo-index flags: 0 1234 5 6 7 8 910 1234
                            # Example flags: 0 0000 0 0 1 0 010 0000
    data = {
        'qr': {'value': 1, 'meaning': "response"} if int(flags[0]) == 1 else {'value': 0, 'meaning': "request"},
        'opcode': opcode.get_token(flags[1:5]),
        'authoritative_answer': {'value': 1, 'meaning': "authoritative"} if int(flags[5]) == 1 else {'value': 0, 'meaning': "non-authoritative"},
        'truncation': {'value': 1, 'meaning': "Truncated"} if int(flags[6]) == 1 else {'value': 0, 'meaning': "Not truncated"},
        'recursion_desired': {'value': 1, 'meaning': "Recursion requested"} if int(flags[7]) == 1 else {'value': 0, 'meaning': "Recursion not requested"},
        'recursion_available': {'value': 1, 'meaning': "Recursion available"} if int(flags[8]) == 1 else {'value': 0, 'meaning': "Recursion not available"},
        'zero': {'value': 0, 'meaning': "Reserved"} if int(flags[9:12], 2) == 0 else {'value': int(flags[9:12], 2), 'meaning': "Error (should be zero)"},
        'rcode': rcode.get_token(flags[12:16])
    }

    return data

def pretty_print(header: Header, tokenized_flags, binary_flags, query):
    print("\nDNS Query Analysis")
    print("=" * 60)
    print(f"Base Query: {query}")
    print("\nDNS Header")
    print("=" * 60)
    print(f"Transaction ID: 0x{header.id.hex()} (bytes: {header.id})")
    print("=" * 60)
    print("Counts:")
    print(f"  Questions: {header.question_count}")
    print(f"  Answers: {header.answer_count}")
    print(f"  Authority RRs: {header.authority_count}")
    print(f"  Additional RRs: {header.additional_records_count}")
    print("=" * 60)
    print("")
    print("Tokenized Flags:")
    print("=" * 60)
    print(f"Binary Flags: {binary_flags}")
    
    for key, value in tokenized_flags.items():
        print(f"{key.replace('_', ' ').title():20}: {value['value']} - {value['meaning']}")
    
    print("=" * 60)

def parser(query: str):
    flags_substring = query[4:8]
    binary_flags = hex_to_bin(flags_substring)
    tokenized_flags = parse_flags(binary_flags)

    flags = Flags(
        qr=tokenized_flags['qr']['value'],
        opcode=tokenized_flags['opcode']['value'],
        authoritative_answer=tokenized_flags['authoritative_answer']['value'],
        truncation=tokenized_flags['truncation']['value'],
        recursion_desired=tokenized_flags['recursion_desired']['value'],
        recursion_available=tokenized_flags['recursion_available']['value'],
        zero=tokenized_flags['zero']['value'],
        response_code=tokenized_flags['rcode']['value']
    )
    header = Header(
        id=bytes.fromhex(query[0:4]),
        flags=flags,
        question_count=int(query[8:12], 16),
        answer_count=int(query[12:16], 16),
        authority_count=int(query[16:20], 16),
        additional_records_count=int(query[20:24], 16)
    )

    pretty_print(header, tokenized_flags, binary_flags, query)
