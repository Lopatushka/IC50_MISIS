import CytotoxicityExperiment as exp

HEK_exp = ['C:/Users/acer/Desktop/Work/Data/MTS/18.12.20_MTS/HEK_plate_1.xlsx',
           'C:/Users/acer/Desktop/Work/Data/MTS/18.12.20_MTS/HEK_plate_2.xlsx']

# Import data & delete blank rows
df = exp.CytotoxicityAssay()
df.read_data(HEK_exp)
df.delete_rows(colname='Тип', to_delete=['blank'])

# Substract background
df.substract_background(490, 700)

# Information about dataset
print('Size of data:', df.get_data().shape)
print('Plates:', df.list_of_plates())
print('All drugs:', df.list_of_drugs(include_controls=False))
print('Control drugs:', df.list_of_controls())
print('Wavelengths:', df.list_of_wlengths())

# Add concentrations
df.add_concentration(axis='vertical', n_of_steps=8,
                     drugs_dict={"MS309": [100, 3],
                                 "MMP58": [100, 3],
                                 "MS306": [100, 3],
                                 "MMAE": [0.5, 10]},
                     exclude=['DMSO'],
                     log_scale=True)

# Normalization to controls
df.normalization(control_dict={"MS309": "DMSO",
                                "MMP58": "DMSO",
                                "MS306": "DMSO",
                                "MMAE": "DMSO"}, digits=3)

# Drop controls
df.drop_control(['DMSO'])

# Subset
#sb = df.subset(drug='DMSO')
#print(sb)

# Reshape
results = df.reshape()
print(results)

# Export to excel
#results.to_excel('C:/Users/acer/Desktop/Work/Data/MTS/18.12.20_MTS/HEK_results.xlsx')

#print(df.get_data().head(16))
#print(df.get_data().tail(16))
