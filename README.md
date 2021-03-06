# BirdieScript

BirdieScript is a programming language designed for code golf—writing programs in as few characters as possible. It is based on [GolfScript](http://www.golfscript.com/), but adds features like variable scoping and I/O, as well as a much larger standard library.

To try it out, run `./ibis` for an interactive REPL environment, or `./ibis FILE` to execute `FILE` as BirdieScript code.

To install Birdiescript, run `python setup.py install`. Then the `ibis` command will be added to your Python scripts directory.

## BirdieScript help

    usage: ibis [-c CMD] [-d] [-e ENC] [-h] [-m DEPTH] [-r] [-v]
                [FILE] ...
    
    ibis - Interactive Birdiescript interpreter.
    
    positional arguments:
      FILE                  run contents of FILE as a script
      ARGS                  arguments to script
    
    optional arguments:
      -c CMD, --cmd CMD     run CMD string as a script
      -d, --debug           show debug output when running script
      -e ENC, --encoding ENC
                            specify the script character encoding
                            [default: UTF-8]
      -h, --help            show this help message and exit
      -m DEPTH, --maxdepth DEPTH
                            set maximum recursion depth [default: 1000]
      -r, --repl            run as REPL environment
      -v, --version         show program's version number and exit
    
    With no FILE, or when FILE is -, read standard input. Set the
    PYTHONIOENCODING environment variable to specify the standard
    input character encoding.
    
    Copyright (C) 2013-2014 Remy Oukaour <http://www.remyoukaour.com>.
    MIT License.
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.
