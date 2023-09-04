import numpy as np

class CSV_Quality_checker:
    def __init__(self, dataframe):
        self.df = dataframe

    
    def calculation_vif(self, column_index):
        '''input col name that want to know vif correlation'''
        independent_cols = [col for i, col in enumerate(self.df.columns) if i != column_index]

        X = self.df.loc[:, independent_cols].values
        y = self.df.loc[:, column_index].values

        vif = 1 / (1 - np.linalg.norm(np.linalg.lstsq(X, y, rcond= None)[0]) ** 2)

        if vif >= 5:
            print(f"WARN vif score : {vif}")
            return vif
        elif 2 <= vif < 5:
            print(f"SUSPECT dependent vif score : {vif}")
            return vif
        else:
            print(f"Fine vif score : {vif}")
            return vif