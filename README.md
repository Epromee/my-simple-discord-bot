# Discord bot & librebot bot

I practiced writing a simple Discord bot. You give it librebot credentials and Discord bot credentials, it passes messages from Discord bot to librebot bot and back.

## installation

lulzurl is my own small library for easier http api calls

```bash
pip install discord
pip install lulzurl
```

then you need to fill ```config.py```

- ```token``` is your Discord bot authorization token
- ```robot_id``` is your Discord bot id
- ```application``` is your librebot bot application id
- ```instance``` is your librebot bot robot id