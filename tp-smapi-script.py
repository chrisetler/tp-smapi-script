#!/usr/bin/env python
import subprocess
import os
from dateutil.parser import parse
import datetime

#load the driver, if it isn't already
def load_driver():
    if (not (os.path.isfile("/sys/devices/platform/smapi/BAT0/installed"))):
        p = subprocess.Popen("sudo modprobe tp-smapi", shell=True)
        p.communicate("") #allow the user to input a password
        p.wait()

#get the battery property with the specified name, return it as a string
def get_value(var_name):
    try:
        fname = "/sys/devices/platform/smapi/BAT0/" + var_name
        f = open(fname)
        var_out = f.readline().rstrip()
        f.close
        return var_out
    except IOError:
        return "IOError"

#read the battery information and load it into a bunch of global variables.
#this should be run every time the screen is updated, to load any changes that could have been made.
def populate_variables():
    #allow other methods to view these values
    global state, cycles, date_used, orig_capacity, curr_capacity, start_charge_thresh
    global stop_charge_thresh
    global start_charge_thresh_supported, stop_charge_thresh_supported
    global force_discharge, inhibit_charge_minutes, force_discharge_supported, inhibit_charge_minutes_supported
    state = get_value("state")
    cycles = get_value("cycle_count")
    date_used = get_value("first_use_date")
    orig_capacity = get_value("design_capacity")
    curr_capacity = get_value("last_full_capacity")
    start_charge_thresh = get_value("start_charge_thresh")
    stop_charge_thresh = get_value("stop_charge_thresh")
    force_discharge = get_value("force_discharge")
    inhibit_charge_minutes = get_value("inhibit_charge_minutes")

    try:
        start_charge_thresh = int(start_charge_thresh)
        start_charge_thresh_supported = True
    except ValueError:
        start_charge_thresh = 0
        start_charge_thresh_supported = False

    try:
        stop_charge_thresh = int(stop_charge_thresh)
        stop_charge_thresh_supported = True
    except ValueError:
        stop_charge_thresh = 0
        stop_charge_thresh_supported = False
    try:
        force_discharge = int(force_discharge)
        force_discharge_supported = True
    except ValueError:
        force_discharge = -1
        force_discharge_supported = False
    try:
        inhibit_charge_minutes = int(inhibit_charge_minutes)
        inhibit_charge_minutes_supported = True
    except ValueError:
        inhibit_charge_minutes = 0
        inhibit_charge_minutes_supported = False



#print the quick fact screen
#this is the screen that first appears when the program is loaded normally.
def display_quick_facts_screen():
    global curr_capacity, orig_capacity, cycles, date_used, state
    global stop_charge_thresh, start_charge_thresh
    global force_discharge, force_discharge_supported, inhibit_charge_minutes, inhibit_charge_minutes_supported
    #calculations
    curr_capacity = int(curr_capacity)
    orig_capacity = int(orig_capacity)
    cycles = int(cycles)
    date_used = parse(date_used)
    today = datetime.date.today()
    elasped_time = today - date_used.date()
    days = elasped_time.days

    percent_of_designed_capacity = float(curr_capacity)/float(orig_capacity)*100
    loss_per_cycle = float(100-percent_of_designed_capacity)/float(cycles)

    loss_per_day = float(100-percent_of_designed_capacity)/float(days)
    day_to_zero_capacity = 1/float(loss_per_day)*100
    day_to_zero_capacity = datetime.timedelta(days = day_to_zero_capacity)
    date_of_zero_capacity = (date_used + day_to_zero_capacity).date()
    days_from_now = (date_of_zero_capacity - today).days

    #print information
    print "Battery Quick Facts: "
    print "The battery is currently " + state + "."
    print "The max capacity of the battery is " + print_dec(percent_of_designed_capacity)+ "% of its designed capacity."
    print "After " + repr(cycles) + " charge cycles, the battery has lost " + print_dec(loss_per_cycle) + "% of its capacity per cycle."
    print "After " + repr(days) + " days of use, the battery has lost " + print_dec(loss_per_day) + "% of its capacity per day."
    print "This is equivelent to a loss of " + print_dec(loss_per_day * 365) + "% per annum."
    print "At this rate, the battery will die on " + str(date_of_zero_capacity) + ", which is " + str(days_from_now) + " days from now."
    print " "
    print "Currently the battery is set to begin charging at " + str(start_charge_thresh) + "% and stop charging at " + str(stop_charge_thresh) + "%."
    print "You can change these thresholds by pressing (2)."
    print ""
    if(not start_charge_thresh_supported):
        print "Your model does not appear to support changing the staring threshold. \nAttempts to change it will probably do nothing."
    if(not stop_charge_thresh_supported):
        print "Your model does not appear to support changing the stopping threshod. \nAttempts to change it will probably do nothing."
    if(force_discharge == 1):
        print "The battery is currently set to force discharging."
    if(inhibit_charge_minutes > 0):
        print "The battery is currently set to disable charing for " + str(inhibit_charge_minutes) + " minute(s)."

