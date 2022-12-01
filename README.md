# Discord bot & botlibre bot

I practiced writing a simple Discord bot. You give it botlibre credentials and Discord bot credentials, it passes messages from Discord bot to botlibre bot and back.

## installation

lulzurl is my own small library for easier http api calls

```bash
pip install discord
pip install lulzurl
```

then you need to fill ```config.py```

- ```token``` is your Discord bot authorization token
- ```robot_id``` is your Discord bot id
- ```application``` is your botlibre bot application id
- ```instance``` is your botlibre bot robot id