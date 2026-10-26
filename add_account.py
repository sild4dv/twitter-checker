import asyncio
import sys

from twscrape import API

USO = 'Uso: python add_account.py <username> "auth_token=XXX; ct0=YYY"'


async def main():
    if len(sys.argv) < 3:
        raise SystemExit(USO)

    username, cookies = sys.argv[1], sys.argv[2]
    api = API("accounts.db")
    # Com cookies, senha e e-mail não são usados (valores de preenchimento)
    await api.pool.add_account(username, "x", "x@x.com", "x", cookies=cookies)
    print("Conta adicionada. Status do pool:")
    for info in await api.pool.accounts_info():
        print(info)


asyncio.run(main())
