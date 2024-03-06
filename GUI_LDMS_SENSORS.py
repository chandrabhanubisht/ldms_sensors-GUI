
import PyQt5
from PyQt5 import QtWidgets,QtCore
import pandas as pd
import os
import re


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My PyQt5 GUI")
        self.setGeometry(100, 100, 800, 600)

        # Create a grid layout
        grid_layout = QtWidgets.QGridLayout()
        try:
            # Add labels and line edits to the grid layout
            delta_label = QtWidgets.QLabel("Delta Version:")
            self.delta_edit = QtWidgets.QLineEdit()
            grid_layout.addWidget(delta_label, 0, 0)
            grid_layout.addWidget(self.delta_edit, 0, 1)

            masterfile_label = QtWidgets.QLabel("Masterfile Name:")
            self.masterfile_edit = QtWidgets.QLineEdit()
            grid_layout.addWidget(masterfile_label, 1, 0)
            grid_layout.addWidget(self.masterfile_edit, 1, 1)

            output_label = QtWidgets.QLabel("Output Directory:")
            self.output_edit = QtWidgets.QLineEdit()
            grid_layout.addWidget(output_label, 2, 0)
            grid_layout.addWidget(self.output_edit, 2, 1)
        except:
            print("layout could not be created")
        # Add a button for executing the code
        try:
            execute_button = QtWidgets.QPushButton("Execute")
            grid_layout.addWidget(execute_button, 3, 0, 1, 2)


        # Connect the clicked signal of the execute button to a function from another module
            execute_button.clicked.connect(self.execute_button_clicked)
        except:
            print("execute button could not be created")
        # Set the grid layout as the central widget
        try:
            central_widget = QtWidgets.QWidget()
            central_widget.setLayout(grid_layout)
            self.setCentralWidget(central_widget)
            self.show()
        except:
            print("could not show GUI")

    def execute_button_clicked(self):

        try:
            PATH_TO_SHAREPOINT_ROOT = os.path.join(os.path.expanduser('~'), 'Nordex SE')
            PATH_TO_LOADS_EXCHANGE_SHAREPOINT = os.path.join(PATH_TO_SHAREPOINT_ROOT,
                                                             'Load Calculation - MLC_Loads_Exchange')
            PATH_TO_REFERENCE_LOADS_DIR = os.path.join(PATH_TO_LOADS_EXCHANGE_SHAREPOINT, 'D4k_Platform',
                                                       'FLAp_Reference_Loads')


            self.Delta_version=self.delta_edit.text()
            self.Masterfile = os.path.join(PATH_TO_REFERENCE_LOADS_DIR, self.Delta_version + '\\' + self.masterfile_edit.text())

            self.Output_directory = self.output_edit.text()
        except:
            ("some issues with reading the GUI")
        # Call the Filter_data() function from the read_alaska_inputs module
        try:
            my_object = Filter_data(self.Masterfile, self.Output_directory,self.Delta_version)
            my_object.read_masterfile()
            my_object.read_different_components()
        except:
            ("could not create the object for reading excels")

    # def return_delta(self):
    #     return self.Delta_version

