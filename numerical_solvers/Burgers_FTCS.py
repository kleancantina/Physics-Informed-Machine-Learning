import numpy as np
import scipy.sparse as sparse
from numerical_solvers.NumericalSolver import BurgersNumericalSolver


class BurgersFTCS(BurgersNumericalSolver):
    def __init__(self, n_spatial, n_temporal, nu=1/(100*np.pi), **kwargs) -> None:
        """
        :param n_spatial: Number of spatial discretisation points
        :param n_temporal: Number of temporal discretisation points
        :param nu: The viscosity parameter of the Burgers' equation
        :param kwargs:
            - u0: allow to pass a vector containing the initial condition. Should have length=n_spatial
        """
        super().__init__(n_spatial, n_temporal, nu, **kwargs)

        # Design matrices
        self.c = (self.k * self.nu) / (self.h ** 2)
        self.A = sparse.diags([self.c, -2 * self.c, self.c], [0, 1, 2],
                              shape=(self.n_spatial - 2, self.n_spatial)).toarray()
        self.d = self.k / (2 * self.h)
        self.B = sparse.diags([-self.d, 0, self.d], [0, 1, 2], shape=(self.n_spatial - 2, self.n_spatial)).toarray()

        # Design matrix: conservation form
        # self.d = self.k / (4 * self.h)
        # self.A = sparse.diags([self.c, 1 - 2 * self.c, self.c], [-1, 0, 1], shape=(self.H + 1, self.H + 1)).toarray()
        # self.B = sparse.diags([-self.d, 0, self.d], [-1, 0, 1], shape=(self.H+1, self.H+1)).toarray()

    def time_integrate(self) -> None:
        """
        Forward Euler time integrator
        """
        for n in range(self.n_temporal - 1):
            u_n = self.u_numerical[:, n]
            u_n_inner = u_n[1:self.n_spatial-1]
            self.u_numerical[1:self.n_spatial-1, n + 1] = u_n_inner + self.A.dot(u_n) - u_n_inner * self.B.dot(u_n)

        # Conservation form:
        # for n in range(1, self.K + 1):
            # u_n = self.U[:, n - 1]
            # self.U[1:self.H, n] = self.A.dot(u_n)[1:self.H] - self.B.dot(u_n ** 2)[1:self.H]
            # self.U[0, n] = self.U[0, n - 1]
            # self.U[self.H, n] = self.U[self.H, n - 1]
