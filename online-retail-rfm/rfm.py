import pandas as pd
import numpy as np
import datetime as dt


#Datasetini okumak
pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)
pd.set_option('display.float_format',lambda x:'%.3f' %x)
df_=pd.read_excel("online_retail_II.xlsx")
df=df_.copy()

#Dataseti Betimsel istatistiklerine Göz Atmak
df.columns
df.shape
df.isnull().sum()
df.describe().T
df["Description"].nunique()
df["Description"].value_counts().head()

#Eksik gözlemleri veri setinden çıkarmak
df.isnull().sum()
df.dropna(inplace=True)

#En çok sipariş edilen 5 ürünü çoktan aza doğru sıralamak
df.groupby("Description").agg({"Quantity":"sum"}).sort_values("Quantity",ascending=False).head()

#Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartmak
df=df[~df["Invoice"].str.contains("C",na=False)]

#Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz
df["TotalPrice"]=df["Quantity"]*df["Price"]

#Recency, Frequency ve Monetary tanımlarını yapınız.
today_date = dt.datetime(2011,12,11)
rfm = df.groupby("Customer ID").agg({"InvoiceDate":lambda InvoiceDate:(today_date-InvoiceDate.max()).days,
                                     "Invoice":lambda Invoice:Invoice.nunique(),
                                     "TotalPrice":lambda TotalPrice:TotalPrice.sum()})

rfm.columns=["recency","frequency","monetary"]

# Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz
rfm["recency_score"]=pd.qcut(rfm["recency"],5,labels=[5,4,3,2,1])
rfm["frequency_score"]=pd.qcut(rfm["frequency"].rank(method="first"),5,labels=[1,2,3,4,5])
rfm["monetary_score"]=pd.qcut(rfm["monetary"],5,labels=[1,2,3,4,5])

rfm["RF_SCORE"]=rfm["recency_score"].astype("str")+rfm["frequency_score"].astype("str")

#RF Skorunun Segment Olarak Tanımlanması
seg_map = {
    r'[1-2][1-2]':'hibernating',
    r'[1-2][3-4]':'at_Risk',
    r'[1-2]5':'cant_loose',
    r'3[1-2]':'about_to_sleep',
    r'33':'need_attention',
    r'[3-4][4-5]':'loyal_customers',
    r'41':'promising',
    r'51':'new_customers',
    r'[4-5][2-3]':'potential_loyalists',
    r'5[4-5]':'champions'
}

rfm["segment"]=rfm["RF_SCORE"].replace(seg_map,regex=True)

rfm.groupby("segment").agg({"segment":"count"})

loyal_cust=rfm[rfm["segment"]=="loyal_customers"]
loyal_cust = loyal_cust.reset_index()
loyal_cust_custID=loyal_cust["Customer ID"]

loyal_cust_custID.to_csv("Loyal_Cust_ID.csv")
