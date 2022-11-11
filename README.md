# akm-bot
Scraper and bot that posts items from the Aga Khan Museum's collection every hour.

`bot.py` is deployed as a Google Cloud Function with a Cloud Scheduler triggering every hour. `scraper.py` was only run once to gather data. It is currently unsuitable for automation, but this is partially down to the AKM's website being designed in an unfriendly way for efficient scraping. If I have time, I may rewrite the scraper to try to automate it.

You can see the bot in action at https://twitter.com/agakhanbot.
