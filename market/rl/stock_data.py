import numpy as np
import random
import pandas as pd
import os

def generate_prices(initial=100, loc=0, scale=5, n=1000):
    b = np.random.normal(loc=loc, scale=scale, size=(n,))
    p = initial + np.cumsum(b)
    return p.tolist()

TRAINING = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'BRK-B', 'TSLA', 'META', 'RKT.L', 'BATS.L', 'DGE.L', 'ULVR.L', 'IMB.L', 'CCH.L', 'EDV.L', 'SMIN.L', 'AZN.L']
TESTING = ['UNH', 'CTEC.L']

def training_episode():
    stock = random.choice(TRAINING)
    data = pd.read_csv(f'data/{stock}.csv')
    start = random.randint(0, len(data) - 200)
    return data['Close'][start:start+200].tolist()

def testing_episode():
    stock = random.choice(TESTING)
    data = pd.read_csv(f'data/{stock}.csv')
    start = random.randint(0, len(data) - 200)
    return data['Close'][start:start+200].tolist()

def training_gen(max_len=None):
    for st in range(max_len if max_len is not None else len(TRAINING)):
        if st >= len(TRAINING):
            break
        cur_stock = TRAINING[st]
        data = pd.read_csv(f'data/{cur_stock}.csv')['Close'].tolist()
    
        for i in range(0, len(data) - 101):
            yield np.array(data[i:i+100]), np.array([data[i+100]])

def testing_gen(max_len=None):
    for st in range(max_len if max_len is not None else len(TESTING)):
        cur_stock = TESTING[st]
        data = pd.read_csv(f'data/{cur_stock}.csv')['Close'].tolist()
        for i in range(0, len(data) - 101):
            yield np.array(data[i:i+100]), np.array([data[i+100]])        
