from __future__ import division

import logging
# logging.basicConfig(level=logging.INFO)
import math

import pandas as pd
from scipy.stats import f


def formatval(v):
    return v if (isinstance(v, str) or int(v) != v) else int(v)


def _plot(
    modelinstance,
    comps=['PC1', 'PC2'],
    classlevels=None,
    markers=None,
    classcolors=None,
    msize=100,
    figsize=(12, 8),
    plotpred=True,
    predsize=None,
    predlevels=None,
    predcolors=None,
    predmarkers=None,
    labels=None,
    predlabels=None,
    textsize=10,
    color='#555555'
):
    """Plot method for plotting scores, with optional classes and predictions"""
    if not markers:
        markers = ['s', '^', 'v', 'o', '<', '>', 'D', 'p']
    if classlevels:
        if not classcolors:
            classcolors = [str(f) for f in pd.np.linspace(0, 1, len(classlevels)+1)[1:]]
        ax = modelinstance.scores.xs(1, level=classlevels[0]).plot(
            kind='scatter',
            x=comps[0], y=comps[1], figsize=figsize, s=msize, zorder=3,
            marker=markers[0], edgecolor='black', linewidth='1', c=classcolors[0])
        for i, lev in enumerate(classlevels[1:]):
            modelinstance.scores.xs(1, level=lev).plot(
                kind='scatter',
                x=comps[0], y=comps[1], s=msize, zorder=3,
                marker=markers[i+1], c=classcolors[i+1],
                edgecolor='black', linewidth='1', ax=ax, grid=True
            )
    else:
        ax = modelinstance.scores.plot(
            kind='scatter',
            x=comps[0], y=comps[1], figsize=figsize, s=msize, zorder=3,
            marker=markers[0], edgecolor='black', linewidth='1', c=color, grid=True)
    el = simpleEllipse(modelinstance.scores[comps[0]], modelinstance.scores[comps[1]], 0.95, 200)
    if labels:
        modelinstance.scores.reset_index(labels).apply(lambda row: ax.annotate(
            row[labels], (row[comps[0]], row[comps[1]]),
            xytext=(10, -5),
            textcoords='offset points',
            size=textsize,
            color='black',
            zorder=4
        ), axis=1)
    ax.plot(el[0], el[1], color='black', linewidth=1)
    ax.axvline(x=0, ls='-', color='black', linewidth=1)
    ax.axhline(y=0, ls='-', color='black', linewidth=1)
    if plotpred and hasattr(modelinstance, 'pred'):
        predsize = predsize or msize * 2
        predmarkers = predmarkers or markers
        try:
            predcolors = predcolors or ['C{}'.format(c+1) for c in range(len(predlevels))]
        except TypeError:
            predcolors = ['C1']
        if predlevels:
            for lev in range(len(predlevels)):
                try:
                    modelinstance.pred.xs(1, level=predlevels[lev]).plot(
                        kind='scatter',
                        x=comps[0], y=comps[1], s=predsize, zorder=5,
                        marker=predmarkers[lev], c=predcolors[lev],
                        edgecolor='black', linewidth='1', ax=ax, grid=True
                    )
                    if not (predlabels is None):
                        modelinstance.pred.xs(1, level=predlevels[lev]).reset_index(predlabels).rename(
                            columns={'index': 'level_0'}
                        ).apply(lambda row: ax.annotate(
                            row[
                                'level_{}'.format(predlabels) if 0 == predlabels else predlabels
                            ],
                            (row[comps[0]], row[comps[1]]),
                            xytext=(10, -5),
                            textcoords='offset points',
                            size=textsize * (2 if predsize is None else (predsize / msize)),
                            color='black',
                            zorder=6
                        ), axis=1)
                except (KeyError, ValueError, IndexError):
                    logging.warning(
                        "Tried to plot prediction data for class {}, but failed. "
                        "Probably there are no datapoints with that class.".format(
                            predlevels[lev]
                        ))
                    raise
        else:
            modelinstance.pred.plot(
                kind='scatter',
                x=comps[0], y=comps[1], s=predsize, zorder=6,
                marker=predmarkers[0], c=predcolors[0],
                edgecolor='black', linewidth='1', ax=ax, grid=True
            )
            if not (predlabels is None):
                modelinstance.pred.reset_index(predlabels).rename(
                    columns={'index': 'level_0'}
                ).apply(lambda row: ax.annotate(
                    formatval(row[
                        'level_{}'.format(predlabels) if 0 == predlabels else predlabels
                    ]),
                    (row[comps[0]], row[comps[1]]),
                    xytext=(10, -5),
                    textcoords='offset points',
                    size=textsize * (2 if predsize is None else (predsize / msize)),
                    color='black',
                    zorder=7
                ), axis=1)
    return ax.figure


