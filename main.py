from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
import sys
import json
import os
from flashcardui import FlashcardMenu


class FlashCardApp(QMainWindow, FlashcardMenu):
    def __init__(self):
        super(FlashCardApp, self).__init__()
        self.setupUi(self)

        self.FONTSIZEWORD = 40
        self.FONTSIZEDEF = 12
        self.terms = {}
        self.words = []
        self.currentWord = ''
        self.showingDefinition = False
        self.index = 0
        self.path = ''
        self.getFilesItem = None
        self.selected = ''

        self.displayField.setReadOnly(True)
        self.displayField.setAlignment(QtCore.Qt.AlignCenter)
        self.addWordButton.clicked.connect(self.addWord)
        self.nextButton.clicked.connect(self.nextWord)
        self.prevButton.clicked.connect(self.previousWord)
        self.flipButton.clicked.connect(self.flipCard)
        self.actionLoad.triggered.connect(self.loadFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.removeWordButton.clicked.connect(self.removeCurrentWord)
        self.setFilDirButton.clicked.connect(self.setFileDir)
        self.loadSelectedButton.clicked.connect(self.loadCurrent)
        self.saveSelectedButton.clicked.connect(self.saveCurrent)
        self.show()

    def addWord(self):
        word = self.wordNameInputField.text()
        definition = self.definitionInputField.toPlainText()
        if word and definition:
            self.terms[word] = definition
            self.words = list(self.terms.keys())
            print(f"Added Word: {word}")
            self.updateUI()
            self.clearField()

    def flipCard(self):
        if self.words:
            self.showingDefinition = not self.showingDefinition
            if self.showingDefinition:
                self.displayField.setFontPointSize(12)
            elif not self.showingDefinition:
                self.displayField.setFontPointSize(40)
            self.updateUI()

    def previousWord(self):
        if self.words:
            if self.showingDefinition:
                self.flipCard()
            if self.index > 0:
                self.index -= 1
            else:
                self.index = len(self.words) - 1   
            print(self.index, self.words, self.currentWord)
            self.currentWord = self.words[self.index]
            print(self.currentWord)
            self.updateUI()

    def nextWord(self):
        if self.words:
            if self.showingDefinition:
                self.flipCard()            
            if self.index < len(self.words) - 1:
                self.index += 1
            else:
                self.index = 0
            print(self.index, self.currentWord, self.words)
            self.currentWord = self.words[self.index]
            print(self.currentWord)
            self.updateUI()


    def updateUI(self):
        print(f"Updating UI - Index: {self.index}, Current Word: {self.currentWord}, Showing Definition: {self.showingDefinition}")
        if self.currentWord:
            if self.words == []:
                self.currentWord = ''
                self.displayField.setText('')

            if self.showingDefinition:
            # Use get method to handle the case where the key is not present
                definition = self.terms.get(self.currentWord, "Definition not available")
                self.displayField.setText(definition)
            else:
                self.displayField.setText(self.currentWord)

            if self.displayField.toPlainText().strip() == '' and self.words != []:
                self.index = 0
                self.currentWord = self.words[self.index]

    
    def saveFile(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Flashcards', '', 'JSON Files (*.json);;All Files (*)')
        if file_path:
            with open(file_path, 'w') as file:
                json.dump({'terms': self.terms}, file)
            print(f"Flashcards saved to {file_path}")
        self.getFiles()

    def loadFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Load Flashcards', '', 'JSON Files (*.json);;All Files (*)')
        
        if file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.terms = data.get('terms', {})
                self.words = list(self.terms.keys())
                self.index = 0
            if self.words:  # Check if there are words before setting currentWord
                self.currentWord = self.words[self.index]
            else:
                self.currentWord = ''

            self.displayField.setText('')
            self.updateUI()


    def clearField(self):
        if self.wordNameInputField.text() != '':
            self.wordNameInputField.setText('')
        if self.definitionInputField.toPlainText() != '':
            self.definitionInputField.setText('')
            
    def getFiles(self):
        if self.path:
            self.setListWidget.clear()
            files = os.listdir(str(self.path))
            for file in files:
                currentFile = os.path.splitext(file)
                if currentFile[1] == '.json':
                    self.getFilesItem = QtWidgets.QListWidgetItem()
                    self.getFilesItem.setText(currentFile[0] + currentFile[1])
                    self.setListWidget.addItem(self.getFilesItem)

    def setFileDir(self):
        file_path = QFileDialog.getExistingDirectory(self, 'Set Path')
        self.path = file_path
        print(self.path)
        self.getFiles()

    def loadCurrent(self):
        if self.path:
            selectedItem = self.setListWidget.currentItem()
            if selectedItem:
                print(self.terms, self.words)
                self.selected = selectedItem.text()
                file = self.path + '/' + str(self.selected)
                with open(file, 'r') as f:
                    data = json.load(f)
                    self.terms = data.get('terms', {})
                    self.words = list(self.terms.keys())
                    self.index = 0
                    self.currentWord = ''
                    print(self.terms, self.words)
            if self.words:  # Check if there are words before setting currentWord
                self.currentWord = self.words[self.index]
            else:
                self.currentWord = ''

            self.displayField.setText('')
            self.updateUI()
    
    def saveCurrent(self):
         if self.terms != {}:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save Flashcards', '', 'JSON Files (*.json);;All Files (*)')
            if file_path:
                with open(file_path, 'w') as file:
                    json.dump({'terms': self.terms}, file)
                print(f"Flashcards saved to {file_path}")
                self.getFiles()
         else:
            if self.path:
                selectedItem = self.setListWidget.currentItem()
                if selectedItem:
                    print(self.terms, self.words)
                    self.selected = selectedItem.text()
                    file = self.path + '/' + self.selected
                    with open(file, 'w') as f:
                        json.dump({'terms': self.terms}, f)
                        print(f"Flashcards saved to {file}")
                        self.getFiles()
       
    def removeCurrentWord(self):
        if self.currentWord:
            self.terms.pop(self.currentWord, None)
            self.words = list(self.terms.keys())
            if self.index >= len(self.words):
                self.index = len(self.words) - 1
            if self.index >= 0:
                self.currentWord = self.words[self.index]
            else:
                self.currentWord = ''
            self.updateUI()

app = QApplication(sys.argv)
FlashCardUI = FlashCardApp()
app.exec_()