from modshogun import CSVFile, RealFeatures, MulticlassLabels, RandomForest, MajorityVote, CARTree, PT_MULTICLASS, MulticlassAccuracy
from numpy import array

def load_file(feat_file, label_file):
    feats = RealFeatures(CSVFile(feat_file))
    labels = MulticlassLabels(CSVFile(label_file))
    return (feats, labels)


def setup_random_forest(num_trees,rand_subset_size,combination_rule,feature_types):
    rf=RandomForest(rand_subset_size,num_trees)
    rf.set_combination_rule(combination_rule)
    rf.set_feature_types(feature_types)

    return rf

train_data_file = 'train.data'
train_label_file = 'train.label'
train_feats, train_labels = load_file(train_data_file, train_label_file)

comb_rule=MajorityVote()
feat_types=array([False]*52)
rand_forest=setup_random_forest(30, 7,comb_rule,feat_types)

rand_forest.set_labels(train_labels)
rand_forest.train(train_feats)

test_data_file ='test.data'
test_label_file = 'test.label'
test_feats,test_labels=load_file(test_data_file,test_label_file)

# apply forest
output_rand_forest_train=rand_forest.apply_multiclass(train_feats)
output_rand_forest_test=rand_forest.apply_multiclass(test_feats)

def train_cart(train_feats,train_labels,feature_types,problem_type):
    c=CARTree(feature_types,problem_type,2,True)
    c.set_labels(train_labels)
    c.train(train_feats)

    return c

# train CART
cart=train_cart(train_feats,train_labels,feat_types,PT_MULTICLASS)

# apply CART model
output_cart_train=cart.apply_multiclass(train_feats)
output_cart_test=cart.apply_multiclass(test_feats)

accuracy=MulticlassAccuracy()

rf_train_accuracy=accuracy.evaluate(output_rand_forest_train,train_labels)*100
rf_test_accuracy=accuracy.evaluate(output_rand_forest_test,test_labels)*100

cart_train_accuracy=accuracy.evaluate(output_cart_train,train_labels)*100
cart_test_accuracy=accuracy.evaluate(output_cart_test,test_labels)*100

print('Random Forest training accuracy : '+str(round(rf_train_accuracy,3))+'%')
print('CART training accuracy : '+str(round(cart_train_accuracy,3))+'%')
print
print('Random Forest test accuracy : '+str(round(rf_test_accuracy,3))+'%')
print('CART test accuracy : '+str(round(cart_test_accuracy,3))+'%')

def get_rf_accuracy(num_trees,rand_subset_size):
    rf=setup_random_forest(num_trees,rand_subset_size,comb_rule,feat_types)
    rf.set_labels(train_labels)
    rf.train(train_feats)
    out_test=rf.apply_multiclass(test_feats)
    acc=MulticlassAccuracy()
    return acc.evaluate(out_test,test_labels)


import matplotlib.pyplot as plt
num_trees4=[5,10,20,50,100]
subset_sizes=range(2,20)
# rf_accuracy_4=[round(get_rf_accuracy(i,7)*100,3) for i in num_trees4]
rf_accuracy_4=[round(get_rf_accuracy(20,i)*100,3) for i in subset_sizes]

print('Random Forest accuracies (as %) :' + str(rf_accuracy_4))


x4=[1]
y4=[60.00] # accuracy for single tree-CART
x4.extend(subset_sizes)
y4.extend(rf_accuracy_4)
plt.plot(x4,y4,'--bo')
plt.xlabel('subset')
plt.ylabel('Accuracy(%)')
plt.xlim([0,22])
plt.ylim([50,90])
plt.show()