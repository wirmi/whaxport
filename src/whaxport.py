# import curses # pip install windows-curses
import os, sqlite3, configparser
from window import *

# Configparser
config = configparser.RawConfigParser()
config.read("./cfg/settings.cfg")

# Global vars
# Cuenta los archivos que se están copiando
contador = 0

# Cuenta los archivos que no existen en el origen
contadorNoExist = 0

ifNull = "Sin nombre"



def GetCheckVars():
	return contacts


def ResetProgram():
	global contador, contadorNoExist, exportFolder

	contador = 0
	contadorNoExist = 0
	
	ConnectDatabases()
	exportFolder = config.get('paths', 'exportFolder')

	ResetTkinter(contacts)

# Program functions

def NotFoundExit(string):
	print(f"\nCheck '{string}' variable in .\\cfg\\settings.cfg file.")
	quit()

def CheckPaths():
	global waFile
	waFile = True

	dataFolder = config.get('paths', 'dataFolder')
	if(not os.path.exists(dataFolder)):
		print("\nData folder not found.")
		NotFoundExit("dataFolder")

	exportFolder = config.get('paths', 'exportFolder') #+ nameSearch + "\\"

	if(not os.path.exists(exportFolder)):
		createFolder = ""
		while(createFolder != "y" and createFolder != "yes" and createFolder != "n" and createFolder != "no"):
			print("\nExport folder does not exist.")
			createFolder = input("Do you want to create it? (y)es | (n)o: ").lower()
			if(createFolder == "n" or createFolder == "no"):
				NotFoundExit("exportFolder")


	database = config.get('paths', 'msgstore')
	if(not os.path.exists(database)):
		print("\nDatabase file not found.")
		NotFoundExit("msgstore")

	if(config.has_option('paths', 'wa')):
		contactsDatabase = config.get('paths', 'wa')
		if(not os.path.exists(contactsDatabase)):
			option = ""
			while(option != "y" and option != "yes" and option != "n" and option != "no"):
				print("\nContacts database file not found.")
				option = input("Do you want to continue without the name of some contacts? (y)es | (n)o: ").lower()
				if(option == "n" or option == "no"):
					NotFoundExit("wa")

			waFile = False
	else:
		option = ""
		while(option != "y" and option != "yes" and option != "n" and option != "no"):
			print("\nContacts database file not set in .\\cfg\\settings.cfg file.")
			option = input("Do you want to continue without the name of some contacts? (y)es | (n)o: ").lower()
			if(option == "n" or option == "no"):
				NotFoundExit("wa")

		waFile = False
		contactsDatabase = ''

	return dataFolder, exportFolder, database, contactsDatabase

def ConnectDatabases():
	global msgstore

	msgstore = sqlite3.connect(database)
	msgstore = msgstore.cursor()

	if(waFile):
		msgstore.execute(f'ATTACH DATABASE "{contactsDatabase}" as wa')

def CloseDatabase():
	msgstore.close()


def GetContacts():
	contacts = []
	ids = []

	if(waFile):
		for row in msgstore.execute(f'select ifnull(wa.display_name, "{ifNull}"), wa.jid, chat._id from wa.wa_contacts as wa\
										inner join jid on wa.jid = jid.raw_string\
										INNER JOIN chat on jid._id = chat.jid_row_id\
										INNER JOIN message_media on chat._id = message_media.chat_row_id\
										group by message_media.chat_row_id\
										order by wa.display_name nulls last'):
			contacts.append(str(row[0]) + " - " + str(row[1].split("-")[0].split("@")[0]))
			ids.append(row[2])

	else:
		for row in msgstore.execute(f'select ifnull(chat.subject, "{ifNull}"), jid.raw_string, chat._id from chat\
										INNER JOIN jid on chat.jid_row_id = jid._id\
										INNER JOIN message_media on chat._id = message_media.chat_row_id\
										where jid.raw_string != "status@broadcast"\
										group by message_media.chat_row_id\
										order by chat.subject nulls last;'):
			contacts.append(str(row[0]) + " - " + str(row[1].split("-")[0].split("@")[0]))
			ids.append(row[2])

	return contacts, ids


def Select(event):
	global exportFolder
	selected, root = GetSelectVars()
	
	if(selected != ''):
		root.withdraw()
		exportFolder += "\\" + selected + "\\"

		CopyFromName(selected)

		option = ""
		while(option != "y" and option != "yes" and option != "n" and option != "no"):
			option = input("\n\nDo you want to copy another contact? (y)es | (n)o: ").lower()
			if(option == "n" or option == "no"):
				quit()

		ResetProgram()
		
	else:
		print("No has seleccionado ningún contacto.")



def CopyFromName(selected):

	_id = ids[contacts.index(selected)]

	print("\nCopiando archivos...\n")
	StartCopy(_id)
	CloseDatabase()

	if(contador != 0):
		CopyDatabases()

	print(contadorNoExist, "archivos no se encontraron en el origen.")
	print(contador, "archivos copiados con éxito en " + os.path.abspath(exportFolder) + ".")

	if(contador == 0):
		print("\nComprueba la ruta dataFolder en el archivo .\\cfg\\settings.cfg")



def StartCopy(_id):
	global contador, contadorNoExist
	for row in msgstore.execute(f'SELECT file_path FROM message_media where chat_row_id={_id}'):
		# print(str(contador) + " - " + str(row[0]))
		sourceFile = (dataFolder + str(row[0])).replace('/', '\\')
		destinationFile = (exportFolder + str(row[0])).replace('/', '\\')
		if(os.path.exists(sourceFile)):
			destinationFolder = destinationFile.rsplit("\\", 1)[0] + "\\"
			if(not os.path.exists(destinationFolder)):
				os.makedirs(destinationFolder)

			copy = ('if not exist "' + destinationFile + '" copy "' + sourceFile + '" "' + destinationFile + '" > NUL')
			os.system(copy)
			contador += 1
		else:
			contadorNoExist += 1



def CopyDatabases():
	destinationFolder = exportFolder + "Databases\\"
	basenameDatabase = database.rsplit("\\", 1)[1]
	
	if(not os.path.exists(destinationFolder)):
		os.mkdir(destinationFolder)

	os.system('if not exist "' + destinationFolder + basenameDatabase + '" copy "' + database + '" "' + destinationFolder + '" > NUL')
	
	if(waFile):
		basenameContacts = contactsDatabase.rsplit("\\", 1)[1]
		os.system('if not exist "' + destinationFolder + basenameContacts + '" copy "' + contactsDatabase + '" "' + destinationFolder + '" > NUL')







if __name__ == "__main__":
	global contacts

	dataFolder, exportFolder, database, contactsDatabase = CheckPaths()

	ConnectDatabases()

	contacts, ids = GetContacts()

	CreateWindow()
	Update(contacts)
	Loop()