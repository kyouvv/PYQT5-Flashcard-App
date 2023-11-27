from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QListWidgetItem
import sys
import json
import os
from flashcardui import FlashcardMenu


class FlashCardApp(QMainWindow, FlashcardMenu):
    def __init__(self):
        super(FlashCardApp, self).__init__()
        self.setupUi(self)

        self.terms = {}
        self.words = []
        self.currentWord = ''
        self.showingDefinition = False
        self.index = 0
        self.path = ''
        self.getFilesItem = None
        self.selected = ''
        self.loadedFile = False

        self.displayField.setReadOnly(True)
        self.displayField.setAlignment(QtCore.Qt.AlignCenter)
        self.addWordButton.clicked.connect(self.addWord)
        self.nextButton.clicked.connect((lambda: self.moveWord(1)))
        self.prevButton.clicked.connect((lambda: self.moveWord(-1)))
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
            self.updateUI()

    def flipCard(self):
        if self.words:
            self.showingDefinition = not self.showingDefinition
            if self.showingDefinition:
                self.displayField.setFontPointSize(12)
            elif not self.showingDefinition:
                self.displayField.setFontPointSize(40)
            self.updateUI()

    def moveWord(self, direction):
        if self.words:
            if self.showingDefinition:
                self.flipCard()

            total_words = len(self.words)
            self.index = (self.index + direction) % total_words
            self.currentWord = self.words[self.index]
            self.updateUI()


    def updateUI(self):
        if not self.words:
            self.currentWord = ''
            self.displayField.setText('')

        if self.currentWord:

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
        self.getFiles()

    def loadFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Load Flashcards', '', 'JSON Files (*.json);;All Files (*)')
        
        if file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.terms = data.get('terms', {})
                self.words = list(self.terms.keys())
                self.index = 0
                self.loadedFile = True
            if self.words:  # Check if there are words before setting currentWord
                self.currentWord = self.words[self.index]
            else:
                self.currentWord = ''

            self.displayField.setText('')
            self.updateUI()
            
    def getFiles(self):
        if self.path:
            self.setListWidget.clear()
            files = os.listdir(str(self.path))
            for file in files:
                currentFile = os.path.splitext(file)
                if currentFile[1] == '.json':
                    self.getFilesItem = QListWidgetItem()
                    self.getFilesItem.setText(currentFile[0] + currentFile[1])
                    self.setListWidget.addItem(self.getFilesItem)

    def setFileDir(self):
        file_path = QFileDialog.getExistingDirectory(self, 'Set Path')
        self.path = file_path
        self.getFiles()

    def loadCurrent(self):
        if self.path:
            self.selected = self.setListWidget.currentItem()
            if self.selected:
                file_name = self.selected.text()
                file = self.path + '/' + str(file_name)
                with open(file, 'r') as f:
                    data = json.load(f)
                    self.terms = data.get('terms', {})
                    self.words = list(self.terms.keys())
                    self.index = 0
                    self.currentWord = ''
                    self.loadedFile = True
            if self.words:  # Check if there are words before setting currentWord
                self.currentWord = self.words[self.index]
            else:
                self.currentWord = ''

            self.displayField.setText('')
            self.updateUI()
    
    def saveCurrent(self):
         if self.terms != {} and self.loadedFile == False:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save Flashcards', '', 'JSON Files (*.json);;All Files (*)')
            if file_path:
                with open(file_path, 'w') as file:
                    json.dump({'terms': self.terms}, file)
                self.getFiles()
         else:
            if self.path:
                if self.selected:
                    file_name = self.selected.text()
                    file = self.path + '/' + file_name
                    with open(file, 'w') as f:
                        json.dump({'terms': self.terms}, f)
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