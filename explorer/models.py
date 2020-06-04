# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from datetime import datetime as dt

fmtTime = '%H' + ':' + '%M' + ', ' + '%d' + ' of ' + '%b' 
# fmtTime = '['+'%Y' + '-' + '%m' + '-' + '%d' + ' ('+'%H'+':'+'%M'+')'+']'

class Kline(models.Model):
    symbol = models.CharField(max_length=10)
    interval = models.CharField(max_length=4)
    opentime = models.IntegerField(db_column='openTime')
    open = models.CharField(max_length=16,blank=True, null=True)
    high = models.CharField(max_length=16,blank=True, null=True)
    low = models.CharField(max_length=16,blank=True, null=True)
    close = models.CharField(max_length=16,blank=True, null=True)
    volume = models.CharField(max_length=16,blank=True, null=True)
    numoftrades = models.IntegerField(
        db_column='numOfTrades', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kline'


class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=10,blank=True, null=True)
    interval = models.CharField(max_length=4,blank=True, null=True)
    entrytime = models.IntegerField(
        db_column='entryTime', blank=True, null=True)
    entryprice = models.CharField(
        max_length=16,db_column='entryPrice', blank=True, null=True)
    exittime = models.IntegerField(
        db_column='exitTime', blank=True, null=True)
    exitprice = models.CharField(
        max_length=16,db_column='exitPrice', blank=True, null=True)

    def duration(self):
        try:
            return self.exittime-self.entrytime
        except:
            try:
                return int(time.time())-self.entrytime
            except:
                return 0

    def profit(self):
        try:
            exp = float(self.exitprice)
            enp = float(self.entryprice)
            return (exp-enp)/enp*100
        except:
            return None 

    def status(self):
        if self.exittime is not None:
            return 'CLOSED'
        else:
            return 'OPEN'

    def state(self):
        if self.entrytime == None or self.exittime != None:
            return 'SOLD'
        elif self.exittime == None:
            return 'BOUGHT'

    def entrytime_human (self):
        try:
            return dt.utcfromtimestamp(self.entrytime)
        except:
            return None 

    def exittime_human (self):
        try:
            return dt.utcfromtimestamp(self.exittime)
        except:
            return None 

    class Meta:
        managed = False
        db_table = 'trade'
