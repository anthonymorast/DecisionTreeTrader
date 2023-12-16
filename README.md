# Decision Tree Trader
---
This project uses interpretable machine learning (ML) algorithms to generate rules-based trading systems. In particular, this repository focuses on classification and regression trees. 
The dataset is generated uses a handful of technical indicators over several periods and using the closing price of a handful of stocks. An asset agnostic dataset is created by 
translating asset-specific values (e.g. moving averages) into categorical variables which consider the relationships of these indicators to one another. For example, rather than
using raw EMA-5 and EMA-10 data, a variable indicating whether the EMA-5 is above or below the EMA-10 is used. 