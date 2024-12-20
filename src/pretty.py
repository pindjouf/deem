def print_query(query):
    colors = {
        'bg':      '\033[48;2;29;32;33m',
        'fg':      '\033[38;2;213;196;161m',
        'red':     '\033[38;2;234;105;98m',
        'green':   '\033[38;2;169;182;101m',
        'yellow':  '\033[38;2;231;138;78m',
        'blue':    '\033[38;2;127;187;179m',
        'purple':  '\033[38;2;211;134;155m',
        'aqua':    '\033[38;2;137;180;130m',
        'gray':    '\033[38;2;146;131;116m',
        'orange':  '\033[38;2;235;139;55m',
        'reset':   '\033[0m'
    }

    def print_header(text):
        print(f"\n{colors['yellow']}{'=' * 60}{colors['reset']}")
        print(f"{colors['orange']}{text:^60}{colors['reset']}")
        print(f"{colors['yellow']}{'=' * 60}{colors['reset']}\n")

    def print_field(label, value, color='fg'):
        print(f"{colors['blue']}{label}: {colors[color]}{value}{colors['reset']}")

    def print_subfield(label, value, color='fg'):
        print(f"  {colors['aqua']}{label}: {colors[color]}{value}{colors['reset']}")

    print_header("Deem and Nets")
    
    print_field("Message ID", f"0x{query.header.id.hex().upper()}", 'purple')
    
    print_header("Flags")
    flags = query.header.flags
    flag_meanings = {
        'qr': "Response" if flags.qr else "Query",
        'aa': "Authoritative" if flags.authoritative_answer else "Non-authoritative",
        'tc': "Truncated" if flags.truncation else "Not truncated",
        'rd': "Recursion desired" if flags.recursion_desired else "Recursion not desired",
        'ra': "Recursion available" if flags.recursion_available else "Recursion not available"
    }
    
    for flag, meaning in flag_meanings.items():
        print_subfield(f"{flag.upper()}", meaning, 'green')
    
    print_subfield("OPCODE", f"{flags.opcode}", 'red')
    print_subfield("RCODE", f"{flags.response_code}", 'red')
    
    print_header("Counts")
    counts = {
        "Questions": query.header.question_count,
        "Answers": query.header.answer_count,
        "Authority Records": query.header.authority_count,
        "Additional Records": query.header.additional_records_count
    }
    for label, count in counts.items():
        print_field(label, count, 'purple')
    
    print_header("Question")
    
    domain = ".".join(label.value for label in query.question.labels)
    print_field("Domain", domain, 'green')
    
    print_field("Type", f"{query.question.q_type['value']} ({query.question.q_type['meaning']})", 'orange')
    print_field("Class", f"{query.question.q_class['value']} ({query.question.q_class['meaning']})", 'orange')
    
    print(f"\n{colors['yellow']}{'=' * 60}{colors['reset']}")

def print_response(response):
    colors = {
        'bg':      '\033[48;2;29;32;33m',
        'fg':      '\033[38;2;213;196;161m',
        'red':     '\033[38;2;234;105;98m',
        'green':   '\033[38;2;169;182;101m',
        'yellow':  '\033[38;2;231;138;78m',
        'blue':    '\033[38;2;127;187;179m',
        'purple':  '\033[38;2;211;134;155m',
        'aqua':    '\033[38;2;137;180;130m',
        'gray':    '\033[38;2;146;131;116m',
        'orange':  '\033[38;2;235;139;55m',
        'reset':   '\033[0m'
    }

    # Server Information
    print(f"{colors['yellow']}Server:   127.0.0.1{colors['reset']}")
    print(f"{colors['yellow']}Address:  127.0.0.1#53053{colors['reset']}")

    # Authority status answer
    if response.authority >= 1:
        print(f"\n{colors['green']}Authoritative answer:{colors['reset']}")
    else:
        print(f"\n{colors['green']}Non-authoritative answer:{colors['reset']}")

    # Domain and IP Address
    print(f"{colors['green']}Name:   {response.answer.name}{colors['reset']}")
    print(f"{colors['green']}Address: {response.answer.rdata}{colors['reset']}")
