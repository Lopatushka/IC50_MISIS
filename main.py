import CytotoxicityExperiment as exp

path_to_file = ["C:/Users/acer/Desktop/Work/Data/MTS/05.04.21_MTS/HEK293_490.xls"]
path_to_back = ["C:/Users/acer/Desktop/Work/Data/MTS/05.04.21_MTS/HEK293_700.xls"]

# Import data & delete blank rows
df = exp.CytotoxicityAssay()
df.read_data(path_to_file)

# Substract background
df.sub_bgrnd(path_to_back)

# Delete blank
df.delete_rows(colname='Образец', to_delete=['Бланк'])

# Information about dataset
print('Size of data:', df.get_data().shape)
print('Plates:', df.list_of_plates())
print('All drugs:', df.list_of_drugs(include_controls=False))
print('Control drugs:', df.list_of_controls())
print('Wavelengths:', df.list_of_wlengths())

# Add concentrations
df.add_concentration(drugs_dict={'DG4ClSe': [100, 3],
                                 'DG4ClSek': [50, 3],
                                 'DG603': [100, 3],
                                 'DG603k': [100, 3],
                                 'DG605': [100, 3],
                                 'DG605k': [100, 3],
                                 'DG606k': [100, 3],
                                 'DG608k': [100, 3],
                                 'DGAllC2': [100, 3],
                                 'Dox': [53, 3]})

# Normalization
df.normalization()

# Drop control samples
df.drop_control()

# Export
path_to_export = "C:/Users/acer/Desktop/Work/Data/MTS/05.04.21_MTS/HEK293_results.xlsx"
df.reshape().to_excel(path_to_export)