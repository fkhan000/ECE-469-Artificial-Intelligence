#Fakharyar Khan
#November 26th, 2023
#Professor Sable
#Artificial Intelligence
                            ######PROJECT #2: NEURAL NETWORK######
import math

#This module implements and trains an MLP with a single hidden layer

#that uses a sigmoid activation function
def sig(x):
    return 1/(1+math.exp(-1*x))

def sig_prime(x):
    return sig(x)*(1-sig(x))


#The node class serves as the base building block of the neural network
#It holds a vector of weights and a bias term. 
class Node:
    def __init__(self, weights, bias):
        self.weights = weights
        self.bias = bias
    
    #The node takes in N inputs and performs a dot product 
    #of the inputs against its weights and then adds its bias term.
    #It then sends the the sum through an activation function
    def __call__(self, x):
        out = -1*self.bias
        for index in range(len(x)):
            out += x[index]*self.weights[index]
        
        #in order to perform back propagation we need to keep track
        #of the output of the node before as well as after the activation
        #function
        self.pre_act = out
        self.output = sig(out)
        return self.output


#This class implements our MLP
class MLP:
    #constructor takes in a list of 2D lists of floats called layers. Each
    # entry in layers represents a single layer with each row representing the weights and
    #bias term of a single node in that layer.
    def __init__(self, layers):

        self.layers = []
        
        for layer in layers:
            self.layers.append([Node(layer[index][1:], layer[index][0]) for index in range(len(layer))])
    
    #since our neural network is fully connected, evaluation is relatively straightforward
    #as each node in a single layer gets the same input
    def __call__(self, x):

        for layer in self.layers:
            #to compute the output from a layer, we pass in the input from the previous layer
            #into every node in the next layer and then stack the outputs into a vector which 
            #will be used as the input into the next layer
            x = [node(x) for node in layer]
        return x
    
    #This function creates the string representation of our neural network
    #that will be used to export its weights into a file
    def __str__(self):
        export = str(len(self.layers[0][0].weights)) + " " + str(len(self.layers[0])) + " " + str(len(self.layers[1])) +"\n"
        
        for layer in self.layers:
           for node in layer:
               export += "%.3f " % round(node.bias, 3)
               for weight in node.weights[:-1]:
                   export += "%.3f " % round(weight, 3)
               export += "%.3f\n" % round(node.weights[-1], 3)
               
        return export[:-1]
               


#In this function we initialize our network using weights received in a given file
def load_weights(file):
    with open(file, "r") as f:
        lines = f.readlines()
        model_size = [int(x) for x in lines[0].split(" ")]
        in_matrix = [[float(x) for x in row.split(" ")] for row in lines[1:model_size[1] + 1]]

        out_matrix = [[float(x) for x in row.split(" ")] for row in lines[model_size[1] + 1:]]
    
    return MLP([in_matrix, out_matrix])

#This function loads in the train or test set from a file and splits into 
#the feature set and the labels
def load_dataset(file):

    with open(file, "r") as f:

        lines = f.readlines()
        data_size = [int(x) for x in lines[0].split(" ")]
        x = [[float(feat) for feat in sample.split(" ")[:data_size[1]]] for sample in lines[1:]]
        y = [[float(label) for label in sample.split(" ")[data_size[1]:]] for sample in lines[1:]]
    
    return x, y


#This function trains our model using back propagation for a given number
#of epochs and step size
def train(model, x, y, epochs, alpha):
    #for each epoch
    for epoch in range(epochs):
        
        #we iterate through the train set
        for index in range(len(x)):
            #evaluate the model on the given training point
            y_pred = model(x[index])
            
            #our error looks like this: 0.5*(y_pred - y)**2 where y = g( sum(out_weights*g(sum(hidden_weights*input_features))))
            #where g is our sigmoid activation function

            out_err = [sig_prime(model.layers[1][idx].pre_act)*(y[index][idx] -y_pred[idx]) for idx in range(len(y_pred))]

            #we first compute the derivative of the error wrt the weights in the hidden layer
            hidden_err = []
            #for each node k in the hidden layer
            for k in range(len(model.layers[0])):
                
                sum = 0
                #there are L output nodes that take the output from the kth node and use it to calculate the output
                for l in range(len(model.layers[1])):
                    #In particular, the kth weight of each of the output nodes is multiplied by the output from the kth hidden node
                    #When we take the derivative of the error wrt to the kth hidden node, we have (y-y_pred)*g'(sum(...))*derivative(sum(output_weights*...)...
                    #but because we're taking the derivative wrt the kth hidden node, all the terms in sum(output_weights*...) that aren't multipled by the 
                    #output from the kth hidden node are zeroed out which leaves us with just the kth weight of each of the output nodes.
                    sum += model.layers[1][l].weights[k]*out_err[l]
                
                hidden_err.append(sig_prime(model.layers[0][k].pre_act)*sum)
            
            
            #For each node in the hidden layer
            for k in range(len(model.layers[0])):
                
                #we update all of the weights in that node
                for l in range(len(x[index])):
                    #when taking the derivative of the output wrt the lth weight of the kth node, everything except for the term
                    #containing the lth input feature is zeroed out. We move a small step in the direction of the calculated derivative 
                    #and repeat for all of the weights in the kth node
                    model.layers[0][k].weights[l] += alpha*x[index][l]*hidden_err[k]
                
                model.layers[0][k].bias += -1*alpha*hidden_err[k]
            
            #We then update the output nodes

            #For each output node
            for k in range(len(model.layers[1])):
                #for every weight in that node
                for l in range(len(model.layers[0])):
                    #we update the output weights
                    model.layers[1][k].weights[l] += alpha*model.layers[0][l].output*out_err[k]
                
                #as well as the bias term
                model.layers[1][k].bias += -1*alpha*out_err[k]

