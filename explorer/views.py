from django.conf.urls import url
from django.http import HttpResponse
from django.template import engines
from django.template.loader import render_to_string
import logging
from django.conf import settings
from explorer.models import Trade, Kline
from numpy import prod
import SMIerg2020 as smi
from datetime import timedelta as td


# Create your views here.

fmt = getattr(settings, 'LOG_FORMAT', None)
lvl = getattr(settings, 'LOG_LEVEL', logging.DEBUG)

logger = logging.getLogger(__name__)
logging.basicConfig(format=fmt, level=lvl)
logger.debug("Logging started on %s for %s" %
             (logging.root.name, logging.getLevelName(lvl)))

pageTitle = 'SMI ergodic indicator'
SYMBOLS = ['ETHBTC','ETHUSDT','BTCUSDT']
INTERVALS = ['1m','30m','1h','4h','8h']

exStr = ' Exit: '
enStr = ' Ntry: '

def fmtTD(x):
    h = int(x/3600)
    m = int((x % 3600)/60)
    if h > 0:
        return str(h) + 'h' + str(m) + 'm'
    else:
        return str(m) + 'm'

# WIDTH = 500 # px
# HEIGHT = 250 # px
# BORDER_WIDTH = 0.5 # px

def tops(x):
    if x >= 0:
        return (1 - x)*50
    if x < 0:
        return 50

def mkPlot(symbol,interval):
    k = smi.getCloses(symbol,interval)
    T = [i[0]-i[1] for i in list(smi.TSI(k,5,50))][:100]
    T.reverse()
    m = max([abs(t) for t in T])
    L = len(T)
    w = 100/L 
    # totalwidth = w*L+0.5*(L+1)
    # totalheight = HEIGHT + 4*BORDER_WIDTH
    return [{'top':tops(x/m),
             'height':abs(x/m*50),
             'left':l*w,
             'width':w,
             # 'totalwidth':totalwidth,
             # 'totalheight':totalheight,
             } for (x,l) in zip(T,range(L))]

# def home(request):
    # symbol = 'ETHBTC'
    # interval = '30m'
def home(request,symbol,interval):
    symbol = symbol.upper()
    interval = interval.lower()
    lastTrades = Trade.objects.filter(
        symbol=symbol, interval=interval).order_by('-id')
    N = len(list(lastTrades)) - 1
    if N > 0:
        T = lastTrades[:N]
        totalprofit = round(
            (prod([i.profit()/100+1 for i in T if i.profit() != None]) - 1)*100, 4)
        averageprofit = round(((totalprofit/100+1)**(1/N)-1)*100, 4)
        if lastTrades[0].exittime == None:
            N = N - 1
        try:
            averageduration = sum([i.duration() for i in T])/N
        except:
            averageduration = 0
    else:
        T = lastTrades[:0]
        totalprofit = 0
        averageprofit = 0
        averageduration = 0
    html = render_to_string('home.html', {
        'title': pageTitle,
        'symbol':symbol,
        'interval':interval,
        'symbols':SYMBOLS,
        'intervals':INTERVALS,
        'trades': T[:9],
        'totalprofit': totalprofit,
        'averageprofit': averageprofit,
        'numoftrades': N,
        'averageduration':fmtTD(averageduration),
        'plot':mkPlot(symbol,interval),
        })
    return HttpResponse(html)
