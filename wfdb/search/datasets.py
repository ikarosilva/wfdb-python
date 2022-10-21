# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
'''
Created on Sep 7, 2022

@author: ikaro
'''
import sys
import urllib.request, json
import pandas as pd
import os
from pathlib import Path
import pandas as pd

CACHE_DIR=os.path.join(".",'cache') #TODO: Discuss with team where cache should reside
dataset_mapper={'abstract':'Data set description','main_storage_size':'Volume of data (GB)','slug':'Source'}

def get_records(db_name: str=None,db_version: str=None,force: bool=False)-> pd.DataFrame:
    record_cache_path=os.path.join(CACHE_DIR, db_name, db_version)
    record_cache_file=os.path.join(record_cache_path,"RECORDS")
    Path(record_cache_path).mkdir(parents=True, exist_ok=True)
    records=None
   
    if os.path.exists(record_cache_file) or force:
        records= pd.read_csv(record_cache_path+"RECORDS")
    else:
        #Download from PhysioNet into cache
        record_url="https://physionet.org/files/%s/%s/RECORDS"%(db_name,db_version)
        with urllib.request.urlopen(record_url) as url:
            myfile = url.read().decode("utf-8")
            records = pd.DataFrame(myfile.split("\n"))
            #records.rename(columns={"0":"record")
            #TODO: rename column and save into cache
    return records

def search_physionet()-> pd.DataFrame:
    '''
        Returns a Pandas Dataframe contain all public datasets in PhysioNet
    '''
    with urllib.request.urlopen("https://physionet.org/rest/database-list/") as url:
        myfile = url.read().decode("utf-8")
        data = json.loads(myfile)
        df = pd.DataFrame.from_dict(data)
        df=df.rename(columns=dataset_mapper)
        df['Source type']='physionet'
        df=df.drop(columns=['compressed_storage_size'])
        df['Volume of data (GB)']=df['Volume of data (GB)']/1e+9
        #df['records']=-1 # For future ....
       
    return df

def search_abstracts(df: pd.DataFrame=None,topics: dict=None)-> pd.DataFrame:
    cols=['Title','Description','Topics','db']
    hits=pd.DataFrame()
    for topic in topics.keys():
        topic_words=topics[topic]
        for _,row in df.iterrows():
            title=[x.lower() for x in row['title'].split(" ")]
            is_relevant = list(set([x for x in title for t in topic_words if x.find(t)>-1]))
            if not len(is_relevant):
                #Search in description if topic is not in title
                desc=[x.lower() for x in row['Data set description'].split(" ")]
                is_relevant = list(set([x for x in desc for t in topic_words if x.find(t)>-1]))
            if len(is_relevant):
                tmp_hits = pd.DataFrame([[row['title'],row['Data set description'],is_relevant,row['Source']]], columns=cols)
                hits=hits.append(tmp_hits)
        if len(hits):
            hits=hits.drop_duplicates(subset=['db'], keep='first').reset_index()
    return hits
   
if __name__ == '__main__':
    '''
     Example search
     TODO: Make this into a CLI
    '''
   
    pd.set_option('display.width', 10000)
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    db_info = search_physionet()
   
    #Search database abstracts
    topics={'fetal':['fetal','pregnan','foetal','premature']}
    hits= search_abstracts(db_info,topics)
    print(hits)
    
