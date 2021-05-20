from telethon import TelegramClient
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import yaml
from typing import Dict, List
import argparse
import time

def load_config(path: str = None) -> Dict:
    with open(path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)
            raise FileNotFoundError(exc)
    return config


async def sendMesssage(data: Dict) -> None:
    for dest in config["telegram"]["destinations"]:
        entity = await client.get_entity(dest)
        await client.send_message(entity=entity, message=str(data))


def getPrice() -> bool:
    sentMessage = True
    for pair in config["binance"]["pairs"]:
        name = config["binance"]["pairs"][pair]["name"]
        limit = config["binance"]["pairs"][pair]["limit"]
        price = binance_client.get_avg_price(symbol=name)
        if int(float(price["price"])) < int(limit):
            with client:
                client.loop.run_until_complete(
                    sendMesssage({"name": name, "price": price["price"]})
                )
            sentMessage = False
    return sentMessage


def main():
    flag = True
    while flag:
        flag = getPrice()
        time.sleep(300)
    print("Exit the code")


parser = argparse.ArgumentParser(description="ETH price telegram bot")
parser.add_argument("--config", "-c", required=False, help="Config yaml location")
args = parser.parse_args()

if __name__ == "__main__":
    config = load_config(args.config)
    api_id = config["telegram"]["api_id"]
    api_hash = config["telegram"]["api_hash"]
    bot_token = config["telegram"]["bot_token"]
    api_key = config["binance"]["api_key"]
    api_secret = config["binance"]["api_secret"]
    binance_client = Client(api_key, api_secret)
    client = TelegramClient("krishna", api_id, api_hash).start(bot_token=bot_token)
    main()
