import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import *
from telegram.ext import *

from cSRC.inf import env as ENV
from cSRC.dbUser import dbUser as USER
from cSRC.dbUser import Admins as ADMINS
from cSRC.dbUser import AdditionalData as ADATA
from cSRC.dbUser import Acc as ACC
from cSRC.dbUser import Bids as BIDS
from cSRC.TokenHandler import TokenHandler, text_transaction_details
from datetime import datetime, timedelta
import random
from captcha.image import ImageCaptcha
from web3 import Web3, Account
from cSRC.walletManager import (
    checkETHBalance,
    checkUSDCBalance,
    calculate_gas_and_eth,
    send_usdt_transaction,
)
import json
import time
import uuid
from random import randint
import asyncio
from cSRC.sha import encrypt as ENCRIPTER
from cSRC.sha import verify as VERIFY_ENCRIPTION

HTML = "HTML"
WALLET_UPDATE = "WALLET_UPDATE"
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.

INLINE_KEYBOARD_1 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Rules", callback_data="Rules"),
            InlineKeyboardButton("Balance", callback_data="Balance"),
        ],
        [
            InlineKeyboardButton("Deposit", callback_data="Deposit"),
            InlineKeyboardButton("Withdraw", callback_data="Withdraw"),
        ],
        [
            InlineKeyboardButton("Airdrop", callback_data="airdrop"),
            InlineKeyboardButton("Stats", callback_data="Stats"),
        ],
        [
            InlineKeyboardButton("Referral Link", callback_data="Referral_Link"),
            InlineKeyboardButton("Play", url="https://t.me/radbidy"),
        ],
    ]
)
SEPERATOR = "__--__"
PLACED_BID = "placed_bid"
WINED_BID = "wined"
REFER_MONEY = "refer_money"


async def no_sk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.message.chat_id, text="No sk tell the admins to activate the bot"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    user = update.effective_user
    if update.message.chat.type == "private":
        # remove_job_if_exists(WALLET_UPDATE,context)
        # context.job_queue.run_repeating(check_if_tx,timedelta(seconds=60),name=WALLET_UPDATE)
        referrable = False
        if not USER.get_user_by_id(user.id):
            newUser = USER(
                user.id,
                user.username,
                str(datetime.now()),
                False,
                random.randint(100, 999),
                0,
                None,
            )
            newUser.create()
            referrable = True
        elif (
            USER.get_user_by_id(user.id).is_human == False
            or USER.get_user_by_id(user.id).refered_by == None
        ):
            referrable = True
        if referrable:
            refferer_id = (
                update.message.text.split()[1]
                if len(update.message.text.split()) > 1
                else None
            )
            if refferer_id:
                if USER.get_user_by_id(int(refferer_id)):
                    refferer = USER.get_user_by_id(int(refferer_id))
                    refferer.referral_points += 1
                    refferer.save()
                    getUser = USER.get_user_by_id(user.id)
                    getUser.refered_by = refferer_id
                    getUser.save()
                else:
                    await update.message.reply_text("Wrong referral link")

        user_data = USER.get_user_by_id(user.id)
        if user_data:
            if not user_data.is_human:
                image = ImageCaptcha(fonts=["font/LGB.ttf"])
                await update.message.reply_photo(
                    image.generate(user_data.captcha),
                    caption="""Please verify you are human by verifying CAPTCHA""",
                    parse_mode=HTML,
                )
            else:
                await context.bot.send_message(
                    user.id,
                    f"""
Your Referral link :
<code>https://t.me/{context.bot.username}?start={user.id}</code>
Earn 10% in USDC in real time for everyone you refer.
""",
                    parse_mode=HTML,
                    reply_markup=INLINE_KEYBOARD_1,
                )
    # else:
    #     reply_markup = ReplyKeyboardMarkup([['BID']],resize_keyboard=True)
    #     await context.bot.send_message(update.message.chat_id,f'Click the BID button to place a bid ',parse_mode=HTML,reply_markup=reply_markup)


async def check_if_tx(context: ContextTypes.DEFAULT_TYPE) -> None:
    datas = TokenHandler()
    print(datas)
    if len(datas) > 0:
        group_data = ADATA.get_group_by_id(1)
        if int(datas[-1]["blockNumber"]) == int(group_data.last_block):
            return
        group_data.last_block = int(datas[-1]["blockNumber"])
        group_data.save()

        for data in datas:
            if int(data["blockNumber"]) > int(group_data.last_block):
                await context.bot.send_message(
                    ADATA.get_group_by_id(1).chat_id,
                    text_transaction_details(data),
                    parse_mode=HTML,
                )


