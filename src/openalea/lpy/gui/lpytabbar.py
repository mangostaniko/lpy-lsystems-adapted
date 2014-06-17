from openalea.vpltk.qt import qt
import svnmanip

QObject = qt.QtCore.QObject
SIGNAL = qt.QtCore.SIGNAL
QMessageBox = qt.QtGui.QMessageBox


class LpyTabBar(qt.QtGui.QTabBar):
    def __init__(self,parent):
        qt.QtGui.QTabBar.__init__(self,parent)
        self.setDrawBase(False)
        self.selection = None
        self.lpystudio = None
        
    def connectTo(self,lpystudio):
        self.lpystudio = lpystudio
        QObject.connect(self,SIGNAL('switchDocument'),lpystudio.switchDocuments)
        QObject.connect(self,SIGNAL('currentChanged(int)'),lpystudio.changeDocument)
        QObject.connect(self,SIGNAL('newDocumentRequest'),lpystudio.newfile)
        
    def mouseMoveEvent(self,event):
        tabselect = self.tabAt(event.pos())
        if tabselect != -1 :
            originaltab = self.currentIndex()
            if tabselect != originaltab:
                pass
                #self.emit(SIGNAL("switchDocument"),tabselect,originaltab)
        qt.QtGui.QTabBar.mouseMoveEvent(self,event)
    def mouseDoubleClickEvent(self,event):
        tabselect = self.tabAt(event.pos())
        if tabselect != -1 :
            self.emit(SIGNAL("newDocumentRequest"))
        qt.QtGui.QTabBar.mouseDoubleClickEvent(self,event)
    def contextMenuEvent(self,event):
        self.selection = self.tabAt(event.pos())
        if self.selection != -1:
            menu = qt.QtGui.QMenu(self)
            action = menu.addAction('Close')
            QObject.connect(action,SIGNAL('triggered(bool)'),self.close)
            action = menu.addAction('Close all except this ')
            QObject.connect(action,SIGNAL('triggered(bool)'),self.closeAllExcept)
            menu.addSeparator()
            if self.lpystudio.simulations[self.selection].readonly:
                action = menu.addAction('Remove Readonly ')
                QObject.connect(action,SIGNAL('triggered(bool)'),self.removeReadOnly)
            else:
                action = menu.addAction('Set Readonly ')
                QObject.connect(action,SIGNAL('triggered(bool)'),self.setReadOnly)
            menu.addSeparator()
            action = menu.addAction('Copy filename ')
            QObject.connect(action,SIGNAL('triggered(bool)'),self.copyFilename)
            action = menu.addAction('Open folder')
            QObject.connect(action,SIGNAL('triggered(bool)'),self.openFolder)
            fname = self.lpystudio.simulations[self.selection].fname
            if fname and svnmanip.hasSvnSupport() and svnmanip.isSvnFile(fname):
                menu.addSeparator()
                action = menu.addAction('SVN Update')
                QObject.connect(action,SIGNAL('triggered(bool)'),self.svnUpdate)
                action = menu.addAction('Is Up-to-date ?')
                QObject.connect(action,SIGNAL('triggered(bool)'),self.svnIsUpToDate)
            menu.exec_(event.globalPos())
    def openFolder(self):
        import os, sys
        fname = os.path.abspath(self.lpystudio.simulations[self.selection].fname)
        mdir = os.path.dirname(fname)
        if sys.platform == 'win32':
                import subprocess
                #os.startfile(mdir)
                #os.system('explorer /select,"'+fname+'"')
                subprocess.call('explorer /select,"'+fname+'"')
        elif sys.platform == 'linux2':
                os.system('xdg-open "'+mdir+'"')
        else:
                os.system('open "'+mdir+'"')
    def close(self):
        self.lpystudio.closeDocument(self.selection)
    def closeAllExcept(self):
        self.lpystudio.closeAllExcept(self.selection)
    def copyFilename(self):
        qt.QtGui.QApplication.clipboard().setText(self.lpystudio.simulations[self.selection].fname)
    def removeReadOnly(self):
        self.lpystudio.simulations[self.selection].removeReadOnly()
    def setReadOnly(self):
        self.lpystudio.simulations[self.selection].setReadOnly()
        
    def svnUpdate(self):
        hasupdated = svnmanip.svnUpdate(self.lpystudio.simulations[self.selection].fname,self)
        if hasupdated: self.lpystudio.simulations[self.selection].reload()
        
    def svnIsUpToDate(self):
        svnmanip.svnIsUpToDate(self.lpystudio.simulations[self.selection].fname,self)
        
        
class LpyTabBarNeighbor(qt.QtGui.QWidget):
    def __init__(self,parent):
        qt.QtGui.QWidget.__init__(self,parent)
        
    def mouseDoubleClickEvent(self,event):
        self.emit(SIGNAL("newDocumentRequest"))
        qt.QtGui.QWidget.mouseDoubleClickEvent(self,event)
