#!/usr/bin/python3

import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import matplotlib.pyplot as plt

np.random.seed(101)
tf.set_random_seed(101)

# tf.compat.v1.disable_eager_execution()
x = np.load("/ass3_volume/x.npy")
y = np.load("/ass3_volume/y.npy")
 
n = len(x) # Number of data points

# Plot of Training Data
# plt.scatter(x, y)
# plt.xlabel('x')
# plt.ylabel('y')
# plt.title("Training Data")
# plt.show()

X = tf.placeholder("float")
Y = tf.placeholder("float")

W = tf.Variable(np.random.randn(), name = "W")
b = tf.Variable(np.random.randn(), name = "b")

learning_rate = 0.01
training_epochs = 1000

# Hypothesis
y_pred = tf.add(tf.multiply(X, W), b)
 
# Mean Squared Error Cost Function
cost = tf.reduce_sum(tf.pow(y_pred-Y, 2)) / (2 * n)
 
# Gradient Descent Optimizer
optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)
 
# Global Variables Initializer
init = tf.global_variables_initializer()

# Starting the Tensorflow Session
with tf.Session() as sess:
	
	# Initializing the Variables
	sess.run(init)
	
	# Iterating through all the epochs
	for epoch in range(training_epochs):
		
		# Feeding each data point into the optimizer using Feed Dictionary
		for (_x, _y) in zip(x, y):
			sess.run(optimizer, feed_dict = {X : _x, Y : _y})
		
		# Displaying the result after every 50 epochs
		if (epoch + 1) % 50 == 0:
			# Calculating the cost a every epoch
			c = sess.run(cost, feed_dict = {X : x, Y : y})
			print("Epoch", (epoch + 1), ": cost =", c, "W =", sess.run(W), "b =", sess.run(b))
	
	# Storing necessary values to be used outside the Session
	training_cost = sess.run(cost, feed_dict ={X: x, Y: y})
	weight = sess.run(W)
	bias = sess.run(b)

# Calculating the predictions
predictions = weight * x + bias
print("Training cost =", training_cost, "Weight =", weight, "bias =", bias, '\n')

# Plotting the Results
# plt.plot(x, y, 'ro', label ='Original data')
# plt.plot(x, predictions, label ='Fitted line')
# plt.title('Linear Regression Result')
# plt.legend()
# plt.show()
# plt.savefig('fig.png')