async def user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    for new_member in update.message.new_chat_members:
        user = new_member
        if user.id == context.bot.id:
            return
        await update.message.reply_html(
            rf"""
Hi {user.mention_html()}!{ADATA.get_group_by_id(1).welcome_text}
            """,
            reply_markup=ReplyKeyboardMarkup([["BID"]], resize_keyboard=True)
            if BIDS.get_bid_by_id(ENV.bid_id).is_valid
            else None,
        )
        if not USER.get_user_by_id(user.id):
            newUser = USER(
                user.id,
                user.username,
                str(datetime.now()),
                False,
                random.randint(100, 999),
                0,
                update.message.chat_id,
            )
            newUser.create()
        user_data = USER.get_user_by_id(user.id)
        user_data.chat_id = update.message.chat_id
        user_data.save()
        if not user_data.is_human:
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Verify",
                            url=f"https://t.me/{context.bot.username}?start=",
                        )
                    ]
                ]
            )
            await update.message.reply_text(
                f"{user.mention_html()} First Verify that you are a human",
                parse_mode=HTML,
                reply_markup=reply_markup,
            )
            await context.bot.ban_chat_member(update.message.chat_id, user.id)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    if update.message.chat.type == "private":
        user = update.effective_user
        if update.message.text.split()[1] == ENV.ADMIN_PASSWORD:
            if not ADMINS.is_admin(user.id):
                new_entry = ADMINS(user.id)
                new_entry.create()
            reply_markup = ReplyKeyboardMarkup([["DataBase"]], resize_keyboard=True)
            await update.message.reply_text(
                "logged in as an admin", reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("Wrong password please try again")


async def change_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    if update.message.chat.type == "private":
        user = update.effective_user
        if ADMINS.is_admin(user.id):
            new_welcome_text = update.message.text.replace("/change_text", "")
            get_group = ADATA.get_group_by_id(1)
            get_group.welcome_text = new_welcome_text
            get_group.save()
            await update.message.reply_text("Successfully changed the text")
        else:
            await update.message.reply_text("Please login first")


# NOT USED
# INLINE
async def bid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        return
    user = update.effective_user
    if not update.message.chat.type == "private":
        new_bid = BIDS(
            update.message.id,
            user.id,
            str(datetime.now()),
            "",
            "0",
            "",
            update.message.chat_id,
            "5",
            True,
        )
        new_bid.create()
        inline_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Bid", callback_data="bid" + SEPERATOR + str(new_bid.id)
                    )
                ]
            ]
        )
        await update.message.reply_text(
            f"""
A bid is started by @{user.mention_html()}
Click the button below to join the bid
""",
            reply_markup=inline_markup,
            parse_mode=HTML,
        )


# rules button


async def rulesHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        return
    await context.bot.send_message(
        update.from_user.id,
        """
What's Rad-Bid?
Think of Rad-Bid as your virtual playground for crypto auctions where you bid with USDC and win USDC instantly.

Alpha Launch Alert! - BASE CHAIN EXCLUSIVE
For our Alpha launch, we're starting with a $100 auction, and guess what? You can join the fun with just $1 worth of USDbC (USDC on Base Chain). Plus, we've got more exciting auctions coming your way soon! 🚀

How Does it Work? - PUBLIC ALPHA 🌟

1. Top-Up Your Wallet: First things first, load up your Rad-Bid wallet with some cool USDbC and ETH. It's like fuel for your crypto adventure.

2. Make Your Bids: Each bid you make costs you just $1 in USDbC, plus network fees paid in ETH.

3. Auction Time: When an auction starts, it becomes a race against the clock! The timer begins when the first bid lands, and if another bid is confirmed within the auction time, the timer resets. This process continues until there are no further bids and the timer reaches zero – with the winner being the last person to bid when the timer runs out.

4. Winner, Winner!: If you're the last one to bid when the clock runs out, you win and you get your pool prize in just a few seconds, deposited right into your Rad-Bid wallet.

5. Get Your Friends in on the Fun: Wanna share the excitement with your pals? You can earn 10% of what they spend when they join in on the fun. Just hit that referral button and grab your unique link!

Important Stuff to Remember
- All your bids are final – no take-backsies! So make 'em count!
- All assets are on Base Chain!

So, there you have it, Rad-Bid in a nutshell! It's like a thrilling game where you use crypto to win more crypto. Time to get bidding and have a blast in the world of cryptocurrency auctions! 🚀💰
""",
        parse_mode=HTML,
    )


async def checkBalance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        return
    user_data = USER.get_user_by_id(update.from_user.id)
    if user_data:
        account = ACC.get_acc_by_id(user_data.id)
        if account:
            balanceETH = checkETHBalance(account.address)
            balanceUSDC = checkUSDCBalance(account.address)
            await context.bot.send_message(
                update.from_user.id,
                f"""
<b>Balance</b>
ETH : {balanceETH}
USDC : {balanceUSDC/1000000}
""",
                parse_mode=HTML,
            )


async def depositBalance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        return
    user_data = USER.get_user_by_id(update.from_user.id)
    if user_data:
        account = ACC.get_acc_by_id(user_data.id)
        if account:
            await context.bot.send_message(
                update.from_user.id,
                f"""
<b>Deposit USDbC and ETH for GAS on BASE Chain to your wallet : </b>
Wallet Address :<code> {account.address} </code>
""",
                parse_mode=HTML,
            )


# bid inline join button
async def joinBidHandler(update: Update, context: ContextTypes.DEFAULT_TYPE, bid_id):
    if ENV.SK_STATUS == False:
        return
    bid_data = BIDS.get_bid_by_id(bid_id)
    if bid_data:
        if bid_data.is_valid:
            bid_data.user_joined = SEPERATOR.join(
                bid_data.user_joined.replace(" ", "").split(SEPERATOR)
                + [str(update.from_user.id)]
            )
            print(bid_data.user_joined)
            bid_data.save()
            inline_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "+ Join the bid",
                            callback_data="bid" + SEPERATOR + str(bid_data.id),
                        )
                    ]
                ]
            )
            await context.bot.send_message(
                chat_id=bid_data.chat_id,
                text=f"""An user has joined the bid\nBID ID:{bid_data.id}\nUser Name : {update.from_user.mention_html()}""",
                parse_mode=HTML,
                reply_markup=inline_markup,
            )
        else:
            await context.bot.send_message(
                bid_data.chat_id, text="The bid is already expired"
            )
    pass


