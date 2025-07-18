import json

def ActionatEachWallet():
    wallet_stats = {}

    with open('user-wallet-transactions.json') as f:
        data = json.load(f)
        
    # We collect the wallet address and action performed by
    # that address/user/wallet into action
    # And together collected them in wallet_stats
    
    for trasactions in data:
        wallet = trasactions['userWallet']
        action = trasactions['action']

        if wallet not in wallet_stats:
            wallet_stats[wallet] = {
                "deposit_count": 0,
                "borrow_count": 0,
                "repay_count": 0,
                "redeem_count": 0,
                "liquidation_count": 0,
                "total_liquidated_collateral_usd": 0,
                "total_liquidated_principal_usd": 0,
            }
            
        if action == "deposit":
            wallet_stats[wallet]["deposit_count"] += 1
        elif action == "borrow":
            wallet_stats[wallet]["borrow_count"] += 1
        elif action == "repay":
            wallet_stats[wallet]["repay_count"] += 1
        elif action == "redeemunderlying":
            wallet_stats[wallet]["redeem_count"] += 1
        elif action == 'liquidationcall':
            wallet_stats[wallet]['liquidation_count'] += 1

            ad = trasactions.get('actionData', {})
            try:
                collateral_amount = float(ad['collateralAmount'])
                collateral_price = float(ad['collateralAssetPriceUSD'])
                principal_amount = float(ad['principalAmount'])
                principal_price = float(ad['borrowAssetPriceUSD'])
            except (KeyError, ValueError, TypeError):
                collateral_amount = 0
                collateral_price = 0
                principal_amount = 0
                principal_price = 0
            wallet_stats[wallet]['total_liquidated_collateral_usd'] += collateral_amount * collateral_price
            wallet_stats[wallet]['total_liquidated_principal_usd'] += principal_amount * principal_price

    return wallet_stats
