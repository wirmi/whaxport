# from functools import partial # pass arguments on tkinter bind
from tkinter import *
import __main__ as main
# from tkinter import filedialog

# Tkinter
selected = ''

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
	listbox.bind('<Double-Button>', main.Select)
	entry.bind("<KeyRelease>", main.Check)
	button.bind("<Button-1>", main.Select)
	button.bind("<Return>", main.Select)


def GetSelectVars():
	return selected, root

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
	contacts = main.GetCheckVars()

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

def ResetTkinter(data):
	global selected

	selected = ''
	entry.delete(0, END)
	entry.focus_set()
	Update(data)
	root.deiconify()

def Loop():
	root.mainloop()