async def callbackHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    callback_data = query.data
    print(query.from_user.id)
    print(callback_data)
    if callback_data == "Rules":
        await rulesHandler(query, context)
    elif callback_data == "Balance":
        await checkBalance(query, context)
    elif callback_data == "Referral_Link":
        await context.bot.send_message(
            query.from_user.id,
            f"""
Your referral link -
<code>https://t.me/{context.bot.username}?start={query.from_user.id}</code>

Refer your friends and instantly earn 10% in USDC every time they place a bid. It's that simple and exciting! 💰🚀
""",
            parse_mode=HTML,
        )
        await context.bot.send_message(
            query.from_user.id,
            f"""Follow us on Twitter - https://twitter.com/radbid_""",
            parse_mode=HTML,
            reply_markup=INLINE_KEYBOARD_1,
        )
    elif callback_data == "Deposit":
        await depositBalance(query, context)
    elif callback_data == "airdrop":
        await context.bot.send_message(query.from_user.id, f"Coming soon")

    elif callback_data == "Withdraw":
        user_data = USER.get_user_by_id(query.from_user.id)
        if user_data:
            user_data.step = "get_pk"
            user_data.save()
            await context.bot.send_message(
                query.from_user.id, f"Please enter the password to verify"
            )
    elif callback_data == "set_password":
        user_data = USER.get_user_by_id(query.from_user.id)
        if user_data:
            user_data.step = "set_password"
            user_data.save()
            await context.bot.send_message(
                query.from_user.id,
                f"<b>Create PIN. The PIN must be equal to or greater than 6 digits.</b>",
                parse_mode=HTML,
            )
            await context.bot.delete_message(query.from_user.id, query.message.id)
    elif callback_data.split(SEPERATOR)[0] == "bid":
        await joinBidHandler(query, context, callback_data.split(SEPERATOR)[1])
    elif callback_data == "Stats":
        user_data = USER.get_user_by_id(query.from_user.id)
        user_account = ACC.get_acc_by_id(user_data.id)
        user_account.transactions = (
            "" if user_account.transactions == None else user_account.transactions
        )
        user_account.save()
        all_tx = user_account.transactions.split(SEPERATOR)
        for i in range(len(all_tx)):
            if "" in all_tx:
                all_tx.remove("")
        total_balance = 0
        for tx in all_tx:
            data = json.loads(tx)
            try:
                if data["type"] == PLACED_BID:
                    total_balance += float(data["amount"])
            except:
                print("Data error at stats")

        total_refered = USER.query_by_field("refered_by", user_data.id)
        await context.bot.send_message(
            query.from_user.id,
            f"<b>Total amount bid: ${float(total_balance):05.2f}\nNumber of users referred: {len(total_refered)}\nReferral fees earned: ${float(user_data.earned_from_referral):05.2f}</b>",
            parse_mode=HTML,
        )


async def sync_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    user = update.effective_user
    if not update.message.chat.type == "private":
        if ADMINS.is_admin(user.id):
            grp = ADATA.get_group_by_id(1)
            grp.chat_id = update.message.chat_id
            grp.save()
            bid_data = BIDS.get_bid_by_id(ENV.bid_id)
            if bid_data:
                bid_data.chat_id = grp.chat_id
                bid_data.is_valid = True
                bid_data.user_joined = ""
                bid_data.total_invested = 0
                bid_data.date_created = str(datetime.now())
                bid_data.save()
                await update.message.reply_text(
                    "updated bid data",
                    reply_markup=ReplyKeyboardMarkup([["BID"]], resize_keyboard=True),
                )
            await update.message.reply_text("Successfully synced the group")
        else:
            await update.message.reply_text("This command only can be used by admins")


async def walletHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    user = update.effective_user
    user_data = USER.get_user_by_id(user.id)
    wallet = ACC.get_acc_by_id(user.id)
    if user_data:
        if not wallet:
            w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))
            account = w3.eth.account.create()
            wallet_address = account.address
            private_key = w3.to_hex(account._private_key)
            encryption = str(uuid.uuid4())
            encrypted_private_key = w3.eth.account.encrypt(
                private_key, str(encryption) + ENV.SK
            )
            new_wallet = ACC(
                user_data.id,
                user.username,
                str(datetime.now()),
                str(json.dumps(encrypted_private_key)),
                "",
                wallet_address,
                encryption,
            )
            new_wallet.create()
        wallet = ACC.get_acc_by_id(user_data.id)
        if wallet:
            return wallet
        return None
    return None


async def sendWithdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_data = USER.get_user_by_id(user.id)
    if user_data:
        user_data.step = ""
        user_data.save()
        await update.message.reply_text("Unavailable function")
    pass


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def resetBID(context: ContextTypes.DEFAULT_TYPE) -> None:
    remove_job_if_exists("reset_bid_timer_1", context)
    remove_job_if_exists("reset_bid_timer_2", context)
    bid_data = BIDS.get_bid_by_id(ENV.bid_id)
    bid_data.is_valid = True
    bid_data.total_invested = "0"
    bid_data.user_joined = ""
    bid_data.save()
    await context.bot.send_message(
        bid_data.chat_id,
        "⚡️ Bidding is LIVE! ⚡️ Who will be the last one standing? 🌪",
        reply_markup=ReplyKeyboardMarkup([["BID"]], resize_keyboard=True),
    )
    pass


