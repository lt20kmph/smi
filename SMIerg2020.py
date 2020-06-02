#!/usr/bin/python

#---> Imports
import requests
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from time import sleep
import time
from datetime import datetime as dt, timedelta as td
import matplotlib.pyplot as plt
from yattag import Doc
from numpy import prod
import numpy as np
from daemonize import Daemonize
#<---


BASE_URL = 'https://api.binance.com'
KLINE_EXT = '/api/v3/klines'
PRICE_EXT = '/api/v3/avgPrice'
SYMBOL= 'ETHBTC'
INTERVAL = '1m'
SLEEPS = {'1m':60
         ,'5m':300
         ,'15m':900
         ,'30m':1800
         ,'1h':3600
         ,'4h':1440
         ,'8h':2880}
pid = '/tmp/smierg.pid'

colorLight = "#9a9a9a"
colorMedium = "#676767"

def priceParameters(symbol):
    return {'symbol':symbol}

def klineParameters(symbol,interval):
    return {'symbol':symbol,'interval':interval}

engine = create_engine('sqlite:///SMIerg.db')
Base = declarative_base(bind=engine)

#--->Class defs
#---> Trade Class
class Trade(Base):
    __tablename__ = 'trade'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    interval = Column(String)
    entryTime = Column(Integer)
    entryPrice = Column(String)
    exitTime = Column(Integer)
    exitPrice = Column(String) 
    __mapper_args__ = {'polymorphic_identity': 'trade'}
    def __init__(self,symbol,interval,entryTime,entryPrice,exitTime,exitPrice):
        self.symbol = symbol
        self.interval = interval
        self.entryTime = entryTime
        self.exitTime = exitTime
        self.entryPrice = entryPrice
        self.exitPrice = exitPrice

    def duration(self):
        try:
            return self.exitTime-self.entryTime
        except:
            try:
                return int(time.time())-self.entryTime
            except:
                return 0

    def profit(self):
        try:
            exp = float(self.exitPrice)
            enp = float(self.entryPrice)
            return (exp-enp)/enp*100
        except:
            return 0

    def status(self):
        if self.exitTime is not None:
            return 'CLOSED'
        else:
            return 'OPEN'

    def state(self):
        if self.entryTime == None or self.exitTime != None:
            return 'SOLD'
        elif self.exitTime == None:
            return 'BOUGHT'
#<---

#--->Class def Kline
class Kline(Base):
    __tablename__ = 'kline'
    symbol = Column(String, primary_key=True)
    interval = Column(String, primary_key=True)
    openTime = Column(Integer, primary_key=True)
    open = Column (String)
    high = Column (String)
    low = Column (String)
    close = Column (String)
    volume = Column (String)
    numOfTrades = Column (Integer)
    def __init__(self,symbol,interval,openTime,open,high,low,close,volume,numOfTrades):
        self.symbol = symbol
        self.interval =interval
        self.openTime = openTime
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.numOfTrades = numOfTrades

#<---
#<---

# Only needed to create table structure
Base.metadata.create_all()

Session = sessionmaker(bind=engine)
s = Session()

#--->dbFunctions
def mkKlines(symbol,interval):
    response = requests.get(BASE_URL + KLINE_EXT
                           ,params=klineParameters(symbol,interval))
    klines = []
    q = s.query(Kline).order_by(Kline.openTime.desc())
    if q.first() != None:
        m = q.first().openTime
    else:
        m = 0
    for k in response.json():
        if k[0] > m:  
            klines += [Kline(symbol
                            ,interval
                            ,k[0]
                            ,k[1]
                            ,k[2]
                            ,k[3]
                            ,k[4]
                            ,k[5]
                            ,k[8]
                            )]
    s.add_all(klines)
    s.commit()

def getCloses(symbol,interval):
    q = s.query(Kline)\
            .filter_by(symbol = symbol,interval = interval)\
            .order_by(Kline.openTime.desc())[:100]
    closes = []
    for k in q:
        closes += [float(k.close)]
    return closes

def addInitialPostion(symbol,interval):
    q = s.query(Trade)\
            .filter_by(symbol = symbol,interval = interval)\
            .first()
    if q == None:
        p = Trade(symbol,interval,None,None,None,None)
        s.add(p)
        s.commit()

def state(symbol,interval):
    q = s.query(Trade)\
            .filter_by(symbol = symbol,interval = interval)\
            .order_by(Trade.id.desc()).first()
    if q.entryTime == None or q.exitTime != None:
        return 'SOLD'
    elif q.exitTime == None:
        return 'BOUGHT'
#<---

#--->Moving average defs
def EMA(L,period):
    E = []
    l = len(L)
    p = period
    for i in range(l):
        if i == 0:
            E.append(L[0])
        else:
            E.append(2/(p+1)*(L[i]-E[i-1])+E[i-1])
    return E

