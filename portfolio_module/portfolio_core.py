#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[3]:


def calculate_returns(prices):
    return prices.pct_change()


# In[5]:


test_prices = pd.DataFrame({'AAPL': [100, 102, 105],'MSFT': [200, 198, 205]})
returns = calculate_returns(test_prices)
print(returns)


# In[7]:


def create_equal_weights(assets):
    n = len(assets)
    return {asset: 1.0/n for asset in assets}


# In[9]:


weights = create_equal_weights(['AAPL', 'MSFT', 'BTC'])
print(weights)

