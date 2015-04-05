#!/usr/bin/python

import sys
import getopt
import json
import atexit

try:
    from termcolor import colored
    color       =   colored
except:
    def color(character, color):
        return character

filename        =   "kapcom.json"

data            =    {
    "joys"          :   [],
    "inputs"        :   [],
    "outputs"       :   [],
    "bargraphs"     :   [],
    "displays"      :   []
}

menu            =   {
    "L":	("Load from File",	"load"),
    "S":	("Save to File",	"save"),
    "M":	("Modify Configuration", {
	    "L":	("List All",	"listall"),
        "G":	("Modify Global", "modifyglobal"),
        "J":	("Modify Joysticks", "modifyjoysticks"),
        "I":	("Modify Inputs", "modifyinputs"),
        "O":	("Modify Outputs", "modifyoutputs"),
        "D":	("Modify Displays", "modifydisplays"),
        "B":	("Modify Bargraphs", "modifybargraphs")
    })
}

def read_from_file(filename):
    with open(filename, 'r') as file:
        data   =   json.load(file)
    file.close()
    
    return data
    
def write_to_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)
    file.close()

def prompt(prompt, default=None, spacing=20):
    value = raw_input('{:<{}}'.format(prompt, spacing))

    if value is "":
        return default
    elif "YES".startswith(value.upper()):
        print "True"
        return True
    elif "NO".startswith(value.upper()):
        print "False"
        return False
    elif value.isdigit():
        return int(value)
    else:
        try:
            return float(value)
        except ValueError:
            return value

def rawprompt(prompt, spacing=20):
    return raw_input('{:<{}}'.format(prompt, spacing))
    


def prompt_for_joy():
    pass
    
def prompt_for_input():
    pass

def prompt_for_output():
    pass
    
def prompt_for_display():
    pass

def prompt_for_bargraph():
    pass

def print_joy(index, long=False):
    global data
    print '{:<5}{}'.format(index, data['joys'][index]["name"])

def item(keyword, index, long=False):
    global data
    return '{:<5}{}'.format(index, data[keyword][index]["name"])
    
def listdata(keyword):
    global data
    print "Joysticks: "
    for index, object in enumerate(data[keyword]):
        print item(keyword, index)
    

    
def list_inputs():
    pass
    
def list_outputs():
    pass
    
def list_displays():
    pass
    
def list_bargraphs():
    pass

def showmenu(menu, title=None):
    def displaymenu(menu, title=None):
        if title is not None:
            print 
            print title + ":"
    
        for key, value in menu.iteritems():
            print '{:<15}{}'.format(color(key, "green"), value[0])
        
        print '{:<15}{}'.format(color("P", "cyan"), "Print Menu")
        print '{:<15}{}'.format(color("X", "red"), "Exit")
        
    displaymenu(menu, title)
    
    input = rawprompt("Entry: ", 10)
    while input.upper() is not "X":
        for key, value in menu.iteritems():
            sub = value[1]
            
            if key.upper() == input.upper():
                if sub is None:
                    print "Undefined action"
                    break
                elif type(sub) is dict:
                    showmenu(sub, value[0])
                    displaymenu(menu, title)
                    break
                elif type(sub) is str:
                    print "Do " + key
                    f = locals().get(sub)
                    if not f:
                        print "Unknown action: " + sub
                        break
                    else:
                        f()
                else:
                    sub()
                    break
            
        else:
            if input.upper() == "P":
                displaymenu(menu, title)
            elif input.upper() == "X":
                return
            else:
                print "Invalid selection"
            
        input = rawprompt("Entry: ", 10)
    

def main(argv):
    global filename
    global data
    global menu
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-f"):
            filename = arg
         
    showmenu(menu, "Main Menu [" + filename + "]")
    
    data = read_from_file(filename)
    list("joys")
    
def usage():
    print color("./configure.py [-f file]")
    
@atexit.register
def finish():
    save    =   prompt("Save now? [Y]", True)
    if save is True:
        savename = prompt("Filename? [" + filename + "]", filename)
        
        write_to_file(savename, data)
    else:
        sure = prompt("Are you sure? [Y]") or True
        if sure:
            exit()
        else:
            main
      
def breakpoint():
    """Python debug breakpoint."""
    
    from code import InteractiveConsole
    from inspect import currentframe
    try:
        import readline # noqa
    except ImportError:
        pass

    caller = currentframe().f_back

    env = {}
    env.update(caller.f_globals)
    env.update(caller.f_locals)

    shell = InteractiveConsole(env)
    shell.interact(
        '* Break: {} ::: Line {}\n'
        '* Continue with Ctrl+D...'.format(
            caller.f_code.co_filename, caller.f_lineno
        )
    )  

if __name__ == "__main__":    
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)



