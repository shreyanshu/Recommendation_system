'''
Created on:
@author:
'''
import pandas as pd
import numpy as np
import os


def fillPeopleProducts(dfpurchases):
    df_people_product = dfpurchases.groupby(['USER_ID', 'PRODUCT_ID']).size().unstack()
    df_people_product = df_people_product.fillna(0).astype(int)
    return df_people_product


def fillProductCoPurchase(dfpurchases):
    dfpeopleProducts = fillPeopleProducts(dfpurchases)
    df_copay = dfpeopleProducts.T.dot(dfpeopleProducts)
    np.fill_diagonal(df_copay.values, 0)
    return df_copay, dfpeopleProducts


def reformatProdData(dfprod):
    '''reformat the dfproducts separating the category from the item description
       leaving only the name of the product in the description column '''
    dfprod['Category'] = dfprod['DESCRIPTION'].str.strip().str.split('(').str.get(1)
    dfprod['DESCRIPTION'] = dfprod['DESCRIPTION'].str.split('(').str.get(0).str.strip()
    dfprod['Category'] = dfprod['Category'].str.slice(0,-1 )


def give_recommendations(df_copay, choice, most_frequent_product):
    product_series = df_copay.loc[choice, :]
    max_copurchase_score = product_series.max()
    print('[Maximum co-purchasing score %i]' % max_copurchase_score)
    if max_copurchase_score>0:
        recommendations = list(product_series[product_series == max_copurchase_score].index)
    else:
        recommendations = most_frequent_product
    print('Recommend with %s :' % choice.upper(), recommendations)
    return recommendations


def findMostBought(dfpeopleProducts):
    series_count = dfpeopleProducts.sum()
    max_val = series_count.max()
    return list(series_count[series_count==max_val].index)


def printRecProducts(dfprod, recommendations):
    dfprod_recommended = dfprod.loc[dfprod['PRODUCT_ID'].isin(recommendations)].copy()
    max_width = dfprod_recommended.Category.str.len().max()
    dfprod_recommended = dfprod_recommended.sort_values('Category')
    dfprod_recommended = dfprod_recommended.groupby('Category')
    for name, group in dfprod_recommended:
        for index, row in group.iterrows():
            if index == group.index.min():
                description = 'IN ' + name.upper().ljust(max_width, ' ') + ' -- ' + row['DESCRIPTION']
                if not pd.isnull(row['PRICE']) :
                    description = description + ', $' + '%.2f'%row['PRICE']
            else:
                description = ' '*(max_width+3) + ' -- ' + row['DESCRIPTION']
                if not pd.isnull(row['PRICE']):
                    description = description + ', $' + '%.2f'%row['PRICE']
            print(description)


def main():
 
    #pd.describe_option('display')
    pd.set_option('display.max_columns', 1000)  # or 1000
    pd.set_option('display.max_rows', 1000)  # or 1000
    pd.set_option('display.width', 1000)  # or 199


    prodfilename = 'prod.csv'; purchasefilename  = 'purchases.csv'
    folder = input('Please enter name of folder with product and purchase data files: ('+ prodfilename + ' and ' + purchasefilename + ')')
    file_purch = os.path.join(folder, purchasefilename) #Create the path to the purchases.csv file
    file_prod =  os.path.join(folder, prodfilename) #Create the path to the prod.csv file

    dfpurchases = pd.read_csv(file_purch)   #Create the purchase DataFrame
    dfprod  = pd.read_csv(file_prod)    #Create the product DataFrame
    if dfprod['PRICE'].dtype != np.number:
        dfprod['PRICE'] = dfprod['PRICE'].replace({' ': None})
        dfprod = dfprod.astype({'PRICE': float})
    reformatProdData(dfprod)
    print('Preparing the co-purchasing matrix…')
    df_copay, dfpeopleProducts = fillProductCoPurchase(dfpurchases)
    max_purchased_items = findMostBought(dfpeopleProducts)
    choice = input('Which product was bought? Enter product id or press enter to quit.')
    while choice!='':
        recommendations = give_recommendations(df_copay, choice, max_purchased_items)
        printRecProducts(dfprod, recommendations)
        choice = input('Which product was bought? Enter product id or press enter to quit.')


main()