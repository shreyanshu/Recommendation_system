'''
Created on:
@author:
'''
def reformatProdData(dfprod):
    '''reformat the dfproducts separating the category from the item description
       leaving only the name of the product in the description column '''
    dfprod['Category'] = dfprod['DESCRIPTION'].str.strip().str.split('(').str.get(1)
    dfprod['DESCRIPTION'] = dfprod['DESCRIPTION'].str.split('(').str.get(0).str.strip()
    dfprod['Category'] = dfprod['Category'].str.slice(0,-1 )