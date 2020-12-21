"""Module for managing the datasets"""
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

def create_datasets():
    """
    Function to create the datasets for supervised training

    @return: Tuple containing training and validation datasets and scaler
    """
    dataset = read_csv('data.csv', header=None).drop_duplicates()
    values = dataset.values
    inputs, output = values[:, :-1], values[:, -1]
    scaler = MinMaxScaler()
    inputs = scaler.fit_transform(inputs)
    train_x, val_x, train_y, val_y = train_test_split(inputs, output, test_size=0.3)
    return (train_x, train_y), (val_x, val_y), scaler