async def resetBidPrompts1(context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(
        str(ENV.time_reset_remaining.total_seconds())
        + " "
        + str(ENV.prompt_reset_time_delta_1.total_seconds())
    )
    if (
        ENV.time_reset_remaining > 2 * ENV.prompt_reset_time_delta_1
        and ENV.time_reset_remaining <= 3 * ENV.prompt_reset_time_delta_1
    ):
        ENV.time_reset_remaining -= ENV.prompt_reset_time_delta_1
        bid_data = BIDS.get_bid_by_id(ENV.bid_id)
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
Bidding opens in {int(ENV.time_reset_remaining.total_seconds()/60)} mins - set those alarms! ⏰
""",
        )
    elif (
        ENV.time_reset_remaining > 1 * ENV.prompt_reset_time_delta_1
        and ENV.time_reset_remaining <= 2 * ENV.prompt_reset_time_delta_1
    ):
        ENV.time_reset_remaining -= ENV.prompt_reset_time_delta_1
        bid_data = BIDS.get_bid_by_id(ENV.bid_id)
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
Just {int(ENV.time_reset_remaining.total_seconds()/60)} mins until BIDs unlock - wallets loaded? 💰
""",
        )


async def resetBidPrompts2(context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(
        str(ENV.time_reset_remaining.total_seconds())
        + " "
        + str(ENV.prompt_reset_time_delta_1.total_seconds())
    )
    if (
        ENV.time_reset_remaining >= 2 * ENV.prompt_reset_time_delta_2
        and ENV.time_reset_remaining < 3 * ENV.prompt_reset_time_delta_2
    ):
        bid_data = BIDS.get_bid_by_id(ENV.bid_id)
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
{int(ENV.time_reset_remaining.total_seconds()/60)} mins left - feel the excitement ignite! 🔥
""",
        )
        ENV.time_reset_remaining -= ENV.prompt_reset_time_delta_2
    elif (
        ENV.time_reset_remaining >= 1 * ENV.prompt_reset_time_delta_2
        and ENV.time_reset_remaining < 2 * ENV.prompt_reset_time_delta_2
    ):
        bid_data = BIDS.get_bid_by_id(ENV.bid_id)
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
{int(ENV.time_reset_remaining.total_seconds()/60)} min 'til BID time - brace yourselves! 🚀
""",
        )
        ENV.time_reset_remaining -= ENV.prompt_reset_time_delta_2
    elif ENV.time_reset_remaining <= ENV.prompt_reset_time_delta_1:
        ENV.time_reset_remaining -= ENV.prompt_reset_time_delta_2


async def bidTimer(context: ContextTypes.DEFAULT_TYPE) -> None:
    ENV.time_remaining -= ENV.update_time_delta

    bid_data = BIDS.get_bid_by_id(ENV.bid_id)
    if ENV.time_remaining <= timedelta(seconds=0):
        await context.bot.send_message(
            bid_data.chat_id,
            f"Announcing winners 👀🌈",
            reply_markup=ReplyKeyboardRemove(),
        )
        await asyncio.sleep(3)

    if ENV.time_remaining <= timedelta(seconds=0):
        remove_job_if_exists("bid", context)
        await context.bot.send_chat_action(
            bid_data.chat_id, constants.ChatAction.TYPING
        )
        all_users = bid_data.user_joined.split(SEPERATOR)
        if "" in all_users:
            all_users.remove("")
        try:
            winner = all_users[-1]
        except:
            winner = None
        user_data = USER.get_user_by_id(winner)
        # if user_data:
        # if user_data.refered_by:
        #     referer = USER.get_user_by_id(user_data.refered_by)
        #     if referer:
        #         referer.earned_from_referral = 0.0 if referer.earned_from_referral == None or referer.earned_from_referral=='' or referer.earned_from_referral=='0' else referer.earned_from_referral
        #         referer.earned_from_referral = float(referer.earned_from_referral)+0.1*bid_data.total_invested
        #         referer.save()
        total_invested = bid_data.total_invested  # Saves for reuse
        bid_data.total_invested = 0
        bid_data.user_joined = ""
        bid_data.is_valid = False
        bid_data.save()
        remove_job_if_exists("reset_bid", context)
        context.job_queue.run_once(
            resetBID, ENV.bid_reset_delta, name="reset_bid", chat_id=bid_data.chat_id
        )
        ENV.time_reset_remaining = ENV.bid_reset_delta
        remove_job_if_exists("reset_bid_timer_1", context)
        remove_job_if_exists("reset_bid_timer_2", context)
        context.job_queue.run_repeating(
            resetBidPrompts1,
            ENV.prompt_reset_time_delta_1,
            name="reset_bid_timer_1",
            chat_id=bid_data.chat_id,
        )
        context.job_queue.run_repeating(
            resetBidPrompts2,
            ENV.prompt_reset_time_delta_2,
            name="reset_bid_timer_2",
            chat_id=bid_data.chat_id,
        )

        if user_data:
            get_user = await context.bot.get_chat_member(bid_data.chat_id, user_data.id)
            await context.bot.send_message(
                bid_data.chat_id,
                f"The winner is {get_user.user.mention_html()} 🥳🙌🏼",
                parse_mode=HTML,
            )
            print(total_invested)
            tx = await send_usdt_transaction(
                ACC.get_acc_by_id(111), ACC.get_acc_by_id(user_data.id), ENV.PRIZE
            )
            try:
                tx = await tx
                # if tx:
                winner_account = ACC.get_acc_by_id(user_data.id)
                winner_account.transactions = SEPERATOR.join(
                    winner_account.transactions.split(SEPERATOR)
                    + [
                        json.dumps(
                            {
                                "tx": tx,
                                "type": WINED_BID,
                                "date": str(datetime.now()),
                                "amount": total_invested,
                            }
                        )
                    ]
                )
                winner_account.save()
                await context.bot.send_message(
                    bid_data.chat_id,
                    f"""
💥 Winner paid - <a href='https://basescan.org/tx/{tx}'>TX#</a> 💥
""",
                    parse_mode=HTML,
                )
            except:
                await context.bot.send_message(
                    bid_data.chat_id,
                    f"<b>Payment issue: Admin wallet lacks funds to pay the winner. Please DM us your bid info (screenshot, timestamp, and TX), and we'll swiftly resolve this matter. </b>",
                    parse_mode=HTML,
                )

        await context.bot.send_message(
            bid_data.chat_id,
            f"Next round in {ENV.BID_RESET_DELTA_MINUTES} mins - stay tuned! 👽",
            parse_mode=HTML,
        )
        remove_job_if_exists("bid", context)
        return

    remove_job_if_exists("bid", context)
    context.job_queue.run_repeating(
        bidTimer, ENV.update_time_delta, name="bid", chat_id=bid_data.chat_id
    )

    if (
        ENV.time_remaining > timedelta(seconds=0)
        and ENV.time_remaining <= 1 * ENV.update_time_delta
    ):
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
Last call for bidders 👀 {int(ENV.time_remaining.total_seconds())} seconds remain!
""",
        )
    elif (
        ENV.time_remaining > 1 * ENV.update_time_delta
        and ENV.time_remaining <= 2 * ENV.update_time_delta
    ):
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
{int(ENV.time_remaining.total_seconds())} seconds till close ⏳
""",
        )
    elif (
        ENV.time_remaining > 2 * ENV.update_time_delta
        and ENV.time_remaining <= 3 * ENV.update_time_delta
    ):
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
The round closes in {int(ENV.time_remaining.total_seconds())} seconds ⏱
Click BID 👇🏻 to join now!!
""",
        )
    elif (
        ENV.time_remaining == 4 * ENV.update_time_delta
        or ENV.time_remaining == 6 * ENV.update_time_delta
    ):
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
The round closes in {int(ENV.time_remaining.total_seconds())} seconds ⏱
Click BID 👇🏻 to join now!!
""",
        )

    pass


