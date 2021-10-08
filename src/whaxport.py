# import curses # pip install windows-curses
import os, sqlite3, configparser
from tkinter import *
# from tkinter import filedialog


# Configparser
config = configparser.RawConfigParser()
config.read("./cfg/settings.cfg")

# Global vars
# Cuenta los archivos que se están copiando
contador = 0

# Cuenta los archivos que no existen en el origen
contadorNoExist = 0


# Tkinter
selected = ''


# Tkinter functions

def ResetProgram():
	global selected, contador, contadorNoExist, exportFolder

	contador = 0
	contadorNoExist = 0
	selected = ''
	entry.delete(0, END)
	entry.focus_set()
	Update(rawContacts)
	ConnectDatabases()
	exportFolder = config.get('paths', 'exportFolder')
	root.deiconify()

def CreateWindow():
	global root, label, entry, listbox, button

	root = Tk()
	root.title('Título de ventana')
	root.iconbitmap('icon.ico')
	root.geometry('315x340') # Window size
	# root.minsize(315, 340)
	root.resizable(0, 0) # x and y max resize size

	# Creating widgets

	label = Label(root, text="Start Typing...",
		font=("Helvetica", 14), fg="grey")

	label.pack(pady=20)

	entry = Entry(root, font=("Helvetica", 20))
	entry.focus_set()
	entry.pack()

	listbox = Listbox(root, selectmode="BROWSE", width=50)
	listbox.pack(pady=20)


	button = Button(root, text="Pulsa")
	button.pack()

	# Events
	listbox.bind("<<ListboxSelect>>", Fillout)
	listbox.bind('<Double-Button>', Select)
	entry.bind("<KeyRelease>", Check)
	button.bind("<Button-1>", Select)
	button.bind("<Return>", Select)

def Update(data):
	listbox.delete(0, END)

	for item in data:
		listbox.insert(END, item)

def Fillout(event):
	global selected

	w = event.widget

	selected = w.get(ANCHOR)

def Check(event):
	global selected

	typed = entry.get()
	# selected = listbox.get(ANCHOR)
	found = False

	if(typed == ''):
		newContacts = contacts
	else:
		newContacts = []
		for item in contacts:
			if(typed.lower() in item.lower()):
				newContacts.append(item)
				if(selected == item):
					found = True

	Update(newContacts)
	
	if(found or typed == '' and selected != ''):
		
		selectedIndex = newContacts.index(selected)
		listbox.selection_set(selectedIndex)
			
		listbox.see(selectedIndex)
	else:
		listbox.selection_clear(0)
		selected = ''



def Select(event):
	global exportFolder

	if(selected != ''):
		root.withdraw()
		# root.destroy()
		exportFolder += "\\" + selected + "\\"
		jid = rawContacts[contacts.index(selected)][1]
		CopyFromName(jid)
		option = input("\n\nDo you want to copy another contact? (y)es | (n)o: ").lower()
		if(option == "n" or option == "no"):
			quit()

		while(option != "y" and option != "yes" and option != "n" and option != "no"):
			option = input("\n\nDo you want to copy another contact? (y)es | (n)o: ").lower()
			if(option == "n" or option == "no"):
				quit()

		ResetProgram()
		
	else:
		print("No has seleccionado ningún contacto")


# Program functions

def NotFoundExit(string):
	print("\nCheck '{}' variable in .\\cfg\\settings.cfg file.".format(string))
	quit()

def CheckPaths():
	global notWa
	notWa = False

	dataFolder = config.get('paths', 'dataFolder')
	if(not os.path.exists(dataFolder)):
		print("\nData folder not found.")
		NotFoundExit("dataFolder")

	exportFolder = config.get('paths', 'exportFolder') #+ nameSearch + "\\"

	if(not os.path.exists(exportFolder)):
		print("\nExport folder does not exist.")
		createFolder = input("Do you want to create it? (y)es | (n)o: ").lower()
		if(createFolder == "n" or createFolder == "no"):
			NotFoundExit("exportFolder")

		while(createFolder != "y" and createFolder != "yes" and createFolder != "n" and createFolder != "no"):
			print("\nExport folder does not exist.")
			createFolder = input("Do you want to create it? (y)es | (n)o: ").lower()
			if(createFolder == "n" or createFolder == "no"):
				NotFoundExit("exportFolder")


	database = config.get('paths', 'msgstore')
	if(not os.path.exists(database)):
		print("\nDatabase file not found.")
		NotFoundExit("msgstore")

	contactsDatabase = config.get('paths', 'wa')
	if(not os.path.exists(contactsDatabase)):
		print("\nContacts database file not found.")
		option = input("Do you want to continue without the name of the contacts? (y)es | (n)o: ").lower()
		if(option == "n" or option == "no"):
			NotFoundExit("wa")

		while(option != "y" and option != "yes" and option != "n" and option != "no"):
			print("\nContacts database file not found.")
			option = input("Do you want to continue without the name of the contacts? (y)es | (n)o: ").lower()
			if(option == "n" or option == "no"):
				NotFoundExit("wa")
		notWa = True

	return dataFolder, exportFolder, database, contactsDatabase

