# CoolTeamName's MagicSemanticSearch

Search Magic: The Gathering cards locally via a FastAPI instance and natural-languages queries.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![very: cool](https://img.shields.io/badge/very-cool-red.svg)](https://cdn.7tv.app/emote/01FYSDX96G0001S5T44EC5WAZ7/4x.gif)
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

## Public instance

A public instance is available [here](https://user-victorjean-410393-user-8001.user.lab.sspcloud.fr/pages/).

## Installation

You can deploy this project on your own machine if you want. You will need *Python* and *Postgresql*, and optionnaly *Gum* if you want an automatic setup.

By default, the opened ports of the server will be 8000 for the API and 8001 for the web server, so **remember to open those ports** if you need external access!

### Linux

You will find in `src/utils/automatic_setup` a convenient shell script. In order to have a flawless installation, remember to install [**Gum**](https://github.com/charmbracelet/gum), Python 3.10+ and Postgresql **(with PGVector)**.Then :
1. Install **Gum** if not installed, Python 3.10+ and Postgres database started. _For example, we use SSPCloud to deploy a Postgres Instance and we append its config to our .env_
```
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
sudo apt update && sudo apt install gum
```
2. Clone the repository and cd inside it
3. `cd src/utils/automatic_setup` in the root directory of our project
4. Make the script executable `chmod +x setup.sh`
5. Launch it!
![Made with VHS](https://vhs.charm.sh/vhs-3LV1WGyhjokjAsHeFBmYXX.gif)

### Windows

You are on your own :).

You should at least have Python and Postgres installed and on your Path. 

You could also use WSL.

## Post-install

Once installed, you can relaunch the server easily!
1. Start the API
   `cd <root directory of the project\>`
   
   `export PYTHONPATH=$(pwd)/src`

   `python src`
3. Start the web server
   `cd <root directory of the project\>`

   `cd src && python -m http.server 8001`
### Tests
Install `pytest-cov` with `pip`. Ensure PYTHONPATH is set to `<root_directory/src` and enjoy running `pytest --cov=src/tests src/` ;) (for tests of the project). Then `pytest --cov=src/ src/` (for all tests, including those testing some utils files).

### .env
Our embedding model is *(for now)* hard coded to the sspcloud openwebui api, you can change it if you look a bit in the code. Remember that your .env file should look like this:
```
# Database Configuration
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
LLM_API_KEY=
```

### A word about SSPCloud

SSPCloud is a community platform for public statistics, offering tools and resources for statistical data processing and data science. We are using their API to embed our cards (openwebui api provided by them).

## Work reports

You can find our progress and weekly reports in the `doc/` folder. That is were you will also find our documentation of how we chose to set up this project (class and table diagrams for instance).

## Contribute

Contributions are much appreciated! If you need any help, contact us or make an issue.
Here is a quick explanation of the project's directories:
- **src**: where the core code leaves, you will find inside
    - **business_object**: the business layer where the computing is done
    - **dao**: the dao layer
    - **utils**: tools to set up the project, or programs that are useful to call sometimes for multiple layers
    - **tests**: the directory where you will find some algorithms proving P=NP
    - **pages**: html files for the website
    - **services**: api
    - **static**: css and js files
- **doc**: class diagrams and mandatory files for our school project


## License

[MIT](https://choosealicense.com/licenses/mit/)
