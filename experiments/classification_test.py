from data_source.data_touse import *
from experiments.useful_tools import KFold_df, normalize
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_recall_fscore_support, classification_report

data = data_github_0()
# data = data.drop(columns=['stars'])


def cart_classifier(dataset):

    dataset = normalize(dataset)
    detail_report = []
    for train, test in KFold_df(dataset, 3):
        train_input = train.iloc[:, :-1]
        train_actual_output = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_output = test.iloc[:, -1]

        model = DecisionTreeClassifier()
        # model = GaussianNB()
        # model = RandomForestClassifier()
        # model = SVC(gamma='scale')
        # model = KNeighborsClassifier()
        model.fit(train_input, train_actual_output)
        test_predict_output = model.predict(test_input)
        test_actual_output = test_actual_output.values
        # print(test_actual_output, "???")
        # print(test_predict_output, "!!!")
        detail_report = classification_report(test_actual_output, test_predict_output,
                                              target_names=['Unarchived', 'Archived'])

    return detail_report


if __name__ == '__main__':
    print(cart_classifier(data))
