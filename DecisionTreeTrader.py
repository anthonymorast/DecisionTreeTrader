from sklearn import tree
import matplotlib.pyplot as plt
import graphviz

class DecisionTree:
    def __init__(self, classification=False, max_depth=None):
        if classification:
            self.classifier = tree.DecisionTreeClassifier(max_depth=max_depth)
        else:
            self.classifier = tree.DecisionTreeRegressor(max_depth=max_depth)

    def train(self, trainx, trainy):
        self.classifier.fit(trainx, trainy)

    def test(self, testx):
        return self.classifier.predict(testx)

    def plot(self, figname, column_names, filled=False, rounded=False):
        tree.plot_tree(self.classifier, filled=filled, rounded=rounded, feature_names=column_names, fontsize=1)
        plt.title("Trading Decisions")
        plt.savefig(figname)
        # dot_data = tree.export_graphviz(self.classifier, out_file="Tree.png") 
        # graph = graphviz.Source(dot_data) 
        # graph.render("itnc") 

    def to_text_rules(self, filename, feature_names):
        text = tree.export_text(self.classifier, feature_names=feature_names)
        with open(filename, 'w') as file:
            file.write(text)
         
