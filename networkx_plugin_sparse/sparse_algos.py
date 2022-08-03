import numpy as np
import scipy as sp
import scipy.sparse  # call as sp.sparse
import networkx as nx
import inspect


def pagerank(
    G,
    alpha=0.85,
    personalization=None,
    max_iter=100,
    tol=1.0e-6,
    nstart=None,
    weight="weight",
    dangling=None,
):
    nodelist = G.nodelist
    N = len(nodelist)
    if N == 0:
        return {}

    A = G.sparse_array

    S = A.sum(axis=1)
    S[S != 0] = 1.0 / S[S != 0]

    Q = sp.sparse.csr_array(sp.sparse.spdiags(S.T, 0, *A.shape))
    A = Q @ A

    # initial vector
    if nstart is None:
        x = np.repeat(1.0 / N, N)
    else:
        x = np.array([nstart.get(n, 0) for n in nodelist], dtype=float)
        x /= x.sum()

    # Personalization vector
    if personalization is None:
        p = np.repeat(1.0 / N, N)
    else:
        p = np.array([personalization.get(n, 0) for n in nodelist], dtype=float)
        if p.sum() == 0:
            raise ZeroDivisionError
        p /= p.sum()
    # Dangling nodes
    if dangling is None:
        dangling_weights = p
    else:
        # Convert the dangling dictionary into an array in nodelist order
        dangling_weights = np.array([dangling.get(n, 0) for n in nodelist], dtype=float)
        dangling_weights /= dangling_weights.sum()
    is_dangling = np.where(S == 0)[0]

    # power iteration: make up to max_iter iterations
    for _ in range(max_iter):
        xlast = x
        x = alpha * (x @ A + sum(x[is_dangling]) * dangling_weights) + (1 - alpha) * p
        # check convergence, l1 norm
        err = np.absolute(x - xlast).sum()
        if err < N * tol:
            return dict(zip(nodelist, map(float, x)))
    raise nx.PowerIterationFailedConvergence(max_iter)


def hits(G, max_iter=100, tol=1.0e-6, nstart=None, normalized=True):
    if len(G.nodelist) == 0:
        return {}, {}
    A = G.sparse_array
    (n, _) = A.shape  # should be square
    ATA = A.T @ A  # authority matrix
    # choose fixed starting vector if not given
    if nstart is None:
        x = np.ones((n, 1)) / n
    else:
        x = np.array([nstart.get(n, 0) for n in list(G)], dtype=float)
        x /= x.sum()

    # power iteration on authority matrix
    i = 0
    while True:
        xlast = x
        x = ATA @ x
        x /= x.max()
        # check convergence, l1 norm
        err = np.absolute(x - xlast).sum()
        if err < tol:
            break
        if i > max_iter:
            raise nx.PowerIterationFailedConvergence(max_iter)
        i += 1

    a = x.flatten()
    h = A @ a
    if normalized:
        h /= h.sum()
        a /= a.sum()
    hubs = dict(zip(G.nodelist, map(float, h)))
    authorities = dict(zip(G.nodelist, map(float, a)))
    return hubs, authorities