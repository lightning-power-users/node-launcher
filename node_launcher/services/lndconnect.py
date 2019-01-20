import base64
import qrcode


def base64URL_from_base64(s):
    return s.replace('+', '-').replace('/', '_').rstrip('=')


def get_deprecated_lndconnect_url(host, port, cert_path, macaroon_path):
    return f'lndconnect:?cert={cert_path}&macaroon={macaroon_path}&host={host}:{port}'


def get_lndconnect_url(host, port, cert_path, macaroon_path):
    with open(cert_path, 'r') as cert_file:
        lines = cert_file.read().split('\n')
        lines = [line for line in lines if line != '']
        cert = ''.join(lines[1:-1])
        cert = base64URL_from_base64(cert)

    with open(macaroon_path, 'rb') as macaroon_file:
        macaroon = base64.b64encode(macaroon_file.read()).decode('ascii')
        macaroon = base64URL_from_base64(macaroon)

    return f'lndconnect://{host}:{port}?cert={cert}&macaroon={macaroon}'


def get_qrcode_img(host, port, cert_path, macaroon_path):
    url = get_lndconnect_url(host, port, cert_path, macaroon_path)

    img = qrcode.make(url)

    return img
