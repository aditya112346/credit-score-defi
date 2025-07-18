import json
from collections import defaultdict

def assetfeatures() :

    with open('user-wallet-transactions.json') as f :
        data = json.load(f)

    agg_amounts = defaultdict(lambda: {'total_deposit_usd':0, 'total_borrow_usd':0, 'total_repay_usd':0, 'total_redeem_usd':0, 'total_liquidatcall_usd':0})
    for transactions in data :
        wallet = transactions['userWallet']
        action = transactions['action']
        try:
            amt = float(transactions['actionData']['amount'])
            price = float(transactions['actionData']['assetPriceUSD'])
            usd_value = amt * price
        except (KeyError, ValueError, TypeError):
            continue

        if action == 'deposit':
            agg_amounts[wallet]['total_deposit_usd'] += usd_value
        elif action == 'borrow':
            agg_amounts[wallet]['total_borrow_usd'] += usd_value
        elif action == 'repay':
            agg_amounts[wallet]['total_repay_usd'] += usd_value
        elif action == 'redeemunderlying' :
            agg_amounts[wallet]['total_redeem_usd'] += usd_value
        elif action == 'liquidationcall' :
            agg_amounts[wallet]['total_liquidatcall_usd'] += usd_value
    
    return dict(agg_amounts)