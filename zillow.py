#Zillow Webscraper by Drew Fingerhut
#4/1/2022

#Importing the necessary Libraries
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests

#Establishing the lists to be populated outside of iteration 
price = []
bed = []
address = []

#Creating the loop for a specified range representing the number of pages to scrape
for i in range(30):

#Passing in a request header as to get the dynamic page rather than the static page that can not be scraped    
    req_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.8',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
                    }

#Generating a new url for each page that is to be requested 
    with requests.Session() as s:
       page_number = i+1
       page = str(page_number)+'_p/'
       city = 'salt-lake-city/' #*****change this city to what you want*****
       url = 'https://www.zillow.com/homes/for_sale/'+city+page    
       r = s.get(url, headers=req_headers)

#Parse the requested html and look for each title card that has the listing info enclosed in it
    soup = BeautifulSoup(r.content, 'html.parser')
    house_elements = soup.find_all("div", class_="list-card-info")

#Search through each title card for price, beds, and address and populating to the preestablished lists only keeping the text
    for house_char in house_elements:
        price_element = house_char.find("div", class_="list-card-price")
        bed_element = house_char.find("ul", class_ ="list-card-details" )
        address_element = house_char.find("address", class_="list-card-addr")
        if price_element != None:    
            price.append(price_element.text)
        elif price_element == None:
            price.append('Blank')
        if bed_element != None:    
            bed.append(bed_element.text)
        elif bed_element == None:
            bed.append('Blank')
        if address_element != None:
            address.append(address_element.text)
        elif address_element == None:
            address.append('Blank')

#Populate the data frame with the listes that were just appended to            
    df = pd.DataFrame ({
                    "Price": price,
                    "Bed": bed,
                    "Address": address
                        })
#Create a save point of the data frame before altering the data to ensure there is not loss    
    df_new = df.copy()

#Replacing unnecessary text in Bed column with spaces so that it can be seperated into individual columns
    df_new['Beds'] = df_new['Bed'].str.replace(' bds',' ')
    df_new['Beds'] = df_new['Beds'].str.replace(' ba',' ')
    df_new['Beds'] = df_new['Beds'].str.replace(' sqft',' ')
    df_new['Beds'] = df_new['Beds'].str.replace(',','')
    df_new['Beds'] = df_new['Beds'].str.replace('--','')
    df_new['Beds'] = df_new['Beds'].str.replace('/',' ')   
    df_new['Beds'] = df_new['Beds'].str.split('-')
    df_new['Beds'] = df_new['Beds'].fillna(0)
    df_new.drop(df_new.tail(1).index,inplace=True)
 
 #CLeaning and dropping the wording such as Multi-family for sale or Townhouse for sale from data frame
    split_df = pd.DataFrame(df_new['Beds'].tolist(),columns=['Info','Lose','Ex'])
    split_df = split_df.drop(['Lose','Ex'],axis=1)
   
 #Splititng Bed coloumn post cleaning into 3 seperate columns for bed, bath, and square feet
    split_df[['Bedrooms','Bathrooms','Sq_Feet']] = split_df['Info'].str.split(' ', n=2,expand=True)
    split_df = split_df.drop(['Info'],axis=1)
    
#Concatting our split data frame to the original and dropping now unnecessary columns    
    full_df = pd.concat([df_new, split_df],axis=1)
    full_df = full_df.drop(['Bed','Beds'],axis=1)

#Displaying our full data frame after iterating through all the pages we defined it to    
full_df