background_tasks = set()
import time


async def txtoReferrer(
    amount: float, from_account: ACC, refferer_acc: ACC, referer: USER
) -> bool:
    tx__ = await send_usdt_transaction(from_account, refferer_acc, float(amount))
    try:
        tx__ = await tx__
        referer.earned_from_referral = (
            0.0
            if referer.earned_from_referral == None
            or referer.earned_from_referral == ""
            or referer.earned_from_referral == "0"
            else referer.earned_from_referral
        )
        referer.earned_from_referral = float(referer.earned_from_referral) + amount
        refferer_acc.transactions = (
            "" if refferer_acc.transactions == None else refferer_acc.transactions
        )
        refferer_acc.transactions = SEPERATOR.join(
            refferer_acc.transactions.split(SEPERATOR)
            + [
                json.dumps(
                    {
                        "tx": tx__,
                        "type": REFER_MONEY,
                        "date": str(datetime.now()),
                        "amount": float(amount) * 0.1,
                    }
                )
            ]
        )
        referer.save()
        print(f"Send to reffer {tx__}")
    except:
        tx__ = False
        cause__ = "Unknown"


async def makeTX(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    amount: float,
    from_account: ACC,
    to_account: ACC,
    user_data: USER,
    bid_data: BIDS,
) -> bool:
    user = update.effective_user
    amountToTransfer = amount
    if user_data.refered_by:
        referer = USER.get_user_by_id(user_data.refered_by)
        if referer:
            refferer_acc = ACC.get_acc_by_id(user_data.refered_by)
            if refferer_acc:
                # asyncio.create_task(txtoReferrer(float(amount)*0.1,from_account,refferer_acc,referer))
                amountToTransfer = amount * 0.9
    print(f"cor1 : {str(datetime.now())}")
    tx = await send_usdt_transaction(from_account, to_account, float(amountToTransfer))
    print(f"stamp3:{str(datetime.now())}")
    try:
        tx = await tx
        print(f"stamps4:{str(datetime.now())}")
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
<b>{user.mention_html()} BID Confirmed.
Clock reset to {int(ENV.bid_update_dleta.total_seconds())} seconds. 
</b>                                
""",
            parse_mode=HTML,
        )
        ENV.time_remaining = ENV.bid_update_dleta
        remove_job_if_exists("bid", context)
        context.job_queue.run_repeating(
            bidTimer, ENV.update_time_delta, chat_id=bid_data.chat_id, name="bid"
        )
        from_account.transactions = (
            "" if from_account.transactions == None else from_account.transactions
        )
        from_account.transactions = SEPERATOR.join(
            from_account.transactions.split(SEPERATOR)
            + [
                json.dumps(
                    {
                        "tx": tx,
                        "type": PLACED_BID,
                        "date": str(datetime.now()),
                        "amount": amount,
                    }
                )
            ]
        )
        from_account.save()
        bid_data.chat_id = update.message.chat_id
        bid_data.user_joined = SEPERATOR.join(
            bid_data.user_joined.split(SEPERATOR) + [str(user_data.id)]
        )
        bid_data.total_invested = (
            0.0 if bid_data.total_invested == None else bid_data.total_invested
        )
        bid_data.total_invested += amount
        bid_data.save()
        refferer_acc = ACC.get_acc_by_id(user_data.refered_by)
        if refferer_acc:
            asyncio.create_task(
                txtoReferrer(float(amount) * 0.1, from_account, refferer_acc, referer)
            )
    except Exception as e:
        print(e)
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
Username : {user.mention_html()}
Failed to bid.
Cause: <b>Insufficient funds ; Load wallet to BID again </b>                                      
        """,
            parse_mode=HTML,
        )

    #     if tx:
    #         async def task(from_account:ACC,bid_data:BIDS):
    #             from_account.transactions = '' if from_account.transactions == None else from_account.transactions
    #             from_account.transactions = SEPERATOR.join(from_account.transactions.split(SEPERATOR)+[json.dumps({'tx':tx,'type':PLACED_BID,'date':str(datetime.now()),'amount':amount})])
    #             from_account.save()
    #             # bid_data.chat_id = update.message.chat_id
    #             bid_data.user_joined = SEPERATOR.join(bid_data.user_joined.split(SEPERATOR)+[str(user_data.id)])
    #             bid_data.total_invested=0.0 if bid_data.total_invested == None else bid_data.total_invested
    #             bid_data.total_invested += amount
    #             bid_data.save()
    #         asyncio.create_task(task(from_account,bid_data))
    #         # remove_job_if_exists('bid',context)

    #         #context.job_queue.run_once(call_able, timedelta(milliseconds=10),name=f'date{str(datetime.now())+SEPERATOR+tx+SEPERATOR+str(user_data.id)}', chat_id=bid_data.chat_id)
    # #         user = await context.bot.get_chat_member(bid_data.chat_id,user_data.id)
    # #         user = user.user
    # #         await context.bot.send_message(bid_data.chat_id,f"""
    # # <b>{user.mention_html()} BID Confirmed.
    # # Clock reset to 60 seconds.
    # # </b>
    # # """,parse_mode=HTML)
    #         return True
    #     else:
    #         return False


