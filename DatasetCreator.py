"""
    Take the same approach as in main.py (move the code here).

    Determine the "interactions" between MAs (and maybe other predictors, 
    need to understand what they measure) to create a symbol-agnostic
    dataset, e.g. ma3<ma5 -- this will create a very wide dataset. Eventually,
    could use the difference between MAs, e.g. MA5 - MA3 = X

    Create two datasets: one that predicts buy/sell (classification) depending
    on whether the 20-period return is >0/<0 and one that predicts 20-period return
    (regression)
"""
import pandas as pd
import numpy as np
from DataHandler import DataHandler
from datetime import timedelta, datetime
import holidays


class DataCreator:
    def __init__(self, startdate : str, enddate : str, apikey : str, target : str, inidcators : list, periods : list, symbols : list, timeframe : str) -> None:
        self.START_DATE = startdate
        self.END_DATE = enddate
        self.API_KEY = apikey
        self.TARGET_STRING = target
        self.SYMBOLS = symbols
        self.INDICATORS = inidcators
        self.PERIODS = periods
        self.TIMEFRAME = timeframe
        self.dh = DataHandler(self.API_KEY)
    
    def build_dataset(self, ):
        fromdtstr = self.START_DATE.strftime("%Y-%m-%d")
        todtstr = self.END_DATE.strftime("%Y-%m-%d")
        data = {
            "sym": [],
            "date": [],
            "indicator": [], 
            "value": [],
            "period_start_price": [],
            "period_end_price": [],
            self.TARGET_STRING: []
        }
        for sym in self.SYMBOLS:
            pricedata = self.dh.HistoricalData(sym, fromdtstr, todtstr, self.TIMEFRAME)
            for ind in self.INDICATORS:
                for period in self.PERIODS:
                    print(f"{sym}-{ind}-{period}")
                    ind_data = self.dh.IndicatorDataByName(sym, period, self.TIMEFRAME, fromdtstr, todtstr, ind)
                    for dp in ind_data:
                        yhat, startprice, endprice = self.get_target_return(dp["date"][:10], pricedata)
                        if not yhat:    # return None if return cannot be calculated (e.g. future dates)
                            continue
                        data["sym"].append(sym)
                        data["date"].append(dp["date"][:10])
                        data["indicator"].append(f"{ind}_{period}")
                        data["value"].append(dp[ind])
                        data["period_start_price"].append(startprice)
                        data["period_end_price"].append(endprice)
                        data[self.TARGET_STRING].append(yhat)
        
        return pd.DataFrame.from_dict(data)

    def get_target_return(self, startdt : str, data : dict) -> float:
        target_date = datetime.strptime(startdt, "%Y-%m-%d") + timedelta(30)
        while target_date in holidays.US() or target_date in holidays.WEEKEND:
            # print(f"target date={target_date} is a holiday or weekend.")
            target_date += timedelta(1)
        if target_date > datetime.now():    # future date, return None as this data point can not be processed
            return None, None, None

        target_date = target_date.strftime("%Y-%m-%d")
        startdata = None
        enddata = None
        for dp in data:
            if dp["date"][:10] == startdt:
                startdata = dp
            if dp["date"][:10] == target_date:
                enddata = dp

            if enddata and startdata:
                break

        if not enddata or not startdata:   # return can't be computed
            return None, None, None

        v_0 = startdata["close"]
        v_T = enddata["close"]
        return ((v_T - v_0) / v_0), v_0, v_T

    def reorg_data(self, raw_data : pd.DataFrame) -> pd.DataFrame:
        all_data = {}
        for sym in raw_data["sym"].unique().tolist():
            print(f"reorganizing sym={sym}")
            data_dict = {
                "sym": [], 
                "date": [],
                "period_start_price": [],
                "period_end_price": [],
                self.TARGET_STRING: []
            }
            symdata = raw_data.loc[raw_data["sym"] == sym]
            for dt in symdata["date"].unique().tolist():
                subset = symdata.loc[symdata["date"] == dt]
                first_row = subset.iloc[0]  # some data stays the same
                data_dict["sym"].append(first_row["sym"])
                data_dict["date"].append(first_row["date"])
                data_dict["period_start_price"].append(first_row["period_start_price"])
                data_dict["period_end_price"].append(first_row["period_end_price"])
                data_dict[self.TARGET_STRING].append(first_row[self.TARGET_STRING])

                for ind in subset["indicator"].tolist():
                    indicator_data = subset.loc[subset["indicator"] == ind]
                    if ind in data_dict:
                        data_dict[ind].append(float(indicator_data["value"]))
                    else:
                        try:
                            data_dict[ind] = [float(indicator_data["value"])]
                        except:
                            print(f"unable to convert {indicator_data['value']} to float")
            all_data[sym] = pd.DataFrame.from_dict(data_dict)
        return all_data

    def create_asset_agnostic_data(self, symbol_data : pd.DataFrame, emaIndicators : list, emaPeriods : list) -> pd.DataFrame:
        """
            Indicators:
                **MAs (all flavors): match each ma with each other MA make flags indicating above/below
                
                Standard Dev.: OK as is
                Willaims: OK as is -100 -> 0
                RSI: OK as is 
                ADX: OK as is 0->100
        """
        comp_cols = [f"{indicator}_{period}" for period in emaPeriods for indicator in emaIndicators]
        print(f"Using MA {comp_cols} for comparison.")
        for idx, col in enumerate(comp_cols):
            if idx == len(col) - 1:
                break

            for i in range(idx + 1, len(comp_cols)):
                check_col = comp_cols[i]
                print(f"Processing {idx}={col} vs {check_col}.")
                symbol_data[f"{col}_above_{check_col}"] = symbol_data[col] > symbol_data[check_col] # symbol_data[col] > symbol_data[check_col]

        return symbol_data, comp_cols
