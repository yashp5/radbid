import pandas as pd
import os
import uuid
import psycopg2
from cSRC.inf import env as ENV


class dbUser:
    db_group_chat_id = int()

    def __init__(
        self,
        id: int,
        user_name=None,
        date_joined=None,
        is_human=False,
        captcha=None,
        referral_points=0,
        refered_by=None,
        chat_id=None,
        step="",
        password=None,
        earned_from_referral=0.0,
    ) -> None:
        self.id = id
        self.user_name = user_name
        self.date_joined = date_joined
        self.is_human = is_human
        self.captcha = captcha
        self.referral_points = referral_points
        self.refered_by = refered_by
        self.chat_id = chat_id
        self.step = step
        self.password = password
        self.earned_from_referral = earned_from_referral

    def create(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (id,user_name,date_joined,is_human,captcha,referral_points,refered_by,chat_id,step,password,earned_from_referral)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
            (
                self.id,
                self.user_name,
                self.date_joined,
                self.is_human,
                self.captcha,
                self.referral_points,
                self.refered_by,
                self.chat_id,
                self.step,
                self.password,
                self.earned_from_referral,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_by_id(id: int):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
        result = cursor.fetchone()

        if result:
            (
                id,
                user_name,
                date_joined,
                is_human,
                captcha,
                referral_points,
                refered_by,
                chat_id,
                step,
                password,
                earned_from_referral,
            ) = result

            user = dbUser(
                id=id,
                user_name=user_name,
                date_joined=date_joined,
                is_human=is_human,
                captcha=captcha,
                referral_points=referral_points,
                refered_by=refered_by,
                chat_id=chat_id,
                step=step,
                password=password,
                earned_from_referral=earned_from_referral,
            )
            conn.close()
            return user

        conn.close()
        return None

    def save(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users SET
            user_name=%s, date_joined=%s, is_human=%s,captcha=%s, referral_points=%s, refered_by=%s, chat_id=%s ,step =%s ,password=%s ,earned_from_referral=%s
            WHERE id=%s 
        """,
            (
                self.user_name,
                self.date_joined,
                self.is_human,
                self.captcha,
                self.referral_points,
                self.refered_by,
                self.chat_id,
                self.step,
                self.password,
                self.earned_from_referral,
                self.id,
            ),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def query_by_field(field_name, field_value):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()
        try:
            query = f"SELECT * FROM users WHERE {field_name} = %s"
            cursor.execute(query, (field_value,))
            results = cursor.fetchall()
            users = []
            for result in results:
                (
                    id,
                    user_name,
                    date_joined,
                    is_human,
                    captcha,
                    referral_points,
                    refered_by,
                    chat_id,
                    step,
                    password,
                    earned_from_referral,
                ) = result

                user = dbUser(
                    id=id,
                    user_name=user_name,
                    date_joined=date_joined,
                    is_human=is_human,
                    captcha=captcha,
                    referral_points=referral_points,
                    refered_by=refered_by,
                    chat_id=chat_id,
                    step=step,
                    password=password,
                    earned_from_referral=earned_from_referral,
                )

                users.append(user)
                conn.close()
            return users
        except Exception as e:
            conn.close()
            print(f"Error: {e}")
            return []

    def delete(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE id=%s", (self.id,))

        conn.commit()
        conn.close()


class Admins:
    db_group_chat_id = int()

    def __init__(self, id: int) -> None:
        self.id = id

    def create(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO admins (id)
            VALUES (%s)
        """,
            (self.id,),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def is_admin(id: int):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM admins WHERE id=%s", (id,))
        result = cursor.fetchone()

        if result:
            (id) = result
            conn.close()
            return True
        conn.close()
        return False

    def delete(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("DELETE FROM admins WHERE id=%s", (self.id,))

        conn.commit()
        conn.close()


class AdditionalData:
    def __init__(
        self, id: int, chat_id: int, welcome_text: str, group_name: str, last_block=None
    ) -> None:
        self.id = id
        self.chat_id = chat_id
        self.welcome_text = welcome_text
        self.group_name = group_name
        self.last_block = last_block

    def create(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO datas (id,chat_id,welcome_text,group_name,last_block)
            VALUES (%s,%s,%s,%s,%s)
        """,
            (
                self.id,
                self.chat_id,
                self.welcome_text,
                self.group_name,
                self.last_block,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_group_by_id(id: int):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM datas WHERE id=%s", (id,))
        result = cursor.fetchone()

        if result:
            (id, chat_id, welcome_text, group_name, last_block) = result
            group_data = AdditionalData(
                id=id,
                chat_id=chat_id,
                welcome_text=welcome_text,
                group_name=group_name,
                last_block=last_block,
            )
            conn.close()
            return group_data
        conn.close()
        return None

    def save(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE datas SET
            chat_id=%s, welcome_text=%s, group_name=%s, last_block=%s
            WHERE id=%s 
        """,
            (
                self.chat_id,
                self.welcome_text,
                self.group_name,
                self.last_block,
                self.id,
            ),
        )

        conn.commit()
        conn.close()

    def delete(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("DELETE FROM datas WHERE id=%s", (self.id,))

        conn.commit()
        conn.close()


class Acc:
    def __init__(
        self,
        id: int,
        user_name="",
        date_created="",
        private_key="",
        public_key="",
        address="",
        encription="",
        transactions="",
    ) -> None:
        self.id = id
        self.user_name = user_name
        self.date_created = date_created
        self.private_key = private_key
        self.public_key = public_key
        self.address = address
        self.encription = encription
        self.transactions = transactions

    def create(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO wallets (id,user_name,date_created,private_key,public_key,address,encription,transactions)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
            (
                self.id,
                self.user_name,
                self.date_created,
                self.private_key,
                self.public_key,
                self.address,
                self.encription,
                self.transactions,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_acc_by_id(id: int):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM wallets WHERE id=%s", (id,))
        result = cursor.fetchone()
        if result:
            (
                id,
                user_name,
                date_created,
                private_key,
                public_key,
                address,
                encription,
                transactions,
            ) = result
            group_data = Acc(
                id=id,
                user_name=user_name,
                date_created=date_created,
                private_key=private_key,
                public_key=public_key,
                address=address,
                encription=encription,
                transactions=transactions,
            )
            conn.close()
            return group_data
        conn.close()
        return None

    def save(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE wallets SET
            user_name=%s, date_created=%s, private_key=%s, public_key=%s ,address=%s, encription=%s, transactions=%s
            WHERE id=%s 
        """,
            (
                self.user_name,
                self.date_created,
                self.private_key,
                self.public_key,
                self.address,
                self.encription,
                self.transactions,
                self.id,
            ),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def get_all_wallets():
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wallets")
        results = cursor.fetchall()
        accounts = []
        for result in results:
            (
                id,
                user_name,
                date_created,
                private_key,
                public_key,
                address,
                encription,
                transactions,
            ) = result
            wallet_data = Acc(
                id=id,
                user_name=user_name,
                date_created=date_created,
                private_key=private_key,
                public_key=public_key,
                address=address,
                encription=encription,
                transactions=transactions,
            )
            accounts.append(wallet_data)
        conn.close()
        return accounts

    def delete(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("DELETE FROM wallets WHERE id=%s", (self.id,))

        conn.commit()
        conn.close()


class Bids:
    def __init__(
        self,
        id: int,
        creator: int,
        date_created="",
        user_joined="",
        total_invested=0.0,
        withdrawal_date="",
        chat_id=None,
        minimum_amount=0.0,
        is_valid=True,
    ) -> None:
        self.id = id
        self.creator = creator
        self.date_created = date_created
        self.user_joined = user_joined
        self.total_invested = total_invested
        self.withdrawal_date = withdrawal_date
        self.chat_id = chat_id
        self.minimum_amount = minimum_amount
        self.is_valid = is_valid

    def create(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO bids (id,creator,date_created,user_joined,total_invested,withdrawal_date,chat_id,minimum_amount,is_valid)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
            (
                self.id,
                self.creator,
                self.date_created,
                self.user_joined,
                self.total_invested,
                self.withdrawal_date,
                self.chat_id,
                self.minimum_amount,
                self.is_valid,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_bid_by_id(id: int):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bids WHERE id=%s", (id,))
        result = cursor.fetchone()

        if result:
            (
                id,
                creator,
                date_created,
                user_joined,
                total_invested,
                withdrawal_date,
                chat_id,
                minimum_amount,
                is_valid,
            ) = result
            group_data = Bids(
                id=id,
                creator=creator,
                date_created=date_created,
                user_joined=user_joined,
                total_invested=total_invested,
                withdrawal_date=withdrawal_date,
                chat_id=chat_id,
                minimum_amount=minimum_amount,
                is_valid=is_valid,
            )
            conn.close()
            return group_data
        conn.close()
        return None

    def save(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE bids SET
            creator=%s, date_created=%s, user_joined=%s, total_invested=%s ,withdrawal_date=%s, chat_id=%s, minimum_amount=%s, is_valid=%s
            WHERE id=%s 
        """,
            (
                self.creator,
                self.date_created,
                self.user_joined,
                self.total_invested,
                self.withdrawal_date,
                self.chat_id,
                self.minimum_amount,
                self.is_valid,
                self.id,
            ),
        )

        conn.commit()
        conn.close()

    def delete(self):
        conn = psycopg2.connect(
            dbname=ENV.DB_NAME,
            user=ENV.DB_USER,
            password=ENV.DB_PASSWORD,
            host=ENV.DB_HOST,
        )
        cursor = conn.cursor()

        cursor.execute("DELETE FROM bids WHERE id=%s", (self.id,))

        conn.commit()
        conn.close()

