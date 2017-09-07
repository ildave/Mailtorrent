# Mailtorrent
v. 1.1

Utility to control a transmission-daemon instance remotely, by sending emails to an email address.

It is possibile to:

* add new torrents, sending magnet links or torrent files links
  * "torrent" in the subject of the email and the links in the body
* receive the status of the downloads
  * "status" in the subject of the email
* start all the torrents if they are paused
  * "start" in the subject of the email
  
Emails must be sent from the email address specified in the config file.

Config file:

    [Config]
    download_path= #path of transmission-daemon watch dir   
    transmission_remote_path= #path of transmission-remote executable   
    email= #the address to send the email to that gets checked be the script   
    password= #password of the email address   
    destination_email= #email to send the status info to and from which commands are accepted   
    smtp_server= #address of smtp server of the script email   
    smtp_port= #address of smtp port of the script email   
    imap_server= #address of imap server of the script email  
    transmission_username= #transmission-daemon username
    transmission_password= #transmission-password username

The script is tested with python 2.7 and a GMail address.  
It runs on OS X and debian-based linux. It should work also on others linux flavours and on Windows, but I have not tested it.

Dependecies:  

* requests - http://docs.python-requests.org/en/latest/#

To launch the script:

`$ python mailtorrent.py /path/to/config/file`

It is useful to put it in the crontab and run it every 15 minutes or such.

Probably this is useful just to me, because my stupid router does not allow me to reach the pc with transmission-daemon I have at home from the outside (NAT does not work correctly for some reasons).
