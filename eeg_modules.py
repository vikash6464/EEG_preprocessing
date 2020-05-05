import pandas as pd


class DataOperations:
    def windowing(self, value, time, data):
        total_number_of_seconds_in_experiment = time[0] * 24 * 60 * 60 + time[1] * 60 * 60+time[2] * 60 + time[3]
        question = int(total_number_of_seconds_in_experiment / value)
        remainder = total_number_of_seconds_in_experiment % value
        print(question, remainder)
        print(total_number_of_seconds_in_experiment)
        data = data.filter(regex="RAW|Time")
        lis = []
        for i in data["TimeStamp"]:
            lis.append(i.split()[1])
        data.insert(1, "Time", lis, True)
        data = data.drop(columns=['TimeStamp'])
        iterated_data = data.filter(regex="RAW")
        print(data)
        rand = 0
        val = int(data['Time'][rand].split(':')[1])
        vas = val
        for i in range(0, question):
            while val < vas + value:
                val = val + 1

        # print(len(lis))
        # print(lis)

        # window_data = data.filter(regex="RAW")
        # window_remainder = len(window_data.index) % value
        # window_data_column_name = window_data.columns.values.tolist()
        # window_list = [0 for x in range(0, len(window_data_column_name))]
        # windowed_list = []
        # window_count = 0
        # for i in window_data.itertuples(index=False, name=None):
        #     for j in range(0, len(i)):
        #         window_list[j] = window_list[j] + i[j]
        #     window_count += 1
        #     if window_count == value:
        #         window_count = 0
        #         for k in range(0, len(i)):
        #             window_list[k] = window_list[k] / value
        #         windowed_list.append(window_list)
        #         window_list = [0 for x in range(0, len(i))]
        # if (window_remainder != 0):
        #     for i in range(0, len(window_list)):
        #         window_list[i] = window_list[i] / window_remainder
        #     windowed_list.append(window_list)
        # windowed_data = pd.DataFrame(data=windowed_list, columns=window_data_column_name)
        # return windowed_data

    def baseline(self, file_path, data):
        baseline_data = pd.read_csv(file_path)
        baseline_data.sort_values(by="TimeStamp", ascending=True, inplace=True)
        baseline_data = data.filter(regex="RAW")
        baseline_data_column_names = baseline_data.columns.values.tolist()
        baseline_data_mean_values = []
        baselined_data = data.filter(regex="RAW")
        baselined_list = [0 for x in range(0, len(baseline_data_column_names))]
        baselined_final_list = []
        for i in baseline_data_column_names:
            baseline_data_mean_values.append(round(baseline_data[i].mean(), 4))
        for i in baselined_data.itertuples(index=False, name=None):
            for j in range(0, len(i)):
                baselined_list[j] = i[j] - baseline_data_mean_values[j]
            baselined_final_list.append(baselined_list)
            baselined_list = [0 for x in range(0, len(baseline_data_column_names))]
        baselined_data = pd.DataFrame(data=baselined_final_list, columns=baseline_data_column_names)
        return baselined_data

    def fill_empty_cells(self, data):
        data = data.filter(regex="RAW")
        data_columns = data.columns.values.tolist()
        for i in data_columns:
            data[i].fillna(data[i].mean(), inplace=True)
        return data


if __name__ == "__main__":
    do = DataOperations()
    do.windowing(5, (0, 0, 6, 23), pd.read_csv("/home/vikas/Desktop/eeg/eeg.csv"))
