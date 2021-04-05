import pandas as pd
from math import log


class CytotoxicityAssay(object):
    """A cytotoxicity essay class.
    Attributes:
        __data: Pandas.DataFrame
        __experiment_name
    """

    def __init__(self):
        self.__data = None
        self.__experiment_name = []

    def read_data(self, paths_list):
        """Read data from .xlsx files. Concatenates files and process dataframes.
        Initialise self.__data, self.__experiment_name. Rename drugs.
        :param paths_list: list, contains paths to .xlsx files
        :return: None
        """
        df = pd.DataFrame()
        plate_number = 0

        for f in paths_list:
            plate_number += 1
            data = pd.read_excel(f, header=None)
            data.columns = data.iloc[2]
            self.__experiment_name.append(data.iloc[0, 0])
            data = data.drop([0, 1, 2])
            data = data.dropna(axis=1)
            data.reset_index(drop=True, inplace=True)
            data['Планшет'] = 'Планшет' + ' ' + str(plate_number)
            data['Образец'] = data['Образец'].apply(lambda x: x.split('_')[0])
            df = df.append(data)

        self.__data = df

    def get_data(self):
        """Get pandas.DataFrame with data
        """
        return self.__data

    def get_exp_name(self):
        """Return experiment_name
        """
        return self.__experiment_name

    def delete_rows(self, colname=None, to_delete=None):
        """Delete rows.
        :param colname: str, name of interesting column
        :param to_delete: list, values in interesting columns needed to delete
        :return: None
        """
        mask = self.__data[colname].apply(lambda x: x not in to_delete)
        self.__data = self.__data[mask]

    def list_of_plates(self):
        """Return the list of plates name
        """
        return self.get_data()['Планшет'].unique().tolist()

    def list_of_controls(self):
        """Return list of controls whose type is 'Контр. образец'
        """
        if 'Контр. образец' not in self.__data['Тип'].unique():
            return []
        else:
            controls = self.__data.loc[self.__data['Тип'] == 'Контр. образец', 'Образец'].unique().tolist()
            return controls

    def list_of_drugs(self, include_controls=True):
        """Return list of drugs.
        :param include_controls: bool, if True, include controls
        :return: list
        """
        list_drugs = self.__data['Образец'].unique().tolist()
        if include_controls:
            return list_drugs
        return [drug for drug in list_drugs if drug not in self.list_of_controls()]

    def list_of_wlengths(self):
        """Return a list of wavelengths.
        """
        wlengths = self.__data['Длина волны'].unique().tolist()
        return wlengths

    def sub_bgrnd_single(self, wlength, wlength_to_subst):
        """ Substruct background absorption if it was measured in single file.
        :param wlength: int, the wavelength of MTS/MTT reagent absorption
        :param wlength_to_subst: int, the background wavelength
        :return: None
        """
        list_of_wlengths = self.list_of_wlengths()
        if (wlength not in list_of_wlengths) or (wlength_to_subst not in list_of_wlengths):
            raise ValueError('Check the values of wavlengths on data!')

        background = self.__data.loc[self.__data['Длина волны'] == wlength_to_subst, "Погл."]
        background.reset_index(drop=True, inplace=True)

        self.__data = self.__data[self.__data['Длина волны'] == wlength]
        self.__data.reset_index(drop=True, inplace=True)

        self.__data["Погл."] = self.__data["Погл."] - background

    def sub_bgrnd(self, paths_to_bgrnd):
        """Substruct background absorption if it was measured in additional file.
        :param paths_to_bgrnd: list, contains paths to .xlsx files wih background measurement
        :return: None
        """
        # Read background file
        df = pd.DataFrame()
        plate_number = 0
        for f in paths_to_bgrnd:
            plate_number += 1
            bgrnd = pd.read_excel(f, header=None)
            bgrnd.columns = bgrnd.iloc[2]
            bgrnd = bgrnd.drop([0, 1, 2])
            bgrnd = bgrnd.dropna(axis=1)
            bgrnd.reset_index(drop=True, inplace=True)
            bgrnd['Планшет'] = 'Планшет' + ' ' + str(plate_number)
            df = df.append(bgrnd)

        self.__data['Погл.'] = self.__data['Погл.'] - bgrnd['Погл.']

    def add_concentration(self, axis='vertical', n_of_steps=8,
                          drugs_dict=None, log_scale=True, exclude=None):
        """Add concentration column 'Концентрация' to dataset.
        :param axis: str {'vertical','horizontal'}, the mode of drug addition
        :param n_of_steps: int, the number of concentrations of each drug
        :param drugs_dict: dict, {drug name: [start concentration, dilution step]}
        :param log_scale: bool, if True, make apply log10 to concentration values
        :param exclude: list, list of drugs to exclude
        :return: None
        :raise: ValueError if drugs_dict.keys() and unique drugs are not equal
        """

        if drugs_dict is None:
            drugs_dict = {}

        def create_concentration(start, step, n, result=None):
            if result is None:
                result = []
            if n == 0:
                return result
            result.append(start)
            create_concentration(start / step, step, n - 1, result)
            return result

        # Checking drugs_dict input
        drugs_in_data = set(self.list_of_drugs(include_controls=False))
        drugs_from_arg = set(drugs_dict.keys())
        if not exclude:
            exclude = []
        if (drugs_in_data ^ drugs_from_arg) - set(exclude):
            raise ValueError(f'The drug set must be equal to the keys in drugs_dict!')

        f = lambda x: isinstance(x, (int, float))
        for li in drugs_dict.values():
            if len(li) == 2:
                if sum(map(f, li)) == 2:
                    continue
            raise ValueError('Incorrect drugs_dict values!')

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

        elif axis == 'horizontal':  # todo add 'horizontal' part in add_concentration()
            pass

    def normalization(self, control_dict=None, axis='vertical', n_of_steps=8, digits=None):
        """Normalize data to controls values. Add 'Погл. нормализ.' column.
        :param control_dict: dict, {drug name : control name}
        :param axis: str, {'vertical', 'horizontal'}, the mode of drug adding
        :param n_of_steps: int, the number of concentrations of each drug
        :param digits: int, number of digits after decimal. If None, no rounding
        :return: None
        """
        # if empty dict use 'Контр. образец' for all drugs
        if not control_dict:
            if 'Контр. образец' not in self.__data['Тип'].unique():
                raise ValueError('There is no Control samples for normalization!')
            else:
                controls = self.__data.loc[self.__data['Тип'] == 'Контр. образец', 'Образец'].unique().tolist()
                n_control_drugs = len(controls)
                if n_control_drugs != 1:
                    raise ValueError('There is more than one Control samples for normalization!')
                else:
                    control_dict = {drug: controls[0] for drug in self.list_of_drugs() if drug != controls}

        # Checking that 'Контр. образец' and drugs are in table
        list_of_drugs = set(self.list_of_drugs())
        drugs_from_dict = set(control_dict.keys())
        controls_from_dict = set(control_dict.values())
        if (drugs_from_dict | controls_from_dict) ^ list_of_drugs:
            raise ValueError('Incorrect control_dict value!')

        self.__data['Погл. нормализ.'] = 0  # Add new column
        # Initialize for control samples
        for control in controls_from_dict:
            self.__data.loc[self.__data['Образец'] == control, 'Погл. нормализ.'] = self.__data.loc[self.__data['Образец'] == control, 'Погл.']

        if axis == 'vertical':
            for drug, control_drug in control_dict.items():
                replicates = sum(self.__data['Образец'] == drug) // n_of_steps

                # Subset control for each drug. Reshape the table and find mean
                control = self.subset(drug=control_drug, n_of_steps=n_of_steps)
                control = control.drop(['Название', 'Концентрация'], axis=1)
                control['Mean'] = control.mean(axis=1)
                to_normalize = list(control['Mean']) * replicates

                self.__data.loc[self.__data['Образец'] == drug, 'Погл. нормализ.'] = 100 * self.__data.loc[
                    self.__data['Образец'] == drug, 'Погл.'] / to_normalize

        elif axis == 'horizontal':  # todo add 'horizontal' part for normalization
            pass

        if isinstance(digits, int):
            self.__data['Погл. нормализ.'] = self.__data['Погл. нормализ.'].apply(lambda x: round(x, digits))

    def drop_control(self, control_names=None):
        """Drop control drugs.
        :param control_names: list, list of control names., e.x. ['DMSO', 'Doc']
        :return: None
        :raise: ValueError if there is no control_names to remove
        """
        if not control_names:
            control_names = self.list_of_controls()
            if not control_names:
                raise ValueError("There is no Control samples to remove!")

        for name in control_names:
            self.__data.drop(self.__data[self.__data['Образец'] == name].index, inplace=True)

        self.__data.reset_index(drop=True, inplace=True)

    def subset(self, drug=None, n_of_steps=8):
        """Subset one particular drug data from the dataframe for GraphPad Prism program.
        :param drug: str, drug name
        :param n_of_steps: int, number of dilution steps for each drug
        :return: pandas.DataFrame or None if there is no such drug name in the dataframe
        """
        if drug not in self.list_of_drugs():
            return

        replicates = sum(self.__data['Образец'] == drug) // n_of_steps

        # Subset by drug name
        subset = self.__data.loc[self.__data['Образец'] == drug]

        # Create empty dataframe
        subset_rechaped = pd.DataFrame(columns=['Название', 'Концентрация'])
        for rep in range(replicates):
            subset_rechaped[rep] = 0

        # Add cols with data to subset_rechaped dataframe and fill them
        j = 0
        rep = 0
        while j < n_of_steps * replicates:
            if 'Погл. нормализ.' in self.__data:
                subset_rechaped[rep] = subset['Погл. нормализ.'][j: (j + n_of_steps)].tolist()
            else:
                subset_rechaped[rep] = subset['Погл.'][j: (j + n_of_steps)].tolist()
            rep += 1
            j += n_of_steps

        if 'Концентрация' in self.__data:
            concentrations = self.__data.loc[self.__data['Образец'] == drug, 'Концентрация'].values[0:n_of_steps]
            subset_rechaped['Концентрация'] = concentrations

        subset_rechaped['Название'] = drug
        return subset_rechaped

    def reshape(self, drugs=None, n_of_steps=8):
        """Reshape dataframe for GraphPad Prism program
        :param drugs: list, list of drugs
        :param n_of_steps: int, number of dilution steps
        :return: pandas.DataFrame
        """
        frames = []
        if not drugs:
            # process all drugs
            drugs = self.list_of_drugs()

        for drug in drugs:
            frames.append(self.subset(drug, n_of_steps=n_of_steps).drop('Название', axis=1))

        return pd.concat(frames, axis=1, keys=drugs)


class CytotoxicityExperiment(object):
    def __init__(self):
        pass
