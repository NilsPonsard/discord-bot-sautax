# sautax-bot

A discord bot written in python

## setup

- place your discord bot token in the `secret` file
- place your riot api key in the `lolKey` file
- place the discord user ID of the admin in the `trustedIDs` file
- compile the [mandelbrot-rust](https://github.com/sautax/mandelbrot-rust), rename it `mandelbrot` and place it in the mandelbrot folder
- have python (>3.5.3) installed on the machine with the `discord.py` framework installed (with [pip](https://pypi.org/project/discord.py/))

## running the bot

You can start the bot by running the `daemon.py` if you want to use the reload functionnality or you can direcly launch `serveur.py`