class Filter_data:

    def __init__(self,Masterfile,Output_directory,delta_version):
        self.Masterfile=Masterfile
        self.Output_directory=Output_directory
        self.delta_version=delta_version
        self.PATH_TO_SHAREPOINT_ROOT = os.path.join(os.path.expanduser('~'), 'Nordex SE')
        self.PATH_TO_LOADS_EXCHANGE_SHAREPOINT = os.path.join(self.PATH_TO_SHAREPOINT_ROOT,
                                                         'Load Calculation - MLC_Loads_Exchange')
        self.PATH_TO_REFERENCE_LOADS_DIR = os.path.join(self.PATH_TO_LOADS_EXCHANGE_SHAREPOINT, 'D4k_Platform',
                                                   'FLAp_Reference_Loads')
        # self.delta_version = MainWindow.return_delta()

    def read_masterfile(self):
        """reads masterfile and finds the reference excel"""
        try:
            print(self.Masterfile)
            with open(self.Masterfile, 'r') as masterfile:
                masterfilecontent = masterfile.read()
                text = masterfilecontent.split('\n')
                info_of_masterfile = {}
                for line in text[0:]:
                    parts = line.split('\t')
                    key = parts[0]
                    if len(parts) == 2:
                        value = parts[1]
                    else:
                        value = ""
                    info_of_masterfile[key] = value
                # print(masterfilecontent)
            print(type(self.delta_version))
            print(info_of_masterfile)
        except:
            print("could not read the master file")
        try:
            self.Blade_loads = self.PATH_TO_REFERENCE_LOADS_DIR + "\\" + self.delta_version + "\\" + info_of_masterfile['Blade_loads']
            self.Gearbox_loads = self.PATH_TO_REFERENCE_LOADS_DIR + "\\" + self.delta_version + "\\" + info_of_masterfile[
                'Gearbox_loads']
            self.Machinery_loads = self.PATH_TO_REFERENCE_LOADS_DIR + "\\" + self.delta_version + "\\" + info_of_masterfile[
                'Machinery_loads']
            self.Tower_loads = self.PATH_TO_REFERENCE_LOADS_DIR + "\\" + self.delta_version + "\\" + info_of_masterfile['Tower_loads']
            self.PitchYaw_loads = self.PATH_TO_REFERENCE_LOADS_DIR + "\\" + self.delta_version + "\\" + info_of_masterfile['PitchYaw_loads']
            self.component_list=[self.Blade_loads,self.Gearbox_loads,self.Machinery_loads,self.Tower_loads,self.PitchYaw_loads]
            print(self.component_list)
        except:
            print('something wrong with paths')
        return(self.component_list)

    def read_excels(self,Component):
        """finds the  sensors which are available in Flap and Alaska simulations"""

        try:
            component = pd.read_excel(Component,sheet_name='Loads')
            list_gb_headers = list(component.iloc[0])
        except:
            print("something wrong with the path,the file might be open")
        try:

            # print(list_gb_headers)
            index_sensors_gb = list_gb_headers.index("sensor")

            index_wohler_gb = list_gb_headers.index("woehler_slopes")
            index_Flap_relevant = list_gb_headers.index("FLAp relevant")
            column_indices = [index_sensors_gb, index_wohler_gb, index_Flap_relevant]
        except:
            print("taking all sensors since FLAp relevance is not given")
            index_sensors_gb = list_gb_headers.index("sensor")

            index_wohler_gb = list_gb_headers.index("woehler_slopes")
            column_indices = [index_sensors_gb, index_wohler_gb]
        try:
            new_df = component.iloc[:,column_indices]
            print(new_df)# here I create a new data frame which will have only the three columns sensors, wohler , flap relevant

            with open(self.Output_directory, 'a') as f:
                # Write the header row to the CSV file
                # f.write(','.join(new_df.columns) + '\n')

                # Iterate over each row of the new dataframe
                for index, row in new_df.iterrows():
                    # Check if the value in the third column is "no" or "optional"
                    try:
                        if row[2] in ['yes',"",'optional',NaN]:
                            # Write the row to the CSV file
                            f.write(','.join([str(x) for x in row]) + '\n')
                            print([str(x) for x in row])
                    except:
                        f.write(','.join([str(x) for x in row]) + '\n')
            print(Component+" read successfully")
        except:
            print("something Failed ,after reading the excel",Component)

    def read_Blade_sensors(self,Blade_loads):
        """performs blade sensor extraction and sensor aliases replacement"""
        with open(Blade_loads, 'r') as Blade:
            try:
                Loads = pd.read_excel(Blade_loads, sheet_name='Loads')                                                  #opens loads sheet
                aliases = pd.read_excel(Blade_loads, sheet_name='SensorAliases', header=0)                              #opens aliases sheet
                list_bl_headers = list(Loads.iloc[0])
                print(list_bl_headers)
            except:
                print("loads or sensor Aliases sheet does not exist")

            try:
                index_sensors_bl = list_bl_headers.index("sensor")
                index_wohler_bl = list_bl_headers.index("woehler_slopes")
            except:
                print("sensor or woehler_slopes column does not exist")
            try:
                index_Flap_relevant = list_bl_headers.index("FLAp relevant")
                column_indices = [index_sensors_bl, index_wohler_bl, index_Flap_relevant]
                self.loads_sheet_df = Loads.iloc[:, column_indices]
            except:
                print("Flap relevant column does not exist so taking all sensors ,possibly an older turbine")
                column_indices = [index_sensors_bl, index_wohler_bl]
                self.loads_sheet_df = Loads.iloc[:, column_indices]
                print(loads_sheet_df)
            try:
                blade_aliase_dict = aliases.set_index('FLAp names')['LDMS keys aligned'].to_dict()
                print(blade_aliase_dict)
            except:
                print("blade_aliases dict could not be created")
            try:
                for index_sensors_bl in self.loads_sheet_df.columns:
                    for i, sensor in enumerate(self.loads_sheet_df[index_sensors_bl]):
                        if sensor in blade_aliase_dict:
                            self.loads_sheet_df.at[i, index_sensors_bl] = blade_aliase_dict[sensor]
                print(self.loads_sheet_df)
            except:
                print("sensor alias replacemet could not be performed")
        return (self.loads_sheet_df)

    def read_different_components(self):
        for load_file in self.component_list:
            if load_file==self.Blade_loads:
                blade_sensors_df=self.read_Blade_sensors(load_file)
                with open(self.Output_directory,'a') as f:
                    for index, row in blade_sensors_df.iterrows():
                        f.write(','.join([str(x) for x in row]) +'\n')
            else :
                self.read_excels(load_file)
        return()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    app.exec_()

