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
    q_type: dict
    q_class: dict

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

def hex_to_ascii(hex_string: str) -> str:
    return bytes.fromhex(hex_string).decode('ascii')

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

def get_labels(question: str) -> List:
    labels = list()
    labels_substring = question[:-8]

    while labels_substring != "":
        length = int(labels_substring[:2], 16)
        value = labels_substring[2:length*2+2]
        if labels_substring[length*2:length*2+2] == "00":
            break
        else:
            node = {'length': length, 'value': hex_to_ascii(value)}
            labels.append(node)
            node_string = labels_substring[:2] + value
            labels_substring = labels_substring.replace(node_string, "")

    return labels

def get_type(type_substring: str) -> dict:
    type_value = int(type_substring, 16)

    type_token = ""
    match type_value:
        case 1:
            type_token = "A"
        case 2:
            type_token = "NS"
        case 5:
            type_token = "CNAME"
        case 6:
            type_token = "SOA"
        case 12:
            type_token = "PTR"
        case 15:
            type_token = "MX"
        case 16:
            type_token = "TXT"
        case 28:
            type_token = "AAAA"
        case 33:
            type_token = "SRV"
        case 252:
            type_token = "AXFR"
        case 255:
            type_token = "ANY"
        case _:
            type_token = "Unknown or unsupported type"

    return {'value': type_value, 'meaning': type_token}


def get_class(class_substring: str) -> dict:
    class_value = int(class_substring, 16)

    class_token = ""
    match class_value:
        case 1:
            class_token = "IN"
        case 3:
            class_token = "CH"
        case 4:
            class_token = "HS"
        case 255:
            class_token = "ANY"
        case _:
            class_token = "Unknown or unsupported class"

    return {'value': class_value, 'meaning': class_token}

def parser(query: str):
    flags_substring = query[4:8]
    binary_flags = hex_to_bin(flags_substring)
    tokenized_flags = parse_flags(binary_flags)

    question_substring = query[24:]
    labels = get_labels(question_substring)
    q_type = get_type(question_substring[-8:-4])
    q_class = get_class(question_substring[-4:])

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
    question = Question(
        labels=labels,
        zero_byte_terminator=question_substring[-10:-8],
        q_type=q_type,
        q_class=q_class
    )
    parsed_query = Query(
        header=header,
        question=question
    )

    return parsed_query
