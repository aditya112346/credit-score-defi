import json

def totalWallets() :

    with open('user-wallet-transactions.json') as f :
        data = json.load(f)

    # We created a set because set cannot have same type of data inside it
    total_unique_wallets = set()

    # We are taking user_wallet address because
    # this is how a user is represented in blockchain
    for trasaction in data :
        total_unique_wallets.add(trasaction['userWallet'])

    return len(total_unique_wallets)
