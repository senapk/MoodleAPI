
# MoodleAPI
Api de publicação automática de vpl's no moodle

É necessário primeiro baixar a biblioteca [Mechanize](https://github.com/python-mechanize/mechanize)

    pip install mechanize

E tambem a biblioteca [Beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

	pip install beautifulsoup4
 
 Depois é necessário configurar as seguintes variáveis(linha 80) 

 -  O caminho da pasta que contém as questões a serem publicadas no moodle. Esse arquivo deverá conter 4 seções e um **%%%**  separando cada sessão. Necessariamente na seguinte ordem:
	
		Título da questão
	    %%%
	    Descrição curta
	    %%%
	    Descrição da questão
	    %%%
	    Casos de teste
		---
		NOME_ARQUIVO_01
		CONTEUDO_ARQUIVO_01
		---
		NOME_ARQUIVO_02
		CONTEUDO_ARQUIVO_02
		---
		NOME_ARQUIVO_N
		CONTEUDO_ARQUIVO_N
- Seu usuário do moodle
- Sua senha do moodle
- Modificar o editor padrão do moodle para *Área de texto simples* **(Meu Perfi > Modificar Perfil > Preferências > editor de texto)**

Uma vez configurado, basta executar o arquivo MoodleAPI.py