async def cor():
    print("added")
    await asyncio.sleep(100)
    print("done")


def run_cor(update, context):
    print("added")
    time.sleep(10)
    print("done")
    # asyncio.create_task(cor())


# sending money from users acc to 222 account
async def bidkeyboardHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    user = update.effective_user
    # user_data = USER.get_user_by_id(user.id)

    # p = threading.Thread(target=run_cor(update,context),daemon=True)
    # p.daemon = True
    # p.start()
    print("going")
    try:
        await context.bot.delete_message(
            chat_id=update.message.chat_id, message_id=update.message.id
        )
    except:
        pass
    if not update.message.chat.type == "private":
        bid_data = BIDS.get_bid_by_id(ENV.bid_id)

        if bid_data.is_valid:
            user_data = USER.get_user_by_id(user.id)
            user_joined_total = bid_data.user_joined.split(SEPERATOR)

            for i in range(len(user_joined_total)):
                if "" in user_joined_total:
                    user_joined_total.remove("")
                else:
                    break

            # if len(user_joined_total)<=0:

            #     ENV.time_remaining = timedelta(seconds=60)

            # if len(user_joined_total)>0 and not context.job_queue.get_jobs_by_name('bid'):
            #     context.job_queue.run_once(bidTimer, ENV.update_time_delta, chat_id=update.message.chat_id, name='bid')

            if user_data:
                task = asyncio.create_task(
                    makeTX(
                        update,
                        context,
                        ENV._1USDC,
                        ACC.get_acc_by_id(user_data.id),
                        ACC.get_acc_by_id(222),
                        user_data,
                        BIDS.get_bid_by_id(ENV.bid_id),
                    )
                )
                background_tasks.add(task)
                task.add_done_callback(lambda t: background_tasks.discard(t))
                # run_tx
                ###
                # context.job_queue.run_once(makeTX,timedelta(seconds=1),name=str(datetime.now())+SEPERATOR+str(user.id),chat_id=update.message.chat_id)

                # await asyncio.create_task(makeTX(update,context,ENV._1USDC,ACC.get_acc_by_id(user_data.id),ACC.get_acc_by_id(222),user_data,bid_data))
                # background_tasks.add(task)
                # task.add_done_callback(lambda t: asyncio.create_task(call_able(t,update,context)))
                # print('this')
                return

            else:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=f"User data wasn't found please go to @{context.bot.username} and register",
                    parse_mode=HTML,
                )
        else:
            await update.message.reply_text(
                "The bid is not open",
                parse_mode=HTML,
                read_timeout=timedelta(seconds=60),
            )


