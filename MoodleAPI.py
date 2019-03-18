'''
TODO: REALIZAR O RM DE QUESTÕES POR ID[MOODLEAPI.py rm 22862]
        https://moodle.quixada.ufc.br/course/mod.php?delete=22266&confirm=1
        https://moodle.quixada.ufc.br/course/mod.php?sesskey=psSlekP7ko&sr=0&delete=22266&confirm=1
TODO: DOWNLOAD -> INCLUIR TODOS OS ARQUIVOS DE TMP NO TXT
TODO: ADD/UPDATE -> INSERIR A CONFIGURAÇÃO DE DATA DE LIMITE DA QUESTÃO
TODO: UPDATE -> CORRIGIR BUG DOS CASOS DE TESTES NÃO ESTAREM SENDO ENVIADOS
TODO: REMOVER TODAS AS URLS ESTÁTICAS DO CÓDIGO E CENTRALIZA-LAS NA CLASSE MOODLEAPI
TODO: INCLUIR EXCEPTIONS
'''
from bs4 import BeautifulSoup
import mechanize
import json
import os
import configparser
import argparse
import sys
import zipfile
import shutil

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
        self.urlFilesSave = urlBase + '/mod/vpl/forms/executionfiles.json.php?id=22862&action=save'
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
    def download(self):
        self.browser.open(self.urlNewVpl)
        self.login()
        soup = BeautifulSoup(self.browser.response().read(), 'html.parser')

        arq = open('teste.txt', 'w')
        sys.stdout = arq 
        #fields = soup.select('form input,textarea,select')
        fields = soup.select('form input')

        params = {}

        for f in fields:
            #params[f['name']] = f['value']
            print(f)
            print(f.attrs)
            if 'value' in f.attrs.keys():
                print(f['value'])
            else:
                print("Don't have")

        print(params)
        arq.close()


        '''self.browser.open(self.urlCourse)
        self.login()
        
        soup = BeautifulSoup(self.browser.response().read(), 'html.parser')
        topics = soup.find('ul', {'class:','topics'})
        childrens = topics.contents

        if (not os.path.exists('vpls')):
            os.mkdir('vpls')
        
        for section in childrens[1:]:
            id_section = section['id']
            desc_section = section['aria-label']
            print('%s - %s' % (id_section.replace('section-',''), desc_section))

            activities = soup.select('#' + id_section + ' > div.content > ul > li > div > div.mod-indent-outer > div > div.activityinstance > a')
            for activity in activities:
                name_folder = 'vpls/'+id_section.replace('section-','') + ' - ' + desc_section 
                if (not os.path.exists(name_folder)):
                    os.mkdir(name_folder)

                id_activity = activity['href'].replace(self.urlBase + '/mod/vpl/view.php?id=','')
                
                self.browser.open("https://moodle.quixada.ufc.br/course/modedit.php?update="+id_activity)
                soupActivity       = BeautifulSoup(self.browser.response().read(), 'html.parser')
                name_activity      = soupActivity.select_one("#id_name")['value']
                desc_activity      = soupActivity.select_one("#id_introeditor").get_text()
                descShort_activity = soupActivity.select_one("#id_shortdescription").get_text()

                print('Realizando o download da atividade %s' % name_activity)

                self.browser.open("https://moodle.quixada.ufc.br/mod/vpl/views/downloadexecutionfiles.php?id="+id_activity)
                arq = open('teste.zip', 'wb')
                arq.write(self.browser.response().read())
                arq.close()

                arq_zip = zipfile.ZipFile('teste.zip')
                arq_zip.extractall('tmp/')
                arq_zip.close()

                arq_cases = open('tmp/vpl_evaluate.cases','r')
                #nameTxt = name_folder+'/'+name_activity.+' @ '+id_activity+'.txt'
                nameTxt = name_folder+'/'+id_activity+'.txt'
                arq_activity = open(nameTxt,'w',encoding="utf-8")

                arq_activity.write(name_activity+'\n%%%\n')
                arq_activity.write(descShort_activity+'\n%%%\n')
                arq_activity.write(desc_activity+'\n%%%\n')
                arq_activity.write(arq_cases.read())
                arq_activity.close()
                arq_cases.close()

                shutil.rmtree('tmp', ignore_errors=True)
        '''               
    def update(self, id_questao, vpl):
        self.browser.open('https://moodle.quixada.ufc.br/course/modedit.php?update='+id_questao)
        self.login()
        print("Atualizando a questão %s" % (vpl.name))

        self.browser.select_form(action='modedit.php')
        self.browser['name'] = vpl.name
        self.browser['shortdescription'] = vpl.shortdescription
        self.browser['introeditor[text]'] = vpl.description
        self.browser.submit()
        print(self.browser.title())

        params = {'files':vpl.executionFiles,
                  'comments':''}
        files = json.dumps(params, default=self.__dumper, indent=2)

        self.browser.open(self.urlFilesSave, 
                               data=files)
            
        print("Questão atualizada com sucesso!!")    
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
                executionFiles = []

                arq = open(f, 'r', encoding="utf-8")
                txt = arq.read().split("%%%")
                lastLine = txt[len(txt) - 1]
                indexExecutionFiles = lastLine.find('---\n')
    
                if(indexExecutionFiles > 0):
                    sub = lastLine[indexExecutionFiles + 4:] #Remover o primeiro ---\n
                    execFiles = ''.join(sub).split('---\n')
                    lastLine = lastLine[:indexExecutionFiles]
                    executionFiles = [ExecutionFile(l) for l in execFiles]
    
                self.vpls.append(VPL(txt[0].strip(), txt[1].strip(), txt[2].strip(), lastLine.strip(), executionFiles))
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
    def __dumper(self, obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__
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
    def __init__(self, name, shortdescription, description, tests, executionFiles):
        self.id               = ""
        self.name             = name
        self.shortdescription = shortdescription
        self.description      = description
        self.tests            = tests
        self.executionFiles   = executionFiles
    def __str__(self):
        return "Id: %s\nDescrição: %s \nDescrição breve: %s \nDescrição: %s\nTestes: %s\nExecutionFiles: %s " % (self.id, self.name, self.shortdescription, self.description, self.tests, self.ExecutionFiles)
    __repr__ = __str__
    
class ExecutionFile(object):
    def __init__(self, strFile):
        self.name     = ''
        self.contents = '',
        self.encoding = 0
        self.__loadFile(strFile)
    def __loadFile(self, strFile):
        aux = strFile.split('\n')
        self.name     = aux[0]
        self.contents = '\n'.join(aux[1:]).strip()
    def __str__(self):
        return "{'Name': '%s','Contents': '%s','Encoding': %d}" % (self.name, self.contents, self.encoding)
    __repr__ = __str__
def main_add(args):
    api = MoodleAPI(args.questoes, args.apiData['login'], args.apiData['senha'], args.apiData['url'], args.apiData['curso'], args.section)
    api.loadFiles()
    for v in api.vpls:
        api.addVpl(v)
def main_list(args):
    api = MoodleAPI("", args.apiData['login'], args.apiData['senha'], args.apiData['url'], args.apiData['curso'], "")
    api.getAll(args.save)
def main_download(args):
    api = MoodleAPI("", args.apiData['login'], args.apiData['senha'], args.apiData['url'], args.apiData['curso'], "")
    api.download()
def main_update(args):
    api = MoodleAPI(args.questoes, args.apiData['login'], args.apiData['senha'], args.apiData['url'], args.apiData['curso'], "")
    api.loadFiles()
    for v in api.vpls:        
        api.update(args.id_questao, v)
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

    #download
    parser_download = subparsers.add_parser('download', help="Realiza o download das atividades do moodle")
    parser_download.set_defaults(apiData=cfg.defaults(), func=main_download)

    #update
    parser_update = subparsers.add_parser('update', help="Realiza o update de atividades do moodle")
    parser_update.add_argument('id_questao', type=str, action='store', help='Id da questão a ser atualizada')
    parser_update.add_argument('questoes', type=str, nargs='+', action='store', help='Pacote de questões')
    parser_update.set_defaults(apiData=cfg.defaults(), func=main_update)

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