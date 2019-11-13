
# Converter for PG SIS timetable to make it more compact
## And you can override styles easily too

### Setup ###

``` 
sudo apt install python3-pip

# optional, if you don't want to install python packages globally:
sudo apt install virtualenv
virtualenv -p python3 .venv
source .venv/bin/activate
# end of optional part

pip3 install -r requirements.txt
```

### Usage examples: ###
```
python3 convert.py -i SIS.html -o sisteme.html
python3 convert.py -i SIS.html -o out.html -m "EA 503,pt,9->sr,16"
python3 convert.py -i SIS.html -o out.html -m "9,EA 503,pt->7"
python3 convert.py -i SIS.html -o out.html -m "EA 503,9,pt->7;EA 06,pt,7->pn;NE 110,czw"
```

### Arguments: ###
- `-i`, `-in`, `--input` specifies source filename
- `-o`, `-out`, `--output` specifies source filename
- `-m` or `--move` specifies string to move courses around.

General pattern looks like: `move_from->move_to` or `move_from->move_to;move_from->move_to;...`.

`move_from` is room, day and hour separated with a comma, e.g. `EA 503,pt,9` with no particular order.

`move_to` is like `move_from` but without room and day or hour may be omitted. In such case day/hour will be taken from `move_from`.

Day is one of: `pn`, `wt`, `sr`, `czw`, `pt`.

**Examples:**
- `-m "EA 31,pn,10->7;EA 31,pn,12->9"`
- `-m "EA 06,sr,14->pn"`
- `-m "EA 06,sr,14->7"`
- `-m "EA 06,sr,14->pn,7"`
