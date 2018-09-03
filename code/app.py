# -*- coding: utf-8 -*-
# compile with "  pyinstaller --noconsole app.py  "
# version: 1.0b
import wx
import os
import psutil
import shutil

import sys


class Logs():
    """class for storing simple test results in temp file"""

    def __init__(self):
        pass

#  save desired text to temp.txt file
    def SaveToTemp(self, text):
        tmp = open("temp.txt","a+")
        tmp.write(text)
        tmp.close()

#  delete temp file if exists on each run and proper exit
    def DeleteTempFile(self):
        try:
            os.remove("temp.txt")
        except OSError:
            pass

# read temp file
    def ReadTemp(self):
        # open file for reading
        try:
            with open("temp.txt","r") as tmp:
                all_results = tmp.read()
            result = all_results.replace(".robot", "").replace("0"," - PASS").replace("1"," - FAIL")
            return result
            # print(result)
        except FileNotFoundError:
            pass

class runner():

    def __init__(self):
        pass

    def kill(self, name):
        os.system("taskkill /f /im {}".format(name))

    def GetFolder(self):
        dialog = wx.DirDialog(None, "Choose a directory:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        dialog.Destroy()
        return path

    def GetTests(self, path):
        tests = []
        files = os.listdir(path)
        for item in files:
            if ".robot" in item:
                tests.append(item)
                # tests.append(path + "\\" + item)
            else:
                continue
        return tests

class gui(wx.Frame):
    X = 1280
    Y = 720
    CHROME_KILL = False
    select_ALL = False
    TEST_LIST = []
    SELECTION = []
    OUTPUT_PATH = "OUTPUT"
    version = "v 1.0"
    RESULT_DATA = "It looks empty here"

    def __init__(self, parent, title):
        super().__init__(parent, title=title, size = (self.X,self.Y))
        # set icon
        icon = wx.Icon('ICO.png', wx.BITMAP_TYPE_ANY)
        self.SetIcon(icon)
        self.Centre()
        self.InitUI()

    def InitUI(self):
        # toolbar
        self.toolbar = self.CreateToolBar()
        # run tool
        self.runTool = self.toolbar.AddTool(wx.ID_ANY, 'run', wx.Bitmap('run.png'))
        # separator
        self.toolbar.AddSeparator()
        # choose folder tool
        self.folderTool = self.toolbar.AddTool(wx.ID_ANY, 'folder', wx.Bitmap('folder.png'))
        # kill chrome tool
        chromeIco = wx.Bitmap("chromeOFF.png", wx.BITMAP_TYPE_PNG)
        self.chromeTool = self.toolbar.AddTool(wx.ID_ANY, 'chrome', wx.Bitmap(chromeIco))
        # set output tool
        self.outputTool = self.toolbar.AddTool(wx.ID_ANY, 'save', wx.Bitmap('save.png'))
        # select button
        self.selectallTool = self.toolbar.AddTool(wx.ID_ANY, 'selectall', wx.Bitmap('selectall.png'))
        self.deselectTool = self.toolbar.AddTool(wx.ID_ANY, 'deselect', wx.Bitmap('deselect.png'))
        # separator
        self.toolbar.AddSeparator()
        # exit tool
        self.exitTool = self.toolbar.AddTool(wx.ID_ANY, 'Quit', wx.Bitmap('exit.png'))

        self.toolbar.Realize()



        #  ----- panel -----
        panel = wx.Panel(self)
        self.LB = wx.ListBox(panel, size = (self.X * 0.97, self.Y * 0.84),
            choices = self.TEST_LIST, style = wx.LB_MULTIPLE, pos = (10,10))
        # output folder info
        self.outputInfo = wx.StaticText(panel, label="output folder: {}".format(self.OUTPUT_PATH), pos = (10, self.Y * 0.86))
        # version info
        self.versionInfo = wx.StaticText(panel, label= self.version, pos = (self.X * 0.96, self.Y * 0.86))

        #  ------ BINDING -------
        self.Bind(wx.EVT_TOOL, self.Run, self.runTool)
        self.Bind(wx.EVT_TOOL, self.Exit, self.exitTool)
        self.Bind(wx.EVT_TOOL, self.ChromeKillSetter, self.chromeTool)
        self.Bind(wx.EVT_TOOL, self.SelectAll, self.selectallTool)
        self.Bind(wx.EVT_TOOL, self.DeSelect, self.deselectTool)
        self.Bind(wx.EVT_TOOL, self.ChooseFolder, self.folderTool)
        self.Bind(wx.EVT_TOOL, self.SetOutput, self.outputTool)

    # exit function
    def Exit(self, e):
        Logs.DeleteTempFile(self)
        self.Close()

    #  set variable used for terminating chrome.exe process, also changes icon
    def ChromeKillSetter(self, e):
        if self.CHROME_KILL == True:
            self.CHROME_KILL = False
            # print("chrome status:",self.CHROME_KILL)
            chromeIco = wx.Bitmap("chromeOFF.png", wx.BITMAP_TYPE_PNG)
            self.chromeTool.SetNormalBitmap(chromeIco)
            self.toolbar.Realize()
            self.toolbar.Refresh()
        else:
            self.CHROME_KILL =True
            # print("chrome status:",self.CHROME_KILL)
            chromeIco = wx.Bitmap("chromeON.png", wx.BITMAP_TYPE_PNG)
            self.chromeTool.SetNormalBitmap(chromeIco)
            self.toolbar.Realize()
            self.toolbar.Refresh()

    def SelectAll(self, e):
        for i in range(self.LB.GetCount()):
            # print(i)
            self.LB.SetSelection(i)

    def DeSelect(self, e):
        self.LB.SetSelection(wx.NOT_FOUND)

    #  reload list of tests
    def ReloadList(self):
        self.LB.Set(self.TEST_LIST)

    #  choosing folder with tests
    def ChooseFolder(self, e):
        self.path = runner.GetFolder(self)
        self.TEST_LIST = runner.GetTests(self, self.path)
        self.ReloadList()
        # print(self.TEST_LIST)

    # set output folder, if not set, default one is used
    def SetOutput(self, e):
        self.OUTPUT_PATH = runner.GetFolder(self)
        self.outputInfo.SetLabel("output folder: {}".format(self.OUTPUT_PATH))
        # print(self.OUTPUT_PATH)

    # show results after test run
    def ShowResultlDialog(self):
        if Logs.ReadTemp(self) is not None:
            self.RESULT_DATA = Logs.ReadTemp(self)
        # print(self.RESULT_DATA)
        wx.MessageBox(self.RESULT_DATA, '- RESULTS -', wx.OK | wx.ICON_INFORMATION)

    # run selected tests and kill chrome if set to True.
    def Run(self, e):
        Logs.DeleteTempFile(self)
        self.SELECTION = self.LB.GetSelections()
        for item in self.SELECTION:
            test_name = (self.TEST_LIST[item])
            # (self.TEST_LIST[item])
            # print(self.CHROME_KILL)
            if self.CHROME_KILL == True:
                # print("------kill chrome----")
                runner.kill(self, "Chrome.exe")
            test = self.path + "\\" + test_name
            # print("robot -d {} {}".format(self.OUTPUT_PATH, test))
            status_code = os.system("robot -d {}\\{} {}".format(self.OUTPUT_PATH, test_name, test))
            Logs.SaveToTemp(self, ("-> {}---> {}\n".format(test_name, status_code)))
        Logs.ReadTemp(self)
        self.ShowResultlDialog()

def main():
    app = wx.App(False)
    ex = gui(None, title='Robot Test Runner')
    ex.Show()
    app.MainLoop()


# if __name__ == '__main__':
if __name__.endswith('__main__'):
    main()
