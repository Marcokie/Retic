from conf import zones
from conf import programs
from conf import defaults
from conf import alarms
import conf
import os
from machine import Pin
from machine import RTC
import time
import micropython
import json

rtc = RTC()


def settime(lt): # (y,m,d,w,h,mi):
    if (all(isinstance(x,int) for x in lt) and len(lt) == 6):
        rtc.datetime(tuple(lt + [0,0]))
    else:
       log.write('{} is incorrect. Please enter list with y,,d,w,h,mi'.format(lt),'ERROR')

def setpins(active=[]):
    """Set and clear pins for configured zones.
    Input:
        active: list of zones to activate. (Other zones will be cleared)"""
    gpio = {}
    for k,v in zones.items():
        if k in active:
            gpio[k] = Pin(v, Pin.OUT,value=0)
        else:
            gpio[k] = Pin(v, Pin.OUT,value=1)
    return gpio


def setrecipe(water=defaults["recipe"],file=defaults["file"]):
    """Set recipe.
    Inputs:
        water: String reference to configured programs or (zone,time) tuple (list). Default configfigured as "recipe"
        file: File name where recipe is stored. Default configured as "file'"
    """
    import microlog as log

    def val(r):  # Recursive function to validate recipe
        if isinstance(r,list):
            if len(r) == 2 and isinstance(r[1],int) and isinstance(r[0],(list,str)):  # Correct terminal list
                return True
            else:
                ret = True
                for x in r:
                    ret = val(x)
                return ret
        return False

    if water in programs:
        if val(programs[water]):
            recipe = programs[water]
        else:
            recipe = []
            log.write('Program {} is invalid'.format(water),'ERROR')
    elif val(water):
        if isinstance(water,list):
            recipe = water
        else:
            recipe = [water]
    else:
        log.write('Recipe is invalid. Format Tuple(s) of Zone(s) and duration. Try again'.format(water),'ERROR')
        recipe = []
    with open(file,'w') as f:
        json.dump(recipe,f)


def getrecipe(file=defaults["file"]):
    """Function: return recipe stored on disk
    Input:
        File name where recipe is stored. Default configured as "file"
    """
    if file not in os.listdir():
        setrecipe([])
    with open(file, "r") as f:
        recipe = json.load(f)
    return recipe


def main():
    import microlog as log
    freq = conf.operation["freq"]
    file = defaults["file"]
    log.write('Spuit v20. Recipe on file: {}'.format(getrecipe()),'INFO')
    while True:
        if os.stat(file)[6] > 2:
            recipe = getrecipe()
            spuit = recipe[0]  # take head
            if not isinstance(spuit[0],list):
                spuit[0] = [spuit[0]]
            gpio = setpins(spuit[0])
            log.write(spuit,'DEBUG')
            spuit[1]-= freq
            if spuit[1] <= 0:
                if len(recipe) > 1:
                    log.write('Zone(s) {} done. Starting {}'.format(spuit[0],recipe[1]),'INFO')
                else:
                    setpins()
                    log.write('All done!','INFO')
                recipe = recipe[1:]
            else:
                recipe = [spuit] + recipe[1:]
            setrecipe(recipe)
        else:
            dtm = (rtc.datetime()[3:6])  # tuple (weekday,hour,min)
            log.write("Weekday,hour,minute: {}".format(dtm),'DEBUG')
            try:
                if dtm[1] == alarms[dtm[0]][0] and alarms[dtm[0]][1] <= dtm[2] < alarms[dtm[0]][1] + 30:
                    setrecipe(alarms[dtm[0]][2])
                    log.write('Set {} recipe: {}'.format(alarms[dtm[0]][2],programs[alarms[dtm[0]][2]]),'INFO')
            except KeyError:  # no aralm for the day
                log.write("not a water day: {}".format(dtm[0]),'DEBUG')
                pass
        time.sleep(freq*60)
