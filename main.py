import CytotoxicityExperiment as exp
HEK_exp = ['C:/Users/acer/Desktop/Work/Data/MTS/18.12.20_MTS/HEK_plate_1.xlsx',
           'C:/Users/acer/Desktop/Work/Data/MTS/18.12.20_MTS/HEK_plate_2.xlsx']

# Import data
df = exp.CytotoxicityAssay()
df.read_data(HEK_exp)

print(df.get_data().columns)

# Delete blank rows
#df.delete_rows(colname='Тип', to_delete=['blank'])

# Information about dataset
print('Size of data:', df.get_data().shape)
print('All drugs:', df.list_of_drugs(include_controls=True))
print('Control drugs:', df.list_of_controls())
print('Wavelengths:', df.list_of_wlengths())

# Substract background
df.substract_background(490, 700)

# Add concentrations
df.add_concentration(axis='vertical', n_of_steps=8,
                         drugs_dict={"MS309": [100, 25], "MMP58": [100, 25], "MS306": [100, 25]},
                         log_scale=True)


# Normalization to controls
    #df.normalization(control_dict={}, digits=3)

    # Drop controls
    #df.drop_control()

    # Subset
    #sb = df.subset(drug='MS-1')
    #print(sb)

    # Reshape
    #results = df.reshape()
    #print(results)

    # Export to excel
    #results.to_excel('C:/Users/acer/Desktop/Work/test_results.xls')

    # print(df.get_data().head(3))
    # print(df.get_data().tail(3))