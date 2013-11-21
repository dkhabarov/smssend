#!/usr/bin/env python
# -*- coding: utf8 -*-
# smssend - smssend is a program to send SMS messages from the commandline.

# Copyright © 2009-2012 by Denis Khabarov aka 'Saymon21'
# E-Mail: saymon at hub21 dot ru (saymon@hub21.ru)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, argparse
if sys.version_info[0] == 2:
	from urllib2 import urlopen, URLError
	from urllib import quote
if sys.version_info[0] == 3:
	from urllib.request import urlopen
	from urllib.error import URLError
	from urllib.parse import quote

from os import getenv
__author__ = "Denis 'Saymon21' Khabarov"
__copyright__ = "Copyright © 2012 Denis 'Saymon21' Khabarov"
__credits__ = []
__license__ = "GPLv3"
__version__ = "0.3"
__maintainer__ = "Denis 'Saymon21' Khabarov"
__email__ = "saymon@hub21.ru"
__status__ = "Development"

cliparser = argparse.ArgumentParser(
epilog='''Returned codes:\n0 - Message send successful\n1 - Service has retured error message\n2 - HTTP Error\n3 - Error for usage this tool\n
Default API ID are read from the files:\nLinux: $HOME/.smssendrc\nWindows: %USERPROFILE%/.smssendrc\n
Example usage:\necho "Hello world" | smssend --api-id=youapiid --to=target_phone_number''',
description='''smssend is a program to send SMS messages from the commandline.\nUsing API service http://sms.ru\nCopyright © 2009-2012 by Denis Khabarov aka 'Saymon21'\nE-Mail: saymon at hub21 dot ru (saymon@hub21.ru)''',
formatter_class=argparse.RawDescriptionHelpFormatter,prog="smssend",usage="%(prog)s --help")
cliparser.add_argument("--api-id",dest="api_id", metavar="VALUE", help="API ID (optional)")
cliparser.add_argument("--to", metavar="PHONENUMBER", help="Telephone number where send sms message (required)",required=True)
cliparser.add_argument("--message",metavar="MESSAGE", help="Read the message from message (a file) instead of stdin (optional)")
cliparser.add_argument("--from",dest="sendername",metavar="VALUE", help="Sender name (optional)")
cliparser.add_argument("--time",metavar="VALUE", help="Send time in UNIX TIME format (optional)")
cliparser.add_argument("--http_timeout",metavar="VALUE", help="Timeout for http connection (optional, default is 10)",default=10)
cliparser.add_argument('--translit',help='Convert message to translit',action='store_true')
cliparser.add_argument("--debug",help="Print debug messages",action="store_true")
cliargs = cliparser.parse_args()
servicecodes={
100:"Сообщение принято к отправке. На следующих строчках вы найдете идентификаторы отправленных сообщений в том же порядке, в котором вы указали номера, на которых совершалась отправка.",
200:"Неправильный api_id",
201:"Не хватает средств на лицевом счету",
202:"Неправильно указан получатель",
203:"Нет текста сообщения",
204:"Имя отправителя не согласовано с администрацией",
205:"Сообщение слишком длинное (превышает 8 СМС)",
206:"Будет превышен или уже превышен дневной лимит на отправку сообщений",
207:"На этот номер (или один из номеров) нельзя отправлять сообщения, либо указано более 100 номеров в списке получателей",
208:"Параметр time указан неправильно",
209:"Вы добавили этот номер (или один из номеров) в стоп-лист",
210:"Используется GET, где необходимо использовать POST",
211:"Метод не найден",
220:"Сервис временно недоступен, попробуйте чуть позже.",
300:"Неправильный token (возможно истек срок действия, либо ваш IP изменился)",
301:"Неправильный пароль, либо пользователь не найден",
302:"Пользователь авторизован, но аккаунт не подтвержден (пользователь не ввел код, присланный в регистрационной смс)",
}

def show_debug_messages(msg):
	if cliargs.debug == True:
		print(msg)

def get_home_path():
	if sys.platform.startswith('freebsd') or sys.platform.startswith('linux'):
		home=getenv('HOME')
	elif sys.platform.startswith('win'):
		home=getenv('USERPROFILE')
	if home is None:
		print("Unable to get home path.")
		sys.exit(3)
	else:
		return home
			
def get_api_id():
	if cliargs.api_id is None:
		try:
			fp=open("%s/.smssendrc" % (get_home_path()))
		except IOError as errstr:
			print(errstr)
			sys.exit(3)
		data=fp.read()
		if len(data) >= 10: # ????
			api_id=data
	else:
		api_id=cliargs.api_id

	return api_id.replace("\n","").replace("\r\n", "")

def get_msg():
	if cliargs.message is None:
		message=sys.stdin.read()
	elif cliargs.message is not None:
		message=cliargs.message
	return message

def main():
	api_id=get_api_id()
	if api_id is None:
		print("Error for get api-id. Check %s/.smssendrc or see --help" %(get_home_path()))
		sys.exit(3)
	
	url="http://sms.ru/sms/send?api_id=%s&to=%s&text=%s&partner_id=3805" %(api_id, cliargs.to, quote(get_msg()))
	if cliargs.debug==True:
		url="%s&test=1" % (url)
	elif cliargs.sendername is not None:
		url="%s&from=%s" % (url, cliargs.sendername)
	elif cliargs.time is not None:
		url="%s&time=%d" % (url, int(cliargs.time))
	elif cliargs.translit == True:
		url='%s&translit=1' % (url)
	
	try:
		res=urlopen(url,timeout=cliargs.http_timeout)
		show_debug_messages("GET: %s %s\nReply:\n%s" %(res.geturl(), res.msg ,res.info()))
	except URLError as errstr:
		show_debug_messages("smssend[debug]: %s" %(errstr))
		sys.exit(2)

	service_result=res.read().splitlines()
	if service_result is not None and int(service_result[0]) == 100:
		show_debug_messages("smssend[debug]: Message send ok. ID: %s" %(service_result[1]))
		sys.exit(0)
	if service_result is not None and int(service_result[0]) != 100:
		show_debug_messages("smssend[debug]: Unable send sms message to %s when service has returned code: %s "%(cliargs.to,servicecodes[int(service_result[0])]))
		sys.exit(1)

if __name__ == "__main__":
	main()

