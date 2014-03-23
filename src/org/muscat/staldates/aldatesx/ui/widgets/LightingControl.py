from org.muscat.staldates.aldatesx.ui.widgets.Screens import ScreenWithBackButton


class LightingControl(ScreenWithBackButton):
    '''
    classdocs
    '''

    def __init__(self, controller, mainWindow):
        self.controller = controller
        ScreenWithBackButton.__init__(self, "Welcome Area Lights", mainWindow)
