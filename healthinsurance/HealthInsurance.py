import pickle
import numpy  as np
import pandas as pd
import inflection

class HealthInsurance (object):
    def __init__ (self):
        self.home_path = ""
        self.annual_premium_scaler =            pickle.load(open(self.home_path + 'features/annual_premium_scaler.pkl', 'rb'))
        self.age_scaler =                       pickle.load(open(self.home_path + 'features/age_scaler.pkl', 'rb'))
        self.vintage_scaler =                   pickle.load(open(self.home_path + 'features/vintage_scaler.pkl','rb'))
        self.target_encode_gender_scaler =      pickle.load(open(self.home_path + 'features/target_encode_gender_scaler.pkl','rb'))
        self.target_encode_region_code_scaler = pickle.load(open(self.home_path + 'features/target_encode_region_code_scaler.pkl','rb'))
        self.policy_sales_channel_scaler =      pickle.load(open(self.home_path + 'features/freq_policy_sales_channel_scaler.pkl','rb'))

    def renomear_colunas( self,df1 ):
        cols_old = df1.columns
        snakecase = lambda x: inflection.underscore( x )
        cols_new = list( map( snakecase, cols_old ) )
        df1.columns = cols_new

        return df1

    def feature_engineering(self,df2):

        # vehicle_age
        df2['vehicle_age'] = df2['vehicle_age'].apply( lambda x: 'over_2_years' if x == '> 2 Years' else 'between_1_2_year' if x == '1-2 Year' else 'below_1_year' ) 

        # vehicle_damage    
        df2['vehicle_damage'] = df2['vehicle_damage'].apply(lambda x: 1 if x == 'Yes' else 0)

        return df2
      

    def preparacao (self,df5):

        # annual_premium (por causa do gráfico)
        df5['annual_premium'] = self.annual_premium_scaler.transform(df5[['annual_premium']].values)

        # age (por causa do gráfico)
        df5['age'] = self.age_scaler.transform(df5[['age']].values)

        # vintage (por causa do gráfico)
        df5['vintage'] = self.vintage_scaler.transform(df5[['vintage']].values)

        # gender - Target Encoding / One Hot Encoding 
        df5.loc[:,'gender'] = df5['gender'].map(self.target_encode_gender_scaler)
        
        # region_code (eu achava que era rescaling) -  Target Encoding / Frequency Encoding
        df5.loc[:,'region_code'] = df5['region_code'].map(self.target_encode_region_code_scaler)

        # policy_sales_channel
        df5.loc[:,'policy_sales_channel'] = df5['policy_sales_channel'].map(self.policy_sales_channel_scaler)
        
        #Feature Selection
        cols_selected = ['annual_premium', 'vintage', 'age', 'region_code', 'vehicle_damage', 'previously_insured', 'policy_sales_channel']
        
        df5 = df5.fillna(0)

        return df5[cols_selected]
    
    def get_prediction( self, model, original_data, test_data ):
        # prediction
        pred = model.predict_proba( test_data )
            
        # join pred into the original data
        original_data['prediction'] = pred[:,1].tolist()
            
        return original_data.to_json( orient='records', date_format='iso' ) 
    
