import sys
import imaplib
import email
import datetime
import re
import requests
from email.parser import HeaderParser
import subprocess
import smtplib
from datetime import datetime
import ConfigParser


def walkMsg(msg):
	for part in msg.walk():
		if part.get_content_type() == "multipart/alternative":
			continue
		if "<html>" in part.get_payload(decode=1).strip():
			continue
		yield part.get_payload(decode=1).strip()

def download_file(url, num):
	local_filename = DOWNLOAD_PATH + num + ".torrent"
	r = requests.get(url, stream=True)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
				f.flush()

def getStatus(username, password):
	cmd = [TRANSMISSION_REMOTE_PATH, "--auth", "{0}:{1}".format(username, password), '-l']
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	output = ""
	for line in p.stdout:
		output += line
	p.wait()
	return output

def sendMail(status):
	session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
	session.ehlo()
	session.starttls()
	session.login(EMAIL, PASSWORD)
	headers = "\r\n".join(["from: " + EMAIL,
                       "subject: " + "TORRENT STATUS",
                       "to: " + DESTINATION_EMAIL,
                       "mime-version: 1.0",
                       "content-type: text/plain"])
	content = headers + "\r\n\r\n" + status
	session.sendmail(EMAIL, DESTINATION_EMAIL, content)

def startAll(username, password):
	cmd = [TRANSMISSION_REMOTE_PATH, "--auth", "{0}:{1}".format(username, password), "-tall", "--start"]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	output = ""
	for line in p.stdout:
		output += line
	p.wait()
	return output

def addMagnet(magnet, username, password):
	cmd = [TRANSMISSION_REMOTE_PATH, "--auth", "{0}:{1}".format(username, password), '--add', magnet]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	output = ""
	for line in p.stdout:
		output += line
	p.wait()
	return output


if len(sys.argv) == 1:
	print "No config file!"
	sys.exit(1)

configFile = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read(configFile)

DOWNLOAD_PATH = config.get("Config", "download_path")
TRANSMISSION_REMOTE_PATH = config.get("Config", "transmission_remote_path")
EMAIL = config.get("Config", "email")
PASSWORD = config.get("Config", "password")
DESTINATION_EMAIL = config.get("Config", "destination_email")
SMTP_SERVER = config.get("Config", "smtp_server")
SMTP_PORT = config.get("Config", "smtp_port")
IMAP_SERVER = config.get("Config", "imap_server")
TRANSMISSION_USERNAME = config.get("Config", "transmission_username")
TRANSMISSION_PASSWORD = config.get("Config", "transmission_password")

dataora = datetime.now() 
print dataora.strftime('%d/%m/%Y %H:%M:%S')

conn = imaplib.IMAP4_SSL(IMAP_SERVER)
try:
	conn.login(EMAIL, PASSWORD)
except imaplib.IMAP4.error:
	print "LOGIN FAILED!!! "
	
conn.select(readonly=0)
rv, messages = conn.search(None, '(UNSEEN)')
if rv == "OK":
	for num in messages[0].split(' '):
		if num:
			typ, data = conn.fetch(num,'(RFC822)')
			hd = conn.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT FROM)])')
			header_data = hd[1][0][1]
			parser = HeaderParser()
			headers = parser.parsestr(header_data)
			if DESTINATION_EMAIL in headers['From'] and "torrent" in headers['Subject'].lower():
				print "Adding torrent"
				msg = email.message_from_string(data[0][1])
				for body in walkMsg(msg):
					results =  re.findall("(?P<url>https?://[^\s]+)", body)
					if results:
						#url = results.group("url")
						#print "url: " + url
						#download_file(url, num)
						i = 0
						for r in results:
							print "url: " + r
							print "Adding URL " + r
							download_file(r, "{0}-{1}".format(num, i))
							i = i + 1
					else:
						magnetResults = re.findall("magnet:\?xt=.*", body)
						if magnetResults:
							for magnet in magnetResults:
								print "Adding magnet " + magnet
								addMagnet(magnet, TRANSMISSION_USERNAME, TRANSMISSION_PASSWORD)
			elif DESTINATION_EMAIL in headers['From'] and "status" in headers['Subject'].lower():
				print "Sending status"
				status = getStatus(TRANSMISSION_USERNAME, TRANSMISSION_PASSWORD)
				sendMail(status)
			elif DESTINATION_EMAIL in headers['From'] and "start" in headers['Subject'].lower():
				print "Start all torrents"
				output = startAll(TRANSMISSION_USERNAME, TRANSMISSION_PASSWORD)
				print output

conn.logout()