def display_more_information_screen():
    print "Battery Information:"
    print "State: " + str(get_value("state"))
    print "Cycle Count: " + str(get_value("cycle_count"))
    print "Current: " + str(get_value("current_now"))
    print "Current (avg. over 1 minute): " + str(get_value("current_avg"))
    print "Power: " + str(get_value("power_now"))
    print "Power (avg. over 1 minute): " + str(get_value("power_avg"))
    print "Last Full Capacity: " + str(get_value("last_full_capacity"))
    #print "Remaining Percent: " + str(get_value("remaining_percent"))
    #print "Remaining Run Time: " + str(get_value("remaining_running_time"))
    print "Remaining Capacity: " + str(get_value("remaining_capacity"))
    print "Voltage: " + str(get_value("voltage"))
    print "Design Voltage: " + str(get_value("design_voltage"))
    print "Manufacturer: " + str(get_value("manufacturer"))
    print "Model: " + str(get_value("model"))
    print "Barcoding: " + str(get_value("barcoding"))
    print "Chemistry: " + str(get_value("chemistry"))
    print "Serial: " + str(get_value("serial"))
    print "Manufacture Date: " + str(get_value("manufacture_date"))
    print "First Use Date: " + str(get_value("first_use_date"))
    print "Temperature (in milli-celcius): " + str(get_value("temperature"))
    #print "Ac Connected: " + str(get_value("ac_connected"))


#page for chaning the battery thresholds
def display_change_thresholds_screen():
    global stop_charge_thresh, start_charge_thresh
    user_response = "-1"
    new_stop_charge_thresh = stop_charge_thresh
    new_start_charge_thresh = start_charge_thresh
    #get the new starting charge threshold
    while(not ((user_response.isdigit() and int(user_response) >= 0 and int(user_response) <=100) or user_response == "")):
        print "Currently, the battery is set to start charging at " + str(start_charge_thresh) +"%. "
        print "Enter a new number between 1-100 to change or press enter to keep the same: "
        user_response = raw_input()
    if(user_response != ""):
        new_start_charge_thresh = int(user_response)
    user_response = "-1"
    #get the new stopping charge threshold
    while(not ((user_response.isdigit() and int(user_response) >= 0 and int(user_response) <=100) or user_response == "")):
        print "Currently, the battery is set to stop charging at " + str(stop_charge_thresh) +"%. "
        print "Enter a new number between 1-100 to change or press enter to keep the same: "
        user_response = raw_input()
    if(user_response != ""):
        new_stop_charge_thresh = int(user_response)
    #update the stop charging threshold, if it has been changed
    if(new_stop_charge_thresh != stop_charge_thresh):
        command_string = "echo " + str(new_stop_charge_thresh) + " > /sys/devices/platform/smapi/BAT0/stop_charge_thresh"
        sudoShell = subprocess.Popen(["sudo","--shell"],shell=False, stdout=False, stdin=subprocess.PIPE)
        sudoShell.communicate(command_string)
        sudoShell.wait()
        stop_charge_thresh = new_stop_charge_thresh
    #update the stop charging threshold, if it has been changed
    if(new_start_charge_thresh != start_charge_thresh):
        command_string = "echo " + str(new_start_charge_thresh) + " > /sys/devices/platform/smapi/BAT0/start_charge_thresh"
        sudoShell = subprocess.Popen(["sudo","--shell"],shell=False, stdout=False, stdin=subprocess.PIPE)
        sudoShell.communicate(command_string)
        sudoShell.wait()
        start_charge_thresh = new_start_charge_thresh
    print "\nThreshold Settings Updated."

