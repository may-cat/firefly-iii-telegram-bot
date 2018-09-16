# Telegram bot for Firefly III (alfa version! Can contain bugs, please send your issues!)

This is bot for [firefly iii](https://github.com/firefly-iii/firefly-iii).

## The idea

Using financial tools needs high level of self-discipline. You need to write down all the transactions every day. Some people can't do that.

This bot reminds you to enter data about your finances and makes some boring operations for you.

That's the easy way for you and your family to manage finances.

### Requirements to Firefly III

Every person that will work with your Firefly III should have it's personal pocket account.

All transactions that bot will create will be attached to budgets, so you should set them.

All transactions should be made in the same currency.

## Self-hosted installation and running

### Installatino ob Ubuntu

Download source code from github (https://github.com/may-cat/firefly-iii-telegram-bot)

Check if python3 and pip3 is installed or install them:

```
apt-get install -y python3 pip3
```

Install python requirements

```
pip3 install -r requirements.txt
```

### Creating telegram bot

Find user `@BotFather` in your telegram. Register new bot with `/newbot` command - you will get access token like this: `677617003:AAEJr4hOJzFGqDNI6CO8jpSJzqdhnNaEghI`.

Copy `config.json.example` to `config.json` and put your access token there.

### Running bot manually

You can run telegram bot manually:

```
python3 bot.py
```

**Notice!** In some countries (for example: in Russia) you can't reach telegram.me server due governement restrictions. Use other country's hosting or VPN, Luke!

### Running bot as daemon

TODO: write algorithm

## Usage

### Connecting

Find your bot (BotFather told you how to do this) and send `/start` command to him. Follow bot's instructions.

It will ask you for your firefly server, for example: `https://demo.firefly-iii.org`.

Then it will ask you for your personal firefly access token. You should  generate it in your Firefly (for example on https://demo.firefly-iii.org/profile page in `Personal Access Tokens` section).

Then bot will ask you to choose account for your pocket. Every day at 8 pm bot will ask you how much money do you have in your pocket. If amount increases - bot asks you, where you got money. If decreases - bot asks you, where did you spend money (on which budget)

### Making transactions

Just tell your bot how much did you spent and some description. For exmaple `12 tea`. Bot will ask you, which budget this transactions should be attached and will add the transaction.

### Sheduled balance actualization

Once a day, at 20:00 bot will ask you, how much money do you have in your pocket.

If amount is more, than firefly III knows for the moment - bot will ask you, from which account did you get the money.

If it's less - bot will calculate the difference and will help you to create transaction for the difference.

## Contribute

Fill free to send you merge requests.

## Contact

You can contact me by e-mail: i@tsupko.tech or by telegram @i_tsupko

## Other stuff

### License

MIT
