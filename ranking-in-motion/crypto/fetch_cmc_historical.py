import requests,datetime as dt,csv,time
rows=[];d=dt.date(2017,11,1)
while d<=dt.date(2019,1,1):
    for a in range(3):
        try:
            j=requests.get("https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listings/historical",params=dict(date=d.isoformat(),limit=25,convertId=2781),headers={"User-Agent":"Mozilla/5.0"},timeout=20).json();break
        except Exception: time.sleep(2)
    for c in j.get("data",[]):
        rows.append((d.isoformat(),c["name"],c["symbol"],c["quotes"][0]["marketCap"]))
    d+=dt.timedelta(days=3);time.sleep(0.3)
w=csv.writer(open("crypto_mcap_raw.csv","w"));w.writerow(["date","name","symbol","market_cap_usd"]);w.writerows(rows)
print(len(rows))