def display_inhibit_charging_screen():
    global inhibit_charge_minutes, inhibit_charge_minutes_supported
    if(inhibit_charge_minutes_supported):
        user_response = "a"
        while(not user_response.isdigit() or int(user_response) < 0):
            print "Enter a number of minutes to inhibit discharing for:"
            user_response = raw_input()
        minutes_to_discharge = int(user_response)
        if(minutes_to_discharge != inhibit_charge_minutes):
            command_string = "echo " + str(minutes_to_discharge) + " > /sys/devices/platform/smapi/BAT0/inhibit_charge_minutes"
            sudoShell = subprocess.Popen(["sudo","--shell"],shell=False, stdout=False, stdin=subprocess.PIPE)
            sudoShell.communicate(command_string)
            sudoShell.wait()
        print "Settings Updated."
    else:
        print "It appears your model does not support this features. Sorry."

def display_force_discharge_screen():
    global force_discharge, force_discharge_supported
    if(force_discharge_supported):
        if(force_discharge == 0):
            force_discharge = 1
            print "Force Discharge is being enabled."
        else:
            force_discharge = 0
            print "Force Discharge is being disabled."
        command_string = "echo " + str(force_discharge) + " > /sys/devices/platform/smapi/BAT0/force_discharge"
        sudoShell = subprocess.Popen(["sudo","--shell"],shell=False, stdout=False, stdin=subprocess.PIPE)
        sudoShell.communicate(command_string)
        sudoShell.wait()
        print "\nSettings Updated."
    else:
        print "You model does not appear to support the force discharge option. Sorry."



#print available options for the user to select.
def print_options():
    #Options
    print "\n"
    print "Please Select an Option:"
    print "0 - Quick Facts"
    print "1 - View More Information"
    print "2 - Edit Thresholds"
    print "3 - Inhibit Charging for n Minutes"
    print "4 - Toggle Force Discharge"
    print "q - Exit"

#print with only two decimal places
def print_dec(var_to_print):
    return format(var_to_print, '.2f')

if __name__ == "__main__":
    #load the driver
    load_driver()
    #check if the battery is installed
    f = open("/sys/devices/platform/smapi/BAT0/installed")
    installed = f.read().rstrip()
    f.close()
    #main
    if (installed[0] == '1'):
        populate_variables()
        #clear and display the home screen
        subprocess.call("clear")
        display_quick_facts_screen()
        print_options()
        option = raw_input()
        #main loop
        while(option != 'q'):
            if(option == '0'):
                subprocess.call("clear")
                populate_variables()
                display_quick_facts_screen()
            elif(option == '1'):
                subprocess.call("clear")
                populate_variables()
                display_more_information_screen()
            elif(option == '2'):
                subprocess.call("clear")
                populate_variables()
                display_change_thresholds_screen()
            elif(option == '3'):
                subprocess.call("clear")
                populate_variables()
                display_inhibit_charging_screen()
            elif(option == '4'):
                subprocess.call("clear")
                populate_variables()
                display_force_discharge_screen()
            else:
                subprocess.call("clear")
                print "Not an option."
            print_options()
            option = raw_input()

    else:
        print "No battery is installed - Exiting."
