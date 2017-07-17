from discord.ext import commands
import json
import glob
import random
import datetime
import calendar
sister_groups = ['nmb48', 'ske48', 'hkt48', 'ngt48', 'nogizaka46', 'jkt48', 'snh48']

from discord.embeds import Embed





class Social48Images(object):
    @staticmethod
    def list_previous_months(count=3):
        curr_date = datetime.datetime.now()
        def get_prev_month(year, month):
            if month == 1:
                year, month = year-1, 12
            else:
                month -= 1
            return year, month

        months = []
        year, month = curr_date.year, curr_date.month
        for _ in range(count):
            months.append('{}-{:02d}'.format(year, month))
            year, month = get_prev_month(year, month)
        return months

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
    
    @commands.command(pass_context=True)
    async def test(self, context):
        video_url = 'https://video.twimg.com/ext_tw_video/886927908026974208/pu/vid/720x720/80aBs03U6PRl4XEW.mp4'
        video_url2 = 'https://moviestat.7gogo.jp/output/gN3r1SOGblf9GtN76wEuUm==/hq/EIOglrc4OQGAsjgE2zkduNq2.mp4'
        embed = Embed()
        embed._video = {
            "url": video_url,
            "height": 720,
            "width": 720
        }
        embed.add_field(name="Test", value="test")

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def usage(self, context):
        owner = await self.bot.get_user_info(self.bot.settings.owner)
        await self.bot.say("""Extended Usage:
    [p]social48 [option:value] [now] [recent] Member Name

Unfortunately due to the way the bot finds images there are a lot of idiosyncrasies.

For example:
    * Some members' nicknames will work. Most of them won't.
    * Spelling is usually Wiki48 spelling, except when it isn't (e.g. `Cho Kurena`)
    * Individual NGT48 members are not available, but try just "ngt48"
    * Asking for a Team 8 member will pull a random photo from every girl in her region.
    * Nogizaka46 is available, except for 3rd gen.
    * No Keyakizaka46
    * No group without public social media (e.g. STU48, AKB48 16th gen)
    * A handful of (mainly graduated(?) Nogi) accounts are filled with seemingly random AKB48 photos. If you find one of these please PM {} with the name and image url.

------

As of 2017-07-17, new experimental options are available: ```
recent           last three months
now              this month
recent:N         N == number of months previous
now:N            N == number of months previous 
                 (same as recent)
dates:YYYY-MM    year and month to search 
                 can omit the month
                 separate multiple dates with commas
                 e.g. 2017-01,2017-03```
Simply type them anywhere after the command (in addition to the member name):```
[p]social48 Muto Tomu recent
[p]social48 recent Tomu
[p]social48 Murayama dates:2014-01,2014-02,2014-03 Yuiri
[p]social48 akb48 recent:2```""".format(owner.mention))

    @commands.command(name="social48", pass_context=True, aliases=["s48", "s"])
    async def social48(self, context, *target):
        """Simple 48g (and Nogi) image bot.

        Default [p]refix: #!

        Aliases: social48, s48, s

        Basic usage:
            [p]social48 Muto Tomu
            [p]social48 recent Tomu

        Type [p]usage for (much) more
        """
        # find member accounts, pick a random image
        options = {}

        if not target:
            target = ['akb48']
        else:
            target = list(target)
            option_indices = []
            for item in target:
                if ':' in item:
                    option_indices.append(target.index(item))
            count = 0

            for index in option_indices:
                opt_str = target.pop(index-count)
                count += 1
                opt_name, opt_val = opt_str.split(':', 1)
                if opt_name in options:
                    # TODO: make sure to check for this when processing options too
                    # a more robust solution would only make lists out of options that are supposed to have multiple values, but i don't even know what options i'm going to include yet
                    try:
                        options[opt_name].append(opt_val)
                    except AttributeError:
                        options[opt_name] = [options[opt_name], opt_val]
                else:
                    if ',' in opt_val:  # multiple values, review this character
                        opt_val = opt_val.split(',')
                    options[opt_name] = opt_val

            if 'now' in target:
                target.remove('now')
                options['now'] = 1
            elif 'recent' in target:
                target.remove('recent')
                options['recent'] = 3
            # if options:
            #     await self.bot.say('WARNING: Options are highly experimental and volatile, and may change at any moment. As of writing, "dates" is the only option available.\n'
            #                        "Found Options: {}".format(list(options.keys())))
            
            target = ' '.join(target)

        if target.lower() in ('ngt48', 'ngt'):
            target = 'NGT48_Info_bot'

        for term in ('yoona',):
            if term in target.lower():
                target = 'akb48'
        
        found = self.find_member(target, self.index)
        if len(found) == 0:
            await self.bot.say('Could not find anything matching "{}"'.format(target))
            return 
        
        # TODO: accept options like "year", "recent", etc.
        match_dates = options.get('dates', [""])
        if match_dates in ("now", "recent") or options.get("now", None) is not None or options.get("recent", None) is not None:
            num_months = options.get("now", None) or options.get("recent", None) or 3
            match_dates = self.list_previous_months(int(num_months))

        if not isinstance(match_dates, list):
            match_dates = [match_dates]

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
                for date in match_dates:
                    images.extend(glob.glob(d + "{}*/*.jpg".format(date)))
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
