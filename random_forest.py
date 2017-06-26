import matplotlib.pyplot as plt
from modshogun import *
from numpy import array


def load_file(feat_file, label_file):
    feats = RealFeatures(CSVFile(feat_file))
    labels = MulticlassLabels(CSVFile(label_file))
    return (feats, labels)


def setup_random_forest(num_trees, rand_subset_size, combination_rule, feature_types):
    rf = RandomForest(rand_subset_size, num_trees)
    rf.set_combination_rule(combination_rule)
    rf.set_feature_types(feature_types)

    return rf


train_data_file = 'train.data'
train_label_file = 'train.label'
train_feats, train_labels = load_file(train_data_file, train_label_file)

comb_rule = MajorityVote()
feat_types = array([False] * 52)
rand_forest = setup_random_forest(30, 7, comb_rule, feat_types)

rand_forest.set_labels(train_labels)
rand_forest.train(train_feats)

test_data_file = 'test.data'
test_label_file = 'test.label'
test_feats, test_labels = load_file(test_data_file, test_label_file)

output_rand_forest_train = rand_forest.apply_multiclass(train_feats)
output_rand_forest_test = rand_forest.apply_multiclass(test_feats)


def train_cart(train_feats, train_labels, feature_types, problem_type):
    c = CARTree(feature_types, problem_type, 2, True)
    c.set_labels(train_labels)
    c.train(train_feats)

    return c


cart = train_cart(train_feats, train_labels, feat_types, PT_MULTICLASS)

output_cart_train = cart.apply_multiclass(train_feats)
output_cart_test = cart.apply_multiclass(test_feats)

accuracy = MulticlassAccuracy()

rf_train_accuracy = accuracy.evaluate(output_rand_forest_train, train_labels) * 100
rf_test_accuracy = accuracy.evaluate(output_rand_forest_test, test_labels) * 100

cart_train_accuracy = accuracy.evaluate(output_cart_train, train_labels) * 100
cart_test_accuracy = accuracy.evaluate(output_cart_test, test_labels) * 100

print('Random Forest training accuracy : ' + str(round(rf_train_accuracy, 3)) + '%')
print('CART training accuracy : ' + str(round(cart_train_accuracy, 3)) + '%')
print
print('Random Forest test accuracy : ' + str(round(rf_test_accuracy, 3)) + '%')
print('CART test accuracy : ' + str(round(cart_test_accuracy, 3)) + '%')


def get_rf_accuracy(num_trees, rand_subset_size):
    rf = setup_random_forest(num_trees, rand_subset_size, comb_rule, feat_types)
    rf.set_labels(train_labels)
    rf.train(train_feats)
    out_test = rf.apply_multiclass(test_feats)
    acc = MulticlassAccuracy()
    return acc.evaluate(out_test, test_labels)


def plot_all():
    # num_trees4 = [5, 20, 50, 100, 200]
    subset_sizes = range(2, 30, 2)
    # rf_accuracy_4 = [round(get_rf_accuracy(i, 6) * 100, 3) for i in num_trees4]
    rf_accuracy_4=[round(get_rf_accuracy(500,i)*100,3) for i in subset_sizes]

    print('Random Forest accuracies (as %) :' + str(rf_accuracy_4))

    x4 = [1]
    y4 = [60.00]
    # x4.extend(num_trees4)
    x4.extend(subset_sizes)
    y4.extend(rf_accuracy_4)
    plt.plot(x4, y4, '--bo')
    plt.xlabel('rand_subset_size')
    plt.ylabel('Accuracy(%)')
    plt.xlim([0, 30])
    # plt.xlim([0, 30])
    plt.ylim([50, 75])
    plt.show()


def train_and_show():
    rf = setup_random_forest(10, 7, comb_rule, feat_types)
    rf.set_labels(train_labels)
    rf.train(train_feats)

    # set evaluation strategy
    eval = MulticlassAccuracy()
    oobe = rf.get_oob_error(eval)

    print('OOB accuracy : ' + str(round(oobe * 100, 3)) + '%')


def get_oob_errors_wine(num_trees, rand_subset_size):
    feat_types = array([False] * 52)
    rf = setup_random_forest(num_trees, rand_subset_size, MajorityVote(), feat_types)
    rf.set_labels(train_labels)
    rf.train(train_feats)
    eval = MulticlassAccuracy()
    return rf.get_oob_error(eval)


def show_diff_of_num_of_trees():
    # subset size 2

    num_trees2 = [10, 20, 50, 100]
    rf_accuracy_2 = [round(get_rf_accuracy(i, 2) * 100, 3) for i in num_trees2]

    print('Random Forest accuracies (as %) :' + str(rf_accuracy_2))

    # subset size 8

    num_trees8 = [5, 10, 50, 100]
    rf_accuracy_8 = [round(get_rf_accuracy(i, 8) * 100, 3) for i in num_trees8]

    print('Random Forest accuracies (as %) :' + str(rf_accuracy_8))
    num_trees4 = [5, 10, 20, 50, 100]
    rf_accuracy_4 = [round(get_rf_accuracy(i, 4) * 100, 3) for i in num_trees4]

    print('Random Forest accuracies (as %) :' + str(rf_accuracy_4))

    # plot results

    x4 = [1]
    y4 = [58]  # accuracy for single tree-CART
    x4.extend(num_trees4)
    y4.extend(rf_accuracy_4)

    x2 = [1]
    y2 = [58]
    x2.extend(num_trees2)
    y2.extend(rf_accuracy_2)

    x8 = [1]
    y8 = [58]
    x8.extend(num_trees8)
    y8.extend(rf_accuracy_8)

    plt.plot(x2, y2, '--bo', label='Subset Size = 2')
    plt.plot(x4, y4, '--r^', label='Subset Size = 4')
    plt.plot(x8, y8, '--gs', label='Subset Size = 8')
    plt.xlabel('Number of trees')
    plt.ylabel('Multiclass Accuracy (as %) ')
    plt.legend(bbox_to_anchor=(0.92, 0.4))
    plt.xlim([0, 110])
    plt.ylim([50, 100])
    plt.show()


# show_diff_of_num_of_trees()
# plot_all()


size=[1,2,4,6,8,10,13]
oobe=[round(get_oob_errors_wine(400,i)*100,3) for i in size]

print('Out-of-box Accuracies (as %) : '+str(oobe))

plt.plot(size,oobe,'--bo')
plt.xlim([0,14])
plt.xlabel('Random subset size')
plt.ylabel('Multiclass accuracy')
plt.show()