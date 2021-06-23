## BEAVER                                        
                                                 
An extremely simple http server. I took up this task to learn about sockets in python.
Where from the name beaver? Well I picked something that rhymes with server.

<br/>
Also it handles just GET requests.

<br/>
CTRL-C? I've been having some issues handling it. My work around is to do `kill (Get-Process -Name 'python').Id` on powershell or `kill -9 $(pgrep python)` on bash. 

#### Usage
Run the code with the following arguments:
- -a - The host address, It is localhost by default
- -p - The port to listen to, It is 8000 by default
- -r - The root directory, It is the current directory by default


### References
- [https://pymotw.com/2/select/index.html#module-select](https://pymotw.com/2/select/index.html#module-select)
- [https://docs.python.org/3/library/socket.html](https://docs.python.org/3/library/socket.html)
- [https://realpython.com/python-sockets/](https://realpython.com/python-sockets/)