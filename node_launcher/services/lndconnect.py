
import base64
import qrcode


def get_deprecated_lndconnect_url(host, port, cert_path, macaroon_path):
    return f'lndconnect:?cert={cert_path}&macaroon={macaroon_path}&host={host}:{port}'


def get_lndconnect_url(host, port, cert_path, macaroon_path):
    with open(cert_path, 'r') as cert_file:
        lines = cert_file.read().split('\n')
        lines = [line for line in lines if line != '']
        cert = ''.join(lines[1:-1])

    with open(macaroon_path, 'rb') as macaroon_file:
        macaroon = base64.b64encode(macaroon_file.read()).decode('ascii')

    return f'lndconnect://{host}:{port}?cert={cert}&macaroon={macaroon}'


def get_qrcode_img(host, port, cert_path, macaroon_path):
    url = get_lndconnect_url(host, port, cert_path, macaroon_path)

    img = qrcode.make(url)

    return img
