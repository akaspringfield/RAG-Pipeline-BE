import tiktoken

def count_tokens(text, model="gpt-4"):
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))