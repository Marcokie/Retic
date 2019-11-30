from conf import operation as op
from machine import RTC
levels = [
    "DEBUG",
    "INFO",
    "ERROR"
]
log_level = op["log_level"]
rtc = RTC()
def setTime(y,m,d,w,h,mi):
    rtc.datetime((y,m,d,w,h,mi,0,0))


def write(msg, lev="ERROR" ):
    try:
        if levels.index(lev) >= levels.index(log_level):
            nt = rtc.datetime()
            dt = '{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(nt[0],nt[1],nt[2],nt[4],nt[5],nt[6])
            logmsg = "{}: {}: {}".format(dt, lev, msg)
            print(logmsg)
            with open("young.log","a+") as f:
                f.write(logmsg + "\n")
    except ValueError as ex:
        nt = rtc.datetime()
        dt = '{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(nt[0],nt[1],nt[2],nt[4],nt[5],nt[6])
        with open("young.log","a+") as f:
            f.write(dt + ": ERROR: " + msg + "\n")


def read(l="young.log"):
    with open(l,'r') as f:
        print(f.read())