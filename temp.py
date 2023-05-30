import PySimpleGUI as sg

# Custom theme for a more appealing GUI
sg.theme('DarkAmber')

# Event handler for the "Select All" button
def select_all():
    for i in range(10):
        window[f'checkbox_{i}'].update(True)

# Event handler for the "Deselect All" button
def deselect_all():
    for i in range(10):
        window[f'checkbox_{i}'].update(False)

# Define the layout of the GUI
layout = [
    [sg.Text("Folder 1: "), sg.Input(key='folder_path_1'), sg.FolderBrowse(button_text='Fetch Folder 1', key='button_1')],
    [sg.Text("Folder 2: "), sg.Input(key='folder_path_2'), sg.FolderBrowse(button_text='Fetch Folder 2', key='button_2')],
    [sg.Button('Select All'), sg.Button('Deselect All')],
    [sg.Text('Fruits:', font='Helvetica 12 bold')]
]

fruits = ['apple', 'banana']

# Add fruit labels with icons to the layout
for i, fruit in enumerate(fruits):
    icon = f'{fruit}.png'  # Assuming you have fruit icons in a folder named "icons"
    full_size_icon = sg.Image(icon, size=(64, 64))
    layout.append([sg.Image(icon, size=(32, 32), tooltip=full_size_icon), sg.Text(fruit, key=f'fruit_{i}', font='Helvetica 12'), sg.Checkbox('', key=f'checkbox_{i}')])

layout.append([sg.Button('Submit', size=(10, 1), font='Helvetica 12')])

# Create the GUI window with title
window = sg.Window('Android Forensics', layout)

# Event loop to process events and get the values from the GUI elements
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'button_1':
        folder_path = sg.popup_get_folder("Select a folder")
        if folder_path:
            window['folder_path_1'].update(folder_path)
    elif event == 'button_2':
        folder_path = sg.popup_get_folder("Select a folder")
        if folder_path:
            window['folder_path_2'].update(folder_path)
    elif event == 'Select All':
        select_all()
    elif event == 'Deselect All':
        deselect_all()
    elif event == 'Submit':
        folder_path_1 = values['folder_path_1']
        folder_path_2 = values['folder_path_2']
        selected_fruits = [fruits[i] for i in range(10) if values[f'checkbox_{i}']]
        sg.popup(f"Folder 1: {folder_path_1}\nFolder 2: {folder_path_2}\nSelected Fruits: {selected_fruits}")

# Close the GUI window
window.close()
