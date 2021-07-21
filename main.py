import configparser
from os import makedirs
import PySimpleGUI as sg
from datetime import date
import time
from pathlib import Path

from PySimpleGUI.PySimpleGUI import theme
# https://docs.python.org/3/library/configparser.html#quick-start
# https://pysimplegui.readthedocs.io/en/latest/

if __name__ == "__main__":

    # Innitialize Variables
    chosenChar = ""
    homeFolderPath = str(Path.home())
    charFolderPath = homeFolderPath + "\\CharData"
    try:
        makedirs(charFolderPath)
    except:
        pass
    thisDate = date.today()
    thisDate = thisDate.strftime("%d/%m/%Y")

    def convertThemes(Theme):
        # Get chosen Theme, and translate it to official name
        if Theme == "Dark Amber":
            return "DarkAmber"
        elif Theme == "Dark Red":
            return "DarkRed2"
        elif Theme == "Gray Blue":
            return "DarkBlue12"
        elif Theme == "Black Red":
            return "DarkBrown4"
        elif Theme == "Light Green":
            return "LightGreen7"
        elif Theme == "Light Purple":
            return "LightPurple"
        else:
            return "GrayGrayGray"

    def newChar(GUITheme="GrayGrayGray"): # Add a new Character
        print("Creating new Character...")

        # Create GUI
        ogThemeList = ["DarkAmber","DarkRed2","DarkBlue12","DarkBrown4","LightGreen7","LightPurple","GrayGrayGray"]
        myThemeList = ["Dark Amber","Dark Red","Gray Blue","Black Red","Light Green","Light Purple","Default Gray"]
        sg.theme(GUITheme)
        layout = [
            [sg.Text('Enter the Name of the new Character:')],
            [sg.InputText(key='input_name')],
            [sg.Text('Choose a Theme:')],
            [sg.Combo(myThemeList, readonly=True, enable_events=True, key='chosenTheme'), sg.Button('Preview Theme', key="Preview")],
            [sg.Button('Continue'), sg.Exit()]
        ]
        window = sg.Window('Average Roll Calculator', layout)
        
        # Save Character and return the Character's name
        while True:
            event, values = window.Read()
            if event is None or event == 'Exit':
                window.Close()
                return ""

            if event == 'Preview':
                # Get chosen Theme, and translate it to official name
                sg.theme(convertThemes(values["chosenTheme"]))
                sg.popup_no_wait('Here is your Theme preview!', 'You can continue by clicking the Ok Button.')
                sg.theme("GrayGrayGray")

            if event == 'Continue':
                newCharacterName = values["input_name"]
                if newCharacterName != "" and values["chosenTheme"] != "":
                    # Add name to CharacterList.ini
                    config = configparser.ConfigParser()
                    listINI = charFolderPath + "\\CharacterList.ini"
                    config[newCharacterName] = {'created': thisDate,
                                                'theme': convertThemes(values["chosenTheme"]),}
                    with open(listINI, 'a') as configfile:
                        config.write(configfile)
                    print("Created new Character!")
                    return newCharacterName
                elif newCharacterName == "":
                    sg.popup_no_wait("Please choose your Character's Name!")
                    pass
                elif values["chosenTheme"] == "":
                    sg.popup_no_wait('Please choose a Theme!', 'You can Preview them with the "Preview Theme" button.')
                    pass
        
    def chooseChar(GUITheme="GrayGrayGray"): # Starting Menu to; Select a Character, or add a new One
        choices = ["Add new Character"]

        # Get all characters
        config = configparser.ConfigParser()
        listINI = charFolderPath + "\\CharacterList.ini"
        config.read(listINI)

        # Add all characters to List of choices
        for name in config.sections():
            choices.append(name)

        # Creating Combobox
        sg.theme(GUITheme)
        layout = [
            [sg.Text('Select your Character, or add a new one')],
            [sg.Combo(choices, readonly=True, enable_events=True, key='charcombo')],
            [sg.Button('Continue'), sg.Exit()]
        ]
        window = sg.Window('Average Roll Calculator', layout)

        # Check if new Character has to be added
        characterName = ""
        while True:
            event, values = window.Read()

            if event is None or event == 'Exit':
                return "Exit"

            if event == 'Continue':
                characterName = values['charcombo']
                characterName = str(characterName)
                if characterName == "Add new Character":
                    window.Close()
                    characterName = newChar()
                elif characterName == "": # No character selected
                    pass
                else:
                    break

        window.Close()
        return characterName
    
    def createMainGUI(chosenChar, GUITheme="GrayGrayGray"): # Work with the selected Character
        sg.theme(GUITheme)
        diceList = ["d4","d6","d8","d10","d12","d20","d100"]
        layout = [
            [sg.Text('Loaded Character:', size=(13, 2)), sg.Text(str(chosenChar), size=(30, 2))],
            [sg.Text('Dice:', size=(6, 1)), sg.Text('Enter what you Rolled:', size=(16, 1)), sg.Text('Enter your modifier:', size=(16, 1))],
            [sg.Combo(diceList, readonly=True, enable_events=True, key='chosenDice', size=(5, 1)), sg.InputText(key='input_roll', size=(19, 1)), sg.InputText(key='input_modifier', size=(19, 1))],
            [sg.Button('Add'), sg.Exit()]
        ]
        window = sg.Window('Average Roll Calculator', layout)

        while True:
            event, values = window.Read()
            if event is None or event == 'Exit':
                break

            if event == "Add":
                #Check to see if everything is filled
                if values["chosenDice"] != "" and values["input_roll"] != "" and values["input_modifier"] != "":
                    # Check if everything is formatted in the right way
                    rollFormat = "0123456789"
                    modFormat = "0123456789+-"
                    rollCheck = all(c in rollFormat for c in values["input_roll"])
                    modCheck = all(c in modFormat for c in values["input_modifier"])
                    if rollCheck == False or modCheck == False:
                        sg.popup_no_wait('Average Roll Calculator', 'Wrong Format!', 'Please only use Digits and +/- for your modifiers')
                    else:
                        # See if modifier has +/-, if not add a +
                        if values["input_modifier"] != "*+" and values["input_modifier"] != "*-":
                            modifier = "+" + values["input_modifier"]

                        # Add to charname.ini
                        print(chosenChar)
                        config = configparser.ConfigParser()
                        charrollsini = charFolderPath + "\\" +  chosenChar + ".ini"
                        config[str(int(time.time()))] = {'dice': values["chosenDice"],
                                                    'rolled': values["input_roll"],
                                                    'modifier': modifier}
                        with open(charrollsini, 'a') as configfile:
                            config.write(configfile)
                        sg.popup_no_wait('Average Roll Calculator', 'Successfully added your roll!')
                else:
                    sg.popup_no_wait('Average Roll Calculator', 'Please fill in all the Fields before adding!')

                if event == 'input_roll' and values['input_roll'] and values['input_roll'][-1] not in ('0123456789'):
                    window['input_roll'].update(values['input_roll'][:-1])
                
                if event == 'input_modifier' and values['input_modifier'] and values['input_modifier'][-1] not in ('0123456789+-'):
                    window['input_modifier'].update(values['input_modifier'][:-1])

        window.Close()

    class main:
        while chosenChar == "":
            chosenChar = chooseChar()
        if chosenChar == "Exit":
            exit()
        #Load Chosen Character
        config = configparser.ConfigParser()
        listINI = charFolderPath + "\\CharacterList.ini"
        config.read(listINI)
        GUITheme = config[chosenChar]["theme"]
        print("Loaded: " + chosenChar)
        createMainGUI(chosenChar, GUITheme)