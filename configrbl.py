import settings
from settings import *
from resetGrbl import resetGrbl

def configrbl():
    print('Going to run configrbl, emptying buffer:')
    print('RECEIVED: '+str(grbl.read_very_eager()))
    print('Sending $$...')
    grbl.write('$$'.encode('utf-8')+b'\n')
    print('Waiting for answer...')
    ans = grbl.read_until(b'ok\r\n', timeout=1)
    print('RECEIVED: '+str(ans))
    corect_ans = '$0=10\\r\\n$1=25\\r\\n$2=0\\r\\n$3=0\\r\\n$4=0\\r\\n$5=1\\r\\n$6=0\\r\\n$10=1\\r\\n$11=0.010\\r\\n$12=0.002\\r\\n$13=0\\r\\n$20=0\\r\\n$21=1\\r\\n$22=1\\r\\n$23=0\\r\\n$24=25.000\\r\\n$25=500.000\\r\\n$26=250\\r\\n$27=1.000\\r\\n$30=1000\\r\\n$31=0\\r\\n$32=0\\r\\n$100=100.000\\r\\n$101=100.000\\r\\n$102=100.000\\r\\n$110=5000.000\\r\\n$111=5000.000\\r\\n$112=5000.000\\r\\n$120=100.000\\r\\n$121=100.000\\r\\n$122=100.000\\r\\n$130=1000.000\\r\\n$131=1000.000\\r\\n$132=1000.000\\r\\nok\\r\\n'
    if corect_ans in str(ans):
        print('Parameters sent by GRBL correct!')
    else:
        input('ERROR: PARAMETERS SENT BY GRBL INCORRECT!!! Press enter to continue')

    ans = grbl.read_until(b'ok\r\n', timeout=1)
    print('RECEIVED: '+str(ans))

if __name__ == "__main__":
    resetGrbl()
    configrbl()
    #input('press enter to close connections')
    grbl.close()
    tn2.close()