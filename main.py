import CytotoxicityExperiment as exp

path_to_file = ["C:/Users/User/Documents/Work/Data/MTS/18.12.20_MTS/HEK_plate_1.xlsx",
                "C:/Users/User/Documents/Work/Data/MTS/18.12.20_MTS/HEK_plate_2.xlsx"]

# Import data & delete blank rows
# df = exp.CytotoxicityAssay()
# data = pd.read_excel("C:/Users/User/Documents/Work/Data/MTS/09.04.21_MTS/row_data/pc3.xlsx")
# df.set_data(data)
#print(df.get_data())

# Standard import
df = exp.CytotoxicityAssay()
df.read_data(path_to_file)
#print(df.get_data())

#Substract background
df.sub_bgrnd_single(wlength=490, wlength_to_subst=700)

# Delete blank
df.delete_rows(colname='Образец', to_delete=['Бланк'])

# Information about dataset
print('Size of data:', df.get_data().shape)
print('Plates:', df.list_of_plates())
print('All drugs:', df.list_of_drugs(include_controls=False))
print('Control drugs:', df.list_of_controls())
print('Wavelengths:', df.list_of_wlengths())


#Add concentrations
df.add_concentration(drugs_dict={'MMAE': [0.5, 10], 'MS309': [100, 3],
                                 'MMP58': [100, 3], 'MS306': [100, 3]})

# Normalization
df.normalization()


# # Drop control samples
# df.drop_control()
#
# print(df.reshape())
#
# # # Export
# path_to_export = "C:/Users/User/Documents/Work/Data/MTS/09.04.21_MTS"
# exp.Export(data=df.reshape(), name='pc3.xlsx', path_to_dir=path_to_export)