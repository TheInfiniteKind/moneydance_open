#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# You would only use this script if using script_info "type" = "homepageview". To create and return a HomePageView instance
# Without an 'initializer' this would be where your main script is executed

global moneydance, moneydance_ui, moneydance_data, moneydance_extension_parameter, moneydance_script_fixed_parameter
global moneydance_homepage_view
global MY_EXTENSION_OBJ, myPrint
global EXTENSION_LOCK

myPrint("@@ scriptinfo homepageview.py was invoked @@")

# PUT YOUR CODE HERE

# Note you should be in the same namespace as your other scripts within the same extension...
# To reference, use global on the object and then just refer to it - e.g.

import threading
from com.moneydance.apps.md.view import HomePageView
from java.lang import Runnable, System
from javax.swing import SwingUtilities, JPanel, JLabel, Box
from javax.swing.border import EmptyBorder
from java.awt import GridBagLayout
from com.moneydance.awt import GridC, CollapsibleRefresher
from com.moneydance.apps.md.view.gui import MoneydanceLAF

class MyHomePageView(HomePageView):

    HPV = None

    @staticmethod
    def getHPV(mdGUI=None):
        if MyHomePageView.HPV is not None: return MyHomePageView.HPV
        with EXTENSION_LOCK:
            if mdGUI is None: raise Exception("ERROR - you must pass mdGUI reference to getHPV() when creating a new instance")
            myPrint("Creating and returning a new single instance of MyHomePageView() using extension lock....")
            MyHomePageView.HPV = MyHomePageView(mdGUI)
        return MyHomePageView.HPV

    def __init__(self, mdGUI):

        self.mdGUI = mdGUI
        self.myModuleID = "extension_tester"
        self.view = None

        self.refresher = None
        self.is_unloaded = False

        self.HPV_LOCK = threading.Lock()  # 'replicate' Java's 'synchronized' statements

        class GUIRunnable(Runnable):
            def run(self): MyHomePageView.getHPV().reallyRefresh()

        self.refresher = CollapsibleRefresher(GUIRunnable())

    def getID(self): return self.myModuleID

    def __str__(self): return "Extension Tester: Test HomePageView"
    def __repr__(self): return self.__str__()
    def toString(self): return self.__str__()

    # Called by Moneydance. Must returns a (swing JComponent) GUI component that provides a view for the given data file.
    def getGUIView(self, book):
        if book: pass
        if self.is_unloaded: return None     # this hides the widget from the home screen

        class CreateViewPanelRunnable(Runnable):
            def run(self):
                HPV = MyHomePageView.getHPV()                                                                           # noqa
                HPV.view = HPV.ViewPanel()

        with self.HPV_LOCK:
            if not SwingUtilities.isEventDispatchThread():
                SwingUtilities.invokeAndWait(CreateViewPanelRunnable())
            else:
                CreateViewPanelRunnable().run()
            HPV = MyHomePageView.getHPV()
            return HPV.view

    class ViewPanel(JPanel):

        def __init__(self):

            HPV = MyHomePageView.getHPV()

            super(self.__class__, self).__init__()

            self.mainBorder = EmptyBorder(3, 14, 3, 0)

            gridbag = GridBagLayout()
            self.setLayout(gridbag)

            self.setOpaque(False)
            self.setBorder(MoneydanceLAF.homePageBorder)

            self.headerPanel = JPanel(GridBagLayout())
            self.headerPanel.setOpaque(False)

            self.headerLabel = JLabel("Extension Tester - HomePageView Widget Header")
            self.headerLabel.setFont(HPV.mdGUI.getFonts().header)
            self.headerLabel.setForeground(HPV.mdGUI.getColors().secondaryTextFG)

            self.titlePnl = JPanel(GridBagLayout())
            self.titlePnl.setOpaque(False)

            self.titlePnl.add(self.headerLabel, GridC.getc().xy(0, 0).wx(9.0).fillx().west())
            self.headerPanel.add(self.titlePnl, GridC.getc().xy(0, 0).wx(1.0).fillx().east())

            self.add(self.headerPanel, GridC.getc().xy(0, 0).wx(1.0).fillx())

            self.listPanel = JPanel(gridbag)
            self.add(self.listPanel, GridC.getc(0, 1).wx(1.0).fillboth())
            self.add(Box.createVerticalStrut(2), GridC.getc(0, 2).wy(1.0))
            self.listPanel.setOpaque(False)

        def updateUI(self): super(self.__class__, self).updateUI()


    # Sets the view as active or inactive. When not active, a view should not have any registered listeners
    # with other parts of the program. This will be called when an view is added to the home page,
    # or the home page is refreshed after not being visible for a while.
    def setActive(self, active):
        if self.is_unloaded: return
        if not active: pass
        else: self.refresh()

    # Forces a refresh of the information in the view. For example, this is called after the preferences are updated.
    def refresh(self):
        if self.is_unloaded: return
        if self.refresher is not None: self.refresher.enqueueRefresh()

    def reallyRefresh(self):
        with self.HPV_LOCK:
            if self.view is not None:
                _view = self.view

                _view.setVisible(False)
                _view.listPanel.removeAll()
                if _view.headerPanel not in _view.getComponents():
                    _view.add(_view.headerPanel, GridC.getc().xy(0, 0).wx(1.0).fillx())

                nameLbl = JLabel("example list item 1 (ts: %s) KOOL! ;->" %(System.currentTimeMillis()))
                nameLbl.setBorder(_view.mainBorder)

                _view.listPanel.add(nameLbl, GridC.getc().xy(0, 1).wx(1.0).fillboth().pady(2))

                _view.setVisible(True)
                _view.invalidate()
                parent = _view.getParent()
                while parent is not None:
                    parent.repaint()
                    parent.validate()
                    parent = parent.getParent()


    # Called when the view should clean up everything. For example, this is called when a file is closed and the GUI
    #  is reset. The view should disconnect from any resources that are associated with the currently opened data file.
    def reset(self): pass

    def unload(self):   # This is my own method (not overridden from HomePageView)
        self.cleanupAsBookClosing()

        with self.HPV_LOCK: self.is_unloaded = True

    def cleanupAsBookClosing(self):

        with self.HPV_LOCK:
            if self.view is not None:
                self.view.removeAll()
            self.view = None
            self.reset()

moneydance_homepage_view = MyHomePageView.getHPV(moneydance.getUI())                                                                             # noqa
myPrint("... returning HomePageView class/instance: %s" %(moneydance_homepage_view))
