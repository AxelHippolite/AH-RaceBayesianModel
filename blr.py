import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from scipy.stats import multivariate_normal, norm

class Prior:
    def __init__(self, mean, cov):
        self.mean = mean
        self.cov = cov

class BLR:
    def __init__(self, prior, noise_var):
        self.prior_cov = prior.cov
        self.prior_mean = prior.mean
        self.prior = multivariate_normal(self.prior_mean, self.prior_cov)

        self.noise_var = noise_var
        self.noise_prec = 1 / noise_var

        self.post = self.prior
        self.post_cov = self.prior_cov
        self.post_mean = self.prior_mean
        self.post_mean_bis = self.prior_mean

    def compute_design_mat(self, features):
        return np.hstack((np.ones((len(features), 1)), features))

    def update_post(self, features, labels):
        design_mat = self.compute_design_mat(features)
        dmat_prod = design_mat.T.dot(design_mat)

        inv_prior_cov = np.linalg.inv(self.prior_cov)
        self.post_cov = np.linalg.inv(inv_prior_cov + self.noise_prec * dmat_prod)
        self.post_mean = self.noise_prec * self.post_cov.dot(design_mat.T.dot(labels))
        self.post = multivariate_normal(self.post_mean.flatten(), self.post_cov, allow_singular=True)
    
    def predict(self, features):
        design_mat = self.compute_design_mat(features)
        pred_mean = design_mat.dot(self.post_mean)
        pred_cov = design_mat.dot(self.post_cov.dot(design_mat.T)) + self.noise_var
        return norm(pred_mean.flatten(), pred_cov)
    
    def test(self):
        x, y = datasets.make_regression(n_samples=100, n_features=1, noise=10)
        
        self.update_post(x, y)

        mesh_features, mesh_labels = np.mgrid[self.post_mean[0]-0.2:self.post_mean[0]+0.2:.01, self.post_mean[1]-0.2:self.post_mean[1]+0.2:.01]
        pos = np.dstack((mesh_features, mesh_labels))
        samples = self.post.rvs(size=100)

        pred = self.predict(np.reshape(np.array([2]), (1, 1)))
        pred_mean, pred_std = float(pred.mean()), float(pred.std())
        pred_x = np.linspace(pred_mean-2, pred_mean+2, 1000)
        pred_pdf = pred.pdf(pred_x)

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        fig.canvas.manager.set_window_title('Bayesian Approach') 
        fig.suptitle('Bayesian Linear Regression')
        ax1.contourf(mesh_features, mesh_labels, self.post.pdf(pos), levels=15)
        ax1.set_title('Posterior PDF')
        ax1.set_xlabel('Intercept'), ax1.set_ylabel('Slope')
        ax2.scatter(x, y, s=6, color='#470e61')
        for i in range(len(samples)):
            x_sampled = np.linspace(min(x), max(x), 1000)
            ax2.plot(x_sampled, x_sampled * samples[i][1] + samples[i][0], color='#24aa83')
        ax2.set_title('Data')
        ax2.set_xlabel('X')
        ax3.set_title('PDF Predictive Posterior')
        ax3.set_xlabel('Predicted Value')
        ax3.plot(pred_x, pred_pdf.T, color='#24aa83')
        ax3.axvline(pred_mean - 1.96 * pred_std, color='#470e61'), ax3.axvline(pred_mean + 1.96 * pred_std, color='#470e61')
        plt.show()