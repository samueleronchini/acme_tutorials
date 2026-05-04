"""
A Cobaya implementation of the Einstein-Telescope likelihood class
Author: Andrea Cozzumbo
Email: calderon@kasi.re.kr 
"""
from cobaya.likelihood import Likelihood
from cobaya.log import LoggedError
from cobaya.conventions import Const 
import sys,os
import numpy as np
import dill as pickle

class MMcosmology(Likelihood):

    def initialize(self):
        """
         Prepare any computation, importing any necessary code, files, etc.

         e.g. here we load some data file, with default dL set in .yaml below,
         or overridden when running Cobaya.
         
         To do: Proper error-handling when data_directory is incorrect/not provided in yaml file
        """

        self.data_file=self.gw_network+'_'+self.fiducial_cosmology+'_'+self.grb_dataset+'.pkl'
        
        try:
            with open(os.path.join(self.data_directory,self.data_file),'rb') as f:
                dataset=pickle.load(f)
        except:
            raise LoggedError(self.log,f"Could not find {self.data_file} in {self.data_directory}. Please provide the absolute path to the directory where the datafiles are stored")

        
        self.log.info("Initialized Einstein-Telescope Likelihood")
        self.log.info("Data file %s read from %s"%(self.data_file,self.data_directory))


        self.z = np.squeeze(dataset[0])
        self.num_events=len(self.z)
        
        density_vp_uncorrected = dataset[1]
        self.dL = dataset[2]
        self.sigma_dL = dataset[3]

        if self.vp_correction:
            self.density = dataset[4]
            print('Taking peculiar velocity correction into account')
        else:
            self.density = density_vp_uncorrected
            

        print('Number of event: ', self.num_events)
           

    def get_requirements(self):
        """
         return dictionary specifying quantities calculated by a theory code are needed

         e.g. here we need D_L(z) and possibly the value of H0 and Om0
        """
        return {'angular_diameter_distance': {'z': self.z}, }

        
    def logp(self, **params_values):
        """
        Taking a dictionary of (sampled) nuisance parameter values params_values
        and return a log-likelihood.
        """
        if self.interpolation_method.lower() == 'gaussian':
            chi2=0
            for i,zi in enumerate(self.z):    
                dL_th=(1+zi)**2 * self.provider.get_angular_diameter_distance(zi)
                chi2+=((dL_th-self.dL[i])/self.sigma_dL[i])**2
            
            log_likelihood = -0.5*chi2
            
            
        elif self.interpolation_method.lower() == 'kde':
            
            log_likelihood=0
            for i,zi in enumerate(self.z):
                
                dL_th=(1+zi)**2 * self.provider.get_angular_diameter_distance(zi)
                
                log_likelihood+=np.log(self.density[i](dL_th))

        return log_likelihood
    
if __name__=='__main__':
    
    MMcosmo=MMcosmology()

