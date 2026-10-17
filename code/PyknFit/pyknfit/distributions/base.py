from abc import ABC, abstractmethod
import numpy as np

class Distribution(ABC):

    @property
    def use_log_scale(self):
        return False
    
    @abstractmethod
    def pdf(self, x, params):
        pass

    @abstractmethod
    def logpdf(self, x, params):
        pass

    @abstractmethod
    def sample(self, n, params):
        pass

    @abstractmethod
    def initialize(self, x, y):
        pass
        
    @abstractmethod
    def create_initial_params(
        self,
        center,
        sigma,
        amplitude
    ):
        pass
        
    @abstractmethod
    def pack_theta(self, params):
        pass

    @abstractmethod
    def unpack_theta(self, theta):
        pass

    @abstractmethod
    def bounds(self):
        pass
        
    @abstractmethod
    def gui_center_value(self, params):
        pass

    @abstractmethod
    def gui_width_value(self, params):
        pass
        
    @abstractmethod
    def table_info(self, params):
        pass
        
    @abstractmethod
    def formula_description(self):
        pass
        
    @abstractmethod
    def derived_quantities_description(self):
        pass