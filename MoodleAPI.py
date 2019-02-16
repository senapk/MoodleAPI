from bs4 import BeautifulSoup
import mechanize
import json
import os
import configparser
import argparse
import sys

class MoodleAPI(object):
    def __init__(self, files, username, password, urlBase, course, section):
        self.files        = files
        self.username     = username
        self.password     = password
        self.urlBase      = urlBase
        self.course       = course
        self.section      = section
        self.urlCourse    = urlBase + "/course/view.php?id=" + course
        self.urlNewVpl    = urlBase + "/course/modedit.php?add=vpl&type=&course=" + course + "&section=" + section + "&return=0&sr=0"
        self.urlNewTest   = urlBase + "/mod/vpl/forms/testcasesfile.php?id=ID_QUESTAO&edit=3"
        self.urlTestSave  = urlBase + "/mod/vpl/forms/testcasesfile.json.php?id=ID_QUESTAO&action=save"
        self.vpls         = []
        self.browser      = mechanize.Browser()
        self.browser.set_handle_robots(False)
    def login(self):
        try:
            self.browser.select_form(action='https://moodle.quixada.ufc.br/login/index.php')
            self.browser['username'] = self.username
            self.browser['password'] = self.password
            self.browser.submit()
            print(self.browser.title())        
        except mechanize.FormNotFoundError as e:
            print("Usuário já logado!")
    def addVpl(self, vpl):
        self.browser.open(self.urlNewVpl)
        self.login()
        print("Enviando a questão %s para a seção %s" % (vpl.name, self.section))
        print(self.browser.title())

        self.browser.select_form(action='modedit.php')
        self.browser['name'] = vpl.name
        self.browser['shortdescription'] = vpl.shortdescription
        self.browser['introeditor[text]'] = vpl.description
        self.browser.submit()
        print(self.browser.title())

        self.getVplId(vpl)
        self.setTests(vpl)
    def getAll(self, saveActivities):
        self.browser.open(self.urlCourse)
        self.login()
        
        soup = BeautifulSoup(self.browser.response().read(), 'html.parser')
        topics = soup.find('ul', {'class:','topics'})
        childrens = topics.contents
        
        if saveActivities:
            arq = open('activities.txt', 'w', encoding='utf-8')
            sys.stdout = arq

        for section in childrens:
            id_section = section['id']
            desc_section = section['aria-label']
            print('%s - %s' % (id_section.replace('section-',''), desc_section))

            activities = soup.select('#' + id_section + ' > div.content > ul > li > div > div.mod-indent-outer > div > div.activityinstance > a')
            for activity in activities:
                id_activity = activity['href'].replace(self.urlBase + '/mod/vpl/view.php?id=','')
                print('\t %s - %s | %s' % (id_activity, activity.get_text(), activity['href']))

    def setTests(self,vpl):
        try:
            self.browser.open(self.urlNewTest.replace("ID_QUESTAO", vpl.id))
            print(self.browser.title())
            self.browser.open(self.urlTestSave.replace("ID_QUESTAO", vpl.id), 
                               data=self.__formatPayloadCaseTests(vpl.tests))
            
            print("Teste cadastrado com sucesso!!")
        except Exception as e:
            print(e)
    def loadFiles(self):
        try:
            files = self.files

            if os.path.isdir(self.files[0]):
                files = [os.path.join(self.files[0], f) for f in os.listdir(self.files[0])]

            for f in files:
                arq = open(f, 'r', encoding="utf-8")
                txt = arq.read().split("%%%")
                self.vpls.append(VPL(txt[0].strip(), txt[1].strip(), txt[2].strip(), txt[3].strip()))
                arq.close()
        except FileNotFoundError as e:
            print(e)       
    def getVplId(self, vpl):
        self.browser.open("https://moodle.quixada.ufc.br/course/view.php?id=344")
        self.login()
        for l in self.browser.links():
            if l.text.replace(" Laboratório Virtual de Programação","") == vpl.name:
                vpl.id = l.url.replace("https://moodle.quixada.ufc.br/mod/vpl/view.php?id=","")
                return vpl.id            
    def __formatPayloadCaseTests(self, tests):
        params = {'files':[
                    {'name':'vpl_evaluate.cases',
                     'contents': tests,
                     'encoding':0}
                    ],
                  'comments':''
                 }
        return json.dumps(params)
