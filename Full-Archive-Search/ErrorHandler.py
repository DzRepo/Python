import sys

def Log(Ex, Description):
    print "Error:", Description
    print "Exception:", Ex
    print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
    
