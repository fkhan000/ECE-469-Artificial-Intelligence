#Fakharyar Khan
#November 26th, 2023
#Professor Sable
#Artificial Intelligence
                            ######PROJECT #2: NEURAL NETWORK######
####PRIME INITIALIZER####
import math
import random

#For the additional dataset, I wanted to see if given the binary representation
#of a number, if my neural network could be trained to predict whether or not that
#number is prime.

#INT_SIZE sets the number of input nodes in the neural network and also determines
#the size of the dataset
SIZE = int(input("Please enter the largest number in the dataset: "))
INT_SIZE = math.ceil(math.log(SIZE)/math.log(2))
#SIZE = 2**INT_SIZE -1
#the number of hidden nodes in the hidden layer of the network
NUM_HIDDEN_NODES = int(input("Please enter the number of hidden nodes to be used in the neural network: "))

#checks whether or not a number is prime
def is_prime(n):
    if n < 2:
        return 0
    #check integers from 2 to floor(sqrt(n)) and see if they divide n
    for i in range(2, (math.floor(n**0.5))):
        if n % i == 0:
            return 0
    return 1

#given an integer returns the binary representation as a string
def to_binary(n):
    form = "#0" + str(INT_SIZE + 2) + "b"
    return  " ".join(list(format(n, form))[2:])

#In this function we generate our train and test set
def generate_dataset():
    #because there are much more composite numbers than primes
    #we can't just use the numbers from 1 to SIZE because we would have 
    #a really big class inbalance and our classifier could get a high
    #accuracy by just always guessing the larger class
    dataset = list(range(1, SIZE))

    #to avoid this we should try to make sure that the two classes
    #are of the same size
    primes = []
    composites =[]

    random.shuffle(dataset)
    
    #we collect all of the primes and composite numbers from 1 to SIZE
    for data in dataset:
        if is_prime(data) == 1:
            primes.append(data)
        else:
            composites.append(data)
    #we then only take as many composite numbers as there are primes
    #from 1 to SIZE as well as the primes and make that our dataset
    dataset = primes + composites[:len(primes)]
    random.shuffle(dataset)

    #we use 80% of the dataset for training and 20% for testing
    x_train = dataset[:int(.8*len(dataset))]
    y_train = [is_prime(n) for n in x_train]
    x_test = dataset[int(.8*len(dataset)):]
    y_test = [is_prime(n) for n in x_test]

    #we then export our train and test set to files called prime_train.txt
    #and prime_test.txt respectively
    with open("prime_train.txt", "w") as f:
        f.write(str(len(x_train)) + " " + str(INT_SIZE) + " 1\n")
        for index in range(len(x_train)):
            f.write(to_binary(x_train[index]) + " " + str(y_train[index]))
            if index != (len(x_train) - 1):
                f.write("\n")
    
    with open("prime_test.txt", "w") as f:
        f.write(str(len(x_test)) + " " + str(INT_SIZE) + " 1\n")
        for index in range(len(x_test)):
            f.write(to_binary(x_test[index]) + " " + str(y_test[index]))
            if index != (len(x_test) - 1):
                f.write("\n")


#this creates the initial weights for our network and exports them
#to a file called prime_init_weights.txt
def initialize_network():

    with open("prime_init_weights.txt", "w") as f:

        #we write the size parameters of our network to the file
        f.write(str(INT_SIZE) + " " + str(NUM_HIDDEN_NODES) + " 1\n")

        #and then for initialization i decided to use xavier initialization.
        #This initialization ensures that the variance of the outputs from each of the nodes
        #don't become so large that the activation function causes the output to become saturated
        for i in range(NUM_HIDDEN_NODES):
            for j in range(INT_SIZE):
                f.write("%.3f " % random.normalvariate(sigma = (6/(INT_SIZE + NUM_HIDDEN_NODES))**0.5))
            f.write("%.3f\n" % random.normalvariate(sigma = (6/(INT_SIZE + NUM_HIDDEN_NODES))**0.5))

        for i in range(NUM_HIDDEN_NODES):
            f.write("%.3f " % random.normalvariate(sigma = (6/(NUM_HIDDEN_NODES + 1))**0.5))
        f.write("%.3f" % random.normalvariate(sigma =  (6/(NUM_HIDDEN_NODES + 1))**0.5))


generate_dataset()
initialize_network()
