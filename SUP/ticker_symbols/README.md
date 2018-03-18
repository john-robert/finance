How to get list of stock symbols
--------------------------------

Downloaded list of stock symbols as txt files for specific stock exchanges (last update: 2018-03-17):
http://www.eoddata.com/symbols.aspx
For XETRA, I downloaded symbols from:
http://www.xetra.com/xetra-en/instruments/instruments

For now there is:
American Stock Excahnge (AMEX), NASDAQ (which belongs to AMEX), New York Stock Exchange (NYSE), London Stock Exchange (LSE), and XETRA.

For 'eoddata' data, you get a tab-sperated txt file with 1 header line as follows: 
	Symbol	Company (multiple copmany words space seperated)
	...		... 
	...		... 


To convert theses files to csv files, I did in Python via the pandas libary:

```
df = pd.read_csv(file+'.txt', sep="\t", header=1, names=["Symbol", "Company"])	# read file with tab seperator, ignore first header line, assign names as column titles
df = df[['Company', 'Symbol']]							# rewrite column order so that first 'Company', then 'Symbol'
df.to_csv(file+'.csv', sep=";")	
```

file as csv file, using tab seperation

where 'file' is the downloaded file name without file extension.
A similar processing applies to the XETRA file downloaded where column organisation is different.
