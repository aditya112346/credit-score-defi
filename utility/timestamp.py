import json 
import numpy as np

def timestampfeatures() :
    with open('user-wallet-transactions.json') as f :
        data = json.load(f)

    wallet_tx_times = {}

    for transactions in data :
        wallet = transactions['userWallet']
        t = transactions['timestamp']
        wallet_tx_times.setdefault(wallet, []).append(t)

    wallet_time_features = {}

    burst_thresh = 120 # This is burst threshold 

    for wallet, times in wallet_tx_times.items():
        times_sorted = sorted(times)
        gaps = [times_sorted[0]] + [t2 - t1 for t1, t2 in zip(times_sorted[:-1], times_sorted[1:])]
        avg_gap = np.mean(gaps) if len(gaps) > 1 else 0
        min_gap = np.min(gaps) if len(gaps) > 1 else 0
        burst_count = sum(1 for gap in gaps if gap < burst_thresh)
        total_txns = len(times_sorted)
        wallet_time_features[wallet] = {
            "avg_time_gap": avg_gap,
            "min_time_gap": min_gap,
            "burst_count": burst_count,
            "total_transactions": total_txns,
        }

    return wallet_time_features