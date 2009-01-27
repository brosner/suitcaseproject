"""Standard builder subclass"""

from suitcase.builders.base import BuilderBase

class Packages(BuilderBase):
    
    """A subclass of BuilderBase with the typical defaults"""
    
    def pre_build(self, package_config):
        """Pre build hook"""
        self.packer.pre_build(package_config)

    def build(self, package_config):
        
        """Builds each package in the standard way as defined by packing format
        
        Assumes that the the files are already in the right format for packing.
        """


        self.package_config = {}
        self.package_config = package_config


        self.package_config['working_dir'] = self.make_working_dir()

        self.packer.run_hook('pre_copy')
        self.packer.copy_files_to_package_dir()
        self.packer.run_hook('post_copy')



        self.packer.run_hook('pre_conf')
        self.packer.make_package_conf_files()
        self.packer.run_hook('post_conf')

        self.packer.build_package()
        self.packer.move_package()
