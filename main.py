import configparser
from os import makedirs
import PySimpleGUI as sg
from datetime import date
import time
from pathlib import Path
import statistics

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
            return "Default1"

    def newChar(GUITheme="Default1"): # Add a new Character
        print("Creating new Character...")

        # Create GUI
        ogThemeList = ["DarkAmber","DarkRed2","DarkBlue12","DarkBrown4","LightGreen7","LightPurple","Default1"]
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
                sg.popup_ok('Here is your Theme preview!', 'You can continue by clicking the Ok Button.')
                sg.theme("Default1")

            if event == 'Continue':
                newCharacterName = values["input_name"]
                if newCharacterName != "" and values["chosenTheme"] != "":
                    if newCharacterName == "Exit" or newCharacterName == "CharData" or newCharacterName == "CharacterList":
                        sg.popup_error("Invalid Character Name!", "Please input another Name.")
                    elif all(x.isalpha() or x.isspace() or x.isdecimal() for x in newCharacterName):
                        # Add name to CharacterList.ini
                        config = configparser.ConfigParser()
                        listINI = charFolderPath + "\\CharacterList.ini"
                        config[newCharacterName] = {'created': thisDate,
                                                    'theme': convertThemes(values["chosenTheme"]),}
                        with open(listINI, 'a') as configfile:
                            config.write(configfile)
                        print("Created new Character!")
                        window.Close()
                        return newCharacterName
                    else:
                        sg.popup_error("Invalid Name!", "Please don't use any special Characters.")
                elif newCharacterName == "":
                    sg.popup_error("Please choose your Character's Name!")
                    pass
                elif values["chosenTheme"] == "":
                    sg.popup_error('Please choose a Theme!', 'You can Preview them with the "Preview Theme" button.')
                    pass
        
    def chooseChar(GUITheme="Default1"): # Starting Menu to; Select a Character, or add a new One
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
                exit()

            if event == 'Continue':
                characterName = values['charcombo']
                characterName = str(characterName)
                if characterName == "Add new Character":
                    window.Hide()
                    characterName = ""
                    characterName = newChar()
                    choices += [characterName]
                    window.Element("charcombo").Update(values=choices)
                    window.UnHide()
                elif characterName == "": # No character selected
                    pass
                else:
                    window.Hide()
                    #Load chosen Character
                    config = configparser.ConfigParser()
                    listINI = charFolderPath + "\\CharacterList.ini"
                    config.read(listINI)
                    GUITheme = config[characterName]["theme"]
                    print("Loaded: " + characterName)
                    createMainGUI(characterName, GUITheme)
                    window.UnHide()
    
    def createMainGUI(chosenChar, GUITheme="Default1"): # Work with the selected Character
        sg.theme(GUITheme)
        diceList = ["d4","d6","d8","d10","d12","d20","d100"]
        layout = [
            [sg.Text('Loaded Character:', size=(13, 2)), sg.Text(str(chosenChar), size=(30, 2))],
            [sg.Text('Dice:', size=(6, 1)), sg.Text('Enter what you Rolled:', size=(16, 1)), sg.Text('Enter your modifier:', size=(16, 1))],
            [sg.Combo(diceList, readonly=True, enable_events=True, key='chosenDice', size=(5, 1)), sg.InputText(key='input_roll', size=(19, 1)), sg.Combo(["+","-"], readonly=True, key='chosenModifier', size=(2,1)), sg.InputText(key='input_modifier', size=(19, 1))],
            [sg.Button('Add'), sg.Button('Show Rolls'), sg.Exit()]
        ]
        window = sg.Window('Average Roll Calculator', layout)

        while True:
            event, values = window.Read()
            if event is None or event == 'Exit':
                break

            if event == "Show Rolls":
                window.Hide()
                showRollsGUI(chosenChar, GUITheme)
                window.UnHide()

            if event == "Add":
                #Check to see if everything is filled
                if values["chosenDice"] != "" and values["input_roll"] != "" and values["input_modifier"] != "" and values["chosenModifier"] != "":
                    # Check if everything is formatted in the right way
                    if str(values["input_roll"]).isdigit() and str(values["input_modifier"]).isdigit():
                        if int(values["input_roll"]) <= int((values["chosenDice"])[1:]):
                            modifier = values["chosenModifier"] + values["input_modifier"]
                            # Add to charname.ini
                            print(chosenChar)
                            config = configparser.ConfigParser()
                            charrollsini = charFolderPath + "\\" +  chosenChar + ".ini"
                            config[str(int(time.time()))] = {'dice': values["chosenDice"],
                                                        'rolled': values["input_roll"],
                                                        'modifier': modifier}
                            with open(charrollsini, 'a') as configfile:
                                config.write(configfile)
                            sg.popup_ok('Average Roll Calculator', 'Successfully added your roll!')
                        else:
                            sg.popup_error('Average Roll Calculator', 'Rolled higher than possible!')
                    else:
                        sg.popup_error('Average Roll Calculator', 'Wrong Format!', 'Please only input Digits!')
                else:
                    sg.popup_error('Average Roll Calculator', 'Please fill in all the Fields before adding!')

                if event == 'input_roll' and values['input_roll'] and values['input_roll'][-1] not in ('0123456789'):
                    window['input_roll'].update(values['input_roll'][:-1])
                
                if event == 'input_modifier' and values['input_modifier'] and values['input_modifier'][-1] not in ('0123456789+-'):
                    window['input_modifier'].update(values['input_modifier'][:-1])

        window.Close()

    def showRollsGUI(chosenChar, GUITheme="Default1"):
        # Create GUI
        sg.theme(GUITheme)
        diceList = ["d4","d6","d8","d10","d12","d20","d100"]
        layout = [
            [sg.Text('Loaded Character:', size=(13, 2)), sg.Text(str(chosenChar), size=(14, 2))],
            [sg.Text('Choosen Dice:', size=(13, 1)), sg.Combo(diceList, readonly=True, enable_events=True, key='chosenDice', size=(5, 1))],
            [sg.Text('Average Rolled:', size=(13, 1)), sg.Text('', key='averageWithout', size=(5, 1))],
            [sg.Text('With modifiers:', size=(13, 1)), sg.Text('', key='averageWit', size=(5, 1))],
            [sg.Text("Table of all Rolls with chosen dice: ", size=(30, 1))],
            [sg.Listbox(values=[], key='rollList', size=(30, 6))],
            [sg.Exit()]
        ]
        window = sg.Window('Average Roll Calculator', layout)

        while True:
            event, values = window.Read()
            if event is None or event == 'Exit':
                window.close()
                break

            if event == "chosenDice":
                #Load chosen Characters rolls-file
                config = configparser.ConfigParser()
                charrollsini = charFolderPath + "\\" +  chosenChar + ".ini"
                config.read(charrollsini)
                #Read data with DiceRoll
                print("Reading Data of: " + chosenChar)
                newlist = []
                averageWithout = []
                averageWith = []
                for each_section in config.sections():
                    rollData = config.items(each_section)
                    if rollData[0][1] == values["chosenDice"]:
                        customString = str(rollData[1][1]) + " " + str(rollData[2][1])
                        newlist += [customString]
                        averageWithout += [int(rollData[1][1])]
                        if "+" in rollData[2][1]:
                            averageWith += [(int(rollData[1][1]) + int((rollData[2][1])[1:]))]
                        else:
                            averageWith += [(int(rollData[1][1]) - int((rollData[2][1])[1:]))]
                #Show all Rolls
                window.Element('rollList').Update(values=newlist)
                #Show averages
                if averageWithout != []:
                    window.Element('averageWithout').Update(str(round(statistics.mean(averageWithout), 2)))
                    window.Element('averageWit').Update(str(round(statistics.mean(averageWith), 2)))

    class main:
        chooseChar()