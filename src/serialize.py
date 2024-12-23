from src.resolver import Response

def serialize(response: Response):
    header = (
        response.header.id +
        int(f"{response.header.flags.qr}{response.header.flags.opcode:04b}{response.header.flags.authoritative_answer}{response.header.flags.truncation}{response.header.flags.recursion_desired}{response.header.flags.recursion_available}{'000'}{response.header.flags.response_code:04b}", 2).to_bytes(2, byteorder='big') +
        (1).to_bytes(2, byteorder='big') +
        (1 if response.answer else 0).to_bytes(2, byteorder='big') +
        (0).to_bytes(2, byteorder='big') +
        (0).to_bytes(2, byteorder='big')
    )

    question = b''
    for label in response.question.labels:
        question += len(label.value).to_bytes(1, byteorder='big')
        question += label.value.encode('ascii')
    question += (0).to_bytes(1, byteorder='big')
    question += response.question.q_type['value'].to_bytes(2, byteorder='big')
    question += response.question.q_class['value'].to_bytes(2, byteorder='big')

    if response.answer:
        answer = b''
        answer += (0xc000 | 12).to_bytes(2, byteorder='big')
        answer += response.answer.a_type.to_bytes(2, byteorder='big')
        answer += response.answer.a_class.to_bytes(2, byteorder='big')
        answer += int(response.answer.ttl).to_bytes(4, byteorder='big')
        
        ip_bytes = bytes(map(int, response.answer.rdata.split('.')))
        answer += len(ip_bytes).to_bytes(2, byteorder='big')
        answer += ip_bytes
        
        return header + question + answer
    else:
        return header + question
