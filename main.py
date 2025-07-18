import pandas as pd
import utility.actions
import utility.timestamp
import utility.assetprice
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Converting the dictionary of wallet_stats to dataframe
wallet_stats = utility.actions.ActionatEachWallet()  # This returns your dict
df_action = pd.DataFrame.from_dict(wallet_stats, orient="index").reset_index()
df_action = df_action.rename(columns={"index": "userWallet"})

# print("Action Feature Table:")
# print(df_action.tail()) 

# Convert the dictionary of wallet_time_features to dataframe
wallet_time_features = utility.timestamp.timestampfeatures() 
df_time = pd.DataFrame.from_dict(wallet_time_features, orient='index').reset_index()
df_time = df_time.rename(columns={'index': 'userWallet'})

# print("Time Feature Table:")
# print(df_time.tail())

# Merged dataframe of timefeatures and action
df_merged = df_action.merge(df_time, on='userWallet', how='left')
# print("Final Merged Features Table:")
# print(df_merged.tail(10))

agg_amounts = utility.assetprice.assetfeatures()
if not isinstance(agg_amounts, dict):
    agg_amounts = dict(agg_amounts)
df_amounts = pd.DataFrame.from_dict(agg_amounts, orient='index').reset_index()
df_amounts = df_amounts.rename(columns={'index': 'userWallet'})

# 4. Merge all features step by step
df_all = df_action.merge(df_time, on='userWallet', how='left')
df_all = df_all.merge(df_amounts, on='userWallet', how='left')

# print("All Features Table:")
# print(df_all.tail(10))

def label_wallet(row):
    # Liquidation: always risky
    if 'liquidation_count' in row and row['liquidation_count'] > 0:
        return 1
    # Never borrowed: safe
    if row['borrow_count'] == 0:
        return 0
    # Borrowed, never repaid: risky
    if row['repay_count'] == 0 and row['borrow_count'] > 0:
        return 1
    # Repaid little vs borrow (USD terms) : risky
    try:
        repay_ratio = row['total_repay_usd'] / row['total_borrow_usd'] if row['total_borrow_usd'] > 0 else 1
    except Exception:
        repay_ratio = 1
    if repay_ratio < 0.4:
        return 1
    # Suspicious burst activity : risky
    if 'burst_count' in row and row['burst_count'] > 20:
        return 1
    # Very low avg time between actions & many txns: risky
    if 'avg_time_gap' in row and row['avg_time_gap'] < 60 and row['total_transactions'] > 10:
        return 1
    # Aggressive borrow+redeem+fast: risky
    if row['borrow_count'] > 10 and row['redeem_count'] > 10 and row.get('avg_time_gap', 99999) < 120:
        return 1
    # Otherwise safe
    return 0

# Add the label column
df_all['is_risky'] = df_all.apply(label_wallet, axis=1)

print("Added is_risky column (last 10 rows):")
print(df_all.tail(10))

feature_cols = [col for col in df_all.columns if col not in ['userWallet', 'is_risky']]
X = df_all[feature_cols]
y = df_all['is_risky']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# ML Model Training
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluation 
y_pred = model.predict(X_test)
print("\nClassification Report (70/30 test set):")
print(classification_report(y_test, y_pred))

# Score calculation (0-1000)
proba_safe = model.predict_proba(X_test)[:, model.classes_.tolist().index(0)]
df_result = X_test.copy()
df_result['is_risky_actual'] = y_test.values
df_result['ML_score_0_1000'] = (proba_safe * 1000).astype(int)

print("\nSample: Final Wallet Scores (ML):")
print(df_result[['ML_score_0_1000']].head(10))

df_result['score_range'] = pd.cut(df_result['ML_score_0_1000'], bins=range(0, 1100, 100), right=False)

# Count per bucket
score_distribution = df_result['score_range'].value_counts().sort_index()

print("\nScore Distribution (per 100 point bin):")
for score_range, count in score_distribution.items():
    print(f"{score_range}: {count} wallets")

# Plot distribution
score_dist = df_result['score_range'].value_counts().sort_index()
score_dist.plot(kind='bar', figsize=(10,6), title="Wallet Risk Score Distribution (0–1000)")
plt.xlabel("Score Range")
plt.ylabel("Number of Wallets")
plt.tight_layout()
plt.savefig("score_distribution.png")  # Save plot
plt.close()

# Save df_result for markdown analysis
df_result.to_csv("scored_wallets.csv", index=False)