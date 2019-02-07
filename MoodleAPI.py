import mechanize
import json
import os

class MoodleAPI(object):
    def __init__(self, localPath, username, password):
        self.localPath    = localPath
        self.username     = username
        self.password     = password
        self.urlNewVpl    = "https://moodle.quixada.ufc.br/course/modedit.php?add=vpl&type=&course=344&section=1&return=0&sr=0"
        self.urlNewTest   = "https://moodle.quixada.ufc.br/mod/vpl/forms/testcasesfile.php?id=ID_QUESTAO&edit=3"
        self.urlTestSave  = "https://moodle.quixada.ufc.br/mod/vpl/forms/testcasesfile.json.php?id=ID_QUESTAO&action=save"
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
        print("Enviando a questão %s" % vpl.name)
        print(self.browser.title())

        self.browser.select_form(action='modedit.php')
        self.browser['name'] = vpl.name
        self.browser['shortdescription'] = vpl.shortdescription
        self.browser['introeditor[text]'] = vpl.description
        self.browser.submit()
        print(self.browser.title())

        self.getVplId(vpl)
        self.setTests(vpl)
    def setTests(self,vpl):
        try:
            self.browser.open(self.urlNewTest.replace("ID_QUESTAO", vpl.id))
            #self.login()
            print(self.browser.title())
            self.browser.open(self.urlTestSave.replace("ID_QUESTAO", vpl.id), 
                               data=self.__formatPayloadCaseTests(vpl.tests))
            
            print("Teste cadastrado com sucesso!!")
        except Exception as e:
            print(e)
    def loadFiles(self):
        files = [os.path.join(self.localPath, f) for f in os.listdir(self.localPath)]

        for f in files:
            arq = open(f, 'r', encoding="utf-8")
            txt = arq.read().split("%%%")
            self.vpls.append(VPL(txt[0].strip(), txt[1].strip(), txt[2].strip(), txt[3].strip()))
            arq.close()       
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

if __name__ == "__main__":
    api = MoodleAPI("PASTA COM AS QUESTÕES","usuario","senha")
    api.loadFiles()
    for v in api.vpls:
        api.addVpl(v)