from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization

with open('pep.txt', 'r', encoding='utf-8') as file:
    lines =  file.readlines()
c5 = ""
for line in lines:
    if line.startswith("c5"):
        c5 = eval(line.split('=')[1].strip())

with open("Certs&keys/private_key.pem", "rb") as key_file:
    rsa_private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=c5,
    )

# Generate a CSR
csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    # Provide various details about who we are.
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
    x509.NameAttribute(NameOID.COMMON_NAME, "mysite.com"),
])).add_extension(
    x509.SubjectAlternativeName([
        # Describe what sites we want this certificate for.
        x509.DNSName("mysite.com"),
        x509.DNSName("www.mysite.com"),
        x509.DNSName("subdomain.mysite.com"),
    ]),
    critical=False,
# Sign the CSR with our private key.
).sign(rsa_private_key, hashes.SHA256())
# Write our CSR out to disk.
with open("Certs&keys/Acsr.pem", "wb") as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))