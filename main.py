"""
    Blog title: Interpretable Machine Learning Trading Decisions
    https://www.youtube.com/watch?v=Av7rrIJvI9M&list=PLvoal9WEcFgLaHAZAYdxrrsAhxkZJicbF&index=4&ab_channel=Quantra

    Severl Models:
    https://christophm.github.io/interpretable-ml-book/rulefit.html#software-and-alternative


    Create a "bot" that trades based off of the output from a decision tree.
    The tree will consider a slough of technical indicators and predict 
    buy/sell signals. This will create an interpretable model which will
    mimic decisions that would be made in a trading day (e.g. is the RSI
    > 50?). A row in the dataset will be the technical indicators and whether
    a buy or sell should have been signaled. Use the 1month price - current price 
    for buy sell, if future price is > e.g. 5% higher than current price the
    predictor is "buy", if < e.g. 5% it is "sell"

    Could also use % return as the target variable.
"""
from DataHandler import *
from DecisionTreeTrader import DecisionTree

from datetime import datetime, timedelta
from DatasetCreator import DataCreator
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt

API_KEY = 'YOUR_API_KEY'
PERIODS = [3, 5, 10, 15, 20, 25, 30, 50, 70, 100, 120, 150, 200]
TIMEFRAME = TimeFrame.ONE_DAY
INDICATORS = Indicators.AllIndicators()
SYMBOLS = ["INTC", "AAPL", "WMT", "WM", "LMT", "SOUN", "SDGR", "MKC", "BUD", "FSLY"]
YEARS_DATA = 5
START_DATE = datetime.today() - timedelta(365*YEARS_DATA)
END_DATE = datetime.today()
RETURN_PERIODS = 20     # 20 periods ~= 1 month
BUILD_DATASET = False
TARGET_STRING = f"{RETURN_PERIODS}_period_return"

if __name__ == '__main__':
    raw_data = None
    feature_data = None
    symbol=""
    if BUILD_DATASET:
        dc = DataCreator(START_DATE, END_DATE, API_KEY, TARGET_STRING, INDICATORS, PERIODS, SYMBOLS, TIMEFRAME)
        raw_data = dc.build_dataset()
        raw_data.to_csv("./data/raw_data.csv", index=False)

        feature_data = dc.reorg_data(raw_data)  # dict from symbol -> symbol data 
        for sym in feature_data:
            feature_data[sym], drop_cols = dc.create_asset_agnostic_data(feature_data[sym], Indicators.EmaIndicators(), PERIODS)
            feature_data[sym] = feature_data[sym].drop(columns=drop_cols)
            feature_data[sym].to_csv(f'./data/{sym}_feature_data.csv', index=False)
        exit()
    else:
        all_data = None
        for symbol in SYMBOLS:
            feature_data = pd.read_csv(f'./data/{symbol}_feature_data.csv')
            feature_data = feature_data.drop(columns=['sym','date','period_start_price','period_end_price'])
            largest_gain = max(feature_data[TARGET_STRING])
            largest_loss = min(feature_data[TARGET_STRING])
            print(f"Largest gain={largest_gain}")

            # endpoints are exclusive => NaNs
            feature_data[TARGET_STRING] = pd.cut(x=feature_data[TARGET_STRING],  bins=[largest_loss - 1, 0, largest_gain + 1], labels=["Loss", "Gain"])

            if all_data is None:
                all_data = feature_data
            else:
                all_data = pd.concat([all_data, feature_data], axis=0, ignore_index=True)

        symbol = 'ALL'
        feature_data = all_data
        print("Final dataframe shape:", all_data.shape)


            # categories
    #        feature_data[TARGET_STRING] = pd.cut(x=feature_data[TARGET_STRING], 
    #                                             bins=[-1.0, -.30, -.10, 0, .10, .30, largest_gain], 
    #                                             #TODO: dynamically define these cuts
    #                                             labels=["30-100pct Loss", "10-30pct Loss", "0-10pct Loss", "0-10pct Gain", "10-30pct Gain", f"30-{largest_gain}pct Gain"])
    
    # TODO: train on one symbol's data and test on anothers
    # TODO: combine data of all symbols then do a train/test split

    if feature_data is None:
        print(f"Dataset is empty.")
        exit()

    print(feature_data)

    y = feature_data[TARGET_STRING]
    x = feature_data.loc[:, feature_data.columns != TARGET_STRING]
    trainx, testx, trainy, testy = train_test_split(x, y, test_size=0.33, shuffle=True)
    max_depth = 7
    tree = DecisionTree(classification=True, max_depth=max_depth)
    tree.train(trainx, trainy)
    yhat = tree.test(testx)

    correct = 0
    wrong = 0
    total = len(testy)
    for idx, value in enumerate(yhat):
        if testy.iloc[idx] == value:
            correct += 1
        else:
            wrong += 1
        print(f"idx={idx}, yhat={value}, actual={testy.iloc[idx]}, right? {testy.iloc[idx] == value}")
    print(f"total={total}, right={correct}, wrong={wrong}, pct right={correct/total}, pct wrong={wrong/total}")
    
    conf_matrix = metrics.confusion_matrix(testy, yhat)
    display = metrics.ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=["Gain", "Loss"])
    display.plot()
    plt.show()
    plt.clf()
    tree.plot(f"plots/{symbol}_{max_depth}.pdf", x.columns, filled=True)
    tree.to_text_rules(f"text_repr/{symbol}_{max_depth}.dat", x.columns)