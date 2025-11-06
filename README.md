# CoolTeamName's MagicSemanticSearch

Search Magic: The Gathering cards locally via a FastAPI instance and natural-languages queries.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

```
                             /\
                            /  \
                           |    |
                         --:'''':--
                           :'_' :
                           _:"":\___
            ' '      ____.' :::     '._
           . *=====<<=)           \    :
            .  '      '-'-'\_      /'._.'
                             \====:_ ""
                            .'     \\
                           :       :
                          /   :    \
                         :   .      '.
         ,. _        snd :  : :      :
      '-'    ).          :__:-:__.;--'
    (        '  )        '-'   '-'
 ( -   .00.   - _
(    .'  _ )     )
'-  ()_.\,\,   -
```

## Installation

You can deploy this project on your own machine if you want. You will need *Python* and *Postgresql*, and optionnaly *Gum* if you want an automatic setup.

### Linux


You will find in `src/utils/automatic_setup` a convenient shell script. In order to have a flawless installation, remember to install Gum, Python and Postgresql.Then :
1. `cd src/utils/automatic_setup` in the root directory of our project
2. Make the script executable `chmod +x setup.sh`
3. Launch it!
![Made with VHS](https://vhs.charm.sh/vhs-3LV1WGyhjokjAsHeFBmYXX.gif)

### Windows

You are on your own :).

You should at least have Python and Postgres installed and on your Path. 

You could also use WSL.

### A word about SSPCloud

SSPCloud is a community platform for public statistics, offering tools and resources for statistical data processing and data science. We are using their API to embed our cards (openwebui api provided by them).

## Usage

### Public instance

Our final goal is for you to be able to access a deployed fastAPI instance/web interface where you can search for Magic the Gathering cards using natural language queries.

But for now you have to run the code locally xP.

## Work reports

You can find our progress and weekly reports in the `doc/` folder. That is were you will also find our documentation of how we chose to set up this project (class and table diagrams for instance).

## License

[MIT](https://choosealicense.com/licenses/mit/)