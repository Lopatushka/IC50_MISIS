import CytotoxicityExperiment as exp

path_to_file = ["C:/Users/User/Documents/Work/Data/MTS/12.04.21_MTS/12.04.21_MTS_HEK293.xlsx"]

# Import data & delete blank rows
df = exp.CytotoxicityAssay()
df.read_data(path_to_file)

# Substract background
df.sub_bgrnd_single(wlength=490, wlength_to_subst=700)

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
                                 'DG4CkSek': [50, 3],
                                 'DG605k': [100, 2],
                                 'DG606k': [200, 2],
                                 'DG618k': [100, 3],
                                 'DGAllC2': [100, 2]
                                 })

# Normalization
df.normalization(control_dict={'DG4ClSe': 'DMSO-dil3', 'DG4CkSek': 'DMSO-dil3',
                               'DG605k': 'DMSO-dil2', 'DG606k': 'DMSO-dil2',
                               'DG618k': 'DMSO-dil3', 'DGAllC2': 'DMSO-dil2'})

# Drop control samples
df.drop_control(control_names=['DMSO-dil2', 'DMSO-dil3'])

print(df.reshape())
#
# # Export
path_to_export = "C:/Users/User/Documents/Work/Data/MTS/12.04.21_MTS/"
exp.Export(data=df.reshape(), name='HEK293.xlsx', path_to_export=path_to_export)

