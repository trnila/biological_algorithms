import numpy as np

def shekel(X):
    return 1.0 / (np.add.reduce((X -3) * X))


def rastrigin(X, A=10):
    n = len(X)
    return A*n + np.add.reduce(X*X - A*np.cos(2 * np.pi * X))

def ackley(X):
    return -20 * np.exp(-0.2 * np.sqrt(0.5 * (np.add.reduce(X ** 2)))) \
           - np.exp(0.5 * (np.add.reduce(np.cos(2 * np.pi * X)))) \
           + np.e + 20

def sphere(X):
    return np.add.reduce(X*X)


#def rosenbrock(X):
    #X1 = np.insert(X, 0, np.array([]))
#    X1 = np.delete(X, 0)
#    X = np.delete(X, -1)

#    return np.add.reduce(100*(X1 - X*X) + (1 - X)**2)

def bukin_n6(X):
    if len(X) != 2:
        raise NotImplementedError

    x = X[0]
    y = X[1]

    return 100*np.sqrt(np.abs(y - 0.01*x**2))+0.01*np.abs(x + 10)



def beale(X):
    if len(X) != 2:
        raise NotImplementedError

    x = X[0]
    y = X[1]
    return (1.5 - x + x*y)**2 \
        + (2.25 - x + x*y**2)**2 \
        + (2.625 - x + x*y**3)**2

def goldstein_price(X):
    if len(X) != 2:
        raise NotImplementedError

    x = X[0]
    y = X[1]

    return (1 + \
           (x + y + 1)**2 * (19 - 14*x + 3*x**2 - 14*y + 6*x*y + 3*y*y)) * \
           (30+(2*x-3*y)**2*(18 - 32*x+12*x**2 + 48*y - 36*x*y + 27*y**2))


def holder_table(X):
    if len(X) != 2:
        raise NotImplementedError

    x = X[0]
    y = X[1]

    return -np.abs(np.sin(x) * np.cos(y) * np.exp(np.abs(1 - np.sqrt(x**2 + y**2)/np.pi))) + 4


def styblinski_tang(X):
    return np.add.reduce(X**4 - 16 * X**2 + 5*X)/2

def griewank(X):
    prod = 1

    for i in range(len(X)):
        prod *= np.cos(X[i] / np.sqrt(i+1))

    return 1 + np.add.reduce(X**2/4000) - prod


def schwefel_2_20(X):
    return np.add.reduce(np.abs(X))

def schwefel_2_23(X):
    return np.add.reduce(X**10)

def plane(X):
    return np.add.reduce(X*0)


def trychtyr(X):
    return -20 * np.exp(-0.2 * np.sqrt(0.5 * (np.add.reduce(X ** 2))))