class VPL(object):
    def __init__(self, name, shortdescription, description, tests):
        self.id               = ""
        self.name             = name
        self.shortdescription = shortdescription
        self.description      = description
        self.tests            = tests
    def __str__(self):
        return "Id: %i\nDescrição: %s \nDescrição breve: %s \nDescrição: %s\nTestes: %s " % (self.id, self.name, self.shortdescription, self.description, self.tests)
    __repr__ = __str__

def main_add(args):
    api = MoodleAPI(args.questoes, args.apiData['login'], args.apiData['senha'], args.apiData['url'], args.apiData['curso'], args.section)
    api.loadFiles()
    for v in api.vpls:
        api.addVpl(v)

def main_list(args):
    api = MoodleAPI("", args.apiData['login'], args.apiData['senha'], args.apiData['url'], args.apiData['curso'], "")
    api.getAll(args.save)

def main():
    login = senha = url = curso = ""
    cfg = configparser.ConfigParser()
    cfg.read('config.ini')
    try:
        login = cfg['DEFAULT']['login']
        senha = cfg['DEFAULT']['senha']
        url   = cfg['DEFAULT']['url']
        curso = cfg['DEFAULT']['curso']
    except Exception as e:
        print(e)
        print("Crie um arquivo config.ini com\n[DEFAULT]\nlogin=seu_login\nsenha=sua_senha\nurl=url_moodle\ncurso=id_curso")

    desc = ("Gerenciar vpls do moodle de forma automatizada\n"
            "Use \"./MoodleAPI.py comando -h\" para obter informações do comando específico.\n\n"
            "Exemplos:\n"
            "    ./MoodleAPI.py add questao.txt -s 2   #Insere a questão contida em \"Questão.txt\" na seção 2 do curso informado no config.ini\n"
            "    ./MoodleAPI.py list                   #Lista todas as questões cadastradas no curso e seus respectivos ids\n"
            )

    parser = argparse.ArgumentParser(prog='MoodleAPI.py', description=desc, formatter_class=argparse.RawTextHelpFormatter)

    subparsers = parser.add_subparsers(title="subcommands", help = "help for subcommand")

    #add
    desc_add = ("Enviar questões para o moodle \n"
                "Ex.: ./MoodleAPI.py add questão.txt [questão.txt ...] [-s X]\n"
                "insere as questões na seção X\n"
                "-s para definir a seção\n"
                "questão.txt - arquivo ou diretório contendo as questões a serem enviadas (Ex.: https://github.com/brunocarvalho7/moodleAPI \n"
               )

    parser_add = subparsers.add_parser('add', help=desc_add)
    parser_add.add_argument('questoes', type=str, nargs='+', action='store', help='Pacote de questões')
    parser_add.add_argument('-s', '--section', metavar='COD_SECTION', default='1', type=str, action='store', help="Código da seção onde a questão será inserida")
    parser_add.set_defaults(apiData=cfg.defaults(), func=main_add)

    #list
    parser_list = subparsers.add_parser('list', help='Lista todas as questões cadastradas no curso e seus respectivos ids')
    parser_list.add_argument('-s', '--save', action="store_true", help="Salvar a lista de atividades em um arquivo")
    parser_list.set_defaults(apiData=cfg.defaults(), func=main_list)

    args = parser.parse_args()

    global term_width
    try:
        term_width = shutil.get_terminal_size()[0]
    except:
        pass
    if(len(sys.argv) > 1):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()