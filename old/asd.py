import pymel.core as pm

def defaultButtonPush():
    print 'Button 1 was pushed.'

def asd():
    pm.window( width=150 )
    # Result: ui.Window('window1') #
    pm.columnLayout( adjustableColumn=True )
    # Result: ui.ColumnLayout('window1|columnLayout9') #
    pm.button( label='Button 1', command='defaultButtonPush()' )
    # Result: ui.Button('window1|columnLayout9|button3') #
    pm.button( label='Button 2' )
    # Result: ui.Button('window1|columnLayout9|button4') #
    pm.button( label='Button 3' )
    # Result: ui.Button('window1|columnLayout9|button5') #
    pm.button( label='Button 4' )
    # Result: ui.Button('window1|columnLayout9|button6') #
    pm.showWindow()

