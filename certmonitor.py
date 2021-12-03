import ssl
import socket
import OpenSSL
from datetime import datetime
import smtplib
import configparser


def parse_conf_file():
    config = configparser.ConfigParser()
    config.read('global.cfg')
    days_before = config.get('general', 'days_before')
    site_file = config.get('general', 'site_file')
    server = config.get('mail-server', 'server')
    user = config.get('mail-server', 'user')
    password = config.get('mail-server', 'password')
    port = config.get('mail-server', 'port')
    recipient1 = config.get('recipients', 'email1')
    recipient2 = config.get('recipients', 'email2')
    recipient3 = config.get('recipients', 'email3')
    recipient4 = config.get('recipients', 'email4')
    recipient5 = config.get('recipients', 'email5')
    return days_before, site_file, server, user, password, port, recipient1, recipient2, recipient3, recipient4, recipient5


def get_certificate(host, port=443, timeout=10):
    context = ssl.create_default_context()
    conn = socket.create_connection((host, port))
    sock = context.wrap_socket(conn, server_hostname=host)
    sock.settimeout(timeout)
    try:
        der_cert = sock.getpeercert(True)
    finally:
        sock.close()
    return ssl.DER_cert_to_PEM_cert(der_cert)


def get_sites(sites):
    f = open(sites, 'r')
    sites = f.readlines()
    return sites


def mailSend(mailBody, server, user, password, port, recipient1, recipient2, recipient3, recipient4, recipient5):
    mail_password = password
    sent_from = user
    textbody = ''
    for elem in mailBody:
        textbody = textbody + elem + '\n'
    print(textbody)
    textbody = f'Subject: The certificates will be out of date soon. \n\r\n {textbody} '
    server = smtplib.SMTP(server, port)
    server.starttls()
    server.ehlo()
    server.login(user, mail_password)
    server.sendmail(sent_from, recipient1, textbody)
    if recipient2 != 'zero':
        server.sendmail(sent_from, recipient2, textbody)
    if recipient3 != 'zero':
        server.sendmail(sent_from, recipient3, textbody)
    if recipient4 != 'zero':
        server.sendmail(sent_from, recipient4, textbody)
    if recipient5 != 'zero':
        server.sendmail(sent_from, recipient5, textbody)
    server.close()


if __name__ == '__main__':
    days_before, site_file, server, user, password, port, recipient1, recipient2, recipient3, recipient4, recipient5 = parse_conf_file()
    sites = get_sites(site_file)
    mailBody = []
    for site in sites:
        try:
            certificate = get_certificate(site.strip())
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
            notAafter = (x509.get_notAfter()).decode()
            notAafter = datetime.strptime(notAafter, '%Y%m%d%H%M%SZ')
            life_days = notAafter - datetime.now()
            if life_days.days <= int(days_before):
                mailBody.append(f'For domain  {site.strip()}  certificates will expire in {life_days.days} days')
        except:
            mailBody.append(f'For domain {site.strip()} sertificate not valid ')
    if len(mailBody) >= 1:
        mailSend(mailBody, server, user, password, port, recipient1, recipient2, recipient3, recipient4, recipient5)
