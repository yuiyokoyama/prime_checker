import os
from dotenv import load_dotenv
from discord_slash import SlashCommand, SlashContext
import discord
from bs4 import BeautifulSoup
from urllib import request
from urllib import parse


def create_request(query):
    s = parse.quote(query)
    url = f"https://www.amazon.co.jp/s?k={s}&i=instant-video&&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&ref=nb_sb_noss"
    req = request.Request(url)
    req.add_header('Referer', 'http://www.python.org/')
    req.add_header('User-Agent', 'Mozilla/5.0')
    return req


def check_prime(query):
    try:
        req = create_request(query)
        with request.urlopen(req) as res:
            html = res.read().decode('utf-8')
            soup = BeautifulSoup(html)

            first_item = soup.find("div", class_="s-card-container")
            title = first_item.find("span", class_="a-text-normal").text
            price = first_item.find_all(
                "div", class_=["a-row", "a-size-base", "a-color-secondary"])[-1]
            href = first_item.find("a").get('href')
            link = "https://www.amazon.co.jp/" + href
            if price is None:
                price = "無料じゃないよ！"
            else:
                price = price.text.split('、')[-1]
                if "￥0" not in price:
                    price = first_item.find_all(
                        "span", class_=["a-size-mini",
                                        "s-play-button-text",
                                        "aok-relative"])
                    if len(price) == 0:
                        price = "無料じゃないよ！"
                    else:
                        price = price[-1].text

            return title, price, link
    except Exception:
        return None, None, None


intents = discord.Intents.default()
bot = discord.Client(intents=intents)
slash_client = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@slash_client.slash(name="prime", description="prime video に無料であるかな～？")
async def prime(ctx: SlashContext, query: str):
    title, price, link = check_prime(query)
    if title is None:
        await ctx.send(content="ﾅﾝｶｼｯﾊﾟｲｼﾀ!( ﾟДﾟ)ﾉ⌒")
        return

    await ctx.send(content=f"ｺﾚｶ?( ﾟДﾟ)ﾉ⌒ | [{title}]({link}) {price} |")


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    bot.run(TOKEN)