#This function calculates and exports the metrics for the model on the test into a given file
def export_metrics(predictions, expected, file):

    #we initialize our table of metrics which will store the TP, FP, FN, and TN count for each class
    #for each class in our dataset
    metrics = [[0 for j in range(4)] for i in range(len(predictions[0]))]

    #This stores the dataset wide count for TP, FP,.. and is used to calculate the microaveraged metrics
    tot_metrics = [0, 0, 0, 0]

    #for each prediction made
    for i in range(len(predictions)):
        #and for each class
        for j in range(len(predictions[0])):
            
            #we check if the prediction is classified as a TP, FP, FN, or TN
            if expected[i][j] == 1 and predictions[i][j] >= 0.5:
                metrics[j][0] += 1
                tot_metrics[0] += 1
            elif expected[i][j] == 0 and predictions[i][j] >= 0.5:
                metrics[j][1] += 1
                tot_metrics[1] += 1
            elif expected[i][j] == 1 and predictions[i][j] < 0.5:
                metrics[j][2] += 1
                tot_metrics[2] += 1
            else:
                metrics[j][3] += 1
                tot_metrics[3] += 1
    
    macro_metrics = [0, 0, 0]

    #we then export our metrics into the given file
    with open(file, "w") as f:
        #for each class
        for i in range(len(predictions[0])):
            #we print out the metrics found for that class into the file
            for metric in metrics[i]:
                f.write(str(metric) + " ")
            
            #use the TP, FP,... counts to calculate accuracy, precision, recall, and F1 score
            acc = float((metrics[i][0] + metrics[i][3])/(sum(metrics[i])))
            precision = float(metrics[i][0]/(metrics[i][0] + metrics[i][1]))
            recall = float(metrics[i][0]/(metrics[i][0] + metrics[i][2]))
            f1 = float(2*precision*recall/(precision + recall))
            
            class_metrics = [precision, recall]
            
            #we calculating our pending macro metrics
            macro_metrics = [macro_metrics[index] + class_metrics[index] for index in range(2)]
            

            for metric in [acc, precision, recall]:
                f.write( ("%.3f " % metric))
            
            f.write("%.3f\n" % f1)
        
        #calculate the total accuracy across the entire dataset
        tot_acc = (tot_metrics[0] + tot_metrics[3])/sum(tot_metrics)

        #then calculate the microaveraged metrics from the total counts for TP, FP,...
        micro_precision = tot_metrics[0]/(tot_metrics[0] + tot_metrics[1])
        micro_recall = tot_metrics[0]/(tot_metrics[0] + tot_metrics[2])
        micro_f1 = 2*micro_precision*micro_recall/(micro_precision + micro_recall)

        
        #write the micro and macro averaged metrics into the file
        for metric in [tot_acc, micro_precision, micro_recall]:
            f.write( ("%.3f " % metric))
        
        f.write("%.3f\n" % micro_f1)
        macro_metrics=  [tot_acc] + [metric/len(predictions[0]) for metric in macro_metrics]

        macro_f1 = 2*(macro_metrics[1]*macro_metrics[2])/(macro_metrics[1] + macro_metrics[2])

        for metric in macro_metrics:
            f.write( ("%.3f " % metric))

        f.write("%.3f" % macro_f1)

#this is the main driver function and serves as the interface for the user, collecting
#the inputs needed to train and evaluate our model
if __name__ == "__main__":

    
    mode = input("Press 0 to train a model or 1 to evaluate a model: ")

    model_file = input("Please enter in the name of the file where the model's weights are given: ")
    model = load_weights(model_file)

    if mode == "0":
        output_file = input("Please enter in the name of the file where you would like the model's weights to be exported to: ")
        data_file = input("Please enter in the name of the file where the training set is located: ")
        num_epochs = int(input("Please enter the number of epochs you would like to train the model for: "))
        alpha = float(input("Please enter the step size used to train the model: "))


        x, y = load_dataset(data_file)

        train(model, x, y, num_epochs, alpha)

        #print out the weights of the model to a file
        with open(output_file, "w") as f:
            print(model, file = f, end = "")
    
    if mode == "1":
        data_file = input("Please enter in the name of the file where the test set is located: ")
        output_file = input("Please enter in the name of the file where you would you like the model's performance metrics to be placed in: ")

        x, y = load_dataset(data_file)
        y_pred = [model(xi) for xi in x]
        export_metrics(y_pred, y, output_file)