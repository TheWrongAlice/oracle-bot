#!/usr/bin/python3
import discord
import asyncio
import httplib2
import json
import re

class Config:
    WIKI = 'http://tibia.fandom.com/'


class TibiaWiki(object):
    @classmethod
    def get_article(cls, title):
        # Get article as JSON
        url = Config.WIKI + 'api.php?action=query&prop=revisions&titles=' + title + '&rvprop=content&format=json'
        resp, data = httplib2.Http().request(url)
        json_data = json.loads(data)

        # TODO: Handle article not found

        return Article(title, json_data)

    @classmethod
    def get_image(cls, title):
        filename = title + '.gif'
        # TODO: I seriously doubt this is the proper way to get images. Read up on it.
        return 'https://vignette.wikia.nocookie.net/tibia/images/5/50/{}/revision/latest?cb=20050417025231&path-prefix=en'.format(filename)

class Article(object):
    def __init__(self, title, json_data):
        self.json_data = json_data
        self.title = title
        self.url = Config.WIKI + 'wiki/' + self.title
        self.text = self.get_content()
        self.infobox = Infobox(self.text)

    def get_content(self):
        # Pull the current revision content
        pages = self.json_data['query']['pages'];
        page = pages[list(pages.keys())[0]]
        text = page['revisions'][0]['*']
        return text

class Infobox(object):
    def __init__(self, raw):
        self.raw = raw

    def get_type(self):
        pattern = r'(?:{{[iI]nfobox )([a-zA-Z]+)(?:\|)'
        search = re.search(pattern, self.raw, re.M|re.I)
        return search.group(1)

    def get_attribute(self, attr):
        pattern = r"(?:\| {}.+= )([a-zA-Z ]+)".format(attr)
        search = re.search(pattern, self.raw, re.M|re.I)
        return search.group(1)

class MessageConstructor(object):
    @classmethod
    def embed_article(cls, article):
        infoboxType = article.infobox.get_type()
        if infoboxType == 'Creature':
            return cls.creature(article)

    @classmethod
    def creature(cls, article):
        embed = discord.Embed(
            title = article.title,
            url = article.url
        )
        embed.set_thumbnail(url=TibiaWiki.get_image(article.title))
        return embed

class OracleBot(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # Don't reply to self
        if message.author == self.user:
            return

        item = TibiaWiki.get_article('Banshee')
        embed = MessageConstructor.embed_article(item)
        tmp = await message.channel.send(embed=embed)

client = OracleBot()
client.run('NTUyOTI5NDQ4ODAyOTEwMjA4.D2P2pw.TeyB7bCTkFFFihOSKEL4KWxUzC0')