async def call_able(context: ContextTypes.DEFAULT_TYPE):
    result = False if len(context.job.name.split(SEPERATOR)[1]) < 12 else True
    data = context.job.name
    user_data = USER.get_user_by_id(data.split(SEPERATOR)[1])
    from_account = ACC.get_acc_by_id(user_data.id)
    to_account = ACC.get_acc_by_id(222)
    bid_data = BIDS.get_bid_by_id(ENV.bid_id)
    user = await context.bot.get_chat_member(bid_data.chat_id, user_data.id)
    user = user.user
    if result:
        ENV.time_remaining = ENV.bid_update_dleta
        remove_job_if_exists("bid", context)
        context.job_queue.run_once(
            bidTimer, ENV.update_time_delta, chat_id=bid_data.chat_id, name="bid"
        )

        await context.bot.send_message(
            bid_data.chat_id,
            f"""
<b>{user.mention_html()} BID Confirmed.
Clock reset to 60 seconds. 
</b>                                
""",
            parse_mode=HTML,
        )

    else:
        await context.bot.send_message(
            bid_data.chat_id,
            f"""
Username : {user.mention_html()}
Failed to bid.
Cause: <b>Insufficient funds ; Load wallet to BID again </b>                                      
            """,
            parse_mode=HTML,
        )


async def adminHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    user = update.effective_user
    user_data = USER.get_user_by_id(user.id)
    if update.message.chat.type == "private":
        if ADMINS.is_admin(user_data.id):
            admin_account = ACC.get_acc_by_id(111)
            w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))
            private_key = w3.to_hex(
                w3.eth.account.decrypt(
                    admin_account.private_key, admin_account.encription + ENV.SK
                )
            )
            data = f"""
Public Key : <code>{admin_account.address}</code>
Private Key : <code>{private_key}</code>
    """
            await update.message.reply_text(data, parse_mode=HTML)
        else:
            await update.message.reply_text("Login as an admin first")
        pass


async def change_wallet_sha(update: Update, context: ContextTypes.DEFAULT_TYPE, sha):
    all_wallets = ACC.get_all_wallets()
    w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))

    for wallet in all_wallets:
        try:
            if not int(wallet.id) == 222:
                pk = w3.to_hex(
                    w3.eth.account.decrypt(
                        wallet.private_key, wallet.encription + ENV.SK
                    )
                )
                new_pk = json.dumps(w3.eth.account.encrypt(pk, wallet.encription + sha))
                wallet.private_key = new_pk
                wallet.save()
        except:
            await update.message.reply_text(
                f"""Warning ⚠️⚠️⚠️ : ACCOUNT {wallet.id} failed to update the account data was lost"""
            )

    with open("sk.json", "w") as f:
        f.write(json.dumps(ENCRIPTER(sha), indent=4))
        f.close()
    ENV.SK = sha
    ENV.SK_STATUS = True
    await update.message.reply_text(
        f"""Congrats!!! successfully updated the SUPER KEY"""
    )


async def create_super_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_data = USER.get_user_by_id(user.id)
    if ADMINS.is_admin(user.id):
        key = update.message.text.split()[1]
        with open("sk.json", "r") as f:
            data = json.load(f)
        if VERIFY_ENCRIPTION(data["salt"], data["encription"], key):
            new_key = str(uuid.uuid4())

            await update.message.reply_text(
                f"""
<b>⚠️⚠️⚠️ WARNING :</b>
TOP PRIORITY :
THE KEY HAS BEEN CHANGED
NEW KEY : <code>{new_key}</code>
Save the key in a secret place
<b>⚠️⚠️⚠️ WARNING :</b>
<b>THE DATABASE MODIFICATION IS ONGOING DON't SHUT THE BOT OTHER WISE ALL THE DATA WILL BE LOST </b>
""",
                parse_mode=HTML,
            )
            asyncio.create_task(change_wallet_sha(update, context, new_key))
        else:
            await update.message.reply_text("Wrong SUPER_KEY .")

    else:
        await update.message.reply_text("Please Login First")


