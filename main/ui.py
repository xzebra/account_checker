import argparse
import cmd
import shlex
import sqlite3
import requests
from lxml import html
import time
import random
from os import system,path,getcwd
from subprocess import check_output
from re import search
from tabulate import tabulate
from main.handlers import color,funcSQL

class Console(cmd.Cmd):
    def __init__(self,db_path):
        cmd.Cmd.__init__(self)
        self.prompt = color.setcolor(':: ', color='Orange')
        self.con    = sqlite3.connect(db_path)
        self.db     = self.con.cursor()
        self.db.execute(funcSQL.sqlite.createTables)
        self.settings   = {'all' :{},'check' :[],'agents':{}}
        self.search_all_agents()
        self.s = requests.Session()

    def login(self, user, password):
		color.display_messages('Trying to login as %s...' % (user), info=True)
		self.s.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
							'ig_vw': '1920', 'csrftoken': '',
							's_network': '', 'ds_user_id': ''})
		self.login_post = {'username': user, 'password': password}
		self.s.headers.update({'Accept-Encoding': 'gzip, deflate',
						'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
						'Connection': 'keep-alive',
						'Content-Length': '0',
						'Host': 'www.instagram.com',
						'Origin': 'https://www.instagram.com',
						'Referer': 'https://www.instagram.com/',
						'User-Agent': ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"),
						'X-Instagram-AJAX': '1',
						'X-Requested-With': 'XMLHttpRequest'})
		r = self.s.get(self.url)
		self.s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
		time.sleep(5 * random.random())
		login = self.s.post(self.url_login, data=self.login_post, allow_redirects=True)
		self.s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
		self.csrftoken = login.cookies['csrftoken']
		time.sleep(5 * random.random())

		if login.status_code == 200:
			r = self.s.get('http://www.instagram.com')
			finder = r.text.find(user)
			if finder != -1:
				return 2;
			else:
				return 1;
		else:
			return 0;  	

    def logout(self):
        self.s.get(self.url_logout)

    def do_list(self,args):
        """ list/check/filter list agents on database """
        arg_parser = argparse.ArgumentParser(prog='list',description='interact with one/all agents')
        arg_parser.add_argument('-i', '--id', dest='id',type=int,metavar='<id>', help='list agent  by id')
        arg_parser.add_argument('-c', '--check',dest='check', action='store_true', help='check credentials by agent Available')
        arg_parser.add_argument('-d', '--db',dest='database', action='store_true', help='list all agents on database')
        try:
            args=arg_parser.parse_args(shlex.split(args))
        except: return
        self.settings['all'] = {}
        self.listbotsprint = []
        for agent in self.db.execute(funcSQL.sqlite.selectAllBots):self.settings['all'][agent[0]] = agent
        if self.settings['all'] == {}:
            return color.display_messages('No Agents registered',info=True)
        if args.database:
            if args.id and not args.check:
                if not args.id in self.settings['all'].keys():
                    return color.display_messages('ID not registered',info=True)
                color.display_messages('Agents:', info=True, sublime=True)
                agent = list(self.settings['all'][args.id])
                self.listbotsprint += list([agent])
                print tabulate(self.listbotsprint, headers=funcSQL.sqlite.headers)

            elif args.check and args.id:
                if not args.id in self.settings['all'].keys():
                    return color.display_messages('ID not registered', info=True)
                color.display_messages('Agents:', info=True, sublime=True)
                agent = list(self.settings['all'][args.id])
                self.listbotsprint += list([agent])
                print tabulate(self.listbotsprint, headers=funcSQL.sqlite.headers)


            elif args.database and not args.check:
                color.display_messages('Agents:', info=True, sublime=True)
                for bots in self.settings['all'].items():self.listbotsprint += list([bots[1]])
                print tabulate(self.listbotsprint, headers=funcSQL.sqlite.headers)
                return color.linefeed()

            elif args.database and not args.id:
                for agent in self.settings['all'].items():
                    agent = list(agent[1])
                    if self.login(agent[1], agent[2]) == 1:
                        funcSQL.DB_updateStatus(self.con, self.db, agent[0], 'On')
                        self.listbotsprint += list([agent])
                    else:
                        funcSQL.DB_updateStatus(self.con, self.db, agent[0], 'Off')
                color.display_messages('Agents:', info=True, sublime=True)
                print tabulate(self.listbotsprint, headers=funcSQL.sqlite.headersCheck)
                color.linefeed()
        else:
            arg_parser.print_help()


    def search_all_agents(self):
        for agent in self.db.execute(funcSQL.sqlite.selectAllBots):self.settings['all'][agent[0]] = agent

    def search_on_agents(self):
        for agent in self.db.execute(funcSQL.sqlite.selectAllBots):
            if not agent[0] in self.settings['agents'].keys():
                self.settings['agents'][agent[0]] = {'creds':{}}
                self.settings['agents'][agent[0]]['creds']['ID']   = agent[0]
                self.settings['agents'][agent[0]]['creds']['User'] = agent[1]
                self.settings['agents'][agent[0]]['creds']['Pass'] = agent[2]
                self.settings['agents'][agent[0]]['creds']['Status'] = agent[3]

    def do_register(self,args):
        """ add bot on database """
        arg_parser = argparse.ArgumentParser(prog='register',description='add bot on database clients')
        arg_parser.add_argument('--user', dest='user',metavar='<Username>', help='login username')
        arg_parser.add_argument('--pass', dest='password',metavar='<Password>', help='login password')
        arg_parser.add_argument('-f', '--file', dest='file',metavar='<filepath>', help='imports clients from a file')
        try:
            args=arg_parser.parse_args(shlex.split(args))
        except: return
        if args.user and args.password:
        	num = self.login(args.user, args.password)


		if num == 0:
			color.display_messages('Login error! Connection error!', error=True)
		elif num == 1:
			color.display_messages('Login error! Check your login data!', error=True)
		elif num == 2:
			color.display_messages('Insert Data: SQL statement will insert a new row', info=True)
			funcSQL.DB_insert(self.con, self.db, args.user, args.password)
			color.display_messages('Bot credentials added with success', sucess=True)

        elif args.file:
            self.all_bot_checked = []
            color.display_messages('Searching for: {} ...'.format(path.realpath(args.file)),info=True)
            if path.exists(args.file):
                self.lines_all_read = [line.rstrip('\n') for line in open(path.realpath(args.file),'r')]
                for items in self.lines_all_read:
                    if len(items.split()) == 2:
                        self.all_bot_checked.append(items)
                if len(self.all_bot_checked) == 0:
                    color.display_messages('Instruction for -f argumments:',info=True,sublime=True)
                    print('You need to use the separator character [space] in this format below\n')
                    print('-----cut here -------\n')
                    print('root:~# cat example.txt\n')
                    print('demo P@ssW0rd')
                    print('Z3br4 botP@ssW0rd')
                    print('\n-----cut here -------\n')
                    print('')
                    return None
                self.ListBot = []
                color.display_messages('All agents imported from file:', info=True,sublime=True)
                for agent in self.all_bot_checked: self.ListBot += list([agent.split()])
                color.linefeed()
                choise = raw_input('{}{}[*]{} Do you want to import?(S/N):'.format(color.colors.BOLD, color.colors.BLUE,color.colors.ENDC,))
                if choise.lower() == 's':
                    color.display_messages('Importing agents...', info=True, sublime=True)
                    for agent in self.all_bot_checked: 
						num = self.login(agent.split()[0], agent.split()[1])
						if num == 0:
							color.display_messages('Login error! Connection error!\n', error=True)
						elif num == 1:
							color.display_messages('Login error! Check your login data!\n', error=True)
						elif num == 2:
							color.display_messages('Insert Data: SQL statement will insert a new row', info=True)
							funcSQL.DB_insert(self.con, self.db, agent.split()[0],agent.split()[1])
							color.display_messages('Bot ' + agent.split()[0] + '@' + agent.split()[1] + ' added with success\n', sucess=True)
            else:
                color.display_messages('File could not be found', error=True)
        else:
            arg_parser.print_help()

    def do_del(self,args):
        """ delete bot using <id>/all """
        arg_parser = argparse.ArgumentParser(prog='del', description='delete a registered bot')
        arg_parser.add_argument('-i', '--id', dest='id', metavar='<id>',type=int, help='delete bot by ID')
        arg_parser.add_argument('-a', '--all',dest='all', action='store_true', help='delete all bots registered')
        try:
            args=arg_parser.parse_args(shlex.split(args))
        except: return
        if args.id:
            self.search_all_agents()
            if not args.id in self.settings['all'].keys():
                color.display_messages('ID not found', info=True)
                return
            items =  self.settings['all'][args.id]
            color.display_messages('Found ID:', sublime=True, info=True)
            color.display_messages('Search query for finding a particular id', info=True)
            color.display_messages('Section DELETE FROM statement.', info=True)
            color.display_messages('ID:{} User:{} Password:{})'.format(items[0], items[1], items[2]), info=True)
            funcSQL.deleteID(self.con, self.db, args.id)
            if funcSQL.lengthDB(self.db) < 1:
                self.db.execute(funcSQL.sqlite.zeraids)
                self.con.commit()
        elif args.all:
            self.db.execute(funcSQL.sqlite.delete_all)
            self.db.execute(funcSQL.sqlite.createTables)
            color.display_messages('All data has been removed.',info=True)
            self.con.commit()
        else:
            arg_parser.print_help()


    def do_help(self,args):
        """ show this help """
        names = self.get_names()
        cmds_doc = []
        names.sort()
        pname = ''
        color.display_messages('Available Commands:', info=True, sublime=True)
        for name in names:
            if name[:3] == 'do_':
                pname = name
                cmd   = name[3:]
                if getattr(self, name).__doc__:
                    cmds_doc.append((cmd, getattr(self, name).__doc__))
                else:
                    cmds_doc.append((cmd, ""))

        self.stdout.write('    {}	 {}\n'.format('Commands', 'Description'))
        self.stdout.write('    {}	 {}\n'.format('--------', '-----------'))
        for command,doc in cmds_doc:
            self.stdout.write('    {:<10}	{}\n'.format(command, doc))
        color.linefeed()

    def do_clear(self,args):
        """ clears the window """
        system('clear')

    def default(self, args):pass
    def emptyline(self):pass

    def do_exit(self, args):
        """ exit the program"""
        print "Quitting."
        raise SystemExit