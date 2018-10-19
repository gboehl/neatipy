#!/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
from .stuff import *
import pydsge
from econsieve import UnscentedKalmanFilter as UKF
from econsieve import GreedyMerweScaledSigmaPoints
from scipy.stats import norm 

def create_filter(self, alpha = .25, scale_obs = 0.):

    dim_v       = len(self.vv)
    beta_ukf 	= 2.

    if not hasattr(self, 'Z'):
        warnings.warn('No time series of observables provided')
    else:
        sig_obs 	= np.std(self.Z, 0)*scale_obs

    spoints     = GreedyMerweScaledSigmaPoints(n=dim_v, alpha=alpha, beta=beta_ukf)
    ukf 		= UKF(dim_x=dim_v, dim_z=self.ny, hx=self.o_func, fx=self.t_func, points=spoints)
    ukf.R 		= np.diag(sig_obs)**2

    CO          = self.SIG @ self.QQ(self.par)

    ukf.Q 		= CO @ CO.T

    self.ukf    = ukf

def get_ll(self, use_rts=True, info=False):

    if info == 1:
        st  = time.time()

    X1, cov, ll     = self.ukf.batch_filter(self.Z)

    if use_rts:
        X1, cov, Ks, ll         = self.ukf.rts_smoother(X1, cov)

    self.ll     = ll
    # self.ll     = self.ukf.get_ll(self.Z, X1, cov)

    return self.ll

"""
from econsieve.stats import logpdf

def get_ll(self, use_rts=True, info=False):

    if info == 1:
        st  = time.time()

    X1, cov, _  = self.ukf.batch_filter(self.Z)

    if use_rts:
        X1, _, _    = self.ukf.rts_smoother(X1, cov)

    exo     = nl.pinv(self.SIG)
    stds    = np.diag(self.QQ(self.par))

    ll  = 0
    for i in range(X1.shape[0]-1):
        eps     = X1[i+1] - self.t_func(X1[i])[0]
        # ll      += np.sum(norm.logpdf(exo @ eps, cov=stds))
        ll      += logpdf(exo @ eps, cov=self.QQ(self.par))

    if info == 1:
        print('Filtering done in '+str(np.round(time.time()-st,3))+'seconds.')

    self.ll     = ll

    return ll
"""

def run_filter(self, use_rts=True, info=False):

    if info == 1:
        st  = time.time()

    X1, cov, ll     = self.ukf.batch_filter(self.Z)

    if use_rts:
        X1, cov, Ks, ll         = self.ukf.rts_smoother(X1, cov)

    EPS     = []
    for i in range(X1.shape[0]-1):
        eps     = X1[i+1] - self.t_func(X1[i])[0]
        EPS.append(eps)

    exo                 = nl.pinv(self.SIG)

    self.ll             = ll

    self.filtered_Z     = (self.hx[0] @ X1.T).T + self.hx[1]
    self.filtered_X     = X1
    self.residuals      = (exo @ np.array(EPS).T).T

    if info == 1:
        print('Filtering done in '+str(np.round(time.time()-st,3))+'seconds.')

    return (self.filtered_Z, self.filtered_X, self.residuals)

