# -*- coding: mbcs -*-

import requests
from bs4 import BeautifulSoup as bs
import time
import json
from utils import c_logging, n_logging
from termcolor import colored, cprint
from getpass import getpass

login_url = "https://ssl.education.lu/saml/module.php/discopower/disco.php?entityID=https%3A%2F%2Fssl.education.lu%2Fsaml%2Fmodule.php%2Fsaml%2Fsp%2Fmetadata.php%2Fdisco&return=https%3A%2F%2Fssl.education.lu%2Fsaml%2Fmodule.php%2Fsaml%2Fsp%2Fdiscoresp.php%3FAuthID%3D_024ae1618cc35755a50cdb4e2aa77bf935aef071a3%253Ahttps%253A%252F%252Fssl.education.lu%252Fsaml%252Fsaml2%252Fidp%252FSSOService.php%253Fspentityid%253Dwebuntis.antiope%2526cookieTime%253D1537873681&returnIDParam=idpentityid&idpentityid=https%3A%2F%2Fssl.education.lu%2Fsamlidp%2Fsaml2%2Fidp%2Fmetadata.php"
session = requests.Session()
session.max_redirects = 999
headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
			}
c_logging(" - Username: ",'green');username=input()
password=getpass(" - Password: ")

#Lecon
#----------------

		
###############################################################################################################################

def get_IAM_link():
	global session
	global IAM_page
	get_jsession_cookie = session.get('https://antiope.webuntis.com/WebUntis/?school=LTB#/basic/main')
	re = session.get(login_url,headers = headers)
	#first_link = re.headers.get("Location")
	IAM_link = bs(re.text,"html.parser")
	link_section = IAM_link.find("div",{"class":"metalist"})
	link_pt1 = "https://ssl.education.lu/saml/module.php/discopower/disco.php"+link_section.find("a").get("href")
	#print ("https://ssl.education.lu/saml/module.php/discopower/disco.php{}".format(link_pt1))
	#print("-------------------------")
	IAM_page = session.get(link_pt1, headers = headers)
	#return first_link

###############################################################################################################################

def get_auth():
	global session
	global IAM_page
	global auth_state_value

	auth_state_search = bs(IAM_page.text,"html.parser")
	auth_state_value = auth_state_search.find("input",{"name":"AuthState"}).get("value")
	#print(auth_state_value)

###############################################################################################################################

def login():
	global session
	global auth_state_value
	global SAMLResponse1
	global SAML

	login_post_url = "https://ssl.education.lu/samlidp/module.php/IAM/loginuserpass.php?"
	payload = {
				"username": username,
				"password": password,
				"AuthState":auth_state_value
				}
	login = session.post(login_post_url,headers = headers, data = payload)
	#print(login.text)

	#VERIFY if login was sucessfull!

	verify = bs(login.text,"html.parser")
	if "Nom d'utilisateur ou mot de passe incorrect" in login.text:
		c_logging(" - Erreur: Nom d'utilisateur ou mot de passe incorrect ",'red')
		sys.exit()
	else:
		c_logging(" - Connexion reussie avec succes (session: {})".format(username),'green')
	#print(login.text)
	#print(error_text)
	SAML = bs(login.text,"html.parser")
	SAMLResponse1 = SAML.find("input",{"name":"SAMLResponse"}).get("value")

###############################################################################################################################

def java1():
	global session
	global SAML
	endpoint1 = "https://ssl.education.lu/saml/module.php/saml/sp/saml2-acs.php/disco"
	
	payload = {
				"SAMLResponse":SAMLResponse1
				}
	post1 = session.post(endpoint1,headers = headers,data = payload)
	text = bs(post1.text,"html.parser")