def _loadingsplot(
    modelinstance,
    comps=['PC1', 'PC2'],
    markers=None,
    color='0.7',
    msize=100,
    figsize=(12, 8),
    showweights=True,
    weightmarkers=None,
    weightcolors=None,
    weightsize=200,
    labels=True,
    textsize=10
):
    """Plot method for plotting loadings"""
    try:
        _loadings = modelinstance.weights
    except AttributeError:
        _loadings = modelinstance.loadings
    ax = _loadings.plot(
        kind='scatter', x=comps[0], y=comps[1], figsize=figsize, s=msize,
        c=color, edgecolor='black', grid=True, zorder=3
    )
    if labels:
        _loadings.apply(lambda row: ax.annotate(
            row.name, (row[comps[0]], row[comps[1]]),
            xytext=(10, -5),
            textcoords='offset points',
            size=textsize,
            color='black',
            zorder=4
        ), axis=1)
    if showweights:
        if weightmarkers is None:
            modelinstance.q.plot(
                kind='scatter', x=comps[0], y=comps[1], s=weightsize,
                c=weightcolors or 'blue', edgecolor='black', grid=True, zorder=5, ax=ax
            )
        else:
            for _m, _c, _x, _y in zip(
                weightmarkers,
                weightcolors or ['blue'] * len(weightmarkers),
                modelinstance.q[comps[0]],
                modelinstance.q[comps[1]]
            ):
                ax.scatter(
                    _x, _y, marker=_m, c=_c, s=weightsize,
                    edgecolor='k', zorder=5
                )
        if labels:
            modelinstance.q.apply(lambda row: ax.annotate(
                row.name, (row[comps[0]], row[comps[1]]),
                xytext=(10, -5),
                textcoords='offset points',
                size=textsize * weightsize / msize,
                color='black',
                zorder=6
            ), axis=1)
    ax.axvline(x=0, ls='-', color='black', linewidth=1, zorder=2.7)
    ax.axhline(y=0, ls='-', color='black', linewidth=1, zorder=2.7)
    return ax.figure


def simpleEllipse(x, y, alfa, length):
    """Helper function to calculate Hotelling's ellipse from scores
    Ported from the bioconductor package pcaMethods, https://doi.org/doi:10.18129/B9.bioc.pcaMethods
    Stacklies W, Redestig H, Scholz M, Walther D and Selbig J (2007).
    “pcaMethods – a Bioconductor package providing PCA methods for incomplete data.”
    Bioinformatics, 23, pp. 1164–1167.
    """
    n = len(x)
    mypi = [i/(length-1)*pd.np.pi*2 for i in range(length)]
    r1 = pd.np.sqrt(x.var() * f.ppf(alfa, 2, n-2) * 2 * (n**2 - 1) / (n * (n - 2)))
    r2 = pd.np.sqrt(y.var() * f.ppf(alfa, 2, n-2) * 2 * (n**2 - 1) / (n * (n - 2)))
    return r1 * pd.np.cos(mypi) + x.mean(), r2 * pd.np.sin(mypi) + y.mean()


