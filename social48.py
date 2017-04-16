from discord.ext import commands
import json
import glob
import random

sister_groups = ['nmb48', 'ske48', 'hkt48', 'ngt48', 'nogizaka46', 'jkt48', 'snh48']

class Social48Images(object):
    @staticmethod
    def find_member(target, index):
        return ([e for e in index if len(e['accounts']) > 0 and e['accounts'][0]['handle'].lower() == target.lower()]
                or
                [e for e in index if e['engNick'].lower() == target.lower()] + \
                [e for e in index if e['engName'].lower()  == target.lower().replace('-', ' ')] + \
                [e for e in index if e['jpnName']  == target]
                or 
                [e for e in index if target.lower() in e['engName'].lower()] + \
                [e for e in index if target.lower().replace('-', ' ') in e['tags']]
                or
                [])

    @staticmethod
    def guess_group(item):
        # todo: make this less fiddly
        if item['type'] in ('member', 'group'):
            if 'akb48' in item['tags'] and 'kennin' not in item['tags']:
                return 'akb48'
            else:
                for group in sister_groups:
                    if group in item['tags']:
                        return group
                else:
                    return 'other'
        else:
            return item['type']

    def __init__(self, bot):
        self.bot = bot
        self.root = '/library/media/akb48/social48/services/'
        self.rng = random.Random()
        self.rng.seed()

        self.services = {
            'ameblo': 'ameblo/{group}/', 
            'gplus': 'gplus/{group}/', 
            'twitter': 'twitter/{group}/', 
            'instagram': 'instagram/', 
            'nanagogo': 'nanagogo/',
            'nogizaka46-blog': 'nogizaka46-blog/'
        }
        with open('/library/media/akb48/social48/social48_index.json', encoding='utf8') as infp:
            self.index = json.load(infp)['members']
        
    @commands.command(name="social48", pass_context=True)
    async def social48(self, context, target="akb48"):
        # find member accounts, pick a random image
        
        for term in ['yoona']:
            if term in target.lower():
                target = 'akb48'
        
        found = self.find_member(target, self.index)
        if len(found) == 0:
            await self.bot.say('Could not find anything matching "{}"'.format(target))
            return 
        
        while found:
            member = found.pop(self.rng.randint(0,len(found)-1))
            group = self.guess_group(member)
            
            if len(member['accounts']) == 0:
                continue
            
            directories = []
            for account in member['accounts']:
                if account['service'] in self.services:
                    new_dir = self.root + self.services[account['service']].format(group=group) + account['handle'] + '/'
                    # await self.bot.say(new_dir)
                    directories.append(new_dir)

            images = []
            for d in directories:
                # await self.bot.say(d)
                # found_images = glob.glob(d + "*/*.jpg"
                images.extend(glob.glob(d + "*/*.jpg"))
            # for i in range(10):
            #    await self.bot.say(images[i])
            if len(images) == 0:
                continue
            else:
                image_file = images[self.rng.randint(0,len(images)-1)]
                break
        else:
            await self.bot.say('Found no images matching "{}"'.format(target))
            return
        
        # await self.bot.say(image_file)
        await self.bot.send_file(context.message.channel, image_file)

def setup(bot):
    soc = Social48Images(bot)
    bot.add_cog(soc)
