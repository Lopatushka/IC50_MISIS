import pandas as pd
from math import log

class CytotoxicityAssay(object):
    """A cytotoxicity essay.

    Attributes:
        __data: Pandas.DataFrame
        __experiment_name
    """

    def __init__(self):
        self.__data = None
        self.__experiment_name = None

    def read_data(self, path):
        """Read data from .xlsx file

        :param path: str, path to .xlsx file
        :return: None
        """
        data = pd.read_excel(path, header=None)
        data.columns = data.iloc[2]
        self.__experiment_name = data.iloc[0, 0]

        data = data.drop([0, 1, 2])
        data = data.dropna(axis=1)

        data.reset_index(drop=True, inplace=True)

        self.__data = data

    def get_data(self):
        """Get pandas.DataFrame with data
        """
        return self.__data

    def get_exp_name(self):
        """Return experiment_name
        """
        return self.__experiment_name

    def list_of_controls(self):
        """Return list of controls whose type is 'Контр. образец'
        """
        if 'Контр. образец' not in self.__data['Тип'].unique():
            return
        else:
            controls = self.__data.loc[self.__data['Тип'] == 'Контр. образец', 'Образец'].apply(
                lambda x: x.split('_')[0]).unique().tolist()
            return controls

    def list_of_drugs(self, include_controls=True):
        """Return list of drugs.

        :param include_controls: bool, if True, include controls
        :return: list
        """
        list_drugs = self.__data['Образец'].apply(lambda x: x.split('_')[0]).unique().tolist()
        if include_controls:
            return list_drugs
        return [drug for drug in list_drugs if drug not in self.list_of_controls()]

    def list_of_wlengths(self):
        wlengths = self.__data['Длина волны'].unique().tolist()
        return wlengths

    def substract_background(self, wlength, wlength_to_subst):
        """ Substruct background absorption if it was measured.
        :param wlength: int, the wavelength of MTS/MTT reagent absorbtion
        :param wlength_to_subst: int, the background wavelength
        :return: None
        """
        background = self.__data.loc[self.__data['Длина волны'] == wlength_to_subst, "Погл."]
        background.reset_index(drop=True, inplace=True)

        self.__data = self.__data[self.__data['Длина волны'] == wlength]
        self.__data.reset_index(drop=True, inplace=True)

        self.__data["Погл."] = self.__data["Погл."] - background

    def add_concentration(self, axis='vertical', n_of_steps=8,
                          drugs_dict={}, log_scale=True):
        """
        Example of input:
        # Name, start concentration, dilution step
            di = {'MS-1': [100, 3],
                 'MS-2' : [40, 4]}
        """

        def create_concentration(start, step, n, result=None):
            if result is None:
                result = []
            if n == 0:
                return result
            result.append(start)
            create_concentration(start / step, step, n - 1, result)
            return result

        self.__data['Образец'] = self.__data['Образец'].apply(lambda x: x.split('_')[0])  # rename drugs

        # Checking
        drugs_in_table = self.__data.loc[self.__data['Тип'] != 'Контр. образец', 'Образец'].unique()
        for drug in drugs_in_table:
            if drug not in drugs_dict:
                raise IndexError(f"{drug} isn't in the dictionary!")

        self.__data['Концентрация'] = 0  # add new column

        if axis == 'vertical':
            for key, value in drugs_dict.items():
                replicates = sum(self.__data['Образец'] == key) // n_of_steps
                concentrations = create_concentration(value[0], value[1], n=n_of_steps)
                # Make concentration in log scale
                if log_scale:
                    concentrations = [log(conc, 10) for conc in concentrations]
                concentrations = concentrations * replicates
                self.__data.loc[self.__data['Образец'] == key, 'Концентрация'] = concentrations

        elif axis == 'horisontal':
            pass

    def normalization(self, control_dict={}, axis='vertical', n_of_steps=8):
        """
        Example of control_dict:
        normalization_dict = {'MS-1': 'DMSO', 'MS-2': 'DMSO'}
        """
        if control_dict == {}:
            # Use Контр. образец for all drugs
            if 'Контр. образец' not in self.__data['Тип'].unique():
                raise ValueError('There is no Control samples for normalization!')

            else:
                controls = self.__data.loc[self.__data['Тип'] == 'Контр. образец', 'Образец'].unique().tolist()
                n_control_drugs = len(controls)
                if n_control_drugs != 1:
                    raise ValueError('There is more than one Control samples for normalization!')
                else:
                    control_dict = {drug: controls[0] for drug in self.list_of_drugs() if drug != controls}

        # Cheking that Контр. образец and drugs are in table...

        self.__data['Погл. нормализ.'] = 0  # add new column

        if axis == 'vertical':
            for drug, control_drug in control_dict.items():
                replicates = sum(self.__data['Образец'] == drug) // n_of_steps

                # Subset control for each drug. Reshape the table and find mean
                control = self.__data.loc[self.__data['Образец'] == control_drug, 'Погл.']
                control = pd.DataFrame(control.values.reshape(n_of_steps, replicates))
                control['Mean'] = control.mean(axis=1)

                to_normalize = list(control['Mean']) * replicates

                self.__data.loc[self.__data['Образец'] == drug, 'Погл. нормализ.'] = 100 * self.__data.loc[
                    self.__data['Образец'] == drug, 'Погл.'] / to_normalize

        elif axis == 'horizontal':
            pass

    def drop_control(self, control_names=[]):
        if not control_names:
            control_names = self.list_of_controls()

        for name in control_names:
            self.__data.drop(self.__data[self.__data['Образец'] == name].index, inplace=True)

        self.__data.reset_index(drop=True, inplace=True)

    def subset(self, drug=None, n_of_steps=8):
        if drug not in self.list_of_drugs():
            return

        replicates = sum(self.__data['Образец'] == drug) // n_of_steps
        concentrations = self.__data.loc[self.__data['Образец'] == drug, 'Концентрация'].values[0:n_of_steps]

        subset = self.__data.loc[self.__data['Образец'] == drug, 'Погл. нормализ.']  # subset
        subset = pd.DataFrame(subset.values.reshape(n_of_steps, replicates))  # reshape 8-3
        subset['Концентрация'] = concentrations
        subset['Название'] = drug
        subset = subset[['Концентрация', 0, 1, 2, 'Название']]  # reorder cols

        return subset

    def reshape(self, drugs=[], n_of_steps=8):
        frames = []
        if not drugs:
            # process all drugs
            drugs = self.list_of_drugs()

        for drug in drugs:
            frames.append(self.subset(drug, n_of_steps=n_of_steps).drop('Название', axis=1))

        return pd.concat(frames, axis=1, keys=drugs)

if __name__ == '__main__':
    path_to_file = 'C:/Users/acer/Desktop/Work/test_data.xls'

    df = CytotoxicityAssay()
    df.read_data(path_to_file)

    # print(df.list_of_drugs(include_controls=True))
    # print(df.list_of_controls())

    print(df.list_of_wlengths())