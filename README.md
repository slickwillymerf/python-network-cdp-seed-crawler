# python-network-cdp-seed-crawler
Python project that aims to discover CDP neighbors and map their Layer-2 topology within a shareable medium like Visio or Draw.io. 

Please forgive organizational or formatting errors - this is my first Github repository. 

Start this script by saving 'main.py' and 'cdp_parse_functions.py' into the same directory, then running 'main.py.' 

Enter SSH credentials, enter a 'seed' device to start CDP crawling from, and wait. There is also an SSH 'test' device you must enter - this simply tests your SSH credentials before kicking off the rest of the script. 

'main.py' will reference functions from 'cdp_parse_functions.py' throughout the script

Some code taken from:

  https://github.com/GoreNetwork/CDP-parser/blob/master/cdp_parse.py
  
  https://bitstudio.dev/drawing-network-topologies-in-python/