class PLS(object):
    """A class for PLS calculated by the NIPALS algorithm.

    Initialize with a Pandas DataFrame or an object that can be turned into a DataFrame
    (e.g. an array or a dict of lists)"""
    def __init__(self, x_df, y_df):
        super(PLS, self).__init__()
        if type(x_df) != pd.core.frame.DataFrame:
            x_df = pd.DataFrame(x_df)
        if type(y_df) != pd.core.frame.DataFrame:
            y_df = pd.DataFrame(y_df)
        # Make sure data is numeric
        self.x_df = x_df.astype('float')
        self.y_df = y_df.astype('float')
        # Check for and remove infs
        if pd.np.isinf(self.x_df).any().any():
            logging.warning("X data contained infinite values, converting to missing values")
            self.x_df.replace([pd.np.inf, -pd.np.inf], pd.np.nan, inplace=True)
        if pd.np.isinf(self.y_df).any().any():
            logging.warning("Y data contained infinite values, converting to missing values")
            self.y_df.replace([pd.np.inf, -pd.np.inf], pd.np.nan, inplace=True)

    def fit(
        self,
        ncomp=None,
        center=True,
        scale=True,
        startcol=None,
        tol=0.000001,
        maxiter=500,
        cv=False
    ):
        """The Fit method, will fit a PLS to the X and Y data"""
        if ncomp is None:
            ncomp = min(self.x_df.shape)
        elif ncomp > min(self.x_df.shape):
            ncomp = min(self.x_df.shape)
            logging.warning(
                'ncomp is larger than the max dimension of the x matrix.\n'
                'fit will only return {} components'.format(ncomp)
            )

        # Convert to np array
        self.x_mat = self.x_df.values
        self.y_mat = self.y_df.values
        if center:
            self.x_mean = pd.np.nanmean(self.x_mat, axis=0)
            self.x_mat = self.x_mat - self.x_mean
            self.y_mean = pd.np.nanmean(self.y_mat, axis=0)
            self.y_mat = self.y_mat - self.y_mean
        if scale:
            self.x_std = pd.np.nanstd(self.x_mat, axis=0, ddof=1)
            self.x_mat = self.x_mat / self.x_std
            self.y_std = pd.np.nanstd(self.y_mat, axis=0, ddof=1)
            self.y_mat = self.y_mat / self.y_std

        TotalSSX = pd.np.nansum(self.x_mat*self.x_mat)
        TotalSSY = pd.np.nansum(self.y_mat*self.y_mat)
        nr, x_nc = self.x_mat.shape
        y_nc = self.y_mat.shape[1]
        # initialize outputs
        # eig = pd.np.empty((ncomp,))
        R2Xcum = pd.np.empty((ncomp,))
        R2Ycum = pd.np.empty((ncomp,))
        PRESS_SS = pd.np.empty((ncomp,))
        loadings = pd.np.empty((x_nc, ncomp))
        scores = pd.np.empty((nr, ncomp))
        u = pd.np.empty((nr, ncomp))
        weights = pd.np.empty((x_nc, ncomp))
        q = pd.np.empty((y_nc, ncomp))
        b = pd.np.empty((ncomp,))

        # NA handling
        x_miss = pd.np.isnan(self.x_mat)
        x_hasna = x_miss.any()
        y_miss = pd.np.isnan(self.y_mat)
        y_hasna = y_miss.any()
        if x_hasna or y_hasna:
            logging.info("Data has NA values")

        if cv:
            if cv is True:
                cv = 7
            cvn = int(pd.np.ceil(nr / cv))
            cvgroups = pd.np.array(range(cvn * cv)).reshape(cvn, cv).T
        else:
            cv = 0
        for comp in range(ncomp):
            PRESS = 0
            for cvround in range(cv + 1):
                if cvround >= cv:
                    # Calculate on full matrix after CV rounds
                    train_x_mat = self.x_mat
                    train_y_mat = self.y_mat
                else:
                    train_x_mat = pd.np.delete(self.x_mat, cvgroups[cvround], 0)
                    train_y_mat = pd.np.delete(self.y_mat, cvgroups[cvround], 0)
                nrt, x_nct = train_x_mat.shape
                y_nct = train_y_mat.shape[1]
                train_x_miss = pd.np.isnan(train_x_mat)
                train_y_miss = pd.np.isnan(train_y_mat)
                # Set u to some column of Y
                if startcol is None:
                    yvar = pd.np.nanvar(self.y_mat, axis=0, ddof=1)
                    startcol_use = pd.np.where(yvar == yvar.max())[0][0]
                else:
                    startcol_use = startcol
                logging.info("PC {}, starting with column {}".format(comp, startcol_use))

                if y_hasna:
                    train_y_mat_0 = pd.np.nan_to_num(train_y_mat)
                    uh = train_y_mat_0[:, startcol_use]
                else:
                    uh = train_y_mat[:, startcol_use]
                th = uh

                if x_hasna:
                    train_x_mat_0 = pd.np.nan_to_num(train_x_mat)

                it = 0
                while True:
                    # X-block weights
                    if x_hasna:
                        U2 = pd.np.repeat(uh*uh, x_nct)
                        U2.shape = (nrt, x_nct)
                        U2[train_x_miss] = 0
                        wh = train_x_mat_0.T.dot(uh) / U2.sum(axis=0)
                    else:
                        wh = train_x_mat.T.dot(uh) / sum(uh*uh)
                    # Normalize
                    wh = wh / math.sqrt(pd.np.nansum(wh*wh))

                    # X-block Scores
                    th_old = th
                    if x_hasna:
                        W2 = pd.np.repeat(wh*wh, nrt)
                        W2.shape = (x_nct, nrt)
                        W2[train_x_miss.T] = 0
                        th = train_x_mat_0.dot(wh) / W2.sum(axis=0)
                    else:
                        th = train_x_mat.dot(wh) / sum(wh*wh)

                    # Y-block weights
                    if y_hasna:
                        T2 = pd.np.repeat(th*th, y_nct)
                        T2.shape = (nrt, y_nct)
                        T2[train_y_miss] = 0
                        qh = train_y_mat_0.T.dot(th) / T2.sum(axis=0)
                    else:
                        qh = train_y_mat.T.dot(th) / sum(th*th)
                    # Normalize
                    # According to Analytica Chimica Acta, 186 (1986) 1-17 this normalization
                    # should be done. However, if so, the results are not the same as th R package
                    # pls plsr method or Evince.
                    # qh = qh / math.sqrt(pd.np.nansum(qh*qh))

                    # Y-block Scores
                    if y_hasna:
                        Q2 = pd.np.repeat(qh*qh, nrt)
                        Q2.shape = (y_nct, nrt)
                        Q2[train_y_miss.T] = 0
                        uh = train_y_mat_0.dot(qh) / Q2.sum(axis=0)
                    else:
                        uh = train_y_mat.dot(qh) / sum(qh*qh)

                    # Check convergence
                    if pd.np.nansum((th-th_old)**2) < tol:
                        break
                    it += 1
                    if it >= maxiter:
                        raise RuntimeError(
                            "Convergence was not reached in {} iterations for component {}".format(
                                maxiter, comp
                            )
                        )

                # Calculate PRESS for this CV
                if cvround < cv:
                    pred_x_mat = self.x_mat[[i for i in cvgroups[cvround] if i < nr]]
                    pred_y_mat = self.y_mat[[i for i in cvgroups[cvround] if i < nr]]
                    pred_x_mat = pd.np.nan_to_num(pred_x_mat)
                    cv_th = pred_x_mat.dot(wh) / sum(wh*wh)
                    cv_bh = sum(uh*th)/sum(th**2)
                    cv_res = pred_y_mat - cv_bh*pd.np.outer(cv_th, qh)
                    cv_res[pd.np.isnan(pred_y_mat)] = 0
                    PRESS += pd.np.sum(cv_res**2)

            PRESS_SS[comp] = PRESS / pd.np.nansum(self.y_mat*self.y_mat)

            # Calculate X loadings and rescale the scores and weights
            if x_hasna:
                T2 = pd.np.repeat(th*th, x_nc)
                T2.shape = (nr, x_nc)
                T2[x_miss] = 0
                ph = train_x_mat_0.T.dot(th) / T2.sum(axis=0)
            else:
                ph = train_x_mat.T.dot(th) / sum(th*th)
            # Normalize
            # According to Analytica Chimica Acta, 186 (1986) 1-17 this normalization
            # should be done. However, if so, the results are not the same as th R package
            # pls plsr method or Evince.
            # pold_len = math.sqrt(pd.np.nansum(ph*ph))
            # ph = ph / pold_len
            # th = th * pold_len
            # wh = wh * pold_len
            loadings[:, comp] = ph
            scores[:, comp] = th
            u[:, comp] = uh
            q[:, comp] = qh
            weights[:, comp] = wh
            bh = sum(uh*th)/sum(th**2)
            b[comp] = bh

            self.x_mat = self.x_mat - pd.np.outer(th, ph)
            self.y_mat = self.y_mat - bh*pd.np.outer(th, qh)

            # Cumulative proportion of variance explained
            R2Xcum[comp] = 1 - (pd.np.nansum(self.x_mat*self.x_mat) / TotalSSX)
            R2Ycum[comp] = 1 - (pd.np.nansum(self.y_mat*self.y_mat) / TotalSSY)

        # "Uncumulate" R2
        self.R2X = pd.np.insert(pd.np.diff(R2Xcum), 0, R2Xcum[0])
        self.R2Y = pd.np.insert(pd.np.diff(R2Ycum), 0, R2Ycum[0])
        self.R2Xcum = pd.Series(R2Xcum, index=["PC{}".format(i+1) for i in range(ncomp)])
        self.R2Ycum = pd.Series(R2Ycum, index=["PC{}".format(i+1) for i in range(ncomp)])

        if cv:
            self.PRESS_SS = pd.Series(PRESS_SS, index=["PC{}".format(i+1) for i in range(ncomp)])
            self.Q2 = 1 - self.PRESS_SS
            self.Q2cum = 1 - pd.np.cumprod(self.PRESS_SS)

        # Convert results to DataFrames
        self.scores = pd.DataFrame(scores, index=self.x_df.index, columns=["PC{}".format(i+1) for i in range(ncomp)])
        self.loadings = pd.DataFrame(loadings, index=self.x_df.columns, columns=["PC{}".format(i+1) for i in range(ncomp)])
        self.u = pd.DataFrame(u, index=self.x_df.index, columns=["PC{}".format(i+1) for i in range(ncomp)])
        self.q = pd.DataFrame(q, index=self.y_df.columns, columns=["PC{}".format(i+1) for i in range(ncomp)])
        self.weights = pd.DataFrame(weights, index=self.x_df.columns, columns=["PC{}".format(i+1) for i in range(ncomp)])
        self.b = pd.Series(b, index=["PC{}".format(i+1) for i in range(ncomp)])
        return True

    def dModY(self):
        """
        Calculates DModY for model, ported from pcaMethods
        (Stacklies W, Redestig H, Scholz M, Walther D and Selbig J (2007).
        “pcaMethods – a Bioconductor package providing PCA methods for incomplete
        data.” Bioinformatics, 23, pp. 1164–1167.)
        Modified to scale with mean
        """
        nr, nc = self.y_mat.shape
        ncomp = self.scores.shape[1]
        A0 = 0 if type(self.y_mean) == int else 1
        ny = pd.np.sqrt(nr / (nr - ncomp - A0))
        F2 = self.y_mat*self.y_mat
        s = pd.np.sqrt(pd.np.nansum(F2, axis=1) / (nc - ncomp)) * ny
        S0 = pd.np.sqrt(pd.np.nansum(F2)/((nr - ncomp - A0) * (nc - ncomp)))
        return s/S0

    def dModX(self):
        """
        Calculates DModX for model, ported from pcaMethods
        (Stacklies W, Redestig H, Scholz M, Walther D and Selbig J (2007).
        “pcaMethods – a Bioconductor package providing PCA methods for incomplete
        data.” Bioinformatics, 23, pp. 1164–1167.)
        Modified to scale with mean
        """
        nr, nc = self.x_mat.shape
        ncomp = self.scores.shape[1]
        A0 = 0 if type(self.x_mean) == int else 1
        ny = pd.np.sqrt(nr / (nr - ncomp - A0))
        E2 = self.x_mat*self.x_mat
        s = pd.np.sqrt(pd.np.nansum(E2, axis=1) / (nc - ncomp)) * ny
        S0 = pd.np.sqrt(pd.np.nansum(E2)/((nr - ncomp - A0) * (nc - ncomp)))
        return s/S0

    def plot(
        self,
        comps=['PC1', 'PC2'],
        classlevels=None,
        markers=None,
        classcolors=None,
        msize=100,
        figsize=(12, 8),
        plotpred=True,
        predsize=None,
        predlevels=None,
        predcolors=None,
        predmarkers=None,
        labels=None,
        predlabels=None,
        color='#555555'
    ):
        """Plot method for plotting scores, with optional classes and predictions"""
        return _plot(
            self, comps, classlevels, markers, classcolors, msize,
            figsize, plotpred, predsize, predlevels, predcolors, predmarkers,
            labels, predlabels, 10, color
        )

    def loadingsplot(
        self,
        comps=['PC1', 'PC2'],
        markers=None,
        color='0.7',
        msize=100,
        figsize=(12, 8),
        showweights=True,
        weightmarkers=None,
        weightcolors=None,
        weightsize=200,
        labels=True,
        textsize=10
    ):
        """Plot method for plotting loadings and optionally weights"""
        return _loadingsplot(
            modelinstance=self,
            comps=comps,
            markers=markers,
            color=color,
            msize=msize,
            figsize=figsize,
            showweights=showweights,
            weightmarkers=weightmarkers,
            weightcolors=weightcolors,
            weightsize=weightsize,
            labels=labels,
            textsize=textsize
        )

    def overviewplot(self):
        return pd.DataFrame(
            {
                'R2Y(cum)': self.R2Ycum,
                'Q2(cum)': getattr(self, 'Q2cum', None)
            },
            columns=['R2Y(cum)', 'Q2(cum)']
        ).plot(kind='bar', color=['g', 'b']).figure

    def dModXPlot(self):
        dmx = self.dModX()
        nr, nc = self.x_mat.shape
        ncomp = self.scores.shape[1]
        A0 = 0 if type(self.x_mean) == int else 1
        fc = pd.np.sqrt(f.isf(0.05, nr - ncomp - A0, nc - ncomp))
        ax = pd.Series(dmx, index=self.x_df.index.get_level_values(0)).plot(kind='bar', color='green')
        ax.hlines(fc, -1, 20)
        return ax.figure

    def dModYPlot(self):
        dmy = self.dModY()
        nr, nc = self.y_mat.shape
        ncomp = self.scores.shape[1]
        A0 = 0 if type(self.y_mean) == int else 1
        fc = pd.np.sqrt(f.isf(0.05, nr - ncomp - A0, nc - ncomp))
        ax = pd.Series(dmy, index=self.y_df.index.get_level_values(0)).plot(kind='bar', color='green')
        ax.hlines(fc, -1, 20)
        return ax.figure


