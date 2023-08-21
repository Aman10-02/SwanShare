import base64
def get_str_from_key():
    with open('public_key.pem', 'rb') as pem_file:
        pem_data = pem_file.read()
    base64_encoded = base64.b64encode(pem_data)
    base64_encoded=base64_encoded.decode()
    print(base64_encoded)
    file_path = "./public.txt"
    with open(file_path, 'w') as file:
        file.write(base64_encoded)

    print("Content written to", file_path)
    return base64_encoded