def TSI(L,fast,slow):
    L = L[::-1]
    l = len(L) - 1
    m = [L[i+1]-L[i] for i in range(l) if L[i+1] - L[i] != 0]
    am = [abs(i) for i in m]
    e = [EMA(EMA(m,slow),fast)[i]/EMA(EMA(am,slow),fast)[i] for i in
            range(len(m))]
    s = EMA(e,5)
    return zip(e,s)
#<---

#--->html generation

fmtTime = '['+'%Y' + '-' + '%m' + '-' + '%d' + ' ('+'%H'+':'+'%M'+')'+']'
exStr = ' Exit: '
enStr = ' Ntry: '
doc, tag, text = Doc().tagtext()

def fmtTD(x):
    h = int(x/3600)
    m = int((x%3600)/60)
    return(str(h)+':'+str(m))

def mkHtml(symbol,interval,n):
    T = s.query(Trade)\
            .filter_by(symbol = symbol,interval = interval)\
            .order_by(Trade.id.desc())
    t = T[:n]
    N = T.count() 
    status = t[0].status()
    tProf = round((prod([i.profit()/100+1 for i in T]) - 1)*100,4)
    aProf = round(sum([i.profit() for i in T])/N,4)
    aDur = sum([i.duration() for i in T[1:]])/N
    with tag('body'):
        with tag('table'):
            with tag('tr'):
                with tag('td'):
                    with tag('b'):
                        text('Status: ')
                    text(status)
                    doc.stag('br')
                    with tag('b'):
                        text('Total profit: ')
                    text(str(tProf)+'%')
                with tag('td'):
                    with tag('b'):
                        text('Av profit: ')
                    text(str(aProf)+'%')
                    doc.stag('br')
                    with tag('b'):
                        text('Av duration: ')
                    text(fmtTD(aDur))
            for i in t:
                with tag('tr'):
                    with tag('td','colspan="2"'):
                        try:
                            with tag('b'):
                                text(dt.utcfromtimestamp(i.exitTime).strftime(fmtTime))
                            text(exStr + str(i.exitPrice))
                            with tag('b'):
                                text( ' ' + '(profit='+ str(round(i.profit(),4)) + '%)')
                            doc.stag('br')
                        except:
                            pass
                        with tag('b'):
                            text(dt.utcfromtimestamp(i.entryTime).strftime(fmtTime))
                        text(enStr + str(i.entryPrice))
            with tag('tr'):
                with tag('td','colspan="2"'):
                    with tag('b'):
                        text('Number of trades: ')
                    text(str(N))
    with open('log.html','w') as f:
        f.write(doc.getvalue())
#<---

#--->Plot
def mkPlot(symbol,interval):
    k = getCloses(symbol,interval)
    T = np.array([i[0]-i[1] for i in list(TSI(k,5,50))])
    x = np.arange(len(T))

    mask1 = T < 0
    mask2 = T >= 0

    plt.bar(x[mask1], T[mask1], color = colorMedium)
    plt.bar(x[mask2], T[mask2], color = colorLight)

    plt.axhline(0, color=colorLight)

    plt.axis('off')
    plt.savefig('smi.png',transparent=True,bbox_inches='tight')
#<---

#---> Buying and Selling
def price(symbol):
    response = requests.get(BASE_URL + PRICE_EXT
                           ,params=priceParameters(symbol))
    return response.json()["price"]


def buy(symbol,interval):
    thetime = int(time.time())
    theprice = price(symbol)
    t = Trade(symbol,interval,thetime,theprice,None,None)
    s.add(t)
    s.commit()

def sell(symbol,interval):
    q = s.query(Trade)\
            .filter_by(symbol = symbol,interval = interval)\
            .order_by(Trade.id.desc()).first()
    thetime = int(time.time())
    theprice = price(symbol)
    s.query(Trade).filter_by(id = q.id)\
            .update({Trade.exitTime:thetime,Trade.exitPrice:theprice}
            ,synchronize_session = False)
    s.commit()

def sellOrbuy(symbol,interval):
    k = getCloses(symbol,interval)
    T = list(TSI(k,5,50))[-1]
    q = s.query(Trade)\
            .filter_by(symbol = symbol,interval = interval)\
            .order_by(Trade.id.desc()).first()
    # st = state(symbol,interval)
    st = q.state()
    print(st)
    print ((T[0],T[1]))
    if (st == 'SOLD') and (T[0] > T[1]):
        print('buy')
        buy(symbol,interval)
    elif (st == 'BOUGHT') and (T[0] < T[1]):
        print('sell')
        sell(symbol,interval)

#<---

def main (symbol,interval):
    while True:
        try:
            mkKlines(symbol,interval)
            addInitialPostion(symbol,interval)
            sellOrbuy(symbol,interval)
            mkHtml(symbol,interval,4)
            mkPlot(symbol,interval)
            sleep(SLEEPS[interval])
        except:
            print("Something went wrong, trying again in " 
                    + str(SLEEPS[interval] + " seconds"))
            sleep(SLEEPS[interval])

daemon = Daemonize(app="smierg", pid=pid, action=main(SYMBOL,INTERVAL))
daemon.start()
"""
vim:foldmethod=marker foldmarker=--->,<---
"""