class Nipals(object):
    """A Nipals class that can be used for PCA.

    Initialize with a Pandas DataFrame or an object that can be turned into a DataFrame
    (e.g. an array or a dict of lists)"""
    def __init__(self, x_df):
        super(Nipals, self).__init__()
        if type(x_df) != pd.core.frame.DataFrame:
            x_df = pd.DataFrame(x_df)
        self.x_df = x_df
        # Make sure data is numeric
        self.x_df = x_df.astype('float')
        # Check for and remove infs
        if pd.np.isinf(self.x_df).any().any():
            logging.warning("Data contained infinite values, converting to missing values")
            self.x_df.replace([pd.np.inf, -pd.np.inf], pd.np.nan, inplace=True)

    def _onecomp(self, mat, comp, hasna, startcol, tol, maxiter):
        nrt, nct = mat.shape
        miss = pd.np.isnan(mat)
        # Set t to column of X with highest var
        if startcol is None:
            xvar = pd.np.nanvar(mat, axis=0, ddof=1)
            startcol_use = pd.np.where(xvar == xvar.max())[0][0]
        else:
            startcol_use = startcol
        logging.info("PC {}, starting with column {}".format(comp, startcol_use))

        if hasna:
            mat_0 = pd.np.nan_to_num(mat)
            th = mat_0[:, startcol_use]
        else:
            th = mat[:, startcol_use]
        it = 0
        while True:
            # loadings
            if hasna:
                T2 = pd.np.repeat(th*th, nct)
                T2.shape = (nrt, nct)
                T2[miss] = 0
                ph = mat_0.T.dot(th) / T2.sum(axis=0)
            else:
                ph = mat.T.dot(th) / sum(th*th)
            # Normalize
            ph = ph / math.sqrt(pd.np.nansum(ph*ph))

            # Scores
            th_old = th
            if hasna:
                P2 = pd.np.repeat(ph*ph, nrt)
                P2.shape = (nct, nrt)
                P2[miss.T] = 0
                th = mat_0.dot(ph) / P2.sum(axis=0)
            else:
                th = mat.dot(ph) / sum(ph*ph)

            # Check convergence
            if pd.np.nansum((th-th_old)**2) < tol:
                break
            it += 1
            if it >= maxiter:
                raise RuntimeError(
                    "Convergence was not reached in {} iterations for component {}".format(
                        maxiter, comp
                    )
                )
        return th, ph

    def fit(
        self,
        ncomp=None,
        tol=0.000001,
        center=True,
        scale=True,
        maxiter=500,
        startcol=None,
        eigsweep=False,
        cv=False
    ):
        """The Fit method, will fit a PCA to the X data.

        Keyword arguments:
        ncomp - number of components, defaults to all
        tol - tolerance for convergence checking, defaults to 1E-6
        center - whether to center the data, defaults to True
        scale - whether to scale the data, defaults to True
        maxiter - maximum number of iterations before convergence is considered failed, defaults to 500
        startcol - column in X data to start iteration from, if set to None, the column with maximal variance is selected, defaults to None
        eigsweep - whether to sweep out eigenvalues from the final scores, defaults to False"""
        self.eigsweep = eigsweep
        if ncomp is None:
            ncomp = min(self.x_df.shape)
        elif ncomp > min(self.x_df.shape):
            ncomp = min(self.x_df.shape)
            logging.warning(
                'ncomp is larger than the max dimension of the x matrix.\n'
                'fit will only return {} components'.format(ncomp)
            )
        # Convert to np array
        self.x_mat = self.x_df.values
        if center:
            self.x_mean = pd.np.nanmean(self.x_mat, axis=0)
            self.x_mat = self.x_mat - self.x_mean
        else:
            self.x_mean = 0
        if scale:
            self.x_std = pd.np.nanstd(self.x_mat, axis=0, ddof=1)
            self.x_mat = self.x_mat / self.x_std
        else:
            self.x_std = 1

        TotalSS = pd.np.nansum(self.x_mat*self.x_mat)
        nr, nc = self.x_mat.shape
        # initialize outputs
        eig = pd.np.empty((ncomp,))
        R2cum = pd.np.empty((ncomp,))
        PRESS_SS = pd.np.empty((ncomp,))
        loadings = pd.np.empty((nc, ncomp))
        scores = pd.np.empty((nr, ncomp))

        # NA handling
        x_miss = pd.np.isnan(self.x_mat)
        hasna = x_miss.any()
        if hasna:
            logging.info("Data has NA values")

        # self.x_mat_0 = pd.np.nan_to_num(self.x_mat)
        # t = [None] * ncomp
        # p = [None] * ncomp
        self.eig = []
        if cv:
            if cv is True:
                cv = 7
            cvxn = int(pd.np.ceil(nr / cv))
            cvxgroups = pd.np.array(range(cvxn * cv)).reshape(cvxn, cv).T
            cvyn = int(pd.np.ceil(nc / cv))
            cvygroups = pd.np.array(range(cvyn * cv)).reshape(cvyn, cv).T
        else:
            cv = 0
        for comp in range(ncomp):
            # Matrixes to keep ps and ts from cv folds
            cvP = pd.np.empty((nr, nc))
            cvT = pd.np.empty((nr, nc))
            PRESS = 0
            # Calculate on full matrix
            th, ph = self._onecomp(self.x_mat, comp, hasna, startcol, tol, maxiter)
            for cvround in range(cv):
                train_mat = pd.np.delete(self.x_mat, cvxgroups[cvround], 0)
                _, ph_cv = self._onecomp(train_mat, comp, hasna, startcol, tol, maxiter)
                train_mat = pd.np.delete(self.x_mat, cvygroups[cvround], 1)
                th_cv, _ = self._onecomp(train_mat, comp, hasna, startcol, tol, maxiter)
                # Make sure the PCs are rotated in the same main direction for all cvs
                if pd.np.corrcoef(ph, ph_cv)[1, 0] < 0:
                    cvP[[grp for grp in cvxgroups[cvround] if grp < nr]] = -ph_cv
                else:
                    cvP[[grp for grp in cvxgroups[cvround] if grp < nr]] = ph_cv
                if pd.np.corrcoef(th, th_cv)[1, 0] < 0:
                    cvT.T[[grp for grp in cvygroups[cvround] if grp < nc]] = -th_cv
                else:
                    cvT.T[[grp for grp in cvygroups[cvround] if grp < nc]] = th_cv
            # Calculate PRESS
            if cv:
                pred_mat = cvP * cvT
                cv_res = self.x_mat - pred_mat
                cv_res[x_miss] = 0
                PRESS = pd.np.sum(cv_res**2)

            PRESS_SS[comp] = PRESS / pd.np.nansum(self.x_mat*self.x_mat)
            # Update X
            self.x_mat = self.x_mat - pd.np.outer(th, ph)
            loadings[:, comp] = ph
            scores[:, comp] = th
            eig[comp] = pd.np.nansum(th*th)

            # Cumulative proportion of variance explained
            R2cum[comp] = 1 - (pd.np.nansum(self.x_mat*self.x_mat) / TotalSS)

        # "Uncumulate" R2
        self.R2 = pd.np.insert(pd.np.diff(R2cum), 0, R2cum[0])
        self.R2cum = pd.Series(R2cum, index=["PC{}".format(i+1) for i in range(ncomp)])

        # Finalize eigenvalues and subtract from scores
        self.eig = pd.Series(pd.np.sqrt(eig))
        if self.eigsweep:
            scores = scores / self.eig.values
        if cv:
            self.PRESS_SS = pd.Series(PRESS_SS, index=["PC{}".format(i+1) for i in range(ncomp)])
            self.Q2 = 1 - self.PRESS_SS
            self.Q2cum = 1 - pd.np.cumprod(self.PRESS_SS)

        # Convert results to DataFrames
        self.scores = pd.DataFrame(scores, index=self.x_df.index, columns=["PC{}".format(i+1) for i in range(ncomp)])
        self.loadings = pd.DataFrame(loadings, index=self.x_df.columns, columns=["PC{}".format(i+1) for i in range(ncomp)])
        return True

    def dModX(self):
        """
        Calculates DModX for model, ported from pcaMethods
        (Stacklies W, Redestig H, Scholz M, Walther D and Selbig J (2007).
        “pcaMethods – a Bioconductor package providing PCA methods for incomplete
        data.” Bioinformatics, 23, pp. 1164–1167.)
        Modified to scale with mean
        """
        nr, nc = self.x_mat.shape
        ncomp = self.scores.shape[1]
        A0 = 0 if type(self.x_mean) == int else 1
        ny = pd.np.sqrt(nr / (nr - ncomp - A0))
        E2 = self.x_mat*self.x_mat
        s = pd.np.sqrt(pd.np.nansum(E2, axis=1) / (nc - ncomp)) * ny
        S0 = pd.np.sqrt(pd.np.nansum(E2)/((nr - ncomp - A0) * (nc - ncomp)))
        return s/S0

    def loadingsplot(
        self,
        comps=['PC1', 'PC2'],
        msize=100,
        figsize=(12, 8),
    ):
        """Plot method for plotting loadings"""
        return _loadingsplot(
            modelinstance=self,
            comps=comps,
            markers=None,
            color='0.7',
            msize=msize,
            figsize=figsize,
            showweights=False,
            weightmarkers=None,
            weightcolors=None,
            weightsize=None,
            labels=True,
            textsize=10
        )

    def plot(
        self,
        comps=['PC1', 'PC2'],
        classlevels=None,
        markers=None,
        classcolors=None,
        msize=100,
        figsize=(12, 8),
        plotpred=True,
        predsize=None,
        predlevels=None,
        predcolors=None,
        predmarkers=None,
        labels=None,
        predlabels=None,
        textsize=10,
        color='#555555'
    ):
        """Plot method for plotting scores, with optional classes and predictions"""
        return _plot(
            self, comps, classlevels, markers, classcolors, msize,
            figsize, plotpred, predsize, predlevels, predcolors, predmarkers,
            labels, predlabels, textsize, color
        )

    def predict(self, new_x):
        self.new_x = (new_x - self.x_mean) / self.x_std
        self.new_x = self.new_x.fillna(0)
        self.pred = self.new_x.dot(self.loadings)
        if self.eigsweep:
            self.pred = self.pred / self.eig.values
        return True

    def overviewplot(self):
        return pd.DataFrame(
            {
                'R2(cum)': self.R2cum,
                'Q2(cum)': getattr(self, 'Q2cum', None)
            },
            columns=['R2(cum)', 'Q2(cum)']
        ).plot(kind='bar', color=['g', 'b']).figure

    def dModXPlot(self):
        dmx = self.dModX()
        nr, nc = self.x_mat.shape
        ncomp = self.scores.shape[1]
        A0 = 0 if type(self.x_mean) == int else 1
        fc = pd.np.sqrt(f.isf(0.05, nr - ncomp - A0, nc - ncomp))
        ax = pd.Series(dmx, index=self.x_df.index.get_level_values(0)).plot(kind='bar', color='green')
        ax.hlines(fc, -1, 20)
        return ax.figure