def ConnectDatabases():
	global wa, msgstore

	wa = sqlite3.connect(contactsDatabase)
	wa = wa.cursor()

	msgstore = sqlite3.connect(database)
	msgstore = msgstore.cursor()

def CloseDatabases():
	wa.close()
	msgstore.close()

def GetContacts():
	rawContacts = []
	contacts = []

	wa.execute('SELECT display_name, jid FROM wa_contacts order by display_name')
	for row in wa.execute('SELECT display_name, jid FROM wa_contacts order by display_name'):
		rawContacts.append(row)
		contacts.append(str(row[0]) + " - " + str(row[1].split("-")[0].split("@")[0]))

	return rawContacts, contacts



# Get the jid (mobile phone number id) from a name
# def GetJid():
# 	wa.execute('SELECT display_name, jid FROM wa_contacts where display_name="{}"'.format(nameSearch))
# 	wa_contacts_jid = wa.fetchall()

# 	if(len(wa_contacts_jid) > 0):
# 		wa_contacts_jid = wa_contacts_jid[0]
# 	else:
# 		print("No se encontró el usuario '" + nameSearch + "'")
# 		quit()

# 	return wa_contacts_jid

def CopyFromName(jid):
	# wa_contacts_jid = GetJid()
	# print(str(wa_contacts_jid[0]) + " | " + str(wa_contacts_jid[1]))
	# jid = wa_contacts_jid[1]

	jid__id = GetJidRowId(jid)
	print(str(jid__id[0]) + " | " + str(jid__id[1]) + " | " + str(jid__id[2]))
	jidRowId = jid__id[1]

	chat__id = GetId(jidRowId)
	print(str(chat__id[0]) + " | " + str(chat__id[1]))
	_id = chat__id[0]

	print("\nCopiando archivos...\n")
	StartCopy(_id)
	CloseDatabases()

	if(contador != 0):
		CopyDatabases()

	print(contadorNoExist, "archivos no se encontraron en el origen.")
	print(contador, "archivos copiados con éxito en " + os.path.abspath(exportFolder) + ".")

	if(contador == 0):
		print("\nComprueba la ruta dataFolder en el archivo .\\cfg\\settings.cfg")


def GetJidRowId(jid):
	msgstore.execute('SELECT user, _id, raw_string FROM jid where raw_string="{}"'.format(jid))
	jid__id = msgstore.fetchall()[0]

	return jid__id


def GetId(jidRowId):
	msgstore.execute('SELECT _id, jid_row_id FROM chat where jid_row_id={}'.format(jidRowId))
	chat__id = msgstore.fetchall()[0]

	return chat__id

def StartCopy(_id):
	global contador, contadorNoExist
	for row in msgstore.execute('SELECT file_path FROM message_media where chat_row_id={}'.format(_id)):
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
	basenameContacts = contactsDatabase.rsplit("\\", 1)[1]
	if(not os.path.exists(destinationFolder)):
		os.mkdir(destinationFolder)

	os.system('if not exist "' + destinationFolder + basenameDatabase + '" copy "' + database + '" "' + destinationFolder + '" > NUL')
	os.system('if not exist "' + destinationFolder + basenameContacts + '" copy "' + contactsDatabase + '" "' + destinationFolder + '" > NUL')







if __name__ == "__main__":
	# nameSearch = input("Escribe el nombre del contacto: ")
	# print()
	# root.deiconify()

	dataFolder, exportFolder, database, contactsDatabase = CheckPaths()

	ConnectDatabases()

	if(notWa):
		quit()
	else:
		rawContacts, contacts = GetContacts()

	CreateWindow()

	Update(contacts)

	root.mainloop()