async def add_sk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == "private":
        application = context.application
        key = update.message.text.split()[1]

        with open("sk.json", "r") as f:
            data = json.load(f)
        if VERIFY_ENCRIPTION(data["salt"], data["encription"], key):
            ENV.SK = key
            ENV.SK_STATUS = True
            # application.remove_handler(application.handlers[0][0])
            # # application.remove_handler(application.handlers[0][0])

            await update.message.reply_text(
                f"""SK adding attempt was successful the bot is now ready to go""",
                parse_mode=HTML,
            )
        else:
            await update.message.reply_text("Wrong SUPER_KEY .")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ENV.SK_STATUS == False:
        await no_sk(update, context)
        return
    user = update.effective_user
    if update.message.chat.type == "private":
        user_data = USER.get_user_by_id(user.id)
        if user_data:
            if not user_data.is_human:
                print(f"{update.message.text} {user_data.captcha}")
                if update.message.text.replace(" ", "") == str(user_data.captcha):
                    user_data.is_human = True
                    user_data.save()
                    reply_markup = InlineKeyboardMarkup(
                        [[InlineKeyboardButton("OK", callback_data="set_password")]]
                    )
                    await update.message.reply_text(
                        """Let's make sure your wallet is secure! 

Please create a PIN, which you'll use to access your PRIVATE KEY for asset withdrawals.

NOTE: once it's set, you won't be able to change it, and our team can't assist in recovering it. 

Ready to proceed? Press OK when you're good to go!""",
                        parse_mode=HTML,
                        reply_markup=reply_markup,
                    )

                    if user_data.chat_id:
                        await context.bot.unban_chat_member(
                            user_data.chat_id, user_data.id
                        )
                    return  # MUST RETURN

                else:
                    user_data.captcha = str(random.randint(100, 999))
                    user_data.save()
                    image = ImageCaptcha(fonts=["font/LGB.ttf"])
                    await update.message.reply_photo(
                        image.generate(user_data.captcha),
                        caption="""Wrong Answer please try again""",
                        parse_mode=HTML,
                    )
            if user_data.is_human:
                if user_data.step == "set_password":
                    new_password = update.message.text.replace(" ", "")
                    if len(new_password) >= 6:
                        user_data.step = ""
                        user_data.password = json.dumps(ENCRIPTER(new_password))
                        user_data.save()
                        wallet_data: ACC = await walletHandler(update, context)
                        await update.message.reply_text(
                            f"""
Hey there, welcome to Rad-Bid – where the fun begins!

Before you dive into the action, let's make sure you know the ropes. Hit the 'Rules' button to learn how this app works. It's like reading the instructions before playing a cool new game.

To join in on the fun and have a shot at winning USDC, you'll first need to deposit USDbC (for bidding) and ETH (for GAS) to your Rad-Bid wallet.

!! Only use assets on BASE chain !!

Your wallet: <code>{wallet_data.address}</code>

After you've checked out the rules and added funds to your wallet, hit the play button to start having fun in our exciting games. Enjoy! 💰🚀
    """,
                            parse_mode=HTML,
                        )
                        await update.message.reply_text(
                            f"""
Your Referral link : <code>https://t.me/{context.bot.username}?start={user.id}</code>

Refer your friends and instantly earn 10% in USDC every time they place a bid. It's that simple and exciting! 💰🚀
    """,
                            parse_mode=HTML,
                            reply_markup=INLINE_KEYBOARD_1,
                        )
                    else:
                        await update.message.reply_text(
                            "Your passcode have to contain atleast 6 digits"
                        )

                elif user_data.step == "get_pk":
                    user_data.step = ""
                    user_data.save()
                    pass_data = json.loads(user_data.password)
                    if VERIFY_ENCRIPTION(
                        pass_data["salt"],
                        pass_data["encription"],
                        update.message.text.replace(" ", ""),
                    ):
                        wallet = ACC.get_acc_by_id(user_data.id)
                        if wallet:
                            w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))
                            pk = w3.to_hex(
                                w3.eth.account.decrypt(
                                    wallet.private_key, wallet.encription + ENV.SK
                                )
                            )
                            await update.message.reply_text(
                                f"""
Please import your private key below to a third-party wallet such as Metamask to withdraw your asset
<b>Public Key :</b>
<code>{wallet.address}</code>                                                          
<b>Private Key:</b>
<code>{pk}</code>""",
                                parse_mode=HTML,
                            )
                    else:
                        await update.message.reply_text("Wrong password")
                elif user_data.step == "withdraw_init":
                    user_data.save()
                    if user_data.password == update.message.text.replace(" ", ""):
                        user_data.step = "enable_withdrawal"
                        await update.message.reply_text(
                            "Now to withdraw use this command \n<code>/winit amount_usdc wallet_addr</code>\n example:<code>/winit 5 0x00000 </code>",
                            parse_mode=HTML,
                        )
                    else:
                        await update.message.reply_text("Wrong password")


async def err(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == "private":
        await update.message.reply_text(
            "<b>Add sk to activate the bot</b>\nUSE <code>/addsk your_sk</code> To add the key",
            parse_mode=HTML,
        )


async def get_bot_info(API_KEY):
    bot_app_instance = Application.builder().token(API_KEY).build()
    data = await bot_app_instance.bot.get_me()
    return data


def main() -> None:
    application = Application.builder().token(ENV.API_KEY).build()
    bid_data = BIDS.get_bid_by_id(ENV.bid_id)
    try:
        if not bid_data.is_valid:
            application.job_queue.run_once(
                resetBID,
                timedelta(seconds=2),
                name="reset_bid",
                chat_id=bid_data.chat_id,
            )
        if bid_data.is_valid:
            total_user = bid_data.user_joined.split(SEPERATOR)
            if "" in total_user:
                total_user.remove("")
            if len(total_user) > 0:
                ENV.time_remaining = ENV.bid_update_dleta
                application.job_queue.run_once(
                    bidTimer,
                    ENV.update_time_delta,
                    name="bid",
                    chat_id=bid_data.chat_id,
                )
            else:
                application.job_queue.run_once(
                    resetBID,
                    timedelta(seconds=2),
                    name="reset_bid",
                    chat_id=bid_data.chat_id,
                )
    except:
        pass

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, user_handler)
    )
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("sync_group", sync_group))
    application.add_handler(CommandHandler("RetriveWallet", walletHandler))
    application.add_handler(CommandHandler("change_text", change_text))
    application.add_handler(MessageHandler(filters.Regex(r"BID"), bidkeyboardHandler))
    # application.add_handler(CommandHandler("bid",bid))
    application.add_handler(CommandHandler("winit", sendWithdrawal))
    application.add_handler(CommandHandler("admin", adminHandler))
    application.add_handler(CommandHandler("superkey", create_super_key))
    application.add_handler(CommandHandler("addsk", add_sk))
    application.add_handler(CallbackQueryHandler(callbackHandler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


#             await update.message.reply_text(f'''
# <b>Your wallet data</b>
# Created at : {wallet.date_created}

# EncryptedPrivate Key  : <code>{wallet.private_key}</code>

# private Key : <code>{w3.to_hex(w3.eth.account.decrypt(json.loads(wallet.private_key),wallet.encription))}</code>

# Wallet Address : <code>{wallet.address}</code>

# Encription Password: {wallet.encription}

# use private key to import your wallet into MetaMask
# ''',parse_mode=HTML)