###############################################################################################################################

	endpoint2 = "https://antiope.webuntis.com/WebUntis/saml/SSO/alias/defaultAlias"
	
	special_headers = {
						"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
						"Accept-Encoding": "gzip, deflate, br",
						"Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
						"Cache-Control": "max-age=0",
						"Connection": "keep-alive",
						"Content-Type": "application/x-www-form-urlencoded",
						"Host": "antiope.webuntis.com",
						"Origin": "https://ssl.education.lu",
						"Upgrade-Insecure-Requests": "1",
						"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
	}

	SAMLResponse2 = text.find("input",{"name":"SAMLResponse"}).get("value")

	payload = {
				"SAMLResponse":SAMLResponse2
				}
	post2 = session.post(endpoint2,headers = special_headers,data = payload,allow_redirects = False)
	get = session.get('https://antiope.webuntis.com/WebUntis/index.do')
	#get = session.get("https://antiope.webuntis.com/WebUntis/index.do#/basic/main",headers = headers)
	#print(get.text)

###############################################################################################################################

def api_devoirs():
	global session
	date = int(time.strftime('%Y%m%d'))
	date_formated = time.strftime('%d/%m/%Y')
	if date == '':
		sys.exit("Date invalide")
	devoirs_url = 'https://antiope.webuntis.com/WebUntis/api/homeworks/lessons?startDate={}&endDate={}'.format(date,date+7)
	get_devoirs = session.get(devoirs_url)
	json_decode = json.loads(get_devoirs.text)
	data = json_decode['data']
	homeworks = data['homeworks']
	cprint("""  _____                  _          
 |  __ \                (_)         
 | |  | | _____   _____  _ _ __ ___ 
 | |  | |/ _ \ \ / / _ \| | '__/ __|
 | |__| |  __/\ V / (_) | | |  \__ \
 
 |_____/ \___| \_/ \___/|_|_|  |___/
                                    
                                    
Nous sommes le {}""".format(date_formated),'magenta')
	print('-----------------------------------------------------------')
	for i in homeworks:
		cprint(i['text'],'cyan')
		#FORMAT DE LA DATE: 20181217 p.ex
		date = i['dueDate']
		int_date = int(date)
		day = abs(date) % 100
		first = int(date / 1000)%10
		second = int(date / 100)%10
		first_month_digit= str(first) #retourne 1er chiffre du mois
		second_month_digit= str(second) #retourne 2e chiffre du mois
		month = first_month_digit+second_month_digit
		year = str(time.strftime('%Y'))
		if month == '01':
			month ='janvier'
		if month == '02':
			month ='fevrier'
		if month == '03':
			month ='mars'
		if month == '04':
			month ='avril'
		if month == '05':
			month ='mai'
		if month == '06':
			month ='juin'
		if month == '07':
			month ='juillet'
		if month == '08':
			month ='aout'
		if month == '09':
			month ='septembre'
		if month == '10':
			month ='octobre'
		if month == '11':
			month ='novembre'
		if month == '12':
			month ='decembre'
		
		cprint('A faire pour le: {} {} {}'.format(day,month,year),'cyan')
		# cprint(i['date'],'cyan')
		if i['lessonId']==22184:
			Lecon = 'MATHS'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22276:
			Lecon = 'TPCHIMIE'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==21956:
			Lecon = 'CHIMIE'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22214:
			Lecon = 'PHYSIQUE'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22153:
			Lecon = 'INFORMATIQUE'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22254:
			Lecon = 'TPELEKTRO'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22095:
			Lecon = 'FRANCAIS'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22224:
			Lecon = 'TECNO'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22227:
			Lecon = 'TECNO'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22260:
			Lecon = 'TPPHYSIQUE'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==21973:
			Lecon = 'CONMO'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==21911:
			Lecon = 'ANGLAIS'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22076:
			Lecon = 'ELEKTROTECHNIK'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22045:
			Lecon = 'EDUPH'
			cprint("Lecon: {}".format(Lecon),"green")
		if i['lessonId']==22206:
			Lecon = 'MECANIQUE'
			cprint("Lecon: {}".format(Lecon),"green")
		print('------')






c_logging(" - Started ",'green')
get_IAM_link()
get_auth()
login()
java1()
api_devoirs()
#open_browser()
#java2()

#"Cookie": "sessionSAMLPROXY={};ROUTEIDiam=.a".format(session.cookies["sessionSAMLPROXY"]),
